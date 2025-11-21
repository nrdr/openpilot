import asyncio
import threading
import json
import queue
import subprocess
import logging
import time

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
    import cereal.messaging as messaging
    from openpilot.system.webrtc.device.video import LiveStreamVideoStreamTrack
    from openpilot.system.manager.process_config import NativeProcess
    from openpilot.common.params import Params
    from openpilot.common.api import Api, api_get
    from openpilot.common.swaglog import cloudlog
    HAS_CEREAL = True
except ImportError:
    HAS_CEREAL = False

# Configure logging
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_offer(pc: RTCPeerConnection) -> None:
  """
  Create an SDP offer and set it as the local description of the provided PeerConnection.
  """
  if not pc:
    logger.error("PeerConnection is None, cannot create offer.")
    return
  try:
    offer: RTCSessionDescription = await pc.createOffer()
    await pc.setLocalDescription(offer)
    logger.info("Created and set local SDP offer.")
    cloudlog.info(f"SDP OFFER:\n{offer.sdp}")
  except Exception:
    logger.exception("Failed to create or set local SDP offer:")
    if pc:
      await pc.close()

async def set_answer(pc: RTCPeerConnection, data: dict) -> None:
  """
  Set the remote answer SDP on the provided PeerConnection.
  """
  if not pc:
    logger.error("PeerConnection is None, cannot set answer.")
    return
  try:
    if 'sdp' not in data or 'type' not in data:
      raise ValueError("Answer data is missing 'sdp' or 'type' field.")
    logger.debug("Received answer data: %s", data)
    answer = RTCSessionDescription(sdp=data['sdp'], type=data['type'])
    cloudlog.info(f"SDP ANSWER:\n{answer.sdp}")
    await pc.setRemoteDescription(answer)
    logger.info("Successfully set remote answer description.")
  except Exception:
    logger.exception("Failed to set remote answer. Data: %s", data)
    if pc:
      await pc.close()

async def set_candidate(pc: RTCPeerConnection, candidate_data: dict) -> None:
  """
  Add a remote ICE candidate to the provided PeerConnection.
  """
  if not pc:
    logger.error("PeerConnection is None, cannot set candidate.")
    return
  logger.debug("Received candidate data: %s", candidate_data)
  try:
    if "candidate" not in candidate_data:
      raise ValueError("Candidate data missing 'candidate' field.")
    candidate_sdp = candidate_data["candidate"]
    parsed_candidate = candidate_from_sdp(candidate_sdp)
    parsed_candidate.sdpMid = candidate_data.get("sdpMid", None)
    parsed_candidate.sdpMLineIndex = candidate_data.get("sdpMLineIndex", None)
    await pc.addIceCandidate(parsed_candidate)
    logger.info("Added remote ICE candidate.")
  except Exception:
    logger.exception("Failed to add ICE candidate:")
    if pc:
      await pc.close()

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
    """
    Initialize the controller handler with safety timeout

    Args:
        safety_timeout: Time in seconds after which controls return to neutral if no input received
    """
    self.last_input_time = time.time()
    self.throttle = 0.0
    self.steering = 0.0
    self.safety_timeout = safety_timeout
    self.input_active = False
    self.lock = asyncio.Lock()

    # Monitor task will be created when start_safety_monitor is called
    self.safety_monitor_task = None
    self.running = True

    self.joystick_sock = messaging.pub_sock('testJoystick')

    logger.info("Controller handler initialized with safety timeout: %.2f seconds", safety_timeout)

  async def handle_controller_message(self, message_data):
    """
    Process controller input message from frontend

    Args:
        message_data: JSON data with controller inputs

    Returns:
        bool: True if message was handled, False otherwise
    """
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
      logger.info(f"Controller input: throttle={self.throttle:.2f}, steering={self.steering:.2f}")

      # Here you would call your vehicle control functions
      await self.apply_control(self.throttle, self.steering)
      return True

    except Exception as e:
      logger.error(f"Error handling controller message: {str(e)}")
      return False

  async def apply_control(self, throttle, steering):
    """
    Apply control values to the vehicle

    Args:
        throttle: Throttle value (-1.0 to 1.0)
        steering: Steering value (-1.0 to 1.0)
    """
    # TODO: Implement your actual vehicle control code here
    # This is a placeholder - replace with your actual vehicle control mechanism
    logger.debug(f"Applied control: throttle={throttle:.2f}, steering={steering:.2f}")
    dat = messaging.new_message('testJoystick')
    dat.testJoystick.axes = [throttle, steering]
    dat.testJoystick.buttons = [False]
    self.joystick_sock.send(dat.to_bytes())

  async def shutdown(self):
    """
    Shutdown the controller handler safely
    """
    logger.info("Shutting down controller handler")
    self.running = False

    if self.safety_monitor_task and not self.safety_monitor_task.done():
      self.safety_monitor_task.cancel()
      try:
        await self.safety_monitor_task
      except asyncio.CancelledError:
        pass

    # Ensure controls are set to neutral when shutting down
    async with self.lock:
      self.throttle = 0.0
      self.steering = 0.0
      await self.apply_control(0.0, 0.0)


class Streamer:
  def __init__(self, sdp_send_queue: queue.Queue, sdp_recv_queue: queue.Queue, ice_send_queue: queue.Queue):
    logger.info("Initializing Streamer instance.")
    
    # Check dependencies first
    if not HAS_AIORTC:
        logger.error("aiortc not available. Install with: pip install aiortc")
        raise ImportError("aiortc is required for streaming functionality")
    
    if not HAS_CEREAL:
        logger.error("cereal/openpilot modules not available")
        raise ImportError("openpilot modules are required for streaming functionality")
    
    self.lock = asyncio.Lock()
    self.pc: RTCPeerConnection | None = None
    self.data_channel: RTCDataChannel | None = None
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
    # Initialize video tracks
    self.tracks: dict[str, LiveStreamVideoStreamTrack] = {}
    if self.params.get_bool("RecordFront"):
      self.tracks["driver"] = LiveStreamVideoStreamTrack("driver")
    if self.params.get_bool("RecordRoad"):
      self.tracks["road"] = LiveStreamVideoStreamTrack("road")
      self.tracks["wideRoad"] = LiveStreamVideoStreamTrack("wideRoad")

  def add_tracks(self) -> None:
    """
    Add video tracks to the PeerConnection with H264 codec preferences.
    """
    if not self.pc:
      logger.error("Cannot add tracks without a PeerConnection.")
      return
    try:
      for track in self.tracks.values():
        # Allow streaming based on user preference
        allow_onroad_streaming = self.params.get_bool("AllowOnroadStreaming")
        if allow_onroad_streaming:
            track.paused = False  # Force tracks to be active for live streaming
        else:
            track.paused |= self.onroad  # Original behavior - pause when onroad
        
        # Add track - aiortc will create transceiver automatically
        sender = self.pc.addTrack(track)
      
      # Configure H264 codec on all transceivers
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
      
      logger.info("All video tracks added successfully.")
    except Exception:
      logger.exception("Failed to add tracks:")
      if self.pc:
        asyncio.ensure_future(self.pc.close())

  def send_track_states(self) -> None:
    """
    Send the current track pause states via the data channel.
    """
    if not self.data_channel:
      logger.warning("Data channel not established. Cannot send track states.")
      return
    track_state = {
      "trackState": {name: track.paused for name, track in self.tracks.items()}
    }
    try:
      self.data_channel.send(json.dumps(track_state))
      logger.debug("Sent updated track states: %s", track_state)
    except Exception:
      logger.exception("Failed to send track states:")

  def attach_event_handlers(self):

    def on_open():
      self.send_track_states()

    def on_message(message: str):
      logger.debug("Received data channel message: %s", message)
      try:
        msg = json.loads(message)
        action = msg.get("action")
        track_type = msg.get("trackType")
        updated = False

        if action == "controller":
          # Process controller input and apply controls with safety measures
          if not self.params.get_bool("JoystickDebugMode"):
            self.params.put_bool("JoystickDebugMode", True)
          asyncio.create_task(self.controller_handler.handle_controller_message(msg))
          return # Don't send track states

        if action in ("startTrack", "stopTrack") and track_type in self.tracks:
          self.tracks[track_type].paused = (action == "stopTrack")
          updated = True
          logger.info("Track '%s' %s", track_type, "stopped" if self.tracks[track_type].paused else "started")
        elif action == "captureTmux":
          capture_result = capture_pane("comma:0.0")
          if capture_result:
            try:
              self.data_channel.send(capture_result) # type: ignore[union-attr]
              logger.debug("Sent tmux capture result.")
            except Exception:
              logger.exception("Failed to send tmux capture result:")
          else:
            logger.warning("No tmux capture result to send.")
        if updated:
          self.send_track_states()
      except Exception:
        logger.exception("Error handling data channel message:")

    async def on_close():
      logger.info("Data channel closed. Stopping streamer...")
      await self.stop()

    async def on_negotiationneeded():
      logger.debug("Negotiation needed. Creating new SDP offer.")
      await create_offer(self.pc)

    self.pc.on("negotiationneeded", on_negotiationneeded)
    self.data_channel.on("open", on_open)
    self.data_channel.on("message", on_message)
    self.data_channel.on("close", on_close)

  def get_ice_configuration(self):
    #TODO for privacy, we can disable the turn server and always use the stun server. This kind of enforces a local connection for when on hotspot.
    try:
      ice_servers_data = api_get('/v1/iceservers', timeout=5,access_token=self.api.get_token()).content
      ice_servers = [
        RTCIceServer(urls=server["urls"],username=server["username"],credential=server["credential"])
        for server in json.loads(ice_servers_data)
      ]
    except Exception:
      logger.exception("Failed to fetch ICE servers:")
      # Fallback to Google STUN server
      ice_servers = [
        RTCIceServer(urls="stun:stun.l.google.com:19302"),
      ]
    configuration = RTCConfiguration(iceServers=ice_servers)
    logger.debug("RTCConfiguration: %s", configuration)
    return configuration

  async def build(self):
    logger.info("Starting WebRTC build process...")
    
    logger.info("Getting ICE configuration...")
    ice_config = self.get_ice_configuration()
    logger.info(f"ICE configuration obtained: {len(ice_config.iceServers)} servers")
    
    logger.info("Creating RTCPeerConnection...")
    self.pc = RTCPeerConnection(ice_config)
    logger.info("RTCPeerConnection created successfully")
    
    logger.info("Adding video tracks...")
    self.add_tracks()
    
    logger.info("Creating data channel...")
    self.data_channel = self.pc.createDataChannel("data")
    logger.info("Data channel created successfully")
    
    logger.info("Attaching event handlers...")
    self.attach_event_handlers()
    
    logger.info("Creating SDP offer...")
    await create_offer(self.pc)
    logger.info("SDP offer creation completed")
    
    logger.info("Waiting for local description...")
    timeout_counter = 0
    while not self.pc.localDescription:
      await asyncio.sleep(0.1)
      timeout_counter += 1
      if timeout_counter > 100:  # 10 seconds
        logger.error("Timeout waiting for local description")
        raise TimeoutError("Local description timeout")
    logger.info("Local description ready")
    
    logger.info("Waiting for ICE gathering to complete...")
    ice_timeout = 0
    while self.pc.iceGatheringState != "complete":
      await asyncio.sleep(0.1)
      ice_timeout += 1
      if ice_timeout > 300:  # 30 seconds
        logger.warning(f"ICE gathering timeout, current state: {self.pc.iceGatheringState}")
        break  # Continue anyway
    logger.info(f"ICE gathering finished, state: {self.pc.iceGatheringState}")
    
    message = json.dumps({
      'type': self.pc.localDescription.type,
      'sdp': self.pc.localDescription.sdp,
    })
    logger.info("Sending SDP message to queue...")
    self.sdp_send_queue.put_nowait(message)
    logger.info("SDP message sent successfully!")

  async def stop(self) -> None:
    """
    Stop the PeerConnection, camera, encoder, and clean up state.
    """
    async with self.lock:
      logger.info("Stopping streamer...")
      self.params.put_bool("LiveStreamRunning", False)
      self.params.put_bool("JoystickDebugMode", False)
      try:
        # Clear any pending messages in sdp_send_queue
        while not self.sdp_send_queue.empty():
          self.sdp_send_queue.get()
        if self.data_channel is not None:
          self.data_channel.close()
          self.data_channel = None
        if self.pc:
          await self.pc.close()
          self.pc = None
        await asyncio.sleep(1)
        logger.info("Streamer stopped successfully.")
      except Exception:
        logger.exception("Error during stop:", )

  async def event_loop(self, end_event: threading.Event):
    """
    Main event loop that processes signaling messages and maintains the PeerConnection.
    Runs until end_event is set.
    """
    logger.info("EVENT LOOP ENTRY POINT - Function started")
    await asyncio.sleep(0.1)  # Test async
    logger.info("EVENT LOOP - Async test passed")
    
    logger.info("STARTING EVENT LOOP - Initializing components...")
    
    # Skip camera/encoder for now to test the basic loop
    logger.info("Skipping camera and encoder processes for testing...")
    # try:
    #   logger.info("Creating camera and encoder processes...")
    #   self.camera = NativeProcess("camerad", "system/camerad", ["./camerad"], True)
    #   self.encoder = NativeProcess("encoderd", "system/loggerd", ["./encoderd", "--stream"], True)
    #   logger.info("Native processes for camera and encoder initialized successfully")
    # except Exception as e:
    #   logger.error(f"Failed to initialize camera/encoder: {e}")
    #   logger.exception("Camera/encoder initialization traceback:")
    #   # Continue anyway - maybe the processes are already running
    logger.info("Starting main event loop...")
    stop_states = ['failed', 'closed']
    connecting_states = ['connecting', 'new']
    loop_iteration = 0
    while not end_event.is_set():
      loop_iteration += 1
      if loop_iteration % 10 == 1:  # Log every 10 iterations
        logger.info(f"Event loop iteration {loop_iteration}")
      self.onroad = self.params.get_bool("IsOnroad") # support some functions while onroad
      try:
        try:
          # Use blocking get with timeout instead of get_nowait to avoid missing messages
          data = self.sdp_recv_queue.get(timeout=0.1 if self.pc else 1.0)
          logger.info(f"RECEIVED SIGNALING MESSAGE: {data}")
        except queue.Empty:
          # Check for messages more frequently when no connection
          if not self.pc:
            logger.debug("No messages in queue, continuing...")
          data = None
        except Exception as e:
          logger.error(f"Error getting message from queue: {e}")
          data = None
        if data:
          interaction_timeout = 6000 # interaction_timeout 10mins
          match data.get('type'):
            case 'start':
              try:
                logger.info("Processing 'start' signal - beginning WebRTC build process...")
                await asyncio.wait_for(self.build(), timeout=30)
                logger.info("WebRTC build completed successfully!")
                connection_timeout = 600 # 1min
                if not self.onroad:
                  self.params.put_bool("LiveStreamRunning", True)
                  logger.info("LiveStreamRunning set to True (not onroad)")
                else:
                  logger.info("Onroad detected - LiveStreamRunning not set")
              except asyncio.TimeoutError:
                logger.error("WebRTC build timed out after 30 seconds")
                await self.stop()
              except Exception:
                logger.exception("Error during 'start' handling:")
                await self.stop()
            case 'answer':
              await set_answer(self.pc, data)
            case 'candidate' if 'candidate' in data:
              await set_candidate(self.pc, data['candidate'])
            case 'bye':
              await self.stop()
        else:
          await asyncio.sleep(0.1 if self.pc else 2)
        if self.pc:
          transeivers = self.pc.getTransceivers()
          dtls_state = None
          if len(transeivers):
            dtls_state = transeivers[0].receiver.transport.state
          if self.pc.connectionState in stop_states or dtls_state in stop_states:
            raise TimeoutError("The connection ended")
          if self.pc.connectionState in connecting_states or dtls_state in connecting_states:
            if connection_timeout:
              connection_timeout -= 1
            else:
              raise TimeoutError("Connection took too long to establish. Closing")
          if interaction_timeout:
            interaction_timeout -= 1
          else:
            self.data_channel.send("bye") # type: ignore[union-attr]
            raise TimeoutError("Interaction timeout. Closing")
      except Exception:
        logger.exception("Stopping:")
        await self.stop()
    await self.stop()