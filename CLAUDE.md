# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

openpilot is an open source driver assistance system by comma.ai. This is a development fork (branch `devel-098`) focused on Honda vehicle support, ECU firmware tools, and longitudinal control improvements. The upstream repo is commaai/openpilot; PRs target the `devel` branch.

## Build System

**SCons** is the build tool (not Make/CMake).

```bash
scons -j$(nproc)              # Build everything
scons --minimal               # Minimal build (no tests/tools)
scons selfdrive/ui/           # Build specific target
scons --asan                  # Address sanitizer
scons --ubsan                 # Undefined behavior sanitizer
```

The root `SConstruct` dispatches to `SConscript` files in each module. Build artifacts include Cap'n Proto generated code, compiled C++ services, Cython extensions, and Qt UI binaries.

## Testing

pytest with parallel execution via xdist (configured in `pyproject.toml`):

```bash
pytest                                        # All tests (parallel by default via -n auto)
pytest selfdrive/test/test_file.py            # Single file
pytest selfdrive/test/test_file.py::test_func # Single test
pytest -m 'not slow'                          # Skip slow tests
```

Key pytest details:
- `conftest.py` auto-creates an isolated `OpenpilotPrefix` environment per test and cleans up processes/env vars after each test
- Tests marked `@pytest.mark.tici` only run on comma 3/3X hardware, auto-skipped on PC
- Tests marked `@pytest.mark.slow` can be excluded with `-m 'not slow'`
- Process replay tests (`selfdrive/test/process_replay/`) validate against reference route data — these are collected separately, not by default pytest collection
- Test randomization is currently disabled in `pytest_sessionstart`

## Linting

```bash
pre-commit run --all-files    # Full lint suite
ruff check .                  # Python linting only
mypy common/                  # Type checking
```

## Code Style Conventions

- **2-space indentation** for Python (configured in ruff and pylint)
- **Line length**: 160 chars (ruff), 100 chars (pylint)
- **Python 3.11** target
- **Imports**: Use fully qualified `openpilot.*` paths — `from openpilot.selfdrive.car...` not `from selfdrive.car...` (enforced by ruff TID251 rule)
- **No unittest**: Use pytest (enforced by ruff banned-api rule)
- C++ uses clang/clang++ with `-std=c++1z`, `-Werror`, `-Wshadow`

## Architecture

### Process-Based System
openpilot runs as a set of independent processes orchestrated by `system/manager/`. Process config is in `system/manager/process_config.py`. Each process is either a Python daemon or native C++ binary.

### Message Passing (cereal/msgq)
All inter-process communication uses pub/sub messaging. Message schemas are defined in Cap'n Proto format in `cereal/log.capnp`. Services are registered in `cereal/services.py`. The `msgq` module provides shared-memory ring buffers for IPC.

### Car Interface Layer (opendbc_repo)
Vehicle-specific code lives in `opendbc_repo/` (separate submodule). Each manufacturer has:
- `carstate.py` — parse CAN messages into standardized car state
- `carcontroller.py` — translate control commands to CAN
- `interface.py` — high-level car interface
- `values.py` — car-specific constants and platform definitions

### Control Pipeline (selfdrive/controls)
Lateral (steering) and longitudinal (speed) control are decoupled. The planner generates trajectories, controllers execute them. Car-specific tuning parameters are in the car interface layer.

### Key Submodules
These directories are separate repos pinned as submodules — avoid editing them directly:
- `cereal/` — message definitions
- `msgq/` / `msgq_repo/` — message queue
- `panda/` — CAN interface hardware firmware
- `opendbc/` / `opendbc_repo/` — vehicle CAN database and car interfaces
- `rednose_repo/` — Kalman filter
- `tinygrad_repo/` — ML inference framework

### Platform Detection
- `TICI` / `AGNOS` — running on comma 3/3X hardware
- `arch` values: `larch64` (comma device), `aarch64` (Linux ARM), `x86_64` (Linux PC), `Darwin` (macOS)
- macOS sets `ZMQ=1` for messaging backend and uses `DYLD_LIBRARY_PATH`

## Environment

- `PYTHONPATH` must include the repo root
- `OPENPILOT_PREFIX` is set per-test for isolation (managed by conftest.py)
- On macOS, some system-level daemons (camerad, sensord, logcatd) are not built
