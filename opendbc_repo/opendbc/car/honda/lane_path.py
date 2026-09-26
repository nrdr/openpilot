# Render OpenPilot's road lanes on the Honda Bosch radarless dash
from dataclasses import dataclass

import numpy as np

NUM_INDICES = 10
OFFSETS_PER_INDEX = 4
NUM_PTS = NUM_INDICES * OFFSETS_PER_INDEX  # 40 lateral offsets, near->far

# LANE_PATH is a 40-point path: each point is a lateral offset from the car's center line at a
# look-ahead distance (up to 100 m). All zeros = perfectly straight lane ahead.
# The message encodes these 40 offsets as 10 MUX indices x 4 offsets each. The camera repeats every index
# across 4 redundant banks: MUX = index + bank*16
# We cycle all 40 MUX values bank-major at ~50 Hz so each index refreshes evenly.
# MUX values: 1-10, 17-26, 33-42, 49-58
# logical index = (mux-1) % 16.
MUX_CYCLE = tuple(idx + bank * 16 for bank in range(4) for idx in range(1, NUM_INDICES + 1))

OFFSET_UNAVAILABLE = 2047  # camera's "no point" sentinel (12-bit signed max)
OFFSET_VALID_MAX = 2046    # clamp real offsets below the sentinel

# Slew-rate limit on the displayed path: the model's lane prediction can jump frame-to-frame when it
# is uncertain, and the dash lanes jump with it. Cap how far each displayed offset may move per
# update so a full swing from center (0) to full scale (OFFSET_VALID_MAX, max turn) takes
# SLEW_FULL_SCALE_SECONDS. The carcontroller refits the path at 50 Hz on both the radarless
# (frame % 2 == 0) and CAN FD (radar 50 Hz tick) paths.
SLEW_UPDATE_RATE_HZ = 50.0
SLEW_FULL_SCALE_SECONDS = 2.0  # center -> max turn takes this long
SLEW_MAX_STEP = OFFSET_VALID_MAX / (SLEW_FULL_SCALE_SECONDS * SLEW_UPDATE_RATE_HZ)  # raw units per update

D_NEAR = 2.0
D_MAX = 100.0
LOOKAHEAD = np.linspace(D_NEAR, D_MAX, NUM_PTS)               # look-ahead distance of each offset
# raw units per meter of lateral. Fit per look-ahead index by regressing the stock radar's raw
# offsets against modelV2's lane-center lateral over the same drive (factory ACC lanes route
# 3792d010590cb83a|00000107, 187 paired sweeps, lane-line probs >= 0.4): the stock encoding uses
# ~29-37 raw/m over the rendered 2-55 m, ~4.6-5.1x the previous law, which is why openpilot's lanes
# rendered noticeably flatter than factory. Correlation with the model lateral rises 0.6 -> 0.96
# with distance; the quadratic below is the correlation-weighted fit of the per-index gains.
GAIN = 29.3 + 0.243 * LOOKAHEAD - 0.00228 * LOOKAHEAD ** 2
# previous law, kept for the HUD-lead lateral consistency ratio in curve_boost()
GAIN_PREV = 6.27 + 0.0106 * LOOKAHEAD + 0.000354 * LOOKAHEAD ** 2

def curve_boost(d: float) -> float:
  """Ratio of the corrected stock-fit gain law to the previous one at look-ahead distance d.

  The HUD lead marker's LAT_SCALE was tuned on-car against lanes rendered with the previous
  (too-flat) law; scaling the lead's lateral by this ratio at the lead's distance keeps the
  marker on the lane now that the lanes carry the full stock curvature."""
  d = min(max(float(d), D_NEAR), D_MAX)
  return (29.3 + 0.243 * d - 0.00228 * d ** 2) / (6.27 + 0.0106 * d + 0.000354 * d ** 2)


LANE_LINE_ON = 3            # LEFT_LANE / RIGHT_LANE shown value
LANE_LENGTH_MAX_VALUE = 33  # full dash reach (have not seen/tested higher)
LANE_WIDTH_DEFAULT = 32

# Dash lane (from modelV2): per-side line confidence -> lane center + draw length
DASH_PATH_PROB_ON = 0.25         # lane-line existence prob to start drawing
DASH_PATH_PROB_OFF = 0.10        # ... and to keep drawing (hysteresis)
DASH_HALF_OFFSET = 1.65          # m, half lane width when only one line is confident
DASH_PATH_FULL_LEN_SPEED = 27.0  # m/s for full draw length
DASH_PATH_LEAD_FULL_DIST = 70.0  # m lead distance for full draw length
DASH_PATH_MIN_REACH = 0.15       # min draw fraction (short stub when stopped / low speed)


def _encode(lat):
  # lane-center lateral (m, +left) at each LOOKAHEAD -> raw offsets; stock offset = -OP lateral
  raw = np.clip(np.round(-GAIN * np.asarray(lat, dtype=float)), -OFFSET_VALID_MAX, OFFSET_VALID_MAX)
  return [int(v) for v in raw]


def encode_lane_path(x, y):
  """OP lane center (x, y arrays, m, +left) -> 40 raw offsets. All-unavailable if the lane doesn't reach D_MAX."""
  x = np.asarray(x, dtype=float)
  y = np.asarray(y, dtype=float)
  if x.size < 2 or x.max() < D_MAX:
    return [OFFSET_UNAVAILABLE] * NUM_PTS
  return _encode(np.interp(LOOKAHEAD, x, y))


# Stock CAN FD radar LANE_PATH behavior (decoded from MDX factory ACC logs with lane lines displayed):
# the path is always a contiguous valid prefix terminated in-band with OFFSET_UNAVAILABLE, at most 24 of
# the 40 points are ever valid (typically 22-23), and the "no lane" idle is 6 valid zero offsets — never
# all-unavailable. There is no LKAS_HUD_2 on this platform, so the dash derives the drawn lane length
# from the in-band terminator; a never-terminated 40-point path renders nothing.
CANFD_MAX_VALID_PTS = 23
CANFD_MIN_VALID_PTS = 6
CANFD_IDLE_OFFSETS = [0] * CANFD_MIN_VALID_PTS + [OFFSET_UNAVAILABLE] * (NUM_PTS - CANFD_MIN_VALID_PTS)

# Stock valid-point count is a linear function of ego speed alone: len = 6.74 + 0.862*vEgo (m/s), clamped
# to [6, 23]. Fit from the factory lanes-on route (~1200 RADAR_LEAD frames vs wheel speed; residuals flat
# against lead distance, so no lead term). At city speed this is roughly double a plain 23*vEgo/27 ramp
# (e.g. 16 points at 38 km/h where the ramp gives 9); matching it matters because the dash never rendered
# openpilot's shorter-than-stock paths.
CANFD_LEN_INTERCEPT = 6.74
CANFD_LEN_SLOPE = 0.862  # points per m/s


def canfd_lane_length(dash_lane) -> int:
  """Valid-point count of the stock-form path. The stock radar mirrors this in RADAR_LEAD's
  LANE_PATH_LENGTH signal (6 when idle), which the dash cross-checks against the in-band terminator."""
  if dash_lane.reach <= 0.0 or dash_lane.offsets[0] == OFFSET_UNAVAILABLE:
    return CANFD_MIN_VALID_PTS
  n = round(CANFD_LEN_INTERCEPT + CANFD_LEN_SLOPE * dash_lane.v_ego)
  return max(CANFD_MIN_VALID_PTS, min(CANFD_MAX_VALID_PTS, n))


def canfd_lane_offsets(dash_lane) -> list[int]:
  """Reshape a DashLane's 40 offsets into the stock CAN FD radar form: a terminated valid prefix whose
  length scales with reach, or the stock idle pattern when there is nothing to draw."""
  if dash_lane.reach <= 0.0 or dash_lane.offsets[0] == OFFSET_UNAVAILABLE:
    return CANFD_IDLE_OFFSETS
  n_valid = canfd_lane_length(dash_lane)
  return list(dash_lane.offsets[:n_valid]) + [OFFSET_UNAVAILABLE] * (NUM_PTS - n_valid)


def create_lane_path(packer, bus, offsets, mux):
  """Pack one LANE_PATH frame for `mux` (one of MUX_CYCLE) from the 40-offset array."""
  base = ((mux - 1) % 16) * OFFSETS_PER_INDEX
  values = {
    "MUX": mux,
    "PATH_OFFSET_1": offsets[base + 0],
    "PATH_OFFSET_2": offsets[base + 1],
    "PATH_OFFSET_3": offsets[base + 2],
    "PATH_OFFSET_4": offsets[base + 3],
  }
  return packer.make_can_msg("LANE_PATH", bus, values)


def create_lkas_hud_2(packer, bus, counter_2, reach=1.0, lane_cross=0, left_line=True, right_line=True):
  """Pack one LKAS_HUD_2 frame enabling the dash lane lines."""
  lane_length = max(0, min(LANE_LENGTH_MAX_VALUE, round(reach * LANE_LENGTH_MAX_VALUE)))
  shown = lane_length > 0   # no length -> drop the lane lines
  values = {
    "COUNTER_2": counter_2,
    "SET_ME_X01": 1,
    "LANE_WIDTH": LANE_WIDTH_DEFAULT,
    "LEFT_LANE": LANE_LINE_ON if (shown and left_line) else 0,
    "RIGHT_LANE": LANE_LINE_ON if (shown and right_line) else 0,
    "LEFT_LANE_CROSSED": 1 if (shown and lane_cross < 0) else 0,
    "RIGHT_LANE_CROSSED": 1 if (shown and lane_cross > 0) else 0,
    "LANE_LENGTH": lane_length,
  }
  return packer.make_can_msg("LKAS_HUD_2", bus, values)


# ---- Fit dash lane from modelV2 ---------------------------------------------------------------

def _line_trusted(prob, was_on):
  # hysteresis to prevent flicker
  return prob >= (DASH_PATH_PROB_OFF if was_on else DASH_PATH_PROB_ON)


def select_lane_render(model, prev_left, prev_right):
  """Dash lane-center (x, y arrays) + which ego lines to draw, from per-side model confidence. `model` = modelV2."""
  lls, probs = model.laneLines, model.laneLineProbs
  if len(lls) < 3 or len(probs) < 3 or len(lls[1].x) == 0:
    return None, None, False, False

  left = _line_trusted(probs[1], prev_left)
  right = _line_trusted(probs[2], prev_right)
  x = np.array(lls[1].x)
  yl, yr = np.array(lls[1].y), np.array(lls[2].y)
  if left and right:
    y = (yl + yr) / 2.0
  elif right:
    y = yr - DASH_HALF_OFFSET
  elif left:
    y = yl + DASH_HALF_OFFSET
  else:
    return None, None, False, False
  return x, y, left, right


@dataclass
class DashLane:
  offsets: list[int]   # 40 raw LANE_PATH offsets (all OFFSET_UNAVAILABLE when blank)
  reach: float         # rendered length fraction (0 = draw nothing)
  left_line: bool
  right_line: bool
  lane_cross: int = 0
  v_ego: float = 0.0   # m/s at fit time; drives the CAN FD valid-point count (stock law is speed-only)


class LanePathFitter:
  """Builds OP's lane-center path from modelV2 for the radarless dash, holding per-side line hysteresis."""
  def __init__(self):
    self._left_on = False
    self._right_on = False
    self._displayed = None  # slewed float copy of the 40 raw offsets currently on the dash

  def _slew(self, offsets):
    """Rate-limit the displayed offsets toward the new fit (SLEW_MAX_STEP per update) so the dash
    lane can't jump when the model's prediction jumps. An all-sentinel fit (path short of D_MAX)
    draws nothing, so pass it through and reset; likewise start at the fit when nothing was drawn
    (no visible jump either way)."""
    if offsets[0] == OFFSET_UNAVAILABLE:
      self._displayed = None
      return offsets
    target = np.asarray(offsets, dtype=float)
    if self._displayed is None:
      self._displayed = target
    else:
      self._displayed = self._displayed + np.clip(target - self._displayed, -SLEW_MAX_STEP, SLEW_MAX_STEP)
    return [int(v) for v in np.round(self._displayed)]

  def update(self, model, v_ego, lead_d) -> DashLane:
    """`model` = modelV2 (None when invalid); `v_ego` m/s; `lead_d` lead distance m (0 = none). Returns a DashLane.
    Returns blank when the model is missing/invalid, no ego line is confident, or the reach rounds to zero.
    Reach is the drawn length based on speed and lead distance. We don't show full reach as at low speeds because
    the model's lane lines tend to be less accurate/confident on busy non-highway streets."""
    blank = DashLane([OFFSET_UNAVAILABLE] * NUM_PTS, 0.0, False, False)

    x = y = None
    left_on = right_on = False
    if model is not None:
      x, y, left_on, right_on = select_lane_render(model, self._left_on, self._right_on)
    if x is None:
      self._displayed = None
      return blank
    self._left_on, self._right_on = left_on, right_on

    reach = float(np.clip(max(v_ego / DASH_PATH_FULL_LEN_SPEED, lead_d / DASH_PATH_LEAD_FULL_DIST, DASH_PATH_MIN_REACH), 0.0, 1.0))
    if round(reach * LANE_LENGTH_MAX_VALUE) <= 0:
      self._displayed = None
      return blank
    return DashLane(self._slew(encode_lane_path(x, y)), reach, left_on, right_on, v_ego=v_ego)
