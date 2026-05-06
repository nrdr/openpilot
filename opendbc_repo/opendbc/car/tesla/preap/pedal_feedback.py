from opendbc.car.tesla.preap.nap_conf import PEDAL_DI_PRESSED, nap_conf

PEDAL_TIMEOUT_MS = 500


class PedalFeedback:
  def __init__(self):
    self.interceptor_value = 0.0
    self.interceptor_value2 = 0.0
    self.interceptor_state = 0
    self.idx = 0
    self.prev_idx = 0
    self.last_seen_ms = 0
    self.available = False
    self.timeout = True
    self.torque_level = 0.0

  def update(self, gas_sensor_msg, curr_time_ms: int) -> bool:
    if not gas_sensor_msg:
      return False

    self.prev_idx = self.idx
    self.interceptor_value = float(nap_conf.pedal_to_di(float(gas_sensor_msg.get("INTERCEPTOR_GAS", 0.0))))
    self.interceptor_value2 = float(nap_conf.pedal_to_di(float(gas_sensor_msg.get("INTERCEPTOR_GAS2", 0.0))))
    self.interceptor_state = int(gas_sensor_msg.get("STATE", 0))
    self.idx = int(gas_sensor_msg.get("IDX", 0))

    if self.idx != self.prev_idx:
      self.last_seen_ms = curr_time_ms

    self.timeout = (curr_time_ms - self.last_seen_ms) > PEDAL_TIMEOUT_MS
    self.available = (not self.timeout) and (self.interceptor_state == 0)
    return True

  def update_torque(self, di_torque1_msg) -> None:
    self.torque_level = di_torque1_msg.get("DI_torqueMotor", 0.0)

  @property
  def gas_pressed(self) -> bool:
    return self.interceptor_value > PEDAL_DI_PRESSED

