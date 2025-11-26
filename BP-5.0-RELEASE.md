# BluePilot 5.0 Release Announcement

**Release Date:** November 23, 2025
**Base:** SunnyPilot 2025.003.0.0
**AGNOS:** 13.1

---

## Overview

BluePilot 5.0 is a **major release** representing months of development focused on improving the user experience, expanding Ford-specific features, and introducing powerful new tools for managing your comma device.

This release brings a completely redesigned web interface, enhanced onroad visuals, improved Ford lateral controls, and numerous quality-of-life improvements throughout the system.

**Watch the release overview:** [BluePilot 5.0 Overview on YouTube](https://www.youtube.com/watch?v=9ggGzCI-zx0)

---

## Highlights

### BluePilot Portal - All-New Web Interface

The biggest addition in BP-5.0 is the **BluePilot Portal**, a modern React-based Progressive Web App (PWA) that provides comprehensive device management from any browser.

**Access it at:** `http://<device-ip>:8088`

**Key Features:**
- **Home Dashboard** - Real-time system status, drive statistics, and disk space visualization
- **Routes Management** - Browse drives, view GPS paths, play back video, and export footage
- **Settings Panel** - Configure all BluePilot parameters with real-time WebSocket updates
- **Diagnostics** - Live TMUX streaming and parameter debugging
- **PWA Support** - Install on your phone for app-like quick access

### Redesigned Settings Experience

The on-device settings have been completely reorganized into focused panels:
- Device, Display, Network, Vehicle, Toggles, Cruise, Steering, Developer, Visuals
- New Models Panel for easy driving model switching
- New Software Panel with integrated updater and branch management

### Enhanced Onroad Visuals

- Improved lane lines, road edges, and path rendering with glow effects
- Smoother curve tracking with reduced path swaying
- Better color consistency and refined rendering logic

### Ford-Specific Improvements

- **Human Turn Detection** - Increased latch time to 3.0 seconds for smoother handling
- **Panda Safety** - Curvature limits refined for better message handling
- **Bug Fixes** - Fixed blocked messages during speed transitions and turns

### Recommended Driving Models by Platform

| Platform | Years | Bus Type | Recommended Models |
|----------|-------|----------|-------------------|
| Ford Bronco Sport | 2021-24 | CAN | Nevada, WD40 |
| Ford Edge | 2022 | CAN | Nevada, WD40 |
| Ford Escape | 2020-22 | CAN | Nevada, WD40 |
| Ford Escape | 2023-24 | CANFD | Nevada, WD40 |
| Ford Expedition | 2022-24 | CANFD | Nevada, WD40, FoF |
| Ford Explorer | 2020-24 | CAN | Nevada, WD40 |
| Ford F-150 | 2021-23 | CANFD | Nevada, WD40, FoF |
| Ford F-150 Lightning | 2022-23 | CANFD | Nevada, WD40, FoF |
| Ford Focus | 2018 | CAN | Nevada, WD40 |
| Ford Kuga | 2020-24 | CAN/CANFD | Nevada, WD40 |
| Ford Maverick | 2022-24 | CAN | Nevada, WD40 |
| Ford Mustang Mach-E | 2021-24 | CANFD | Nevada, WD40 |
| Ford Ranger | 2024 | CANFD | Nevada, WD40 |
| Lincoln Aviator | 2020-24 | CAN | Nevada, WD40 |

**Model Notes:**
- **Nevada** - Recommended for all Ford platforms
- **WD40** - Recommended for all Ford platforms
- **FoF** - Optimized specifically for F-150, F-150 Lightning, and Expedition

---

## What's New

### Web Interface & Data Management
- BluePilot Portal with modern React UI
- Routes viewer with video playback and camera selection
- Video exports for front, wide, and driver cameras
- Direct qlog/rlog downloads for data analysis
- Real-time parameter configuration
- Backup and restore functionality

### User Interface
- Completely redesigned settings menu structure
- BP Models Panel for driving model selection
- BP Software Panel for software management
- Enhanced sidebar with WiFi status display
- Perceptual brightness correction system

### Vehicle Features
- Brake status indicator using CAN signals
- Radar overlay with correct speed units
- Improved stop sign detection and display
- More accurate hybrid battery gauge
- Option to bypass BluePilot lateral controls

### Ford Lateral Controls
- Improved human turn detection with longer latch
- Better EPAS wind-up prevention
- Fixed message blocking during transitions
- Escape MK4.5 naming correction

### Developer Tools
- Customizable onroad debug panel
- UI crash detection system
- Unified logging throughout BluePilot code

### Performance
- Refactored renderer for better performance
- Thread safety improvements
- Fixed web server startup crashes
- General stability improvements

---

## Installation

### Fresh Install
```
installer.comma.ai/BluePilotDev/bp-5.0
```

### Upgrade from Previous Version
1. Go to **Settings** > **Software**
2. Press **CHECK** at Download
3. Select **bp-5.0** as Target Branch
4. Install and reboot

---

## Documentation

For complete details on all changes and features:

- **[CHANGELOG.md](CHANGELOG.md)** - Full changelog with all changes
- **[README.md](README.md)** - Complete feature documentation
- **[CHANGELOG_SP.md](CHANGELOG_SP.md)** - Upstream SunnyPilot changes
- **[README_SP.md](README_SP.md)** - SunnyPilot feature documentation

---

## Known Issues

- Routes Panel video playback is in beta and may have performance issues on some devices
- Some features are still being refined

---

## Getting Help

Join the **#ford** channel on the [SunnyPilot Discord](https://discord.sunnypilot.com) for:
- Installation assistance
- Feature questions
- Bug reports
- Community discussion

---

## Upstream Features

BluePilot 5.0 includes all features from SunnyPilot 2025.003.0.0:
- MADS (Modular Assistive Driving System)
- Neural Network Lateral Control (NNLC)
- Dynamic Experimental Control (DEC)
- Speed Limit Assist (SLA)
- Intelligent Cruise Button Management (ICBM, not yet available for Ford vehicles)
- Driving Model Manager with 86+ models
- sunnylink integration
- And much more...

See [CHANGELOG_SP.md](CHANGELOG_SP.md) for complete upstream changes.

---

## Thank You

Thanks to everyone who contributed to this release through testing, feedback, and development. Special thanks to the SunnyPilot team and the Ford community.

---

**Safe driving!**

*- The BluePilot Team*
