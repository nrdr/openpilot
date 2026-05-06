from opendbc.car.tesla.values import CruiseButtons

_PHASE_IDLE = 0
_PHASE_ENGAGING = 1
CANCEL_DELAY_FRAMES = 10
CC_ENGAGE_TIMEOUT_FRAMES = 50


class StockCCSpoofer:
  def __init__(self):
    self.cc_engage_phase = _PHASE_IDLE
    self.cc_engage_start_frame = 0
    self.cancel_pending = False
    self.cancel_frame = -1_000_000

  def update(self, CS, frame: int, tesla_can, can_bus_party: int):
    can_sends = []

    if getattr(CS, "preap_cc_cancel_needed", False):
      self.cancel_pending = True
      self.cancel_frame = frame
      self.cc_engage_phase = _PHASE_IDLE
      CS.preap_cc_cancel_needed = False

    if getattr(CS, "preap_cc_engage_needed", False) and self.cc_engage_phase == _PHASE_IDLE:
      self.cc_engage_phase = _PHASE_ENGAGING
      self.cc_engage_start_frame = frame
      CS.preap_cc_engage_needed = False

    if self.cancel_pending and (frame - self.cancel_frame) >= CANCEL_DELAY_FRAMES and frame % 10 == 0:
      sent = self._send(CS, tesla_can, can_bus_party, CruiseButtons.CANCEL)
      if sent is not None:
        can_sends.append(sent)
        self.cancel_pending = False
    elif self.cc_engage_phase == _PHASE_ENGAGING and frame % 10 == 0:
      if (frame - self.cc_engage_start_frame) >= CC_ENGAGE_TIMEOUT_FRAMES or getattr(CS, "di_cruise_state", "OFF") == "ENABLED":
        self.cc_engage_phase = _PHASE_IDLE
      else:
        sent = self._send(CS, tesla_can, can_bus_party, CruiseButtons.SET_ACCEL)
        if sent is not None:
          can_sends.append(sent)

    return can_sends

  @staticmethod
  def _send(CS, tesla_can, can_bus_party: int, button: int):
    msg_stw = getattr(CS, "msg_stw_actn_req", None)
    if msg_stw is None:
      return None
    counter = (int(msg_stw.get("MC_STW_ACTN_RQ", 0)) + 1) % 16
    return tesla_can.create_action_request(button, can_bus_party, counter, msg_stw)

