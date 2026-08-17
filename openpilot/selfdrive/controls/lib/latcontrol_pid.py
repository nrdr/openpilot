import math

import numpy as np

from openpilot.cereal import log
from opendbc.car.honda.values import CAR as HONDA
from openpilot.selfdrive.controls.lib.latcontrol import LatControl
from openpilot.common.pid import PIDController


_CIVIC_TAIL_X = (105.022, 111.968, 118.982, 126.058, 133.203, 140.419, 147.705, 155.055, 162.478, 169.966, 177.528,
                  185.157, 192.86, 200.64, 208.495, 216.42, 224.423, 232.498, 240.652, 248.879, 257.186, 265.575,
                  274.046, 282.592, 291.221, 299.928, 308.719, 317.588, 326.545, 335.589, 344.722, 353.935, 363.239, 1135.663)
_CIVIC_TAIL_Y = (90, 95.053, 100.06, 105.018, 109.93, 114.799, 119.623, 124.399, 129.132, 133.818, 138.461, 143.058,
                  147.614, 152.128, 156.602, 161.031, 165.42, 169.766, 174.073, 178.337, 182.563, 186.75, 190.899,
                  195.007, 199.078, 203.109, 207.103, 211.057, 214.975, 218.858, 222.706, 226.515, 230.29, 720)
_CIVIC_C120 = (
  (0, 3.161, 4.712, 6.252, 9.375, 12.501, 15.624, 18.752, 31.248, 39.042, 46.866, 52.893, 58.973, 65.014, 71.15,
   72.196, 73.261, 74.349, 75.463, 76.604, 77.778, 78.99, 80.247, 82.521, 85.047, 87.555, 94.123, 96.059,
   97.8, 99.767, 101.605, 103.351) + _CIVIC_TAIL_X,
  (0, 3.162, 4.769, 6.402, 9.524, 12.699, 15.747, 19.05, 31.744, 39.506, 47.236, 52.989, 58.723, 64.352, 70,
   70.931, 71.831, 72.701, 73.543, 74.36, 75.154, 75.931, 76.693, 77.977, 79.289, 80.512, 83.615, 84.576,
   85.485, 86.58, 87.685, 88.821) + _CIVIC_TAIL_Y,
)
_CIVIC_C020 = (
  (0, 4.128, 8.173, 12.142, 16.111, 20.158, 28.328, 32.296, 40.559, 45.697, 50.844, 56.007, 61.179, 66.567,
   71.98, 73.014, 74.068, 75.144, 76.247, 77.376, 78.539, 79.738, 80.983, 83.217, 85.698, 88.153, 94.526,
   96.394, 98.074, 99.964, 101.733, 103.414) + _CIVIC_TAIL_X,
  (0, 4.128, 8.193, 12.099, 16.119, 20.039, 28.126, 32.083, 40.164, 45.142, 50.106, 55.06, 60, 65.009, 70,
   70.925, 71.82, 72.689, 73.532, 74.353, 75.153, 75.937, 76.709, 78.007, 79.341, 80.586, 83.728, 84.69,
   85.596, 86.675, 87.757, 88.862) + _CIVIC_TAIL_Y,
)
_CURVES = {
  HONDA.HONDA_CLARITY: (
    (0, 2.016, 8, 11.902, 15.799, 19.8, 23.7, 31.7, 39.462, 44.588, 49.862, 55.122, 60.396, 65.769, 71.173,
     73.026, 74.958, 76.989, 79.152, 81.168, 83.403, 85.638, 91.532, 94.853, 96.638, 98.306, 99.89, 101.406,
     108.627, 115.904, 123.239, 130.631, 138.089, 145.605, 153.18, 160.814, 168.509, 176.263, 184.079,
     191.956, 199.902, 207.911, 215.983, 224.118, 232.325, 240.598, 248.935, 257.338, 265.814, 274.358,
     282.968, 291.646, 300.392, 309.206, 318.09, 327.043, 336.076, 345.179, 354.354, 363.601, 1047.17),
    (0, 2.029, 8.104, 12.002, 15.999, 20, 23.999, 31.999, 39.665, 44.681, 49.807, 54.887, 59.95, 64.983, 70,
     71.641, 73.212, 74.729, 76.217, 77.508, 78.857, 80.146, 83.473, 85.45, 86.585, 87.709, 88.843, 90,
     95.643, 101.24, 106.792, 112.298, 117.766, 123.189, 128.568, 133.903, 139.195, 144.445, 149.652,
     154.816, 159.944, 165.031, 170.076, 175.08, 180.049, 184.978, 189.867, 194.716, 199.531, 204.306,
     209.043, 213.741, 218.402, 223.024, 227.609, 232.157, 236.672, 241.151, 245.594, 250, 720),
  ),
  HONDA.HONDA_CIVIC: _CIVIC_C120,
  HONDA.HONDA_CRV_5G: (
    (0, 4.1, 8.2, 12.203, 14.247, 16.303, 20.403, 24.503, 28.506, 32.704, 40.904, 46.179, 51.464, 56.771,
     62.088, 67.408, 72.75, 74.599, 76.528, 78.557, 80.721, 82.702, 84.9, 92.755, 95.917, 97.601, 99.177,
     100.675, 102.109, 108.892, 115.729, 122.621, 129.569, 136.572, 143.632, 150.748, 157.921, 165.138,
     172.413, 179.746, 187.138, 194.59, 202.101, 209.672, 217.305, 225, 232.756, 240.575, 248.457,
     256.402, 264.411, 272.484, 280.622, 288.81, 297.062, 305.382, 313.768, 322.221, 330.743, 339.332,
     347.991, 1050.146),
    (0, 4.1, 8.197, 12.194, 14.159, 16.115, 20.167, 24.049, 28, 32.098, 40.122, 45.172, 50.203, 55.227,
     60.233, 65.126, 70, 71.619, 73.186, 74.718, 76.241, 77.555, 78.944, 83.674, 85.647, 86.753, 87.835,
     88.914, 90, 95.228, 100.416, 105.565, 110.674, 115.743, 120.774, 125.766, 130.72, 135.626, 140.495,
     145.326, 150.12, 154.878, 159.599, 164.284, 168.933, 173.547, 178.126, 182.669, 187.178, 191.652,
     196.092, 200.497, 204.868, 209.198, 213.494, 217.758, 221.989, 226.187, 230.353, 234.487, 238.589, 720),
  ),
  HONDA.HONDA_INSIGHT: (
    (0, 4, 6.08, 8.186, 12.093, 16.279, 20.372, 24.465, 28.465, 32.651, 41.023, 46.35, 51.688, 57.048,
     62.418, 67.848, 73.3, 74.895, 76.558, 78.308, 80.174, 83.766, 90.489, 93.189, 95.975, 98.48, 105.666,
     112.895, 120.168, 127.484, 134.859, 142.279, 149.744, 157.253, 164.807, 172.407, 180.053, 187.745,
     195.498, 203.299, 211.146, 219.04, 226.983, 234.973, 243.011, 251.098, 259.25, 267.45, 275.7, 284,
     292.35, 300.75, 309.2, 317.702, 326.272, 334.893, 343.566, 352.291, 962.671),
    (0, 4, 6.011, 8, 11.908, 15.955, 19.955, 23.955, 27.909, 31.91, 39.955, 45.028, 50.086, 55.14, 60.177,
     65.102, 70, 71.403, 72.82, 74.266, 75.767, 78.566, 83.674, 85.75, 87.95, 90, 95.965, 101.89,
     107.777, 113.626, 119.448, 125.232, 130.98, 136.689, 142.361, 147.996, 153.595, 159.157, 164.694,
     170.196, 175.661, 181.091, 186.486, 191.846, 197.17, 202.461, 207.728, 212.959, 218.157, 223.322,
     228.453, 233.55, 238.614, 243.646, 248.655, 253.63, 258.574, 263.485, 720),
  ),
  HONDA.HONDA_ACCORD: (
    (0, 4.638, 9.303, 14.006, 18.738, 23.507, 28.305, 33.142, 38.008, 42.903, 47.827, 52.791, 57.785,
     62.819, 67.884, 72.989, 78.124, 85.865, 93.684, 101.581, 109.557, 117.614, 125.752, 133.971,
     142.273, 150.676, 159.163, 167.736, 176.394, 185.14, 193.973, 202.896, 211.908, 221.031, 230.247,
     239.555, 248.956, 258.452, 268.044, 277.732, 287.517, 297.421, 307.424, 317.528, 327.733, 338.041,
     348.453, 358.969, 369.591, 1115.33),
    (0, 4.606, 9.176, 13.721, 18.231, 22.714, 27.163, 31.587, 35.977, 40.332, 44.654, 48.952, 53.217,
     57.457, 61.665, 65.849, 70, 76.151, 82.238, 88.261, 94.222, 100.12, 105.957, 111.733, 117.449,
     123.117, 128.725, 134.276, 139.767, 145.203, 150.58, 155.903, 161.17, 166.393, 171.563, 176.678,
     181.739, 186.748, 191.705, 196.61, 201.464, 206.277, 211.04, 215.752, 220.416, 225.031, 229.598,
     234.117, 238.589, 720),
  ),
  HONDA.HONDA_CIVIC_BOSCH_DIESEL: (
    (0, 2.324, 4.657, 6.999, 9.351, 11.707, 14.073, 16.448, 18.833, 21.227, 23.631, 26.045, 28.468, 33.334,
     38.239, 43.174, 48.148, 53.153, 58.197, 63.282, 68.408, 73.565, 78.763, 86.278, 93.869, 101.552) + _CIVIC_TAIL_X,
    (0, 2.315, 4.623, 6.922, 9.214, 11.493, 13.765, 16.029, 18.286, 20.534, 22.776, 25.01, 27.236, 31.657,
     36.048, 40.402, 44.725, 49.013, 53.27, 57.499, 61.7, 65.864, 70, 75.874, 81.683, 87.439) + _CIVIC_TAIL_Y,
  ),
}
_RATIOS = {
  HONDA.HONDA_CLARITY: (18.5, 12.72),
  HONDA.HONDA_CIVIC: (17.24, 10.93),
  HONDA.HONDA_CIVIC_BOSCH: (17.24, 10.93),
  HONDA.HONDA_CIVIC_BOSCH_DIESEL: (17.24, 10.93),
  HONDA.HONDA_ACCORD: (18.31, 11.82),
  HONDA.HONDA_CRV_5G: (17.94, 12.3),
  HONDA.HONDA_INSIGHT: (16.82, 12.58),
}


class _LatStiction:
  TRACK, CAPTURE, HOLD, REACQUIRE = range(4)

  def __init__(self, dt):
    self.dt = dt
    self.reset()

  def reset(self):
    self.state = self.TRACK
    self.hold_torque = self.relative_motion = self._dwell_s = self._drift = self._reacquire_from = 0.0
    self._state_s = 0.12

  def _enter(self, state, output):
    self.state, self._state_s, self._dwell_s, self._drift = state, 0.0, 0.0, 0.0
    if state == self.HOLD:
      self.hold_torque = float(np.clip(output, -1.0, 1.0))
    elif state == self.REACQUIRE:
      self._reacquire_from = output

  def _passthrough(self, live_torque):
    self._enter(self.TRACK, live_torque)
    return live_torque

  def _reacquire(self, live_torque):
    if self._reacquire_from * live_torque <= 0.0:
      return self._passthrough(live_torque)
    weight = float(np.clip(self._state_s / 0.08, 0.0, 1.0))
    output = self._reacquire_from + weight * (live_torque - self._reacquire_from)
    if weight >= 1.0:
      self._enter(self.TRACK, live_torque)
      output = live_torque
    return output

  def update(self, active, v_ego, error, desired_rate, wheel_rate, live_torque, steering_pressed, lane_changing, saturated):
    self._state_s += self.dt
    raw_motion = wheel_rate - desired_rate
    if not active or steering_pressed or lane_changing or saturated:
      self.relative_motion = raw_motion
      return self._passthrough(live_torque)

    self.relative_motion += float(np.clip(self.dt / 0.05, 0.0, 1.0)) * (raw_motion - self.relative_motion)
    e_hi = float(np.interp(v_ego, (8.0, 30.0), (0.9, 0.4)))
    e_lo = float(np.interp(v_ego, (8.0, 30.0), (0.35, 0.2)))
    closing = float(np.sign(error)) * self.relative_motion

    if self.state == self.TRACK:
      settled = abs(error) <= e_lo and abs(self.relative_motion) <= 3.0
      self._dwell_s = self._dwell_s + self.dt if settled else 0.0
      capture_error = e_lo + min(0.12 * max(closing, 0.0), 5.0)
      if self._state_s >= 0.12 and abs(desired_rate) < 100.0 and closing > 1.0 and abs(error) <= capture_error:
        self._enter(self.CAPTURE, live_torque)
      elif settled and self._dwell_s >= 0.15:
        self._enter(self.HOLD, live_torque)
        return self.hold_torque
      else:
        return live_torque

    if self.state == self.CAPTURE:
      output = live_torque
      if live_torque * self.relative_motion > 0.0:
        removal = min(abs(live_torque), 0.008 * abs(self.relative_motion), 0.25)
        output -= float(np.sign(live_torque)) * removal * float(np.clip(self._state_s / 0.08, 0.0, 1.0))
      settled = abs(error) <= e_lo and abs(self.relative_motion) <= 3.0
      self._dwell_s = self._dwell_s + self.dt if settled else 0.0
      moving_away = closing <= 0.0 and abs(error) >= e_hi
      if settled and self._dwell_s >= 0.15:
        self._enter(self.HOLD, output)
        return self.hold_torque
      if abs(desired_rate) >= 100.0:
        return self._passthrough(live_torque)
      if moving_away or self._state_s >= 0.75:
        self._enter(self.REACQUIRE, output)
        return self._reacquire(live_torque)
      return output

    if self.state == self.HOLD:
      if abs(desired_rate) >= 100.0 or (self.hold_torque * live_torque < 0.0 and abs(live_torque) >= 0.03):
        return self._passthrough(live_torque)
      self._drift += error * self.dt
      breakaway = abs(error) >= e_hi or abs(self.relative_motion) >= 6.0 or abs(self._drift) >= 0.35
      urgent = abs(error) >= 2.0 * e_hi or abs(self.relative_motion) >= 12.0
      if urgent or (breakaway and self._state_s >= 0.2):
        if urgent:
          return self._passthrough(live_torque)
        self._enter(self.REACQUIRE, self.hold_torque)
        return self._reacquire(live_torque)
      return self.hold_torque

    return self._reacquire(live_torque)


class LatControlPID(LatControl):
  def __init__(self, CP, CI, dt):
    super().__init__(CP, CI, dt)
    self.pid = PIDController((CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV),
                             (CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV),
                             pos_limit=self.steer_max, neg_limit=-self.steer_max)
    self.ff_factor = CP.lateralTuning.pid.kf
    self.get_steer_feedforward = CI.get_steer_feedforward_function()
    self.car_fingerprint = CP.carFingerprint
    self.tuned = self.car_fingerprint in _RATIOS
    self.eps_modified = any(fw.ecu == "eps" and b"," in fw.fwVersion for fw in CP.carFw)
    self.center_ratio, self.outer_ratio = _RATIOS.get(self.car_fingerprint, (CP.steerRatio, CP.steerRatio))
    if self.car_fingerprint == HONDA.HONDA_CIVIC_BOSCH:
      eps_fw = {fw.fwVersion.split(b"\x00", 1)[0].replace(b",", b"-") for fw in CP.carFw if fw.ecu == "eps"}
      self.angle_curve = _CIVIC_C020 if eps_fw & {b"39990-TBA-C020", b"39990-TGG-A120"} else _CIVIC_C120
    else:
      self.angle_curve = _CURVES.get(self.car_fingerprint)
    self.lane_changing = False
    self.stiction = _LatStiction(dt)
    self.previous_desired_angle = self.previous_output = 0.0
    self.previous_saturated = False
    self.center_fade = 1.0
    self.phase_direction = self.steering_pressed_duration = 0.0
    self.previous_steering_pressed = False

  def update(self, active, CS, VM, params, steer_limited_by_safety, desired_curvature, curvature_limited, lat_delay):
    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    pid_log.steeringRateDeg = float(CS.steeringRateDeg)

    base_angle = math.degrees(VM.get_steer_from_curvature(-desired_curvature, CS.vEgo, params.roll))
    if self.tuned:
      if self.lane_changing:
        angle_steers_des_no_offset = base_angle * self.outer_ratio / VM.sR
      else:
        linear_angle = base_angle * self.center_ratio / VM.sR
        angle_steers_des_no_offset = math.copysign(float(np.interp(abs(linear_angle), *self.angle_curve)), linear_angle)
    else:
      angle_steers_des_no_offset = base_angle
    angle_steers_des = angle_steers_des_no_offset + params.angleOffsetDeg
    error = angle_steers_des - CS.steeringAngleDeg

    pid_log.steeringAngleDesiredDeg = angle_steers_des
    pid_log.angleError = error
    if not active:
      output_torque = 0.0
      pid_log.active = False
      self.stiction.reset()
      self.previous_desired_angle = angle_steers_des_no_offset
      self.previous_output = 0.0
      self.previous_saturated = False
      self.center_fade = 1.0
      self.phase_direction = self.steering_pressed_duration = 0.0
      self.previous_steering_pressed = False
    else:
      angle_delta = angle_steers_des_no_offset - self.previous_desired_angle
      phase = angle_steers_des_no_offset * angle_delta
      if self.tuned and phase != 0.0 and (CS.vEgo > 0.22352 or self.phase_direction == 0.0):
        self.phase_direction = float(np.sign(phase))
      phase = abs(phase) * self.phase_direction

      steering_pressed = bool(CS.steeringPressed)
      if self.tuned and self.eps_modified:
        if not steering_pressed:
          self.steering_pressed_duration = 0.0
          self.previous_steering_pressed = False
        elif self.previous_steering_pressed or abs(self.previous_output) < 0.1 or CS.steeringTorque * self.previous_output < 0.0:
          self.steering_pressed_duration, self.previous_steering_pressed = 1.0, True
        else:
          self.steering_pressed_duration = min(1.0, self.steering_pressed_duration + self.dt)
          steering_pressed = self.steering_pressed_duration >= 0.28
          self.previous_steering_pressed = steering_pressed

      if self.tuned:
        kf = float(np.interp(CS.vEgo, (0.0, 11.176, 22.352), (6e-5, 3e-5, 3e-5))) if self.car_fingerprint == HONDA.HONDA_ACCORD else \
          float(np.interp(CS.vEgo, (0.0, 11.175, 11.176, 22.352), (2.4e-6, 1.8e-6, 3.6e-6, 6e-6)))
      else:
        kf = self.ff_factor
      ff = kf * self.get_steer_feedforward(angle_steers_des_no_offset, CS.vEgo)
      freeze_speed = 2.0 if self.tuned and self.eps_modified else 5.0
      freeze_integrator = (steer_limited_by_safety or steering_pressed or CS.vEgo < freeze_speed
                           or (self.tuned and self.stiction.state != self.stiction.TRACK)
                           or (self.tuned and phase < 0.0 and self.pid.i * error > 0.0))
      self.pid.update(error, feedforward=ff, speed=CS.vEgo, freeze_integrator=freeze_integrator)

      if self.tuned and self.eps_modified:
        if CS.leftBlinker or CS.rightBlinker:
          self.center_fade = 0.0
        else:
          self.center_fade += self.dt / (0.25 + self.dt) * (1.0 - self.center_fade)
        boost = 1.0 + self.center_fade * float(np.clip(4.0 - abs(angle_steers_des_no_offset), 0.0, 1.0)) * \
          float(np.clip((CS.vEgo - 22.352) / 2.2352, 0.0, 1.0))
        output_torque = float(np.clip(self.pid.p * boost + self.pid.i + self.pid.d + self.pid.f, -self.steer_max, self.steer_max))
      else:
        output_torque = float(self.pid.control)

      if self.tuned:
        stiction_limited = (curvature_limited or self.previous_saturated or abs(output_torque) >= self.steer_max - 1e-3
                            or CS.steerFaultTemporary or CS.steerFaultPermanent)
        output_torque = float(self.stiction.update(active, CS.vEgo, error, angle_delta / self.dt, float(CS.steeringRateDeg),
                                                   output_torque, steering_pressed, self.lane_changing, stiction_limited))

      pid_log.active = True
      pid_log.p = float(self.pid.p)
      pid_log.i = float(self.pid.i)
      pid_log.f = float(self.pid.f)
      pid_log.output = float(output_torque)
      pid_log.saturated = bool(self._check_saturation(self.steer_max - abs(output_torque) < 1e-3, CS,
                                                      steer_limited_by_safety, curvature_limited))
      self.previous_desired_angle = angle_steers_des_no_offset
      self.previous_output = output_torque
      self.previous_saturated = bool(pid_log.saturated)

    return output_torque, angle_steers_des, pid_log
