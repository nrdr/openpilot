import asyncio
import json
import logging
import queue
import subprocess

from aiortc import RTCPeerConnection, RTCConfiguration, RTCIceServer, RTCSessionDescription, RTCRtpCodecCapability
from aiortc.sdp import candidate_from_sdp

from openpilot.common.api import Api, api_get
from openpilot.common.params import Params
from openpilot.system.webrtc.device.video import LiveStreamVideoStreamTrack


logger = logging.getLogger(__name__)


def capture_pane(session_window_pane: str) -> str | None:
  try:
    result = subprocess.run(
      ["tmux", "capture-pane", "-peJS-7200", "-t", session_window_pane],
      capture_output=True,
      text=True,
      check=False,
    )
    if result.returncode != 0:
      logger.warning("tmux capture-pane returned code %d: %s", result.returncode, result.stderr)
      return None
    return json.dumps({"tmuxCapture": result.stdout})
  except Exception:
    logger.exception("Exception while capturing pane '%s':", session_window_pane)
    return None


class Streamer:
  def __init__(self, sdp_send_queue: queue.Queue, sdp_recv_queue: queue.Queue, ice_send_queue: queue.Queue):
    self.lock = asyncio.Lock()
    self.pc: RTCPeerConnection | None = None
    self.data_channel = None
    self.sdp_send_queue = sdp_send_queue
    self.sdp_recv_queue = sdp_recv_queue
    self.ice_send_queue = ice_send_queue
    self.params = Params()
    self.api = Api(self.params.get("DongleId"))
    self.onroad = self.params.get_bool("IsOnroad")
    self.tracks: dict[str, LiveStreamVideoStreamTrack] = {}
    self._init_tracks()

  def _init_tracks(self) -> None:
    self.tracks["wideRoad"] = LiveStreamVideoStreamTrack("wideRoad")
    if self.params.get_bool("RecordFront"):
      self.tracks["driver"] = LiveStreamVideoStreamTrack("driver")

  def add_tracks(self) -> None:
    if not self.pc:
      return
    for track in self.tracks.values():
      transceiver = self.pc.addTransceiver(track, direction="sendonly")
      h264_capability = RTCRtpCodecCapability(
        mimeType="video/H264",
        clockRate=90000,
        parameters={
          "level-asymmetry-allowed": "1",
          "packetization-mode": "1",
          "profile-level-id": "42e01f",
        },
      )
      transceiver.setCodecPreferences([h264_capability])

  def send_track_states(self) -> None:
    if not self.data_channel:
      return
    track_state = {"trackState": {name: track.paused for name, track in self.tracks.items()}}
    try:
      self.data_channel.send(json.dumps(track_state))
    except Exception:
      logger.exception("Failed to send track states")

  def _attach_event_handlers(self) -> None:
    async def on_open() -> None:
      self.send_track_states()

    def on_message(message: str) -> None:
      try:
        msg = json.loads(message)
        action = msg.get("action")
        track_type = msg.get("trackType")

        if action in ("startTrack", "stopTrack") and track_type in self.tracks:
          self.tracks[track_type].paused = (action == "stopTrack")
          self.send_track_states()
          return

        if action == "captureTmux":
          capture_result = capture_pane("comma:0.0")
          if capture_result:
            self.data_channel.send(capture_result)
      except Exception:
        logger.exception("Error handling data channel message")

    async def on_close() -> None:
      await self.stop()

    async def on_icecandidate(candidate) -> None:
      if candidate is None:
        return
      candidate_data = {
        "candidate": candidate.to_sdp(),
        "sdpMid": candidate.sdpMid,
        "sdpMLineIndex": candidate.sdpMLineIndex,
      }
      self.ice_send_queue.put_nowait(json.dumps(candidate_data))

    self.pc.on("icecandidate", on_icecandidate)
    self.data_channel.on("open", on_open)
    self.data_channel.on("message", on_message)
    self.data_channel.on("close", on_close)

  def _get_ice_configuration(self) -> RTCConfiguration:
    try:
      ice_servers_data = api_get("/v1/iceservers", timeout=5, access_token=self.api.get_token()).content
      ice_servers = [
        RTCIceServer(urls=server["urls"], username=server["username"], credential=server["credential"])
        for server in json.loads(ice_servers_data)
      ]
    except Exception:
      logger.exception("Failed to fetch ICE servers")
      ice_servers = [RTCIceServer(urls="stun:stun.l.google.com:19302")]
    return RTCConfiguration(iceServers=ice_servers)

  async def _create_offer(self) -> None:
    offer = await self.pc.createOffer()
    await self.pc.setLocalDescription(offer)

  async def _set_answer(self, data: dict) -> None:
    answer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
    await self.pc.setRemoteDescription(answer)

  async def _set_candidate(self, candidate_data: dict) -> None:
    candidate_sdp = candidate_data["candidate"]
    parsed_candidate = candidate_from_sdp(candidate_sdp)
    parsed_candidate.sdpMid = candidate_data.get("sdpMid")
    parsed_candidate.sdpMLineIndex = candidate_data.get("sdpMLineIndex")
    await self.pc.addIceCandidate(parsed_candidate)

  async def build(self) -> None:
    self.pc = RTCPeerConnection(self._get_ice_configuration())
    self.add_tracks()
    self.data_channel = self.pc.createDataChannel("data")
    self._attach_event_handlers()
    await self._create_offer()
    while not self.pc.localDescription:
      await asyncio.sleep(0.1)
    while self.pc.iceGatheringState != "complete":
      await asyncio.sleep(0.1)
    message = json.dumps({
      "type": self.pc.localDescription.type,
      "sdp": self.pc.localDescription.sdp,
    })
    self.sdp_send_queue.put_nowait(message)

  async def stop(self) -> None:
    async with self.lock:
      self.params.put_bool("LiveView", False)
      try:
        while not self.sdp_send_queue.empty():
          self.sdp_send_queue.get_nowait()
        if self.data_channel is not None:
          self.data_channel.close()
          self.data_channel = None
        if self.pc:
          await self.pc.close()
          self.pc = None
      except Exception:
        logger.exception("Error during stop")

  async def event_loop(self, exit_event) -> None:
    stop_states = ["failed", "closed"]
    while exit_event is None or not exit_event.is_set():
      self.onroad = self.params.get_bool("IsOnroad")
      try:
        try:
          data = self.sdp_recv_queue.get_nowait()
        except queue.Empty:
          data = None
        if data:
          msg_type = data.get("type")
          if msg_type == "start":
            if self.onroad:
              self.sdp_send_queue.put_nowait(json.dumps({"error": "Live View unavailable while onroad"}))
              continue
            if not self.params.get_bool("LiveViewEnabled"):
              self.sdp_send_queue.put_nowait(json.dumps({"error": "Live View disabled"}))
              continue
            await self.build()
            self.params.put_bool("LiveView", True)
          elif msg_type == "answer":
            await self._set_answer(data)
          elif msg_type == "candidate" and "candidate" in data:
            await self._set_candidate(data["candidate"])
          elif msg_type == "bye":
            await self.stop()
        else:
          await asyncio.sleep(0.1 if self.pc else 1.0)

        if self.pc:
          if self.onroad:
            await self.stop()
            continue
          transceivers = self.pc.getTransceivers()
          dtls_state = transceivers[0].receiver.transport.state if transceivers else None
          if self.pc.connectionState in stop_states or dtls_state in stop_states:
            await self.stop()
      except Exception:
        logger.exception("Streamer stopping after error")
        await self.stop()
    await self.stop()
