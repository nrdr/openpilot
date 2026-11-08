"""Persistence for the Honda Bosch gas/wind learner (ported from the Biscuit-Labs SOURCE).

The actuator code (opendbc ``CarController.bosch_longitudinal``) learns two scalar factors. The
host owns the filesystem, so it assigns ``CarController.bosch_learning_params`` to an object with
``persist(frame)``. ``attach`` does that in one call from card.py.

Single source of truth: the learned factors live ONLY in ``LEARNER_META_PATH`` (this class is its one writer). They
are deliberately NOT stored in the Params keys HondaGasFactorParams / HondaWindFactorParams. Those keys already belong
to two other learners, each with its own integrity record: nrdr's HondaParamsProvider (sha256 digest in
/data/honda_learner_meta.json, nrdr/car/opendbc.py) and MVL (nrdr/car/mvl_state.py). A third writer on the same keys
would invalidate the first one's digest and, with MVL on, be overwritten by the second.
"""
import json
import math
import os

# Records which learner version, and which car, the saved factors belong to, plus the factors themselves. A separate
# file from nrdr/car/mvl_state.py's /data/honda_learner_meta.json so neither record can vouch for the other.
LEARNER_META_PATH = "/data/star7_honda_gas_learner.json"


def _read_state(path):
  try:
    with open(path) as f:
      state = json.load(f)
    return state if isinstance(state, dict) else {}
  except (OSError, ValueError):
    return {}


def _write_state(path, state):
  try:
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
      json.dump(state, f)
      f.flush()
      os.fsync(f.fileno())
    os.replace(tmp, path)
    return True
  except OSError:
    return False


def _factor(value):
  if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
    return 1.0
  return float(value)


class BoschLearningParams:
  def __init__(self, owner, meta_path=LEARNER_META_PATH):
    self.owner = owner
    self.meta_path = meta_path
    self.fingerprint = str(getattr(getattr(owner, "CP", None), "carFingerprint", ""))
    state = _read_state(meta_path)
    mine = state.get("car_fingerprint") == self.fingerprint
    factors = [_factor(state.get("gas_factor")), _factor(state.get("wind_factor"))] if mine else [1.0, 1.0]
    self.version = getattr(owner, "learner_version", None)
    if self.version is not None and not (mine and state.get("version") == self.version):
      # Saved factors came from different learner math: start this learner from 1.0 once and record it.
      factors = [1.0, 1.0]
      self._write(factors)
    owner.set_factors(*factors)
    self.saved = (owner.bosch_gas_factor, owner.bosch_wind_factor)

  def _write(self, factors):
    return _write_state(self.meta_path, {"version": self.version, "car_fingerprint": self.fingerprint,
                                         "gas_factor": factors[0], "wind_factor": factors[1]})

  def persist(self, frame):
    if frame > 0 and frame % 6000 == 0:
      # Learning only moves while openpilot drives the pedals; skip rewriting unchanged values.
      factors = (self.owner.bosch_gas_factor, self.owner.bosch_wind_factor)
      if factors == self.saved:
        return
      if self._write(factors):
        self.saved = factors


def attach(car, meta_path=LEARNER_META_PATH):
  """Give a Honda Bosch CarController its persistence object. ``car`` is a CarInterface (uses ``.CC``) or a
  CarController. Returns the BoschLearningParams, or None when the car has no Bosch longitudinal actuator."""
  controller = getattr(car, "CC", car)
  cp = getattr(car, "CP", None) or getattr(controller, "CP", None)
  if controller is None or getattr(cp, "brand", None) != "honda":
    return None
  owner = getattr(controller, "bosch_longitudinal", None)
  if owner is None:
    return None
  controller.bosch_learning_params = BoschLearningParams(owner, meta_path)
  return controller.bosch_learning_params
