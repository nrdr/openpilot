"""
nrdr pure-feedback lateral: the curvature servo (NrdrCurvServo).

latcontrol_pid's setpoint is normally born from the steer-ratio map
(get_steer_from_curvature) and only audited by the slow bounded trim. This
mode inverts the hierarchy: the angle setpoint is a STATE, slewed by an
integrator on TRUE curvature error (desired vs IMU yaw/v) plus a rate-kick
on changes in desired curvature. Steady state is exactly kappa_des ==
kappa_meas with zero steer-ratio knowledge: the only constant is a
deliberately rough scale (SR_ROUGH, flat 15) that times transients and can
never bias where the servo settles. Bank/crown and angle-offset error are
absorbed the same way - feedback finds whatever angle the road requires.

The SR map is demoted to two jobs: parking-speed duty (kappa = yaw/v is too
noisy below ~10 mph, so the map steers there, crossfaded out by BLEND_TOP)
and safety reference (sustained large servo-vs-map disagreement trips the
divergence watchdog and drops the mode back to the map, latched).

Physics costs, stated up front: turn-in timing is only as right as SR_ROUGH
(integrator cleans the residual within ~T), and bank entry lags ~T before
feedback catches it. Ships dormant behind NrdrCurvServo (default OFF);
overrides NrdrCurvatureTrim when both are set.
"""
import math

RAD_TO_DEG = 180.0 / math.pi


def _interp(x, xp, fp):
  if x <= xp[0]:
    return fp[0]
  if x >= xp[-1]:
    return fp[-1]
  for i in range(len(xp) - 1):
    if x < xp[i + 1]:
      f = (x - xp[i]) / (xp[i + 1] - xp[i])
      return fp[i] + f * (fp[i + 1] - fp[i])
  return fp[-1]


def _clip(x, lo, hi):
  return lo if x < lo else (hi if x > hi else x)


class CurvServo:
  MIN_SPEED = 4.5              # m/s; below: the map owns the setpoint (kappa noise x2.7 under 10 m/s)
  BLEND_TOP = 7.0              # m/s; map->servo crossfade complete
  SR_ROUGH = 15.0              # flat scale guess: transient timing only, never the fixed point
  KUS_ROUGH = 0.0010           # rad/(m/s^2); understeer term of the rough scale (Clarity fit)
  T_BP = (8.0, 25.0)           # m/s -> loop time-constant schedule
  T_V = (2.5, 1.2)             # s; jitter ~0.05 deg 1-sigma at measured kappa noise
  SLEW_BP = (4.5, 15.0, 30.0)  # m/s
  SLEW_V = (60.0, 25.0, 10.0)  # deg/s cap on setpoint motion (kick + integrator combined)
  CLAMP_DEG = 150.0            # absolute sanity clamp on the servo state
  DIVERGE_DEG = 25.0           # sustained |servo - map| beyond this trips the watchdog
  DISARM_S = 5.0

  def __init__(self, dt: float, wheelbase: float):
    self.dt = dt
    self.L = wheelbase
    self.sign_k = 0.0        # sign of d(theta)/d(kappa_msg); set once via ensure_sign()
    self.theta_deg = 0.0     # the servo state: full angle setpoint, no-offset domain
    self._prev_kdes = 0.0
    self._diverge_s = 0.0
    self.disarmed = False    # latched until reset(); caller logs once on rising edge

  def reset(self) -> None:
    self.theta_deg = 0.0
    self._prev_kdes = 0.0
    self._diverge_s = 0.0
    self.disarmed = False

  def ensure_sign(self, probe_deg: float) -> None:
    """probe_deg: the setpoint transform of a small positive message-domain curvature
    (same construction the road-proven trim relied on). Fixes the gain sign once."""
    if self.sign_k == 0.0 and probe_deg != 0.0:
      self.sign_k = 1.0 if probe_deg > 0.0 else -1.0

  def _gain(self, v_ego: float) -> float:
    # deg of wheel per unit of message curvature, sign folded in
    return self.SR_ROUGH * (self.L + self.KUS_ROUGH * v_ego * v_ego) * RAD_TO_DEG * self.sign_k

  def _toward(self, target: float, step: float) -> None:
    self.theta_deg += _clip(target - self.theta_deg, -step, step)

  def update(self, active: bool, v_ego: float, kappa_des: float, kappa_meas: float,
             theta_map_deg: float, theta_meas_deg: float,
             steering_pressed: bool, pose_ok: bool, saturated: bool) -> float:
    """Returns the full angle setpoint (no-offset degrees). theta_map_deg is the
    SR-map setpoint, used only below MIN_SPEED, as the disarm fallback, and as
    the watchdog reference. All curvatures in message convention."""
    slew = _interp(v_ego, self.SLEW_BP, self.SLEW_V) * self.dt

    if not active or self.sign_k == 0.0:
      # bumpless engage: park the state on the wheel's true position
      self.theta_deg = theta_meas_deg
      self._prev_kdes = kappa_des
      self._diverge_s = 0.0
      return theta_map_deg

    if self.disarmed:
      self._toward(theta_map_deg, 2.0 * slew)
      self._prev_kdes = kappa_des
      return theta_map_deg

    if steering_pressed:
      # follow the driver so control resumes from THEIR angle, not a stale one
      self._toward(theta_meas_deg, 2.0 * slew)
      self._prev_kdes = kappa_des
      w = _interp(v_ego, (self.MIN_SPEED, self.BLEND_TOP), (0.0, 1.0))
      return (1.0 - w) * theta_map_deg + w * self.theta_deg

    if not pose_ok or v_ego <= self.MIN_SPEED:
      # parachute / parking duty: walk the state onto the map so handback is seamless
      self._toward(theta_map_deg, 2.0 * slew)
      self._prev_kdes = kappa_des
      return theta_map_deg

    g = self._gain(v_ego)
    kick = g * (kappa_des - self._prev_kdes)
    self._prev_kdes = kappa_des
    integ = 0.0
    if not saturated:  # anti-windup: never integrate against a torque-limited inner loop
      T = _interp(v_ego, self.T_BP, self.T_V)
      integ = g * (kappa_des - kappa_meas) * (self.dt / T)
    self.theta_deg = _clip(self.theta_deg + _clip(kick + integ, -slew, slew),
                           -self.CLAMP_DEG, self.CLAMP_DEG)

    # divergence watchdog: the map is wrong in percent, never in tens of degrees.
    # Sustained big disagreement means a broken sensor or sign - fall back, latched.
    if abs(self.theta_deg - theta_map_deg) > self.DIVERGE_DEG:
      self._diverge_s += self.dt
      if self._diverge_s >= self.DISARM_S:
        self.disarmed = True
    else:
      self._diverge_s = 0.0

    w = _interp(v_ego, (self.MIN_SPEED, self.BLEND_TOP), (0.0, 1.0))
    return (1.0 - w) * theta_map_deg + w * self.theta_deg
