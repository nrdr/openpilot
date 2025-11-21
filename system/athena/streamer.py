import asyncio
import json
import logging
import queue
import subprocess
import threading
import time
from typing import Optional

from openpilot.common.api import Api, api_get
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
import cereal.messaging as messaging

try:
    from aiortc import (
        RTCPeerConnection, RTCConfiguration, RTCSessionDescription,
        RTCDataChannel, RTCRtpCodecCapability, RTCIceServer
    )
    from aiortc.sdp import candidate_from_sdp
    HAS_AIORTC = True
except ImportError:
    HAS_AIORTC = False

try:
    from openpilot.system.webrtc.device.video import LiveStreamVideoStreamTrack
    HAS_VIDEO_TRACK = True
except ImportError:
    HAS_VIDEO_TRACK = False

logger = logging.getLogger(__name__)


def capture_pane(session_window_pane: str) -> str | None:
  """
  Capture the output of a tmux pane and return it as JSON.
  """
  try:
    result = subprocess.run(
      ["tmux", "capture-pane", "-peJS-7200", "-t", session_window_pane],
      capture_output=True,
      text=True,
      check=False
    )
    if result.returncode != 0:
      logger.warning("tmux capture-pane returned code %d: %s", result.returncode, result.stderr)
      return None
    return json.dumps({"tmuxCapture": result.stdout})
  except Exception:
    logger.exception("Exception while capturing pane '%s':", session_window_pane)
    return None


class ControllerHandler:
  """
  Safety-focused handler for Xbox controller inputs using asyncio
  """
  def __init__(self, safety_timeout=0.5):
    self.last_input_time = time.time()
    self.throttle = 0.0
    self.steering = 0.0
    self.safety_timeout = safety_timeout
    self.input_active = False
    self.lock = asyncio.Lock()
    self.safety_monitor_task = None
    self.running = True
    self.joystick_sock = messaging.pub_sock('testJoystick')
    logger.info("Controller handler initialized with safety timeout: %.2f seconds", safety_timeout)

  async def handle_controller_message(self, message_data):
    try:
      data = message_data
      if data.get('action') != 'controller':
        return False

      async with self.lock:
        self.throttle = data.get('throttle', 0.0)
        self.steering = data.get('steering', 0.0)
        self.last_input_time = time.time()
        self.input_active = True

      # Log the received input
      # logger.info(f"Controller input: throttle={self.throttle:.2f}, steering={self.steering:.2f}")

      await self.apply_control(self.throttle, self.steering)
      return True

    except Exception as e:
      logger.error(f"Error handling controller message: {str(e)}")
      return False

  async def apply_control(self, throttle, steering):
    # logger.debug(f"Applied control: throttle={throttle:.2f}, steering={steering:.2f}")
    dat = messaging.new_message('testJoystick')
    dat.testJoystick.axes = [throttle, steering]
    dat.testJoystick.buttons = [False]
    self.joystick_sock.send(dat.to_bytes())

  async def shutdown(self):
    logger.info("Shutting down controller handler")
    self.running = False
    if self.safety_monitor_task and not self.safety_monitor_task.done():
      self.safety_monitor_task.cancel()
      try:
        await self.safety_monitor_task
      except asyncio.CancelledError:
        pass
    async with self.lock:
      self.throttle = 0.0
      self.steering = 0.0
      await self.apply_control(0.0, 0.0)


class Streamer:
  def __init__(self, sdp_send_queue: queue.Queue, sdp_recv_queue: queue.Queue, ice_send_queue: queue.Queue):
    logger.info("Initializing Streamer instance.")

    if not HAS_AIORTC:
        logger.error("aiortc not available. Install with: pip install aiortc")
        raise ImportError("aiortc is required for streaming functionality")

    self.sdp_send_queue = sdp_send_queue
    self.sdp_recv_queue = sdp_recv_queue
    self.ice_send_queue = ice_send_queue
    self.params = Params()
    self.onroad = self.params.get_bool("IsOnroad")

    dongle_id = self.params.get("DongleId")
    if isinstance(dongle_id, bytes):
        dongle_id = dongle_id.decode('utf8')
    self.api = Api(dongle_id)

    self.controller_handler = ControllerHandler(safety_timeout=0.5)
    self.tracks: dict[str, LiveStreamVideoStreamTrack] = {}
    self.pc: Optional[RTCPeerConnection] = None
    self.data_channel: Optional[RTCDataChannel] = None

  def get_ice_configuration(self):
    try:
      ice_servers_data = api_get('/v1/iceservers', timeout=5, access_token=self.api.get_token()).content
      ice_servers = [
        RTCIceServer(urls=server["urls"], username=server["username"], credential=server["credential"])
        for server in json.loads(ice_servers_data)
      ]
    except Exception:
      logger.exception("Failed to fetch ICE servers:")
      ice_servers = [RTCIceServer(urls="stun:stun.l.google.com:19302")]

    configuration = RTCConfiguration(iceServers=ice_servers)
    return configuration

  def attach_data_channel_handlers(self):
    if not self.data_channel:
        return

    def on_open():
        pass

    def on_message(message: str):
        try:
            msg = json.loads(message)
            action = msg.get("action")

            if action == "controller":
                if not self.params.get_bool("JoystickDebugMode"):
                    self.params.put_bool("JoystickDebugMode", True)
                asyncio.create_task(self.controller_handler.handle_controller_message(msg))
            elif action == "captureTmux":
                capture_result = capture_pane("comma:0.0")
                if capture_result:
                    try:
                        self.data_channel.send(capture_result)
                    except Exception:
                        pass
        except Exception:
            logger.exception("Error handling data channel message:")

    self.data_channel.on("open", on_open)
    self.data_channel.on("message", on_message)

  async def event_loop(self, end_event: threading.Event):
    cloudlog.info("Streamer event loop started")

    while not end_event.is_set():
      try:
        # Wait for start signal
        try:
          data = self.sdp_recv_queue.get(timeout=1.0)
        except queue.Empty:
          await asyncio.sleep(0.1)
          continue

        if not data or data.get('type') != 'start':
          continue

        cloudlog.info("Processing start signal")

        # Set LiveStreamRunning
        if not self.params.get_bool("IsOnroad"):
          self.params.put_bool("LiveStreamRunning", True)
          cloudlog.info("LiveStreamRunning set to True")

        # Create PeerConnection
        cloudlog.info("Creating WebRTC peer connection...")
        ice_config = self.get_ice_configuration()
        self.pc = RTCPeerConnection(ice_config)

        # Add video tracks
        cloudlog.info("Adding video tracks...")
        try:
          if HAS_VIDEO_TRACK:
            if self.params.get_bool("RecordFront"):
              driver_track = LiveStreamVideoStreamTrack("driver")
              driver_track.paused = False
              self.pc.addTrack(driver_track)
              cloudlog.info("Added driver video track")

            if self.params.get_bool("RecordRoad"):
              road_track = LiveStreamVideoStreamTrack("road")
              road_track.paused = False
              self.pc.addTrack(road_track)
              cloudlog.info("Added road video track")

              wide_road_track = LiveStreamVideoStreamTrack("wideRoad")
              wide_road_track.paused = False
              self.pc.addTrack(wide_road_track)
              cloudlog.info("Added wideRoad video track")
          else:
            cloudlog.error("LiveStreamVideoStreamTrack not available")
        except Exception as e:
          cloudlog.error(f"Failed to add video tracks: {e}")

        # Configure H264
        try:
          h264_capability = RTCRtpCodecCapability(
            mimeType="video/H264",
            clockRate=90000,
            parameters={
              "level-asymmetry-allowed": "1",
              "packetization-mode": "1",
              "profile-level-id": "42e01f"
            }
          )
          for transceiver in self.pc.getTransceivers():
            if transceiver.kind == "video":
              transceiver.setCodecPreferences([h264_capability])
        except Exception as e:
          cloudlog.error(f"Failed to set codec preferences: {e}")

        # Create Data Channel
        self.data_channel = self.pc.createDataChannel("data")
        self.attach_data_channel_handlers()
        cloudlog.info("Data channel created")

        # Create Offer
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        cloudlog.info("SDP offer created")

        # Wait for ICE gathering
        for _ in range(100):
          if self.pc.iceGatheringState == "complete":
            break
          await asyncio.sleep(0.1)

        # Send SDP
        real_sdp = {
          "type": self.pc.localDescription.type,
          "sdp": self.pc.localDescription.sdp
        }
        self.sdp_send_queue.put_nowait(json.dumps(real_sdp))
        cloudlog.info(f"SDP sent: {self.pc.localDescription.type}")

        # Wait for Answer
        answer_timeout = 30
        answer_start = time.time()
        answer_received = False

        while time.time() - answer_start < answer_timeout and not answer_received:
          try:
            answer_data = self.sdp_recv_queue.get(timeout=0.5)

            if isinstance(answer_data, dict) and answer_data.get('type') == 'answer':
              answer = RTCSessionDescription(sdp=answer_data['sdp'], type=answer_data['type'])
              await self.pc.setRemoteDescription(answer)
              cloudlog.info("SDP answer set - WebRTC negotiation complete!")
              answer_received = True

              # Keep-alive loop
              cloudlog.info("Entering keep-alive loop...")
              while not end_event.is_set():
                try:
                  msg = self.sdp_recv_queue.get_nowait()

                  if isinstance(msg, dict):
                    if msg.get('type') == 'candidate':
                      pass # Handle candidate if needed
                    elif msg.get('type') == 'stop':
                      cloudlog.info("Received stop signal")
                      break
                    elif msg.get('type') == 'start':
                      cloudlog.info("Received start signal (restart)")
                      self.sdp_recv_queue.put_nowait(msg)
                      break
                except queue.Empty:
                  await asyncio.sleep(0.1)

                  if self.pc.connectionState in ["closed", "failed"] or self.pc.iceConnectionState in ["closed", "failed"]:
                    cloudlog.warning("WebRTC connection lost")
                    break
                  continue

              # Cleanup
              cloudlog.info("Closing WebRTC connection...")
              self.params.put_bool("LiveStreamRunning", False)
              self.params.put_bool("JoystickDebugMode", False)
              await self.pc.close()
              self.pc = None
              break # Exit answer wait loop

          except queue.Empty:
            await asyncio.sleep(0.1)
            continue

        if not answer_received:
          cloudlog.error(f"Timeout waiting for SDP answer after {answer_timeout}s")
          if self.pc:
            await self.pc.close()
            self.pc = None

      except Exception as e:
        cloudlog.exception(f"Error in streamer event loop: {e}")
        await asyncio.sleep(1)