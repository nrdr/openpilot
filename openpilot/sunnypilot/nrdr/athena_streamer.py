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


def capture_pane(target: str) -> str | None:
  try:
    result = subprocess.run(["tmux", "capture-pane", "-peJS-7200", "-t", target], capture_output=True, text=True, check=False)
    if result.returncode != 0:
      logger.warning("tmux capture-pane returned code %d: %s", result.returncode, result.stderr)
      return None
    return json.dumps({"tmuxCapture": result.stdout})
  except Exception:
    logger.exception("failed to capture tmux pane %s", target)
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
    self.onroad = not self.params.get_bool("IsOffroad")
    self.tracks: dict[str, LiveStreamVideoStreamTrack] = {}
    self._init_tracks()

  def _init_tracks(self) -> None:
    self.tracks["wideRoad"] = LiveStreamVideoStreamTrack("wideRoad")
    if self.params.get_bool("RecordFront"):
      self.tracks["driver"] = LiveStreamVideoStreamTrack("driver")

  def _add_tracks(self) -> None:
    if self.pc is None:
      return
    for track in self.tracks.values():
      transceiver = self.pc.addTransceiver(track, direction="sendonly")
      transceiver.setCodecPreferences([RTCRtpCodecCapability(
        mimeType="video/H264",
        clockRate=90000,
        parameters={"level-asymmetry-allowed": "1", "packetization-mode": "1", "profile-level-id": "42e01f"},
      )])

  def _send_track_states(self) -> None:
    if self.data_channel is None:
      return
    try:
      self.data_channel.send(json.dumps({"trackState": {name: track.paused for name, track in self.tracks.items()}}))
    except Exception:
      logger.exception("failed to send stream track states")

  def _attach_handlers(self) -> None:
    async def on_open() -> None:
      self._send_track_states()

    def on_message(message: str) -> None:
      try:
        msg = json.loads(message)
        action = msg.get("action")
        track_type = msg.get("trackType")
        if action in ("startTrack", "stopTrack") and track_type in self.tracks:
          self.tracks[track_type].paused = action == "stopTrack"
          self._send_track_states()
        elif action == "captureTmux":
          capture = capture_pane("comma:0.0")
          if capture is not None:
            self.data_channel.send(capture)
      except Exception:
        logger.exception("failed to handle stream data message")

    async def on_close() -> None:
      await self.stop()

    async def on_icecandidate(candidate) -> None:
      if candidate is not None:
        self.ice_send_queue.put_nowait(json.dumps({
          "candidate": candidate.to_sdp(),
          "sdpMid": candidate.sdpMid,
          "sdpMLineIndex": candidate.sdpMLineIndex,
        }))

    self.pc.on("icecandidate", on_icecandidate)
    self.data_channel.on("open", on_open)
    self.data_channel.on("message", on_message)
    self.data_channel.on("close", on_close)

  def _ice_configuration(self) -> RTCConfiguration:
    try:
      response = api_get("/v1/iceservers", timeout=5, access_token=self.api.get_token())
      servers = [
        RTCIceServer(urls=server["urls"], username=server["username"], credential=server["credential"])
        for server in json.loads(response.content)
      ]
    except Exception:
      logger.exception("failed to fetch ICE servers")
      servers = [RTCIceServer(urls="stun:stun.l.google.com:19302")]
    return RTCConfiguration(iceServers=servers)

  async def _set_answer(self, data: dict) -> None:
    await self.pc.setRemoteDescription(RTCSessionDescription(sdp=data["sdp"], type=data["type"]))

  async def _set_candidate(self, data: dict) -> None:
    candidate = candidate_from_sdp(data["candidate"])
    candidate.sdpMid = data.get("sdpMid")
    candidate.sdpMLineIndex = data.get("sdpMLineIndex")
    await self.pc.addIceCandidate(candidate)

  async def build(self) -> None:
    self.pc = RTCPeerConnection(self._ice_configuration())
    self._add_tracks()
    self.data_channel = self.pc.createDataChannel("data")
    self._attach_handlers()

    ice_complete = asyncio.Event()

    def on_ice_gathering_state_change() -> None:
      if self.pc is None or self.pc.iceGatheringState == "complete":
        ice_complete.set()

    self.pc.on("icegatheringstatechange", on_ice_gathering_state_change)
    await self.pc.setLocalDescription(await self.pc.createOffer())
    on_ice_gathering_state_change()
    await ice_complete.wait()
    self.sdp_send_queue.put_nowait(json.dumps({"type": self.pc.localDescription.type, "sdp": self.pc.localDescription.sdp}))

  async def stop(self) -> None:
    async with self.lock:
      self.params.put_bool("LiveView", False)
      try:
        while not self.sdp_send_queue.empty():
          self.sdp_send_queue.get_nowait()
        if self.data_channel is not None:
          self.data_channel.close()
          self.data_channel = None
        if self.pc is not None:
          await self.pc.close()
          self.pc = None
      except Exception:
        logger.exception("failed to stop stream")

  async def event_loop(self, exit_event) -> None:
    while exit_event is None or not exit_event.is_set():
      self.onroad = not self.params.get_bool("IsOffroad")
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

        if self.pc is not None:
          transceivers = self.pc.getTransceivers()
          dtls_state = transceivers[0].receiver.transport.state if transceivers else None
          if self.onroad or self.pc.connectionState in ("failed", "closed") or dtls_state in ("failed", "closed"):
            await self.stop()
      except Exception:
        logger.exception("stream stopped after error")
        await self.stop()
    await self.stop()
