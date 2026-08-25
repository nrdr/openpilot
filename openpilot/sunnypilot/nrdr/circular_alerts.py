class StandstillLatch:
  def __init__(self):
    self.active = False
    self.true_frames = 0
    self.false_frames = 0

  def update(self, standstill: bool, started: bool, fps: float) -> bool:
    if not started:
      self.active = False
      self.true_frames = 0
      self.false_frames = 0
      return False

    if standstill:
      self.true_frames += 1
      self.false_frames = 0
      if self.true_frames >= max(1, int(0.1 * fps)):
        self.active = True
    else:
      self.false_frames += 1
      self.true_frames = 0
      if self.false_frames >= int(fps):
        self.active = False
    return self.active
