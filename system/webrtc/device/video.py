import asyncio
import time

import av
from aiortc import MediaStreamTrack

from cereal import messaging
from openpilot.common.realtime import DT_MDL, DT_DMON
from openpilot.common.swaglog import cloudlog


class LiveStreamVideoStreamTrack(MediaStreamTrack):
  kind = "video"

  camera_to_sock_mapping = {
    "driver": "livestreamDriverEncodeData",
    "wideRoad": "livestreamWideRoadEncodeData",
    "road": "livestreamRoadEncodeData",
  }

  def __init__(self, camera_type: str):
    super().__init__()
    # Configuración específica para cada tipo de cámara
    dt = DT_DMON if camera_type == "driver" else DT_MDL
    self._dt = dt
    self._clock_rate = 90000  # Clock rate estándar para video
    from fractions import Fraction
    self._time_base = Fraction(1, self._clock_rate)

    # Guardar camera_type para uso posterior
    self.camera_type = camera_type

    # CRITICAL: Override _id directly (not via property) because aiortc uses self._id internally
    # This ensures the MSID in SDP contains the correct track ID
    import uuid
    self._id = f"{camera_type}:{str(uuid.uuid4())}"

    # Configurar el socket para recibir datos del stream
    self._sock = messaging.sub_sock(self.camera_to_sock_mapping[camera_type], conflate=True)
    self._pts = 0
    self._t0_ns = time.monotonic_ns()
    # Initialize paused state
    # CRITICAL: Must start False because streamer.py uses |= operator.
    # If True, it will stay True forever unless explicitly unpaused.
    # False | False (offroad) = False (Active) -> Correct
    # False | True (onroad) = True (Paused) -> Correct
    self.paused = False  # Start paused, streamer will unpause

  @property
  def id(self):
    """Override the id property from VideoStreamTrack to return our custom track ID"""
    return self._id

  @id.setter
  def id(self, value):
    """Allow setting the track ID"""
    self._id = value

  async def recv(self):
    # Handle paused state - drain socket while paused
    while True:
      while self.paused:
        await asyncio.sleep(0.2)
        messaging.drain_sock(self._sock)

      msg = messaging.recv_one_or_none(self._sock)
      if msg is not None:
        break
      await asyncio.sleep(0.005)

    evta = getattr(msg, msg.which())

    packet = av.Packet(evta.header + evta.data)
    packet.time_base = self._time_base

    self._pts =  ((time.monotonic_ns() - self._t0_ns) * self._clock_rate) // 1_000_000_000
    packet.pts = self._pts

    return packet

  def codec_preference(self) -> str | None:
    return "H264"
