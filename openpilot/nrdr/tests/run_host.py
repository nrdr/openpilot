"""Windows checks: replace only device logging, not the controller or car schemas.

Native validation must invoke pytest directly, without this host-only adapter.
"""
import logging
import sys
import types

if sys.platform == "win32":
  module = types.ModuleType("openpilot.common.swaglog")
  module.cloudlog = logging.getLogger("host_bare_validation")
  sys.modules[module.__name__] = module

import pytest

raise SystemExit(pytest.main(sys.argv[1:]))
