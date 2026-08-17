import math
from dataclasses import dataclass, field

from opendbc.can import CANParser
from opendbc.car import Bus, structs
from opendbc.car.honda.hondacan import CanBus
from opendbc.car.honda.values import CAR, DBC


HEADER_MESSAGES = [0x280, 0x284, 0x2D0, 0x2D4, 0x2D8, 0x2DC]
RANGE_TAGS = frozenset({0x74, 0x94})
STRENGTH_IDLE = 0xFE
RANGE_RAW_UNSET = 0x8000
RANGE_RAW_SATURATION = 0xFF80
LAT_SCALE_DEG_PER_LSB = 0.001
STALE_SECONDS = 0.15
TRACK_ID_STRIDE = 1000
BORN_CYCLES = 2
VALID_COUNT_MAX = 5
RANGE_MIN = -3.0
RANGE_MAX = 230.0
COUNTER_STALL_CYCLES = 3
PENDING_FRAME_MAX = 8

VREL_MAX = 100.0
VREL_DT_MAX = 0.5
KF_RANGE_VARIANCE = 0.012
KF_RANGE_NOISE = 0.05
KF_RATE_NOISE = 4.0
KF_INITIAL_RATE_VARIANCE = 1.0e4
KF_NIS_THRESHOLD = 4.0
KF_NIS_INFLATION = 10.0
KF_CONVERGENCE_UPDATES = 2
ACCEL_EMA_ALPHA = 0.25

_KF_OK, _KF_BREAK, _KF_RESEED = range(3)


@dataclass
class TrackRecord:
  range_frame: dict[str, float] | None = None
  meta_frames: dict[int, dict[str, float]] = field(default_factory=dict)
  recovered_clobber: bool = False


class SlotRangeKF:
  __slots__ = ("r", "v", "a", "p00", "p01", "p11", "t", "n")

  def __init__(self, range_value: float, timestamp_nanos: int):
    self._seed(range_value, timestamp_nanos)

  def _seed(self, range_value: float, timestamp_nanos: int):
    self.r = range_value
    self.v = 0.0
    self.a = math.nan
    self.p00 = KF_RANGE_VARIANCE
    self.p01 = 0.0
    self.p11 = KF_INITIAL_RATE_VARIANCE
    self.t = timestamp_nanos
    self.n = 1

  @property
  def converged(self) -> bool:
    return self.n >= KF_CONVERGENCE_UPDATES

  def update(self, measurement: float, timestamp_nanos: int) -> int:
    dt = (timestamp_nanos - self.t) * 1e-9
    if dt <= 0:
      return _KF_OK
    if dt > VREL_DT_MAX:
      self._seed(measurement, timestamp_nanos)
      return _KF_RESEED
    if abs((measurement - self.r) / dt) > VREL_MAX:
      return _KF_BREAK

    range_prediction = self.r + self.v * dt
    rate_noise = KF_RATE_NOISE * dt
    p00 = self.p00 + 2.0 * dt * self.p01 + dt * dt * self.p11 + KF_RANGE_NOISE * dt
    p01 = self.p01 + dt * self.p11
    p11 = self.p11 + rate_noise
    innovation = measurement - range_prediction
    innovation_variance = p00 + KF_RANGE_VARIANCE

    if innovation * innovation / innovation_variance > KF_NIS_THRESHOLD:
      extra_noise = KF_RATE_NOISE * (KF_NIS_INFLATION - 1.0) * dt
      p11 += extra_noise
      p01 += extra_noise * dt
      p00 += extra_noise * dt * dt
      innovation_variance = p00 + KF_RANGE_VARIANCE

    range_gain = p00 / innovation_variance
    rate_gain = p01 / innovation_variance
    previous_rate = self.v
    self.r = range_prediction + range_gain * innovation
    self.v += rate_gain * innovation
    self.p00 = (1.0 - range_gain) * p00
    self.p01 = (1.0 - range_gain) * p01
    self.p11 = p11 - rate_gain * p01

    if self.converged:
      acceleration = (self.v - previous_rate) / dt
      self.a = acceleration if math.isnan(self.a) else (1.0 - ACCEL_EMA_ALPHA) * self.a + ACCEL_EMA_ALPHA * acceleration

    self.t = timestamp_nanos
    self.n += 1
    return _KF_OK


def is_civic_bosch_radar(CP) -> bool:
  return CP.carFingerprint == CAR.HONDA_CIVIC_BOSCH and Bus.radar in DBC[CP.carFingerprint]


class CivicBoschRadar:
  def __init__(self, CP):
    messages = [(message, 20) for message in HEADER_MESSAGES]
    self.parser = CANParser(DBC[CP.carFingerprint][Bus.radar], messages, CanBus(CP).camera)
    self.trigger_message = HEADER_MESSAGES[-1]
    self.updated_messages = set()
    self.points = {}
    self.filters: dict[int, SlotRangeKF] = {}
    self.pending: dict[int, list[dict[str, float]]] = {}
    self.clobber_recovered = 0
    self.valid_counts: dict[int, int] = {}
    self.incarnations: dict[int, int] = {}
    self.last_counter: int | None = None
    self.counter_stall_cycles = 0
    self.last_trigger_nanos = -1

  def update(self, can_strings):
    updated = self.parser.update(can_strings)
    self.updated_messages.update(updated)
    self._harvest_frames(updated)

    if self.trigger_message not in self.updated_messages:
      now = self.parser._last_update_nanos
      if self.points and self.last_trigger_nanos >= 0 and (now - self.last_trigger_nanos) * 1e-9 > STALE_SECONDS:
        return self._stale_data()
      return None

    result = self._build_radar_data()
    self.updated_messages.clear()
    return result

  def _stale_data(self):
    self.points.clear()
    self.filters.clear()
    self.pending.clear()
    self.valid_counts.clear()
    self.last_trigger_nanos = -1
    self.last_counter = None
    self.counter_stall_cycles = 0
    result = structs.RadarData()
    if not self.parser.can_valid:
      result.errors.canError = True
    result.errors.radarUnavailableTemporary = True
    return result

  def _track_id(self, slot: int) -> int:
    return slot * TRACK_ID_STRIDE + self.incarnations.get(slot, 0)

  def _clear_slot(self, slot: int):
    count = max(self.valid_counts.get(slot, 0) - 1, 0)
    self.valid_counts[slot] = count
    if count == 0:
      self.points.pop(slot, None)
      self.filters.pop(slot, None)

  def _harvest_frames(self, updated_addresses):
    for address in updated_addresses:
      if address not in HEADER_MESSAGES:
        continue
      values = self.parser.vl_all[address]
      names = list(values)
      if not names or not values[names[0]]:
        continue
      frames = self.pending.setdefault(HEADER_MESSAGES.index(address), [])
      for index in range(len(values[names[0]])):
        frames.append({name: values[name][index] for name in names})
      del frames[:-PENDING_FRAME_MAX]

  def _assemble_record(self, slot: int) -> TrackRecord:
    record = TrackRecord()
    for frame in self.pending.get(slot, ()):
      tag = int(frame["TRACK_TAG"])
      if tag in RANGE_TAGS:
        record.range_frame = frame
        record.recovered_clobber = False
      else:
        record.meta_frames[tag] = frame
        record.recovered_clobber |= record.range_frame is not None
    return record

  def _update_counter_fault(self, result):
    counter = int(self.parser.vl[self.trigger_message]["CNTR"])
    if self.last_counter is not None and counter == self.last_counter:
      self.counter_stall_cycles += 1
    else:
      self.counter_stall_cycles = 0
    self.last_counter = counter
    if self.parser.can_valid and self.counter_stall_cycles >= COUNTER_STALL_CYCLES:
      result.errors.radarFault = True

  def _valid_range_frame(self, frame, result) -> float | None:
    raw_range = int(frame["RANGE_RAW"])
    if int(frame["STRENGTH"]) == STRENGTH_IDLE or raw_range == RANGE_RAW_UNSET or raw_range >= RANGE_RAW_SATURATION:
      return None
    distance = frame["RANGE"]
    if not RANGE_MIN <= distance <= RANGE_MAX:
      result.errors.wrongConfig = True
      return None
    return distance

  def _update_filter(self, slot: int, distance: float, timestamp_nanos: int) -> SlotRangeKF:
    range_filter = self.filters.get(slot)
    if range_filter is None:
      range_filter = self.filters[slot] = SlotRangeKF(distance, timestamp_nanos)
    elif range_filter.update(distance, timestamp_nanos) == _KF_BREAK:
      self.incarnations[slot] = self.incarnations.get(slot, 0) + 1
      self.points.pop(slot, None)
      range_filter = self.filters[slot] = SlotRangeKF(distance, timestamp_nanos)
    return range_filter

  def _build_radar_data(self):
    result = structs.RadarData()
    if not self.parser.can_valid:
      result.errors.canError = True

    now = self.parser._last_update_nanos
    self.last_trigger_nanos = now
    self._update_counter_fault(result)

    for address in HEADER_MESSAGES:
      slot = HEADER_MESSAGES.index(address)
      if address not in self.updated_messages:
        self._clear_slot(slot)
        continue

      record = self._assemble_record(slot)
      if record.recovered_clobber:
        self.clobber_recovered += 1
      frame = record.range_frame
      distance = None if frame is None else self._valid_range_frame(frame, result)
      if distance is None:
        self._clear_slot(slot)
        continue

      if self.valid_counts.get(slot, 0) == 0:
        self.incarnations[slot] = self.incarnations.get(slot, 0) + 1
        self.filters.pop(slot, None)
      self.valid_counts[slot] = min(self.valid_counts.get(slot, 0) + 1, VALID_COUNT_MAX)

      range_filter = self._update_filter(slot, distance, now)
      relative_speed = range_filter.v if range_filter.converged else math.nan
      if self.valid_counts[slot] < BORN_CYCLES:
        self.points.pop(slot, None)
        continue

      if slot not in self.points:
        self.points[slot] = structs.RadarData.RadarPoint()
        self.points[slot].trackId = self._track_id(slot)
        self.points[slot].deprecated.yvRel = math.nan

      point = self.points[slot]
      point.dRel = distance
      point.yRel = -distance * math.sin(math.radians(frame["LAT_RAW"] * LAT_SCALE_DEG_PER_LSB))
      point.vRel = relative_speed
      point.deprecated.aRel = range_filter.a
      point.deprecated.measured = not math.isnan(relative_speed)

    self.pending.clear()
    result.points = list(self.points.values())
    return result
