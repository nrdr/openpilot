"""
nrdr cascade outer loop: slow setpoint trim driven by TRUE curvature error.

The inner loop (latcontrol_pid) is an angle servo on the high-resolution wheel
sensor. This outer loop audits the geometry: it integrates the difference
between desired curvature and MEASURED curvature (IMU yaw_rate / v - no steer
ratio anywhere in it) into a bounded setpoint correction, so any error in the
rack model (curve, scalar, spec sheet, tire wear, column twist) becomes a
transient the trim eats in a few seconds instead of a bias nothing downstream
can detect. Angle error is structurally blind to rack-map error; this is not.

Design + data-derived constants: see nrdr_cascade_design.md. Ships dormant
behind NrdrCurvatureTrim (default OFF); road use gated on offline log replay.
"""


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


class CurvatureTrim:
  MIN_SPEED = 4.5           # m/s; kappa = yaw/v degenerates below (noise x2.7 under 10 m/s)
  RATE_FREEZE_DEGS = 25.0   # don't learn geometry mid-slew
  CLAMP_DEG = 2.5           # worst observed map error ~2 deg equivalent
  T_BP = (8.0, 25.0)        # m/s
  T_V = (4.0, 2.0)          # s; jitter 0.12-0.15 deg 1-sigma at these (measured kappa noise)
  T_LEAK = 30.0             # s; decay when the error signal is gated off
  DISARM_PEG_S = 10.0       # pegged-at-clamp watchdog -> self-zero (sign-error protection)

  def __init__(self, dt: float):
    self.dt = dt
    self.trim_deg = 0.0
    self._pegged_s = 0.0
    self.disarmed = False   # latched until reset(); caller may log once on rising edge

  def reset(self) -> None:
    self.trim_deg = 0.0
    self._pegged_s = 0.0
    self.disarmed = False

  def update(self, active: bool, v_ego: float, dtheta_err_deg: float,
             steering_pressed: bool, steering_rate_deg: float,
             lane_changing: bool, pose_ok: bool, saturated: bool,
             near_center: bool = False) -> float:
    """dtheta_err_deg: (setpoint-domain) angle equivalent of the curvature error,
    computed by the caller through the SAME curvature->angle map used for the
    setpoint, so the correction sign is right by construction for any convention."""
    if self.disarmed:
      self.trim_deg = 0.0
      return 0.0

    # near_center: map error is ~zero at zero angle by definition (any steer ratio is
    # correct there), so integrating near center couples pure IMU noise into the setpoint
    # (owner-felt as 'loose on straights'). Freeze + leak instead.
    integrate = (active and pose_ok and not steering_pressed and not lane_changing
                 and not saturated and not near_center and v_ego > self.MIN_SPEED
                 and abs(steering_rate_deg) < self.RATE_FREEZE_DEGS)

    if integrate:
      T = _interp(v_ego, self.T_BP, self.T_V)
      self.trim_deg += dtheta_err_deg * (self.dt / T)
      if self.trim_deg > self.CLAMP_DEG:
        self.trim_deg = self.CLAMP_DEG
      elif self.trim_deg < -self.CLAMP_DEG:
        self.trim_deg = -self.CLAMP_DEG
    else:
      # freeze value, bleed slowly so a stale correction can't outlive its cause
      self.trim_deg -= self.trim_deg * (self.dt / self.T_LEAK)

    # watchdog: sustained saturation at the clamp means the error signal is not
    # converging (wrong sign / broken sensor) - zero and latch off until reset()
    if abs(self.trim_deg) >= self.CLAMP_DEG - 1e-9 and integrate:
      self._pegged_s += self.dt
      if self._pegged_s >= self.DISARM_PEG_S:
        self.trim_deg = 0.0
        self.disarmed = True
    else:
      self._pegged_s = 0.0

    return self.trim_deg
