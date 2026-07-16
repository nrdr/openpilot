"""
CurvServo unit tests. The core claim under test: with a deliberately WRONG
scale constant (SR_ROUGH=15 flat), the servo still converges to EXACTLY the
desired curvature on plants whose true steer ratio is 13 or 19 - because the
constant only times transients, never sets the fixed point. Plus: bumpless
engage/override, slew caps, low-speed map fallback, blend continuity, sign
symmetry, noise jitter bound, divergence watchdog, saturation anti-windup.

Run:  PYTHONPATH=<repo parent> python3 selfdrive/controls/lib/tests/test_nrdr_curv_servo.py
"""
import math
import random
import unittest

from openpilot.selfdrive.controls.lib.nrdr_curv_servo import CurvServo

DT = 0.01
L = 2.75                 # Clarity wheelbase
RAD_TO_DEG = 180.0 / math.pi
TAU_INNER = 0.15         # s; inner angle loop response
TAU_VEH = 0.35           # s; yaw response to road-wheel angle
MAP_SR = 16.5            # the (wrong-ish) map used for fallback/watchdog reference


def g_of(sr, v, kus=0.0012):
  """deg of wheel per unit curvature for a plant with true ratio sr."""
  return sr * (L + kus * v * v) * RAD_TO_DEG


class Plant:
  """First-order inner loop + first-order yaw response, true SR != servo's 15."""
  def __init__(self, sr_true, v, sign=1.0):
    self.g_true = g_of(sr_true, v) * sign
    self.theta = 0.0     # achieved wheel angle, deg
    self.kappa = 0.0     # measured curvature

  def step(self, theta_cmd):
    self.theta += (theta_cmd - self.theta) * (DT / TAU_INNER)
    self.kappa += (self.theta / self.g_true - self.kappa) * (DT / TAU_VEH)
    return self.theta, self.kappa


def make_servo():
  s = CurvServo(DT, L)
  s.ensure_sign(1.0)  # transform probe sign for a positive message curvature
  return s


def run(servo, plant, v, kappa_des_fn, n, pressed_fn=None, pose_ok=True,
        saturated=False, noise_sigma=0.0, rng=None, theta_map_fn=None):
  outs, kappas, thetas = [], [], []
  for i in range(n):
    kd = kappa_des_fn(i)
    theta_map = theta_map_fn(i) if theta_map_fn else kd * g_of(MAP_SR, v)
    pressed = pressed_fn(i) if pressed_fn else False
    km = plant.kappa + (rng.gauss(0.0, noise_sigma) if noise_sigma else 0.0)
    out = servo.update(True, v, kd, km, theta_map, plant.theta, pressed, pose_ok, saturated)
    theta, kappa = plant.step(out)
    outs.append(out)
    kappas.append(kappa)
    thetas.append(theta)
  return outs, kappas, thetas


class TestCurvServo(unittest.TestCase):

  def _engage(self, servo, kd=0.0, theta_meas=0.0, v=25.0):
    # a few inactive frames: state parks on the measured angle, prev_kdes seeds
    for _ in range(5):
      servo.update(False, v, kd, 0.0, 0.0, theta_meas, False, True, False)

  def test_converges_exactly_with_wrong_plant_sr(self):
    for sr_true in (13.0, 19.0):
      servo, v = make_servo(), 25.0
      plant = Plant(sr_true, v)
      self._engage(servo)
      kd = 3e-3
      _, kappas, _ = run(servo, plant, v, lambda i: kd if i * DT > 1.0 else 0.0, 800)
      # kick alone is off by |1 - 15/sr_true| (~21% at sr 19); integrator must have eaten
      # most of that by 3s and ALL of it by 7s - exactness despite believing SR=15
      self.assertLess(abs(kappas[400] - kd) / kd, 0.12, f"sr_true={sr_true}")
      self.assertLess(abs(kappas[-1] - kd) / kd, 0.005, f"sr_true={sr_true}")
      self.assertLess(max(kappas) / kd, 1.25, f"sr_true={sr_true}: overshoot bounded")

  def test_bumpless_engage_and_global_slew(self):
    servo, v = make_servo(), 25.0
    plant = Plant(17.0, v)
    plant.theta = 12.0  # engage mid-corner, wheel already at 12 deg
    self._engage(servo, kd=2e-3, theta_meas=12.0)
    slew_step = 10.0 * DT + 1e-9  # SLEW_V at 30 m/s is 10 deg/s; at 25 it's higher - use per-frame check below
    outs, _, _ = run(servo, plant, v, lambda i: 2e-3, 600)
    self.assertLess(abs(outs[0] - 12.0), 0.5, "first engaged setpoint must start at the wheel")
    max_step = max(abs(b - a) for a, b in zip(outs, outs[1:]))
    from openpilot.selfdrive.controls.lib.nrdr_curv_servo import _interp
    self.assertLessEqual(max_step, _interp(v, CurvServo.SLEW_BP, CurvServo.SLEW_V) * DT + 1e-9)

  def test_override_resume_is_continuous(self):
    servo, v = make_servo(), 20.0
    plant = Plant(17.0, v)
    self._engage(servo)
    kd = 2.5e-3
    pressed_fn = lambda i: 300 <= i < 500  # driver holds the wheel for 2s mid-corner
    outs, _, _ = run(servo, plant, v, lambda i: kd, 1000, pressed_fn=pressed_fn)
    from openpilot.selfdrive.controls.lib.nrdr_curv_servo import _interp
    lim = 2.0 * _interp(v, CurvServo.SLEW_BP, CurvServo.SLEW_V) * DT + 1e-9
    max_step = max(abs(b - a) for a, b in zip(outs, outs[1:]))
    self.assertLessEqual(max_step, lim, "no snap through override entry/exit")

  def test_lowspeed_output_is_exactly_the_map(self):
    servo = make_servo()
    v = 3.0
    plant = Plant(17.0, v)
    self._engage(servo, v=v)
    theta_map_fn = lambda i: 30.0 + 5.0 * math.sin(i * 0.01)
    outs, _, _ = run(servo, plant, v, lambda i: 4e-3, 200, theta_map_fn=theta_map_fn)
    for i, o in enumerate(outs):
      self.assertAlmostEqual(o, theta_map_fn(i), places=9)

  def test_blend_continuity_across_speed_ramp(self):
    servo = make_servo()
    plant = Plant(17.0, 7.0)
    self._engage(servo, v=3.0)
    kd = 3e-3
    outs = []
    for i in range(1400):
      v = 3.0 + i * DT  # 3 -> 17 m/s
      theta_map = kd * g_of(MAP_SR, v)
      out = servo.update(True, v, kd, plant.kappa, theta_map, plant.theta, False, True, False)
      plant.step(out)
      outs.append(out)
    max_step = max(abs(b - a) for a, b in zip(outs, outs[1:]))
    self.assertLess(max_step, 0.8 * DT * 60.0, "crossing the blend zone must not step the setpoint")

  def test_sign_symmetry(self):
    res = []
    for s in (1.0, -1.0):
      servo, v = make_servo(), 25.0
      plant = Plant(17.0, v)
      self._engage(servo)
      outs, _, _ = run(servo, plant, v, lambda i: s * 3e-3, 500)
      res.append(outs)
    for a, b in zip(res[0], res[1]):
      self.assertAlmostEqual(a, -b, places=9)

  def test_straightline_jitter_bound(self):
    servo, v = make_servo(), 28.0
    plant = Plant(17.0, v)
    self._engage(servo)
    rng = random.Random(0)
    outs, _, _ = run(servo, plant, v, lambda i: 0.0, 3000, noise_sigma=2.5e-4, rng=rng)
    tail = outs[500:]
    mean = sum(tail) / len(tail)
    sigma = math.sqrt(sum((o - mean) ** 2 for o in tail) / len(tail))
    self.assertLess(sigma, 0.10, f"straight-line setpoint jitter {sigma:.3f} deg")

  def test_watchdog_disarms_on_sign_flip_and_latches(self):
    servo, v = make_servo(), 25.0
    plant = Plant(17.0, v, sign=-1.0)  # broken sensor: yaw reads backwards
    self._engage(servo)
    outs, _, _ = run(servo, plant, v, lambda i: 2e-3, 2000)
    self.assertTrue(servo.disarmed, "sign-flipped feedback must trip the divergence watchdog")
    theta_map = 2e-3 * g_of(MAP_SR, v)
    self.assertLess(abs(outs[-1] - theta_map), 1.0, "after disarm the output walks back to the map")
    # latched: healthy frames do not re-arm
    servo.update(True, v, 2e-3, 2e-3, theta_map, theta_map, False, True, False)
    self.assertTrue(servo.disarmed)

  def test_saturation_freezes_integration(self):
    servo, v = make_servo(), 25.0
    self._engage(servo, kd=3e-3)
    theta0 = servo.theta_deg
    for _ in range(300):  # constant kappa_des (no kick), huge error, inner loop saturated
      servo.update(True, v, 3e-3, 0.0, 3e-3 * g_of(MAP_SR, v), theta0, False, True, True)
    self.assertAlmostEqual(servo.theta_deg, theta0, places=9,
                           msg="saturated inner loop: the servo must not wind up")


if __name__ == "__main__":
  unittest.main()
