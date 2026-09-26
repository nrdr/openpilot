import math
from dataclasses import dataclass

from opendbc.can.parser import CANParser
from opendbc.car.honda import lane_path

# HUD_OBJECTS represents the moving car icons on the dash.
# The message is multiplexed. Mux values (1-10, 17-26, 33-42, 49-58) map to the same 10 slots.
# A persistent object_id is minted for each identified car. The slots work as a stack with slot 0
# (mux 1, 17, 33, 49) being the lead car if present. If lead not present, slot 0 can be an adjacent car.
# For example, if there are 2 cars (one lead, one adjacent), the lead car would be slot 0 and
# the adjacent car would be slot 1. If the lead car disappears, the adjacent car would move to slot 0.
# At 50 Hz and 10 slots, each slot gets 5Hz updates.
NUM_SLOTS = 10

# ---- Receive: camera HUD_OBJECTS -> snapshot --------------------------------
# Empty slot sentinel is max value of 1023, or 196.9 m after scaling
LONG_DIST_CAP_M = 195.0


@dataclass
class HudObject:
  slot: int
  object_id: int     # 1..31 when valid, 0 when empty
  d_rel: float       # longitudinal distance from ego (m)
  y_rel: float       # lateral position (+left) of ego (m)
  is_lead_car: bool  # camera's lead tag (slot 0 when present)
  valid: bool
  car_type: int = -1      # 7 = CAR, -7 = TRUCK, -1 = inactive
  rotation: int = -128    # 0 straight, <0 left, >0 right, -128 = inactive


class HudObjectTracker:
  """Persists the 10 HUD_OBJECTS slots"""

  def __init__(self):
    self._tracks: list[HudObject] = [
      HudObject(slot=i, object_id=0, d_rel=0.0, y_rel=0.0, is_lead_car=False, valid=False)
      for i in range(NUM_SLOTS)
    ]

  def update(self, cp_cam: CANParser) -> None:
    # 'slot' is derived from MUX: (mux - 1) % 16 collapses the four bank ranges (1-10, 17-26, 33-42, 49-58)
    # to 0-based indices 0-9.
    # Using vl_all to catch any missed frames, though not strictly necessary since update() is called
    # at 100Hz and this signal updates at 50Hz.
    # The message is subscribed with NaN frequency in get_can_parsers: not every radarless camera
    # emits it, so it must not gate the parser's validity.
    vla = cp_cam.vl_all["HUD_OBJECTS"]

    muxes = vla["MUX"]
    obj_ids = vla["OBJECT_ID"]
    long_dists = vla["LONG_DIST"]
    lat_dists = vla["LAT_DIST"]
    lead_flags = vla["IS_LEAD_CAR"]
    car_types = vla["CAR_TYPE"]
    rotations = vla["ROTATION"]

    for mux, oid, ld, yd, lead, ct, rot in zip(muxes, obj_ids, long_dists, lat_dists, lead_flags,
                                               car_types, rotations, strict=True):
      slot = (int(mux) - 1) % 16
      if 0 <= slot < NUM_SLOTS:
        valid = oid != 0 and ld < LONG_DIST_CAP_M
        self._tracks[slot] = HudObject(
          slot=slot,
          object_id=int(oid),
          d_rel=float(ld),
          y_rel=float(yd),
          is_lead_car=bool(lead),
          valid=valid,
          car_type=int(ct),
          rotation=int(rot),
        )

  def snapshot(self) -> list[HudObject]:
    return self._tracks


# ---- Author: OP's lead in slot 0 + camera's adjacent cars forwarded in slots 1-9 --------------------

# Byte-faithful empty-slot values (decoded from stock HUD_OBJECTS); an inconsistent frame risks the dash rejecting it.
INACTIVE = {
  "OBJECT_ID": 0,
  "IS_LEAD_CAR": 0,
  "CAR_TYPE": -1,
  "ROTATION": -128,
  "LONG_DIST": 196.9,    # raw 1023 = empty
  "LAT_DIST": 204.7,     # max
}

CAR_TYPE_CAR = 7
LONG_DIST_MAX_M = 194.0  # keep an active lead below the 196.9 empty sentinel
LAT_DIST_LIM_M = 204.7   # 12-bit signed @0.1 -> ±204.x m

# The dash renders LAT_DIST in the ego frame but under-scales it ~0.3x
# So scale OP's lead yRel by LAT_SCALE to land the lead car marker on our lane
LAT_SCALE = 0.35

# Used when no rotation available from camera (OP disengaged)
ROT_BAND_M = 1.5         # m of lateral offset per rotation step
ROT_MAX = 6              # ±6 -> ±30 deg

# OP has no persistent lead identity, so LeadObjectId mints a new OBJECT_ID on a fresh lead or a range discontinuity
# (a handoff to a different car). dRel is noisy, so instead of a per-sample range-rate test we run a leaky predictor
# (feed-forward vRel, leak toward dRel) and re-id only when the residual accumulates past REID_GAP_M.
REID_GAP_M = 8.0         # m, accumulated |dRel - predicted| above this = a different car
REID_TAU = 1.5           # s, predictor leak time-constant
REID_REFRACTORY = 1.5    # s, collapse a multi-frame transition into one re-id
MAX_OBJECT_ID = 31       # OBJECT_ID is 5-bit (1..31; 0 = empty)


class LeadObjectId:
  """Tracks a stable slot-0 OBJECT_ID for OP's lead, re-IDing on a fresh lead or a range discontinuity."""
  def __init__(self):
    self.object_id = 0
    self._on = False
    self._pred = 0.0      # leaky predicted dRel
    self._prev_t = 0.0
    self._reid_t = -1e9

  def update(self, status: bool, d_rel: float, v_rel: float, now: float) -> int:
    """Returns the OBJECT_ID to send for slot 0 (0 when there's no lead)."""
    if not status:
      self.object_id = 0
      self._on = False
      return 0

    new_lead = not self._on
    if self._on:
      dt = max(now - self._prev_t, 1e-3)
      self._pred += v_rel * dt                          # feed-forward: d(dRel)/dt ~= vRel
      self._pred += min(dt / REID_TAU, 1.0) * (d_rel - self._pred)   # leak toward the measurement
      if abs(d_rel - self._pred) > REID_GAP_M and now - self._reid_t > REID_REFRACTORY:
        new_lead = True
    self._prev_t = now

    if new_lead:
      self.object_id = self.object_id % MAX_OBJECT_ID + 1   # wrap 1..31, never 0
      self._reid_t = now
      self._pred = d_rel                                    # reset the predictor to the new lead
    self._on = True
    return self.object_id


# LeadSmoother stabilizes the rendered lead marker without lagging real motion: feed vRel forward for dRel (no lag on
# approach/pull-away) then leak toward the measurement to reject jitter, with the residual clamped against outlier
# spikes and feed-forward gated off near zero vRel (a stopped lead is a pure low-pass); yRel is a plain low-pass. It
# snaps (not smooths) on a lead identity change.
DREL_SMOOTH_TAU = 0.6     # s, dRel leak time-constant
YREL_SMOOTH_TAU = 0.5     # s, yRel low-pass time-constant
FF_VREL_MIN = 0.5         # m/s, feed vRel forward only above this
DREL_RESID_CLAMP = 1.5    # m, cap the leak's input residual so an outlier spike barely moves it


class LeadSmoother:
  """Smooths the lead's (dRel, yRel) for a stable dash marker. Call update() per TX tick; it snaps on a new id."""
  def __init__(self):
    self._id = 0
    self._d = 0.0
    self._y = 0.0
    self._t = 0.0

  def update(self, d_rel: float, y_rel: float, v_rel: float, object_id: int, now: float) -> tuple[float, float]:
    """Returns the smoothed (d_rel, y_rel) to render. `object_id` change = a new car -> snap to it."""
    if object_id != self._id:                 # fresh lead / handoff -> snap to it, don't slide across
      self._id, self._d, self._y, self._t = object_id, d_rel, y_rel, now
      return d_rel, y_rel
    dt = max(now - self._t, 1e-3)
    self._t = now
    if abs(v_rel) >= FF_VREL_MIN:              # feed-forward real motion (no lag); off near zero -> pure low-pass
      self._d += v_rel * dt
    resid = min(max(d_rel - self._d, -DREL_RESID_CLAMP), DREL_RESID_CLAMP)   # clamp -> spike reject
    self._d += (1.0 - math.exp(-dt / DREL_SMOOTH_TAU)) * resid
    self._y += (1.0 - math.exp(-dt / YREL_SMOOTH_TAU)) * (y_rel - self._y)
    return self._d, self._y


def lead_rotation(lateral_left_m: float) -> int:
  """Rotation from a lead's lateral offset. Used for OP's lead when camera isn't feeding a rotation (disengaged).
  Negative is rotating to left, positive is rotating to right.
  """
  magnitude = min(round(abs(lateral_left_m) / ROT_BAND_M), ROT_MAX)
  return -magnitude if lateral_left_m > 0 else magnitude


LEAD_PROB_ON = 0.5    # modelV2 leadsV3 prob to start rendering a lead
LEAD_PROB_OFF = 0.35  # ...and to keep rendering it (hysteresis against threshold flapping)
LEAD_HOLD_S = 0.6     # s: bridge a dropped lead briefly so single-frame prob dips don't blink the marker

# modelV2.leadsV3's three entries are the model's lead prediction at time horizons t = 0 s, +2 s and
# +4 s -- NOT three simultaneous cars. All three usually describe the same physical vehicle, so the
# extra entries are only rendered when spatially distinct from every already-rendered object (a
# genuinely different car: the one ahead of the lead, or a cut-in the model already resolves at the
# longer horizon). Only used when there are no camera tracks to forward (CAN FD), so slots 1-2 are
# otherwise blank.
EXTRA_LEAD_SLOTS = (1, 2)     # dash slots for distinct leadsV3[1]/[2]; slot 0 stays OP's lead
EXTRA_LEAD_MIN_SEP_D = 5.0    # m: closer than this longitudinally...
EXTRA_LEAD_MIN_SEP_Y = 1.5    # m: ...and this laterally = the same car, don't render it twice


@dataclass
class ModelLead:
  """OP's lead derived from modelV2.leadsV3"""
  status: bool
  dRel: float
  yRel: float   # +left
  vRel: float
  prob: float = 0.0   # model lead prob; carried so the author can apply on/off hysteresis


def leads_from_model(model, v_ego, n=3):
  """Up to n ModelLeads from modelV2.leadsV3 (index 0 = the lead OP acts on). modelV2's lateral is
  +right, so it is negated to match the dash's +left. v is made relative (v - vEgo) for the
  smoother's feed-forward. Data stays populated below LEAD_PROB_ON too (status False, prob carried):
  the HUD author's hysteresis keeps an already-rendered lead alive down to LEAD_PROB_OFF instead of
  blinking it at the 0.5 threshold."""
  out = []
  for i in range(n):
    if model is None or len(model.leadsV3) <= i or len(model.leadsV3[i].x) == 0:
      out.append(ModelLead(False, 0.0, 0.0, 0.0))
      continue
    lead = model.leadsV3[i]
    out.append(ModelLead(bool(lead.prob >= LEAD_PROB_ON), float(lead.x[0]), -float(lead.y[0]),
                         float(lead.v[0]) - v_ego, prob=float(lead.prob)))
  return out


def lead_from_model(model, v_ego):
  """OP's lead from modelV2.leadsV3[0] (see leads_from_model)."""
  return leads_from_model(model, v_ego, n=1)[0]


def create_hud_object(packer, bus, mux, track):
  """Pack one HUD_OBJECTS frame for mux.

  `track` is None for an inactive slot, else a dict {d_rel, y_rel, object_id, is_lead_car, car_type, rotation}.
  CAR_TYPE/ROTATION are borrowed from the stock camera (OP doesn't provide them); CHECKSUM/COUNTER by the packer.
  """
  values = {"MUX": mux}
  if track is None:
    values.update(INACTIVE)
  else:
    values.update({
      "OBJECT_ID": int(track["object_id"]),
      "IS_LEAD_CAR": int(track["is_lead_car"]),
      "CAR_TYPE": int(track["car_type"]),
      "ROTATION": int(track["rotation"]),
      "LONG_DIST": min(max(track["d_rel"], 0.0), LONG_DIST_MAX_M),
      "LAT_DIST": min(max(track["y_rel"], -LAT_DIST_LIM_M), LAT_DIST_LIM_M),
    })
  return packer.make_can_msg("HUD_OBJECTS", bus, values)


def forward_hud_object(packer, bus, mux, tracks):
  """Forward the camera's object for `mux`. Used in stock ACC, where the camera owns the lead. This is
  necessary to keep mux reliably synced between hud_objects and lane_path."""
  slot = (mux - 1) % 16
  st = tracks[slot] if (tracks and slot < len(tracks)) else None
  track = ({"d_rel": st.d_rel, "y_rel": st.y_rel, "object_id": st.object_id, "is_lead_car": st.is_lead_car,
            "car_type": st.car_type, "rotation": st.rotation} if (st is not None and st.valid) else None)
  return create_hud_object(packer, bus, mux, track)


class HudObjectAuthor:
  """Authors HUD_OBJECTS: OP's lead in slot 0 (stable id via LeadObjectId + dRel/yRel smoothing via LeadSmoother),
  the camera's non-lead cars forwarded in slots 1-9, cycling MUX. The carcontroller calls create() once per
  ~50 Hz tick and sends the returned frame."""
  def __init__(self):
    self._track_id = LeadObjectId()
    self._smoother = LeadSmoother()
    self._lead_id = 0       # OBJECT_ID currently emitted for OP's lead (0 = none)
    self._prev_op_id = 0    # last LeadObjectId id, to detect a fresh lead / handoff
    self._lead_on = False   # hysteresis state for the rendered lead
    self._lead_hold: ModelLead | None = None   # last rendered lead, for the drop-hold bridge
    self._lead_seen_t = -1e9
    # distinct leadsV3[1]/[2] rendered as non-lead cars in slots 1-2 (CAN FD, where tracks is None)
    self._extra_ids = {slot: LeadObjectId() for slot in EXTRA_LEAD_SLOTS}
    self._extra_smooth = {slot: LeadSmoother() for slot in EXTRA_LEAD_SLOTS}
    self._extra_emit = dict.fromkeys(EXTRA_LEAD_SLOTS, 0)   # emitted OBJECT_ID per extra slot

  def _update_extras(self, extra_leads, lead, in_use, now):
    """Per-tick state update for the extra leads; returns {slot: track-dict-or-None}. Extras must
    stay distinct from the primary lead and from each other, and their OBJECT_IDs must not collide
    with the primary's or one another's."""
    rendered = [(lead.dRel, lead.yRel)] if lead.status else []
    out = {}
    for slot, ex in zip(EXTRA_LEAD_SLOTS, extra_leads or (), strict=False):
      distinct = ex.status and all(abs(ex.dRel - d) >= EXTRA_LEAD_MIN_SEP_D or
                                   abs(ex.yRel - y) >= EXTRA_LEAD_MIN_SEP_Y
                                   for d, y in rendered)
      op_id = self._extra_ids[slot].update(distinct, ex.dRel, ex.vRel, now)
      if not distinct:
        self._extra_emit[slot] = 0
        out[slot] = None
        continue
      emit = self._extra_emit[slot]
      if emit == 0 or emit in in_use:
        emit = op_id
        while emit in in_use:
          emit = emit % MAX_OBJECT_ID + 1
        self._extra_emit[slot] = emit
      in_use.add(emit)
      d_rel, y_rel = self._extra_smooth[slot].update(ex.dRel, LAT_SCALE * ex.yRel, ex.vRel, emit, now)
      rendered.append((ex.dRel, ex.yRel))
      out[slot] = {"d_rel": d_rel, "y_rel": y_rel, "object_id": emit, "is_lead_car": 0,
                   "car_type": CAR_TYPE_CAR, "rotation": lead_rotation(y_rel / LAT_SCALE)}
    return out

  def _gate_lead(self, lead: ModelLead, now: float) -> ModelLead:
    """On/off hysteresis + short drop-hold for the rendered lead. leadsV3[0].prob hovers around the
    0.5 threshold in real traffic, which blinked the dash marker at a sub-second cadence the stock
    radar never produces; render from LEAD_PROB_ON, keep rendering down to LEAD_PROB_OFF, and bridge
    a full drop for LEAD_HOLD_S (dead-reckoned on vRel) before blanking the slot."""
    if lead.prob >= (LEAD_PROB_OFF if self._lead_on else LEAD_PROB_ON):
      self._lead_on = True
      self._lead_hold = lead
      self._lead_seen_t = now
      return lead if lead.status else ModelLead(True, lead.dRel, lead.yRel, lead.vRel, lead.prob)
    if self._lead_on and self._lead_hold is not None and now - self._lead_seen_t < LEAD_HOLD_S:
      h = self._lead_hold
      return ModelLead(True, h.dRel + h.vRel * (now - self._lead_seen_t), h.yRel, h.vRel, h.prob)
    self._lead_on = False
    self._lead_hold = None
    return ModelLead(False, 0.0, 0.0, 0.0)

  def _lead_object_id(self, status: bool, op_id: int, stock_lead_id: int | None, in_use: set[int]) -> int:
    """OBJECT_ID to emit for OP's lead: prefer the camera's own lead id, else hold a minted id, re-picking out of
    the forwarded stock ids only on a fresh lead / handoff or a collision. 0 when there is no lead."""
    if not status:
      self._lead_id = 0
    elif stock_lead_id is not None:
      self._lead_id = stock_lead_id
    elif self._lead_id == 0 or op_id != self._prev_op_id or self._lead_id in in_use:
      # advance from the current id instead of picking the lowest free one: with no camera ids in
      # use (CAN FD, tracks is None) lowest-free always yielded 1, so a handoff to a different car
      # kept OBJECT_ID 1 and rendered as the same object teleporting -- and the smoother, keyed on
      # the emitted id, slid between the two cars instead of snapping. A fresh id per handoff
      # matches the stock radar and makes the snap take effect.
      nxt = self._lead_id % MAX_OBJECT_ID + 1
      while nxt in in_use:
        nxt = nxt % MAX_OBJECT_ID + 1
      self._lead_id = nxt
    self._prev_op_id = op_id
    return self._lead_id

  def create(self, packer, bus, lead, tracks, mux: int, now: float, extra_leads=None):
    """`lead` = carControlSP.leadOne; `tracks` = the camera's HudObject snapshot (may be None); `mux` = the shared
    LANE_PATH/HUD_OBJECTS multiplexor for this frame. Returns one packed HUD_OBJECTS frame for the slot the mux lands
    on (OP's lead in slot 0, else a forwarded camera adjacent car — including in slot 0 when OP has no lead — else
    inactive). re-ID + smoothing run every tick so their state stays continuous across the non-lead frames."""
    lead = self._gate_lead(lead, now)
    op_id = self._track_id.update(lead.status, lead.dRel, lead.vRel, now)
    stock_lead, in_use = None, set()
    for t in (tracks or ()):
      if not t.valid:
        continue
      if t.is_lead_car:
        stock_lead = t                # the camera's lead -> dropped, but we borrow its id / car_type / rotation
      elif t.slot != 0:
        in_use.add(t.object_id)       # ids of the adjacent cars we forward -> OP's lead id must avoid these
    stock_lead_id = stock_lead.object_id if stock_lead is not None else None
    lead_id = self._lead_object_id(lead.status, op_id, stock_lead_id, in_use)
    if lead.status:
      in_use.add(lead_id)

    # scale the lateral by the lane-gain correction at the lead's distance so the marker tracks the
    # lane rendering (LAT_SCALE was tuned against the previous, flatter lane gain law)
    lat_scale = LAT_SCALE * lane_path.curve_boost(lead.dRel)
    d_rel, y_rel = self._smoother.update(lead.dRel, lat_scale * lead.yRel, lead.vRel, lead_id, now)

    # extra distinct leadsV3 entries only render where the camera provides no cars to forward
    extras = self._update_extras(extra_leads, lead, in_use, now) if tracks is None else {}

    slot = (mux - 1) % 16
    if slot == 0 and lead.status:
      track = {"d_rel": d_rel, "y_rel": y_rel, "object_id": lead_id, "is_lead_car": 1,
               "car_type": stock_lead.car_type if stock_lead is not None else CAR_TYPE_CAR,
               # disengaged -> no camera rotation; calculate one from the lead's lateral
               "rotation": stock_lead.rotation if stock_lead is not None else lead_rotation(y_rel / lat_scale)}
    elif slot in extras:
      track = extras[slot]
    # forward slots 1-9 and slot 0 when not a lead
    else:
      st = tracks[slot] if (tracks and slot < len(tracks)) else None
      track = ({"d_rel": st.d_rel, "y_rel": st.y_rel, "object_id": st.object_id, "is_lead_car": 0,
                "car_type": st.car_type, "rotation": st.rotation}
                # never forward the camera's lead: if OP has no lead, the HUD must not flag one OP isn't acting on
               if (st is not None and st.valid and not st.is_lead_car) else None)
    return create_hud_object(packer, bus, mux, track)
