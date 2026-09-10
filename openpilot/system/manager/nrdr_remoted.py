#!/usr/bin/env python3
"""Framework process adapter for the NRDR remote-services loop."""

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.nrdr.features.services.remoted import _park, _validate_params, run


def main() -> None:
  from openpilot.nrdr.features.services.car_tune_report import CarTuneReporter

  params = Params()
  try:
    _validate_params(params)
  except Exception:
    cloudlog.exception("nrdr_remoted: unavailable params")
    _park()

  run(params, CarTuneReporter)


__all__ = ("main",)


if __name__ == "__main__":
  main()
