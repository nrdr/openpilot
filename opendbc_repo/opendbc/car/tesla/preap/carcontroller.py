import numpy as np

from opendbc.can import CANPacker
from opendbc.car import Bus
from opendbc.car.carlog import carlog
from opendbc.car.tesla.pedal.controller import get_zero_torque
from opendbc.car.tesla.preap.interface import get_preap_accel_limits
from opendbc.car.tesla.preap.nap_conf import PEDAL_DI_MIN, PEDAL_DI_ZERO, nap_conf
from opendbc.car.tesla.preap.teslacan import TeslaCANPreAP
from opendbc.car.tesla.preap.virtual_das import VirtualDAS
from opendbc.car.tesla.values import CANBUS, CruiseButtons

ENGAGE_GRACE_FRAMES = 50


def init_preap_can(dbc_names):
  tesla_can = TeslaCANPreAP(CANPacker(dbc_names[Bus.party]))
  tesla_can.pedal_can_bus = nap_conf.pedal_can_bus
  return tesla_can


class PreAPLongController:
  def __init__(self):
    self.prev_pedal_di = 0.0
    self.prev_requested_long = False
    self.preap_long_engage_frame = -1_000_000
    self.engage_a_max = 0.0
    self.vdas = VirtualDAS(dt=0.02)

  def update(self, CC, CS, frame: int, tesla_can, can_bus_party: int):
    can_sends = []
    actuators = CC.actuators
    requested_long = CS.cruiseEnabled and CS.enableLongControl
    long_active = requested_long and CC.longActive
    use_pedal = nap_conf.use_pedal and self._pedal_ready()

    if (not self.prev_requested_long) and requested_long:
      self.preap_long_engage_frame = frame
      zero_torque_di = get_zero_torque().get(CS.out.vEgo)
      self.prev_pedal_di = max(CS.pedal_interceptor_value, zero_torque_di)
      self.vdas.reset(a_init=0.0, pedal_di_init=self.prev_pedal_di)
      _, self.engage_a_max = get_preap_accel_limits(CS.out.vEgo)

    if use_pedal:
      pedal_button_press = CS.cruise_buttons != CS.prev_cruise_buttons and CS.cruise_buttons != CruiseButtons.IDLE
      if ((not self.prev_requested_long) and requested_long) or (self.prev_requested_long and not requested_long) or pedal_button_press:
        CS.preap_cc_cancel_needed = True

    self.prev_requested_long = requested_long

    if frame % 2 == 0:
      if use_pedal:
        get_zero_torque().update(CS.pedal.torque_level, self.prev_pedal_di, CS.out.vEgo)

      if requested_long and use_pedal:
        try:
          if CS.out.gasPressed:
            self.prev_pedal_di = max(CS.pedal_interceptor_value, PEDAL_DI_ZERO)
            can_sends.append(tesla_can.create_pedal_command(0, enable=0))
          elif long_active:
            accel_request = float(actuators.accel)
            engage_elapsed_frames = frame - self.preap_long_engage_frame
            in_engage_grace = engage_elapsed_frames < ENGAGE_GRACE_FRAMES
            if in_engage_grace:
              accel_request = max(0.0, min(accel_request, (engage_elapsed_frames / ENGAGE_GRACE_FRAMES) * self.engage_a_max))

            self.prev_pedal_di = self.vdas.update(
              accel_request, CS.out.vEgo, self.prev_pedal_di, a_ego=CS.out.aEgo,
              freeze_integrator=in_engage_grace, orientation_ned=list(CC.orientationNED),
            )
            can_sends.append(tesla_can.create_pedal_command(nap_conf.di_to_pedal(self.prev_pedal_di), enable=1))
          else:
            zero_torque_di = get_zero_torque().get(CS.out.vEgo)
            self.prev_pedal_di = zero_torque_di
            can_sends.append(tesla_can.create_pedal_command(nap_conf.di_to_pedal(zero_torque_di), enable=1))
        except Exception:
          carlog.exception("Pre-AP pedal command failed; sending disabled")
          can_sends.append(tesla_can.create_pedal_command(nap_conf.di_to_pedal(PEDAL_DI_ZERO), enable=0))
          self.prev_pedal_di = 0.0
      else:
        if nap_conf.use_pedal:
          can_sends.append(tesla_can.create_pedal_command(nap_conf.di_to_pedal(PEDAL_DI_ZERO), enable=0))
        self.prev_pedal_di = 0.0

    return can_sends

  @staticmethod
  def _pedal_ready() -> bool:
    return nap_conf.pedal_calibrated and abs(nap_conf.pedal_factor) > 1e-6

