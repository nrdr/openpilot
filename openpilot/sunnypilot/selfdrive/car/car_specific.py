"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.cereal import log, custom
from opendbc.car import structs

from opendbc.car.chrysler.values import RAM_DT
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.selfdrived.events import ET, Events
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

EventName = log.OnroadEvent.EventName
EventNameSP = custom.OnroadEventSP.EventName
GearShifter = structs.CarState.GearShifter
GAS_INTERCEPTOR_STARTUP_GRACE_FRAMES = int(10. / DT_CTRL)


class CarSpecificEventsSP:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP):
    self.CP = CP
    self.CP_SP = CP_SP

    self.low_speed_alert = False
    self.gas_interceptor_healthy = False
    self.gas_interceptor_bootstrap_frames = 0

  def update(self, CS: structs.CarState, CS_SP: custom.CarStateSP, events: Events):
    events_sp = EventsSP()

    if self.CP_SP.enableGasInterceptor:
      interceptor_state = CS_SP.gasInterceptorState
      if self.gas_interceptor_healthy:
        if interceptor_state != 0:
          events.add(EventName.gasInterceptorFault)
      elif interceptor_state == 0:
        self.gas_interceptor_healthy = CS.canValid
      elif interceptor_state in (4, 5):
        self.gas_interceptor_bootstrap_frames += 1
        if events.contains(ET.ENABLE) or self.gas_interceptor_bootstrap_frames > GAS_INTERCEPTOR_STARTUP_GRACE_FRAMES:
          events.add(EventName.gasInterceptorFault)
      else:
        events.add(EventName.gasInterceptorFault)

    if self.CP.brand == 'chrysler':
      if self.CP.carFingerprint in RAM_DT:
        # remove belowSteerSpeed event from CarSpecificEvents as RAM_DT uses a different logic
        if events.has(EventName.belowSteerSpeed):
          events.remove(EventName.belowSteerSpeed)

        # TODO-SP: use if/elif to have the gear shifter condition takes precedence over the speed condition
        # TODO-SP: add 1 m/s hysteresis
        if CS.vEgo >= self.CP.minEnableSpeed:
          self.low_speed_alert = False
        if self.CP.minEnableSpeed >= 14.5 and CS.gearShifter != GearShifter.drive:
          self.low_speed_alert = True
      if self.low_speed_alert:
        events.add(EventName.belowSteerSpeed)

    elif self.CP.brand == 'toyota':
      if self.CP.openpilotLongitudinalControl:
        if CS.cruiseState.standstill and not CS.brakePressed and self.CP_SP.enableGasInterceptor:
          if events.has(EventName.resumeRequired):
            events.remove(EventName.resumeRequired)

    return events_sp
