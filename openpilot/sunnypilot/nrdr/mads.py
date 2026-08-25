class AutoLkas:
  def __init__(self):
    self.armed = True
    self.enabled_prev = False

  def request(self, CS, main_enabled: bool, events, event_name) -> None:
    main_available = bool(CS.cruiseState.available)
    if not main_available:
      self.armed = True
    if main_enabled and self.armed and main_available:
      events.add(event_name.lkasEnable)

  def update(self, enabled: bool) -> None:
    if enabled and not self.enabled_prev:
      self.armed = False
    self.enabled_prev = enabled
