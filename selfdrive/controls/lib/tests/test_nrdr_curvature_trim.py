import math
import random

from openpilot.selfdrive.controls.lib.nrdr_curvature_trim import CurvatureTrim

DT = 0.01
ok = 0

def step(tr, err, **kw):
  d = dict(active=True, v_ego=27.0, dtheta_err_deg=err, steering_pressed=False,
           steering_rate_deg=0.0, lane_changing=False, pose_ok=True, saturated=False,
           near_center=False)
  d.update(kw)
  return tr.update(**d)

# 1. closed-loop convergence: map error 2.0deg, perfect inner loop -> err = eps - trim
tr = CurvatureTrim(DT)
eps = 2.0
for i in range(int(3 * 2.0 / DT)):     # 3 time constants at highway T=2s
  step(tr, eps - tr.trim_deg)
assert abs(tr.trim_deg - eps) < 0.12 * eps, f"convergence: {tr.trim_deg}"
ok += 1

# 2. jitter under measured noise (0.15deg white @100Hz), 60s, no bias
tr = CurvatureTrim(DT); random.seed(0)
vals = []
for i in range(6000):
  step(tr, random.gauss(0.0, 0.15))
  vals.append(tr.trim_deg)
m = sum(vals) / len(vals)
sd = math.sqrt(sum((x - m) ** 2 for x in vals) / len(vals))
assert sd < 0.05 and max(abs(x) for x in vals) < 0.25, f"jitter sd={sd:.4f} peak={max(abs(x) for x in vals):.3f}"
ok += 1

# 3. clamp respected under huge error
tr = CurvatureTrim(DT)
for i in range(500):
  step(tr, 50.0)
assert tr.trim_deg <= tr.CLAMP_DEG + 1e-9, tr.trim_deg
ok += 1

# 4. watchdog: sustained peg (non-converging error) disarms within ~10s and zeroes
for i in range(int(12.0 / DT)):
  step(tr, 50.0)
assert tr.disarmed and tr.trim_deg == 0.0, (tr.disarmed, tr.trim_deg)
# stays zero even with normal error until reset
assert step(tr, 1.0) == 0.0
tr.reset()
assert not tr.disarmed
ok += 1

# 5. freeze conditions hold value (leak only): build trim, then press wheel
tr = CurvatureTrim(DT)
for i in range(400):
  step(tr, 2.0 - tr.trim_deg)
held = tr.trim_deg
step(tr, 5.0, steering_pressed=True)
assert abs(tr.trim_deg - held) < held * 0.01 and tr.trim_deg < held, "freeze should leak, not integrate"
for gate in [dict(lane_changing=True), dict(pose_ok=False), dict(saturated=True),
             dict(v_ego=3.0), dict(steering_rate_deg=40.0), dict(active=False)]:
  before = tr.trim_deg
  step(tr, 5.0, **gate)
  assert tr.trim_deg <= before, f"gate {gate} integrated!"
ok += 1

# 6. leak decays a stale trim toward zero when gated off for a long time
tr = CurvatureTrim(DT)
for i in range(400):
  step(tr, 2.0 - tr.trim_deg)
for i in range(int(60.0 / DT)):
  step(tr, 0.0, active=False)
assert abs(tr.trim_deg) < 0.35, f"leak too slow: {tr.trim_deg}"
ok += 1

# 7b. near-center gate: no integration on straights (leak only)
tr = CurvatureTrim(DT)
for i in range(400):
  step(tr, 2.0 - tr.trim_deg)
before = tr.trim_deg
step(tr, 5.0, near_center=True)
assert tr.trim_deg <= before, "near_center integrated!"
ok += 1

# 7. sign symmetry
tr = CurvatureTrim(DT)
for i in range(400):
  step(tr, -2.0 - tr.trim_deg)
assert tr.trim_deg < -1.5
ok += 1

print(f"ALL {ok} TESTS PASS")
