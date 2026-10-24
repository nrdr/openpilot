"""Rack maps for the Firmware steer ratio: yaw-measured where a car has been measured, else predicted from its specs.

Table A gives the EPS's angle shape, not the car's absolute ratio, so on its own the Firmware steer ratio
anchors it to CP.steerRatio. Where a car has been measured, this replaces that anchor with what the car does:
an effective rack ratio by wheel angle, after Table A, and a slip factor, fitted against the car's own VSA
yaw sensor (0x94, scale checked against GPS heading) with JamesL787 tools/lateral/fit_rack_map.py:

  lin = R(angle) * L * [k (1 - sf v^2) - g sf roll]

where lin is Table A's linear angle for the physical wheel angle, k the curvature, L the wheelbase the fit used.
VehicleModel has the same form with one ratio for every angle and the slip factor of the tyre-stiffness
defaults; here both are measured. Each ratio is the mean of the left- and right-turn medians, so an angle
offset cancels, and sf comes from how R changes with speed inside one angle band, so R's shape cannot leak
into it. Ported from JamesL787 ns-bosch-radar-testing honda_eps_rack_map.py; the same tables and arithmetic.

A map applies only to the car/EPS images it lists: one measured car can cover another image only when it is the
same car (the TEG-A010's covers the TBA-A030: the same 2016-18 Civic sedan, same published specs, byte-identical
Table A). Any other image nobody has measured gets a map predicted from its own car's published specs through its
own Table A (honda_spec_plant); its table says "spec" in its provenance.
"""
from dataclasses import dataclass, field
from functools import lru_cache
import math

import numpy as np

from openpilot.nrdr.features.lateral.honda_spec_plant import CIVIC_2019_SEDAN_SPEC, CIVIC_HATCH_SPORT_SPEC, CRV_2017_SPEC, \
  HondaSteeringSpec, spec_ratio_table
from openpilot.nrdr.features.lateral.honda_vgr import HONDA_VGR_PROFILES, HondaVgrProfile, normalize_honda_eps_firmware

GRAVITY = 9.81
# Angle grid the map is solved on: Table A's knots plus this many even steps (the source uses the same grid)
GRID_STEPS = 1001


@dataclass(frozen=True)
class RackMapTable:
  name: str
  fingerprint: str
  firmware: tuple[str, ...]
  wheelbase: float           # m, the L the fit used; the ratio is only meaningful with it
  ratio_bp: tuple[float, ...]  # physical wheel angle, deg
  ratio_v: tuple[float, ...]   # effective rack ratio after Table A
  slip_factor: float         # 1 / (m/s)^2
  provenance: str

  def __post_init__(self) -> None:
    if len(self.ratio_bp) != len(self.ratio_v) or len(self.ratio_bp) < 2:
      raise ValueError("rack map tables need matching angle and ratio arrays")
    if any(b <= a for a, b in zip(self.ratio_bp, self.ratio_bp[1:], strict=False)):
      raise ValueError("rack map angles must increase")
    values = (self.wheelbase, self.slip_factor, *self.ratio_bp, *self.ratio_v)
    if not all(math.isfinite(v) for v in values) or self.wheelbase <= 0.0 or min(self.ratio_v) <= 0.0:
      raise ValueError("rack map values must be finite, with a positive wheelbase and ratios")

  @property
  def measured(self) -> bool:  # fitted against the car's yaw sensor, not predicted from its specs
    return not self.provenance.startswith("spec")


# Clarity TRW-A020: routes 341-36b (owner JamesL787). The effective ratio still falls with angle after Table A,
# 17.3 near centre to 16.0 at 400 deg: the rack is quicker off centre than Table A says. Fitted on routes 341-35d
# alone the table is within 0.04 of this one; on held-out routes 363-36b it predicts the car's curvature within
# ~1% below 16 m/s and 1-5% above. paramsd's single ratio with VehicleModel's slip factor asked for 3-6% too much
# wheel in the city, the over-steer through tight turns.
CLARITY_TRW_A020_RACK = RackMapTable(
  "Clarity TRW-A020", "HONDA_CLARITY", ("39990-TRW-A020",), 2.75,
  ratio_bp=(6.5, 15.0, 32.0, 57.0, 85.0, 125.0, 175.0, 230.0, 305.0, 400.0),
  ratio_v=(17.34, 17.08, 16.94, 16.78, 16.78, 16.65, 16.48, 16.37, 16.29, 16.02),
  slip_factor=-0.0005,
  provenance="VSA yaw (0x94 bus 0), routes 341-36b",
)

# Civic Bosch TBA-C020: its VSA yaw (0x94 bus 1, 0.244 deg/s per count, GPS-checked) over routes 294 / 289 / 2b7 /
# 2c6 / 2d4 / 1b8 / 251 (34 min of turning at >= 3 deg). Held out one route at a time it predicts the car's
# curvature within ~1% at 70 deg and up and within 0.97-1.03 below.
CIVIC_TBA_C020_RACK = RackMapTable(
  "Civic Bosch TBA-C020", "HONDA_CIVIC_BOSCH", ("39990-TBA-C020",), 2.70,
  ratio_bp=(5.0, 12.5, 27.1, 53.5, 85.6, 123.4, 174.5, 226.6, 283.0),
  ratio_v=(14.93, 14.81, 14.79, 14.78, 14.70, 14.62, 14.49, 14.38, 14.27),
  slip_factor=-0.00065,
  provenance="VSA yaw (0x94 bus 1), routes 294/289/2b7/2c6/2d4/1b8/251",
)

# Civic TEG-A010, through the C120 Table A its image carries: its VSA yaw (0x94 bus 0, 0.2414 deg/s per count +
# 0.098 clockwise from 359k GPS pairs) over the owner's routes 0000012d-00000139 (2026-10-14/15, 3,800 s moving at
# >= 3 deg). Held out route by route it lands within ~1-3% in most bands. Adding the rev-b drive 0000013d
# (2026-10-17) refits it within 0.5% (14.22 -> 13.85, same slip factor), so it holds across the reflash. CP's 15.38
# delivered 6-11% more curvature than asked on those drives, most in slow turns past 150 deg. The TBA-A030 is the
# same 2016-18 Civic sedan (US part number; the TEG is the Japanese one): same published steering specs, the same
# byte-identical Table A, and its corrected PTM build carries the TEG's command row. So it takes this map; its own
# spec prediction would be 2% further off (14.46 against the measured 14.23 at centre).
CIVIC_TEG_A010_RACK = RackMapTable(
  "Civic TEG-A010", "HONDA_CIVIC", ("39990-TEG-A010", "39990-TBA-A030"), 2.70,
  ratio_bp=(5.1, 13.5, 26.2, 55.2, 86.6, 120.2, 175.8, 221.6, 293.1),
  ratio_v=(14.16, 14.16, 14.18, 14.09, 14.08, 14.01, 13.94, 13.86, 13.78),
  slip_factor=-0.00067,
  provenance="VSA yaw (0x94 bus 0), routes 0000012d-00000139; 0000013d agrees within 0.5%; the A030 is the same car",
)

# Insight TXM-A040: its VSA yaw (0x94 bus 1, 0.2428 deg/s per count + 0.157 clockwise, from 70k GPS pairs) over
# the owner's konik route 0000001e, split in halves (7 min of turning). Held out half against half it lands within
# ~2%. Thin past 50 deg: 10-24 s per band.
INSIGHT_TXM_A040_RACK = RackMapTable(
  "Insight TXM-A040", "HONDA_INSIGHT", ("39990-TXM-A040",), 2.70,
  ratio_bp=(4.6, 13.8, 35.8, 55.1, 83.3, 122.0, 174.0, 220.7),
  ratio_v=(17.86, 17.86, 17.86, 17.40, 17.28, 17.28, 17.21, 17.17),
  slip_factor=-0.00066,
  provenance="VSA yaw (0x94 bus 1), route 0000001e",
)

MEASURED_RACK_MAP_TABLES = (CLARITY_TRW_A020_RACK, CIVIC_TBA_C020_RACK, CIVIC_TEG_A010_RACK, INSIGHT_TXM_A040_RACK)


def _spec_table(name: str, fingerprint: str, firmware: str, table_a: str, spec: HondaSteeringSpec) -> RackMapTable:
  profile = next(p for p in HONDA_VGR_PROFILES if p.name == table_a)
  ratio_bp, ratio_v, slip_factor = spec_ratio_table(spec, profile)
  return RackMapTable(name, fingerprint, (firmware,), spec.wheelbase, ratio_bp, ratio_v, slip_factor,
                      provenance=f"spec: Honda lock turns {spec.lock_turns} and lock ratio {spec.lock_ratio} through " +
                                 f"its Table A ({table_a}); R0 +-2.5%, not road-measured")


# Images with no measurement: each on its own car's specs and its own Table A.
CIVIC_TBA_C120_SPEC_RACK = _spec_table("Civic Bosch TBA-C120", "HONDA_CIVIC_BOSCH", "39990-TBA-C120", "Civic C120/A030/TEG",
                                       CIVIC_2019_SEDAN_SPEC)
CIVIC_TGG_A120_SPEC_RACK = _spec_table("Civic hatch TGG-A120", "HONDA_CIVIC_BOSCH", "39990-TGG-A120", "Civic C020/TGG-A120",
                                       CIVIC_HATCH_SPORT_SPEC)
CRV_TLA_A040_SPEC_RACK = _spec_table("CR-V TLA-A040", "HONDA_CRV_5G", "39990-TLA-A040", "CR-V TLA-A040", CRV_2017_SPEC)
SPEC_RACK_MAP_TABLES = (CIVIC_TBA_C120_SPEC_RACK, CIVIC_TGG_A120_SPEC_RACK, CRV_TLA_A040_SPEC_RACK)

RACK_MAP_TABLES = MEASURED_RACK_MAP_TABLES + SPEC_RACK_MAP_TABLES
_TABLE_BY_CAR_FIRMWARE = {(table.fingerprint, firmware): table for table in RACK_MAP_TABLES for firmware in table.firmware}


def get_rack_map_table(CP) -> RackMapTable | None:
  """The table listing this exact car and reported EPS (measured, else spec), never one from a different car."""
  if str(getattr(CP, "brand", "")).lower() != "honda":
    return None
  fingerprint = str(getattr(CP, "carFingerprint", ""))
  for firmware in getattr(CP, "carFw", ()):
    if firmware.ecu == "eps":
      table = _TABLE_BY_CAR_FIRMWARE.get((fingerprint, normalize_honda_eps_firmware(firmware.fwVersion)))
      if table is not None:
        return table
  return None


@dataclass(frozen=True)
class RackMapGeometry:
  """Table A's shape on a car's rack map (yaw-measured or spec-predicted), in the firmware profile's interface.

  physical_to_linear / linear_to_physical give the linear angle at the CP ratio VehicleModel runs, so
  every speed-free consumer (controlsd's measured angle, lane-change shaping, the hybrid) uses the map's
  ratio by angle. Those cannot carry the map's slip factor; the two control paths that know the speed,
  angle_from_curvature and curvature_from_angle, use the full map."""
  profile: HondaVgrProfile
  table: RackMapTable
  cp_ratio: float
  angle_grid: np.ndarray = field(init=False, repr=False, compare=False)
  path_grid: np.ndarray = field(init=False, repr=False, compare=False)

  def __post_init__(self) -> None:
    if not (math.isfinite(self.cp_ratio) and self.cp_ratio > 0.0):
      raise ValueError("CP ratio must be finite and positive")
    last = self.profile.physical_knots[-1]
    angles = np.unique(np.r_[np.asarray(self.profile.physical_knots, dtype=float), np.linspace(0.0, last, GRID_STEPS)])
    linear = np.radians([self.profile.physical_to_linear(a) for a in angles])
    path = linear / np.interp(angles, self.table.ratio_bp, self.table.ratio_v)  # = L * k at zero roll and slip
    if np.any(np.diff(path) <= 0.0):
      raise ValueError("rack map must be monotonic to invert")
    if self.table.ratio_bp[-1] > last:
      raise ValueError("rack map bands must lie inside Table A's knots")
    object.__setattr__(self, "angle_grid", angles)
    object.__setattr__(self, "path_grid", path)

  @property
  def name(self) -> str:
    return f"{self.table.name} {'measured' if self.table.measured else 'spec'} rack map"

  @property
  def center_ratio(self) -> float:
    return float(self.table.ratio_v[0])

  # Past Table A's last knot (beyond lock on every car here, and past every table's last band) the map
  # continues with its last ratio along Table A's own tail, so it stays invertible at any angle.
  def _path(self, angle_deg: float) -> float:
    a = abs(angle_deg)
    if a > self.angle_grid[-1]:
      path = math.radians(self.profile.physical_to_linear(a)) / self.table.ratio_v[-1]
    else:
      path = float(np.interp(a, self.angle_grid, self.path_grid))
    return math.copysign(path, angle_deg)

  def _angle(self, path: float) -> float:
    p = abs(path)
    if p > self.path_grid[-1]:
      angle = self.profile.linear_to_physical(math.degrees(p * self.table.ratio_v[-1]))
    else:
      angle = float(np.interp(p, self.path_grid, self.angle_grid))
    return math.copysign(angle, path)

  def physical_to_linear(self, angle_deg: float) -> float:
    return math.degrees(self.cp_ratio * self._path(angle_deg))

  def linear_to_physical(self, angle_deg: float) -> float:
    return self._angle(math.radians(angle_deg) / self.cp_ratio)

  def angle_from_curvature(self, curvature: float, v_ego: float, roll: float) -> float:
    """Physical wheel angle, deg, for a curvature in the sign VehicleModel.get_steer_from_curvature takes."""
    sf = self.table.slip_factor
    path = self.table.wheelbase * (curvature * (1.0 - sf * v_ego ** 2) - GRAVITY * sf * roll)
    return self._angle(path)

  def curvature_from_angle(self, angle_deg: float, v_ego: float, roll: float) -> float:
    """Curvature, in VehicleModel.calc_curvature's sign, that a physical wheel angle gives. Inverse of the above."""
    sf = self.table.slip_factor
    return (self._path(angle_deg) / self.table.wheelbase + GRAVITY * sf * roll) / (1.0 - sf * v_ego ** 2)


@lru_cache(maxsize=16)
def _geometry(profile: HondaVgrProfile, table: RackMapTable, cp_ratio: float) -> RackMapGeometry:
  return RackMapGeometry(profile, table, cp_ratio)


def rack_map_geometry(CP, profile: HondaVgrProfile | None, cp_ratio: float) -> RackMapGeometry | None:
  """controlsd resolves the selection every frame; building the map's grid costs ~1 ms, so each is built once."""
  table = get_rack_map_table(CP)
  if profile is None or table is None:
    return None
  return _geometry(profile, table, float(cp_ratio))
