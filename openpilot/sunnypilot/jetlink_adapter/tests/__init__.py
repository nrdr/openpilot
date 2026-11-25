# nrdr vendors jetlink at jetlink_repo/ and launch_chffrplus.sh links it to ./jetlink;
# a checkout that has not run the launch script still imports it from here.
import sys
from pathlib import Path

_VENDORED = Path(__file__).resolve().parents[4] / 'jetlink_repo'
if _VENDORED.is_dir() and str(_VENDORED) not in sys.path:
  sys.path.append(str(_VENDORED))
