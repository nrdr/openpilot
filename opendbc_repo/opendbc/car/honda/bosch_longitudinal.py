import copy
import math

import numpy as np

from opendbc.car import ACCELERATION_DUE_TO_GRAVITY, DT_CTRL, structs
from opendbc.car.honda.bosch_a_radar import VERIFIED_BOSCH_A_CARS
from opendbc.car.honda.brake_onset import BrakeOnsetCompensation
from opendbc.car.honda.bosch_low_speed_brake import LowSpeedBrakeAssist
from opendbc.car.honda.bosch_gas_learner import CivicGasLearner, LEARN_VERSION, gas_lookup_accel
from opendbc.car.honda.values import CAR, HondaFlags

LongCtrlState = structs.CarControl.Actuators.LongControlState
BOSCH_BRAKE_FORCE_ON = -0.12
BOSCH_BRAKE_FORCE_RELEASE = -0.02
# Bosch-A stop-and-go brake cycling, measured on the Civic (STATUS 263/265, route 0000001f--39b2448f7d). At 2-4 m/s with a command of
# -0.1..-0.3 the brake request toggled 15-25 times a minute: brake-on cut the gas from ~30-40 to 0, and every release
# jumped the gas straight to the 60-unit cap. Replay of this class on 1f's logged command, open loop, 50 Hz, with
# long-control drops resetting it, against the old path on the same harness (the state machine reproduces the
# logged BRAKE_REQUEST on 90.4 % of frames; no closed-loop gap or jerk numbers):
#   BOSCH_A_BRAKE_FORCE_ON: brake request only below -0.20, the bottom of the gas lookup, so the band between it and
#     -0.12 coasts with the gas off instead of braking. The only change that cuts toggles: 3.69 -> 3.17 per minute
#     (an earlier sim that ignored long-control drops said 2.11).
#   BOSCH_A_BRAKE_MIN_HOLD_S: once on, the request stays on this long unless the command asks for real acceleration
#     (above BOSCH_A_BRAKE_HOLD_ESCAPE). Holds under 1.5 s 27.6 % -> 16.7 %; the rest are long-control drops and the
#     escape (about 0.2 per minute, each shortening a hold by 0.04-0.4 s).
#   BOSCH_A_RELEASE_GAS_START / _RAMP_S: after a release the gas starts at most at 35 and reaches the lookup over 1 s,
#     instead of the 60 cap. Gas on the release frame 60 -> 35; mean over the first second 121 -> 81.
#   BOSCH_A_LAUNCH_GAS_RAMP_S: a release straight out of stopping (a launch from a stop, not a stop-and-go brake cycle)
#     ramps over 0.5 s instead. Route 0000007c--0ea998a750 16:59 (owner bookmark, "didn't want to move, I tapped the
#     gas"): openpilot released and sent gas 36 -> 232 over 0.8 s with no motion; clean launches on 7c/72/75/76 take
#     0.9-1.7 s from release to motion. Replay cannot model the car's standstill release, so the gain is unmeasured:
#     owner-approved road test 2026-11-03. The brake-cycling releases above keep the 1 s ramp.
# Stopping still forces the request on, and a long-control drop still clears it, exactly as before.
# Runs on every car with the Bosch-A radar harness (bosch_a_harness), owner 2026-10-24: the CR-V 5G is static only.
BOSCH_A_BRAKE_FORCE_ON = -0.20
BOSCH_A_BRAKE_MIN_HOLD_S = 1.5
BOSCH_A_BRAKE_HOLD_ESCAPE = 0.2
BOSCH_A_RELEASE_GAS_START = 35.0
BOSCH_A_RELEASE_GAS_RAMP_S = 1.0
BOSCH_A_LAUNCH_GAS_RAMP_S = 0.5

CLASSIC_BOSCH_CARS = frozenset((
  CAR.HONDA_NBOX_2G,
  CAR.HONDA_ACCORD,
  CAR.HONDA_CIVIC_BOSCH,
  CAR.HONDA_CIVIC_BOSCH_DIESEL,
  CAR.HONDA_CIVIC_2022,
  CAR.HONDA_CRV_5G,
  CAR.HONDA_CRV_HYBRID,
  CAR.HONDA_HRV_3G,
  CAR.HONDA_CITY_7G,
  CAR.ACURA_RDX_3G,
  CAR.ACURA_RDX_3G_MMR,
  CAR.HONDA_INSIGHT,
  CAR.HONDA_E,
  CAR.HONDA_E_ADVANCE,
  CAR.ACURA_MDX_4G,
  CAR.HONDA_ODYSSEY_5G_MMR,
  CAR.ACURA_TLX_2G,
  CAR.HONDA_FIT_4G,
  CAR.ACURA_INTEGRA,
  CAR.ACURA_ADX,
))
HONDA_BOSCH_RADARLESS = frozenset((
  CAR.HONDA_CIVIC_2022,
  CAR.HONDA_HRV_3G,
  CAR.HONDA_CITY_7G,
  CAR.HONDA_FIT_4G,
  CAR.ACURA_INTEGRA,
  CAR.ACURA_ADX,
))

def update_honda_bosch_braking(braking: bool, gas_pedal_force: float, stopping: bool, long_active: bool) -> bool:
  if not long_active:
    return False
  if stopping:
    return True
  if braking:
    return gas_pedal_force <= BOSCH_BRAKE_FORCE_RELEASE
  return gas_pedal_force < BOSCH_BRAKE_FORCE_ON

class BoschABrakeEdge:
  """Bosch-A harness brake request with a deeper on threshold, a minimum hold and a gas ramp after release."""
  def __init__(self, dt: float):
    self.dt = dt
    self.reset()

  def reset(self):
    self.braking = False
    self.hold_s = 0.0
    self.release_s = math.inf
    self.stopping = False
    self.ramp_s = BOSCH_A_RELEASE_GAS_RAMP_S

  def update(self, gas_pedal_force: float, stopping: bool, long_active: bool) -> bool:
    if not long_active:
      self.reset()
      return False
    was_braking = self.braking
    was_stopping = self.stopping
    self.stopping = stopping
    if stopping:
      self.braking = True
    elif self.braking:
      held = self.hold_s < BOSCH_A_BRAKE_MIN_HOLD_S and gas_pedal_force <= BOSCH_A_BRAKE_HOLD_ESCAPE
      self.braking = held or gas_pedal_force <= BOSCH_BRAKE_FORCE_RELEASE
    else:
      self.braking = gas_pedal_force < BOSCH_A_BRAKE_FORCE_ON
    if self.braking:
      self.hold_s = self.hold_s + self.dt if was_braking else 0.0
      self.release_s = math.inf
    else:
      if was_braking:
        self.release_s = 0.0
        self.ramp_s = BOSCH_A_LAUNCH_GAS_RAMP_S if was_stopping else BOSCH_A_RELEASE_GAS_RAMP_S
      else:
        self.release_s += self.dt
    return self.braking

  def limit_gas(self, gas: float) -> float:
    """Gas after a brake release rises from BOSCH_A_RELEASE_GAS_START to the lookup over ramp_s (shorter for a launch)."""
    if self.braking or self.release_s >= self.ramp_s or gas <= BOSCH_A_RELEASE_GAS_START:
      return gas
    return BOSCH_A_RELEASE_GAS_START + (gas - BOSCH_A_RELEASE_GAS_START) * self.release_s / self.ramp_s


def get_honda_bosch_wind_brake_mps2(v_ego: float) -> float:
  return float(np.interp(v_ego, [0.0, 13.4, 22.4, 31.3, 40.2], [0.0, 0.049, 0.136, 0.267, 0.441]))

def bosch_a_harness(cp):
  """A verified classic Bosch car running the Bosch-A radar harness (same car gate as BoschARadar)."""
  return (cp.carFingerprint in VERIFIED_BOSCH_A_CARS and not cp.radarUnavailable and
          not cp.flags & (HondaFlags.BOSCH_RADARLESS | HondaFlags.BOSCH_CANFD | HondaFlags.BOSCH_ALT_RADAR))

def qualified(cp):
  return (cp.brand == "honda" and cp.carFingerprint in CLASSIC_BOSCH_CARS and cp.flags & HondaFlags.BOSCH and
          not cp.flags & HondaFlags.BOSCH_CANFD and cp.openpilotLongitudinalControl and
          not cp.passive and not cp.dashcamOnly and not cp.notCar and
          bool(cp.flags & HondaFlags.BOSCH_RADARLESS) == (cp.carFingerprint in HONDA_BOSCH_RADARLESS))


# Port note (nrdr): star7's CarControllerParams gives Bosch cars the gas table [-0.2, 2.0] -> [0, gas_max]
# (values.py CarControllerParams.__init__ in Honda-PTM-Testing). nrdr's table is [0, 2.0] -> [0, 1600] and is shared with
# its non-Bosch-A paths, so BoschLongitudinal gets its own copy of the params with star7's table. Numbers are star7's.
STAR7_GAS_LOOKUP_BP = [-0.2, 2.0]
STAR7_GAS_MAX = {CAR.HONDA_CIVIC_BOSCH: 750, CAR.HONDA_ODYSSEY_5G_MMR: 2000, CAR.ACURA_RDX_3G_MMR: 2000, CAR.ACURA_RDX_3G: 2200}
STAR7_GAS_MAX_DEFAULT = 1600


def star7_params(cp, params):
  """A copy of the controller params carrying star7's Bosch gas table for this car."""
  p = copy.copy(params)
  p.BOSCH_GAS_LOOKUP_BP = list(STAR7_GAS_LOOKUP_BP)
  p.BOSCH_GAS_LOOKUP_V = [0, STAR7_GAS_MAX.get(cp.carFingerprint, STAR7_GAS_MAX_DEFAULT)]
  return p


class BoschLongitudinal:
  def __init__(self, cp, params):
    if not qualified(cp):
      raise ValueError("Honda road load requires its admitted classic Bosch profile")
    self.CP = cp
    self.params = params
    self.pitch = 0.0
    self.accel = 0.0
    self.gas = 0.0
    self.bosch_braking = False
    self.bosch_last_gas = 0.0
    # Civic Bosch runs the ns live gas learner (bosch_gas_learner.py); every other car keeps the shared learner below.
    self.civic_learner = CivicGasLearner() if cp.carFingerprint == CAR.HONDA_CIVIC_BOSCH else None
    self.learner_version = LEARN_VERSION if self.civic_learner is not None else None
    # Bosch-A harness cars only (owner 2026-10-24). The brake_onset.py fit and the edge numbers are from the Civic;
    # on the CR-V 5G they are static only. update() runs every other control frame.
    bosch_a = bosch_a_harness(cp)
    self.brake_onset = BrakeOnsetCompensation(2 * DT_CTRL) if bosch_a else None
    self.brake_edge = BoschABrakeEdge(2 * DT_CTRL) if bosch_a else None
    self.low_speed_brake = LowSpeedBrakeAssist(2 * DT_CTRL) if bosch_a else None
    self.set_factors(1.0, 1.0)

  def set_factors(self, gas, wind):
    if self.civic_learner is not None:
      self.civic_learner.load(gas, wind)
      self.bosch_gas_factor = self.civic_learner.raw_gasfactor
      self.bosch_wind_factor = self.civic_learner.raw_windfactor
      return
    self.bosch_gas_factor = float(gas) if math.isfinite(gas) and 0.01 <= gas <= 3.0 else 1.0
    self.bosch_wind_factor = float(wind) if math.isfinite(wind) and 0.1 <= wind <= 5.0 else 1.0
    self.bosch_wind_factor_before_brake = self.bosch_wind_factor
    self.bosch_gas_factor_before_gasmax = self.bosch_gas_factor
    self.bosch_wind_factor_before_gasmax = self.bosch_wind_factor

  def observe_orientation(self, orientation):
    if len(orientation) == 3 and math.isfinite(orientation[1]):
      self.pitch = orientation[1]

  def update(self, CC, CS, accel):
    actuators = CC.actuators
    hill_brake = math.sin(self.pitch) * ACCELERATION_DUE_TO_GRAVITY
    wind_brake_mps2 = get_honda_bosch_wind_brake_mps2(CS.out.vEgo)
    min_gas = self.params.BOSCH_GAS_LOOKUP_BP[0]
    self.accel = float(np.clip(accel, self.params.BOSCH_ACCEL_MIN, self.params.BOSCH_ACCEL_MAX))
    target = self.accel
    if self.brake_onset is not None:
      self.accel = self.brake_onset.update(self.accel, active=bool(
        CC.longActive and actuators.longControlState == LongCtrlState.pid and
        not CS.out.gasPressed and not CS.out.brakePressed))
    if self.low_speed_brake is not None:
      lcs = actuators.longControlState
      self.accel = self.low_speed_brake.update(target, self.accel, CS.out.aEgo, CS.out.vEgo,
        active=bool(CC.longActive and lcs in (LongCtrlState.pid, LongCtrlState.stopping) and
                    not CS.out.gasPressed and not CS.out.brakePressed),
        stopping=lcs == LongCtrlState.stopping)
      self.accel = float(np.clip(self.accel, self.params.BOSCH_ACCEL_MIN, self.params.BOSCH_ACCEL_MAX))
    if self.civic_learner is not None:
      return self._update_civic(CC, CS, hill_brake, wind_brake_mps2, min_gas)
    gas_pedal_force = self.accel + hill_brake
    if self.CP.carFingerprint not in HONDA_BOSCH_RADARLESS:
      gas_pedal_force += wind_brake_mps2 * self.bosch_wind_factor
      if actuators.longControlState == LongCtrlState.pid and (not CS.out.gasPressed):
        gas_error = self.accel - CS.out.aEgo
        if gas_error != 0.0 and gas_pedal_force > min_gas:
          if self.CP.carFingerprint == CAR.HONDA_INSIGHT:
            gas_learn_speed = 150.0
          elif self.CP.carFingerprint in (CAR.ACURA_RDX_3G, CAR.ACURA_RDX_3G_MMR):
            gas_learn_speed = 300.0
          else:
            gas_learn_speed = 50.0
          gas_learn_force = gas_pedal_force
          self.bosch_gas_factor = float(np.clip(self.bosch_gas_factor + gas_error / gas_learn_speed * gas_learn_force, 0.1, 3.0))
        if gas_error != 0.0 and (not CS.out.brakePressed) and (CS.out.vEgo > 0.0):
          wind_learn_speed = 100.0 if self.CP.carFingerprint in (CAR.ACURA_RDX_3G, CAR.ACURA_RDX_3G_MMR) else 1000.0
          wind_adjust = 1.0 + wind_brake_mps2 / wind_learn_speed
          if gas_error > 0.0:
            self.bosch_wind_factor = float(np.clip(self.bosch_wind_factor * wind_adjust, 0.1, 3.0))
          else:
            self.bosch_wind_factor = float(np.clip(self.bosch_wind_factor / wind_adjust, 0.1, 3.0))
        if gas_pedal_force <= 0.0:
          self.bosch_wind_factor = max(self.bosch_wind_factor, self.bosch_wind_factor_before_brake)
        else:
          self.bosch_wind_factor_before_brake = self.bosch_wind_factor
        if gas_pedal_force >= self.params.BOSCH_ACCEL_MAX:
          self.bosch_gas_factor = min(self.bosch_gas_factor, self.bosch_gas_factor_before_gasmax)
          self.bosch_wind_factor = min(self.bosch_wind_factor, self.bosch_wind_factor_before_gasmax)
        else:
          self.bosch_gas_factor_before_gasmax = self.bosch_gas_factor
          self.bosch_wind_factor_before_gasmax = self.bosch_wind_factor
    gas_lookup_input = gas_pedal_force * self.bosch_gas_factor
    self.gas = float(np.interp(gas_lookup_input, self.params.BOSCH_GAS_LOOKUP_BP, self.params.BOSCH_GAS_LOOKUP_V))
    self.gas = min(self.gas, max(60.0, self.bosch_last_gas + 60.0))
    stopping = actuators.longControlState == LongCtrlState.stopping
    self.bosch_braking = self._update_braking(gas_pedal_force, stopping, CC.longActive)
    self.bosch_last_gas = self.gas
    return self.accel, self.gas, gas_pedal_force, self.bosch_braking

  def _update_civic(self, CC, CS, hill_brake, wind_brake_mps2, min_gas):
    actuators = CC.actuators
    learner = self.civic_learner
    gas_pedal_force = self.accel + hill_brake + wind_brake_mps2 * learner.windfactor
    learner.update(self.accel, CS.out.aEgo, gas_pedal_force, wind_brake_mps2,
                   engaged=CC.longActive and actuators.longControlState == LongCtrlState.pid,
                   gas_pressed=CS.out.gasPressed, brake_pressed=CS.out.brakePressed, v_ego=CS.out.vEgo,
                   pitch=self.pitch, at_accel_max=gas_pedal_force >= self.params.BOSCH_ACCEL_MAX)
    # Saved values are the learned factors; the applied ones trail them through the filter.
    self.bosch_gas_factor = learner.raw_gasfactor
    self.bosch_wind_factor = learner.raw_windfactor
    lookup = gas_lookup_accel(gas_pedal_force, hill_brake, learner.gasfactor, min_gas)
    self.gas = float(np.interp(lookup, self.params.BOSCH_GAS_LOOKUP_BP, self.params.BOSCH_GAS_LOOKUP_V))
    self.gas = min(self.gas, max(60.0, self.bosch_last_gas + 60.0))
    stopping = actuators.longControlState == LongCtrlState.stopping
    self.bosch_braking = self._update_braking(gas_pedal_force, stopping, CC.longActive)
    self.bosch_last_gas = self.gas
    return self.accel, self.gas, gas_pedal_force, self.bosch_braking

  def update_mvl_gas(self, CC, CS, accel, hill_brake, wind_brake_mps2, params):
    """MVL on (owner decision 2026-11-08): MVL keeps its planner and actuator path, only the Civic gas learner is star7's.

    Returns (gas_pedal_force, gas) for MVL's own ACC_CONTROL builder; MVL's learned gas factor, gas alpha and wind
    factor are not applied on top. params is MVL's table, unchanged. Only valid when civic_learner is not None."""
    actuators = CC.actuators
    learner = self.civic_learner
    min_gas = params.BOSCH_GAS_LOOKUP_BP[0]
    gas_pedal_force = accel + hill_brake + wind_brake_mps2 * learner.windfactor
    learner.update(accel, CS.out.aEgo, gas_pedal_force, wind_brake_mps2,
                   engaged=CC.longActive and actuators.longControlState == LongCtrlState.pid,
                   gas_pressed=CS.out.gasPressed, brake_pressed=CS.out.brakePressed, v_ego=CS.out.vEgo,
                   pitch=self.pitch, at_accel_max=gas_pedal_force >= params.BOSCH_ACCEL_MAX)
    self.bosch_gas_factor = learner.raw_gasfactor
    self.bosch_wind_factor = learner.raw_windfactor
    lookup = gas_lookup_accel(gas_pedal_force, hill_brake, learner.gasfactor, min_gas)
    gas = float(np.interp(lookup, params.BOSCH_GAS_LOOKUP_BP, params.BOSCH_GAS_LOOKUP_V))
    return gas_pedal_force, gas

  def _update_braking(self, gas_pedal_force, stopping, long_active):
    """Brake request; on Bosch-A harness cars also the minimum hold and the gas ramp after release (self.gas)."""
    if self.brake_edge is None:
      return update_honda_bosch_braking(self.bosch_braking, gas_pedal_force, stopping, long_active)
    braking = self.brake_edge.update(gas_pedal_force, stopping, long_active)
    self.gas = self.brake_edge.limit_gas(self.gas)
    return braking
