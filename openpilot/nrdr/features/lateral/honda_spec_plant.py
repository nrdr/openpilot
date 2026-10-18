"""Rack maps predicted from a Honda's published specs and its EPS image's Table A, for images nobody has measured.

Every yaw-measured rack map (honda_rack_map) is Table A, then a tan, then ONE ratio per car:

  curvature * L * (1 - sf v^2) = tan(lin / R0),   lin = Table A's linear angle (radians)

which reproduces the Clarity, C020, Insight and TEG maps within 2% from 15 to 230 deg. R0 comes from the road-wheel
angle at lock that Honda publishes (lock-to-lock turns, and the steering ratio Honda quotes, which is the ratio at
lock) seen through Table A; the slip factor from the axle loads (cornering stiffness ~ load^0.8). Held out one measured
car at a time, R0 lands within 1.6% rms (2.5% worst: the Insight and the TEG share published geometry but differ 4.4%
measured, so published specs cannot do better) and the slip factor within 10%. A car's own measurement replaces its
spec map as soon as one exists. Ported from JamesL787 ns-bosch-radar-testing honda_eps_spec_plant.py, the same
constants and arithmetic.
"""
from dataclasses import dataclass

import numpy as np

from openpilot.nrdr.features.lateral.honda_vgr import HondaVgrProfile

LB = 0.45359237
DRIVER_KG = 80.0       # the slip-factor masses are curb weight plus a driver, 50 kg of it on the front axle
DRIVER_FRONT_KG = 50.0
# R0 = SPEC_R0_GAIN * lin(lock) / road angle at lock: mean over the four yaw-measured cars (held out 1.13-1.17)
SPEC_R0_GAIN = 1.149
# sf = -SPEC_SLIP_GAIN * (m_front^0.2 - m_rear^0.2) / L: mean over the same cars (held out -9.7..+4.4%)
# Refit to the same four measured maps after allocating the driver's 80 kg
# exactly once (50 kg front, 30 kg rear). This coefficient is empirical.
SPEC_SLIP_GAIN = 0.0055454
SPEC_TABLE_POINTS = 12


@dataclass(frozen=True)
class HondaSteeringSpec:
  """What Honda publishes for one car (hondanews.com / hondainfocenter.com), plus openpilot's wheelbase."""
  lock_turns: float         # steering-wheel turns lock to lock
  lock_ratio: float         # the steering ratio Honda quotes: steering-wheel angle / road-wheel angle at lock
  curb_mass_lb: float
  front_weight_fraction: float
  wheelbase: float          # m

  @property
  def lock_deg(self) -> float:  # steering-wheel angle at lock, one side
    return self.lock_turns * 180.0


# The first four are the yaw-measured cars, which set the constants.
CLARITY_SPEC = HondaSteeringSpec(2.41, 12.72, 4052, 0.57, 2.75)
CIVIC_SPORT_SEDAN_SPEC = HondaSteeringSpec(2.11, 11.12, 2847, 0.608, 2.70)   # 2019 Civic Sport sedan (TBA-C020)
INSIGHT_SPEC = HondaSteeringSpec(2.54, 12.58, 3000, 0.61, 2.70)
CIVIC_2016_SEDAN_SPEC = HondaSteeringSpec(2.22, 10.93, 2800, 0.61, 2.70)    # 2016-18 Civic sedan (TEG-A010, TBA-A030)
CIVIC_2019_SEDAN_SPEC = HondaSteeringSpec(2.22, 10.94, 2850, 0.609, 2.70)   # 2019-21 Civic sedan LX/EX (TBA-C120)
CIVIC_HATCH_SPORT_SPEC = HondaSteeringSpec(2.11, 11.12, 2900, 0.60, 2.70)   # Civic hatchback Sport (TGG-A120)
CRV_2017_SPEC = HondaSteeringSpec(2.30, 12.3, 3398, 0.59, 2.66)             # CR-V 2017-19 (TLA-A040)


def tan_ratio(linear_deg, r0: float):
  """The effective rack ratio (honda_rack_map's) at a linear angle: lin / tan(lin / R0), -> R0 at centre."""
  lin = np.radians(np.maximum(np.asarray(linear_deg, dtype=float), 1e-6))
  return lin / np.tan(lin / r0)


def spec_r0(spec: HondaSteeringSpec, profile: HondaVgrProfile) -> float:
  """The rack ratio after Table A, at centre."""
  return SPEC_R0_GAIN * profile.physical_to_linear(spec.lock_deg) / (spec.lock_deg / spec.lock_ratio)


def spec_axle_masses(spec: HondaSteeringSpec) -> tuple[float, float]:
  curb_mass = spec.curb_mass_lb * LB
  front = curb_mass * spec.front_weight_fraction + DRIVER_FRONT_KG
  rear = curb_mass * (1.0 - spec.front_weight_fraction) + DRIVER_KG - DRIVER_FRONT_KG
  return front, rear


def spec_slip_factor(spec: HondaSteeringSpec) -> float:
  front, rear = spec_axle_masses(spec)
  return -SPEC_SLIP_GAIN * (front ** 0.2 - rear ** 0.2) / spec.wheelbase


def spec_ratio_table(spec: HondaSteeringSpec, profile: HondaVgrProfile) -> tuple[tuple, tuple, float]:
  """(physical angles, rack ratios, slip factor) for a RackMapTable: the tan shape up to lock, inside Table A's knots."""
  r0 = spec_r0(spec, profile)
  end = min(spec.lock_deg, profile.physical_knots[-1] - 0.5)
  angles = tuple(float(a) for a in np.round(np.linspace(5.0, end, SPEC_TABLE_POINTS), 1))
  ratios = tuple(round(float(r), 3) for r in tan_ratio([profile.physical_to_linear(a) for a in angles], r0))
  return angles, ratios, round(spec_slip_factor(spec), 6)


def r0_of_table(ratio_bp, ratio_v, profile: HondaVgrProfile) -> float:
  """The tan-shape R0 that best fits a measured rack table (angles of 12 deg and up)."""
  angles = np.asarray(ratio_bp, dtype=float)
  keep = angles >= 12.0
  lin = np.array([profile.physical_to_linear(a) for a in angles[keep]])
  measured = np.asarray(ratio_v, dtype=float)[keep]
  candidates = np.linspace(10.0, 22.0, 12001)
  errors = [np.mean((tan_ratio(lin, r) / measured - 1.0) ** 2) for r in candidates]
  return float(candidates[int(np.argmin(errors))])
