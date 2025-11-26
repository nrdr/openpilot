# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is BluePilot, a fork of SunnyPilot (which is a fork of OpenPilot) focused on Ford-specific enhancements for Comma3/Comma3X devices. The project aims to develop, test, and stage Ford vehicle improvements before submission to the parent SunnyPilot project.

## Development Commands

### Building the Project
```bash
# Main build system uses SCons
scons -j$(nproc)
./tools/op.sh build

# Build with specific options
scons --kaitai    # Regenerate kaitai struct parsers
scons --asan      # Build with AddressSanitizer
scons --ubsan     # Build with UndefinedBehaviorSanitizer
scons --coverage  # Build with test coverage
scons --minimal   # Minimal build for running openpilot

# Build for stock UI instead of sunnypilot UI
scons --stock-ui
```

### Testing
```bash
# Run pytest tests
pytest

# Run specific test directory
pytest selfdrive/test/
pytest system/tests/
pytest sunnypilot/

# Run tests with markers
pytest -m "not slow"  # Skip slow tests
pytest -m tici        # Run only TICI hardware tests

# Run C++ tests
pytest selfdrive/test/cpp_harness.py
```

### Linting and Code Quality
```bash
# Run all linters
./scripts/lint/lint.sh

# Run specific linters
ruff check .
mypy .
codespell .

# Fast lint (skip slow checks)
./scripts/lint/lint.sh --fast

# Format code
ruff format .
```

### Running Locally
```bash
# Launch environment
./launch_env.sh

# Launch openpilot
./launch_openpilot.sh

# For development with ChffrPlus
./launch_chffrplus.sh

# Launch QT UI
./selfdrive/ui/ui
```

## Architecture Overview

### Core Components

1. **selfdrive/** - Main self-driving functionality
   - `controls/` - Vehicle control logic (lateral/longitudinal)
   - `car/` - Vehicle-specific interfaces and configurations
   - `modeld/` - Neural network model processing
   - `locationd/` - Localization and calibration
   - `monitoring/` - Driver monitoring system
   - `ui/` - User interface components

2. **sunnypilot/** - SunnyPilot-specific extensions
   - `modeld/` - Model extensions and alternatives
   - `mads/` - Modified Assist Driving System
   - `mapd/` - Map data integration
   - `models/` - Neural network model management

3. **bluepilot/** - Ford-specific BluePilot features
   - `params/` - BluePilot parameters and configuration
   - `logger/` - BluePilot-specific logging
   - `data_collection/` - Data collection and training utilities

4. **system/** - System-level services
   - `hardware/` - Hardware abstraction layer
   - `manager/` - Process management
   - `loggerd/` - Logging infrastructure
   - `updated/` - Update management

5. **tools/** - Development and debugging tools
   - `replay/` - Drive log replay tools
   - `cabana/` - CAN bus analysis tool
   - `sim/` - Simulation environment

### Key Design Patterns

- **Message-based Architecture**: Uses cereal/messaging for inter-process communication
- **SubMaster/PubMaster Pattern**: Pub-sub messaging between components
- **CarInterface Abstraction**: Each vehicle brand implements a standard interface
- **Process Isolation**: Components run as separate processes managed by system/manager

### Ford-Specific Features (BluePilot)

The codebase includes extensive Ford vehicle enhancements:
- Improved longitudinal controls with separate gas/brake signals
- Anti-windup logic for turns in EPAS systems
- OEM-style lateral control logic with curvature blending
- Enhanced lane change logic
- Custom tuning profiles for CAN vs CANFD vehicles
- Blue Cruise dashboard integration
- Blindspot indicators and stop sign detection overlays

### Build System

- Uses SCons as the primary build system
- Supports multiple architectures: larch64 (TICI), aarch64, x86_64, Darwin
- Python dependencies managed via pyproject.toml
- C++ compilation with various sanitizer options

### Testing Infrastructure

- pytest for Python tests with custom markers
- C++ test harness for native code
- Test coverage reporting
- Continuous integration setup
- Hardware-specific tests for TICI devices

## Important Considerations

1. **Safety Critical**: This is safety-critical automotive software. All changes must adhere to comma.ai's safety policy
2. **Process Management**: Components are managed by system/manager/process_config.py
3. **Message Flow**: Understanding cereal message definitions is crucial for inter-process communication
4. **Hardware Variants**: Code must support both Comma3 and Comma3X hardware
5. **Ford Specifics**: Ford vehicles may use either CAN or CANFD protocols with different tuning requirements

## Branch Management

BluePilot uses versioned branches (e.g., bp-1.1, bp-2.1) rather than traditional stable/staging branches. Each release branch is preserved for reference and comparison.

## Installation URLs

Installation follows the pattern: `installer.comma.ai/BluePilotDev/{branch-name}`
Example: `installer.comma.ai/BluePilotDev/bp-2.1`
