#!/usr/bin/env python3
"""Remove the optional reminder-timing panel from a generated clean build."""

import argparse
import copy
import json
from pathlib import Path

import yaml

PANEL_ID = "nrdr_driver_monitoring"
PARAM_KEY = "NrdrDriverMonitoringReminderPercent"


def without_monitoring_panel(document: dict) -> dict:
  result = copy.deepcopy(document)
  removed = 0

  def walk(node):
    nonlocal removed
    if isinstance(node, dict):
      for key, value in node.items():
        if key == "sub_panels":
          kept = [panel for panel in value if panel.get("id") != PANEL_ID]
          removed += len(value) - len(kept)
          node[key] = kept
        walk(node[key])
    elif isinstance(node, list):
      for item in node:
        walk(item)

  walk(result)
  if removed != 1:
    raise ValueError(f"expected exactly one {PANEL_ID} panel, found {removed}")
  if PARAM_KEY in json.dumps(result):
    raise ValueError("reminder customization still appears outside its panel")
  return result


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("build_dir", type=Path)
  root = parser.parse_args().build_dir.resolve()
  source = root / "openpilot/nrdr/ui/sunnylink/pages/steering.yaml"
  compiled = root / "openpilot/sunnypilot/sunnylink/settings_ui.json"
  # Validate both documents before modifying either one.
  source_data = without_monitoring_panel(yaml.safe_load(source.read_text(encoding="utf-8")))
  compiled_data = without_monitoring_panel(json.loads(compiled.read_text(encoding="utf-8")))
  source.write_text(yaml.safe_dump(source_data, sort_keys=False, allow_unicode=True), encoding="utf-8")
  compiled.write_text(json.dumps(compiled_data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
  main()
