![](https://private-user-images.githubusercontent.com/56047663/329263894-14976646-2e10-4c51-946b-e5e0b91821ee.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTUyNjIyMzksIm5iZiI6MTcxNTI2MTkzOSwicGF0aCI6Ii81NjA0NzY2My8zMjkyNjM4OTQtMTQ5NzY2NDYtMmUxMC00YzUxLTk0NmItZTVlMGI5MTgyMWVlLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA1MDklMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwNTA5VDEzMzg1OVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTMxMzQwZTE0NjQ0NjNmNTgxMzdmNGI2ZTc4ZGRmNWZmMGE4MmEwMTE2ODc1MDE5ODBjNzk0ZTlkNjc3ZjNmMjcmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.cqqRUk4IZHyoqETqO2fRK89kfSrYXxI1eovSVQ7X0I4)

Table of Contents
=======================

- [Table of Contents](#table-of-contents)
    - [Upstream SunnyPilot Features](#upstream-sunnypilot-features)
  - [What's New in bp-5.0](#whats-new-in-bp-50)
    - [User Interface \& Experience](#user-interface--experience)
    - [Software \& Management](#software--management)
    - [Web Interface \& Data Management](#web-interface--data-management)
    - [Vehicle Features](#vehicle-features)
    - [Ford-Specific Lateral Control](#ford-specific-lateral-control)
    - [BluePilot Settings \& Tuning](#bluepilot-settings--tuning)
    - [Performance \& Stability](#performance--stability)
    - [Known Issues](#known-issues)
    - [Backend Architecture](#backend-architecture)
    - [API Endpoints](#api-endpoints)
    - [Development](#development)

---

<details><summary><h3>💭 Updates on Branch Names and Links</h3></summary>

---

As of May 2025, we are updating the way branches are named and how links are generated. We had initially intended to use a branch naming system similar to openpilot and sunnypilot where there was a "stable" or "release" branch which included all fully vetted code, and then "staging" or "beta" branches with new code that would eventually move into the stable/release branches.  However as we evolved we found everyone liked being able to bounce between newer and older branches to compare features and control. Moving forwards all releases will simply be named bp-"feature release number" as an example "staging-1.1" which features the bluepilot 1.1 features (custom tuning) will become "bp-1.1".  We will not delete older branches so that anyone can go back and view older code for references.  Branches that no longer work properly will be denoted as -deprecated.

To install any version of bluepilot, use the following URL formula (URL is case sensitive)

installer.comma.ai/BluePilotDev/"branch name"

For example

installer.comma.ai/BluePilotDev/bp-5.0

will install the **bp-5.0** branch (current release based on SunnyPilot v2025.001.000).  Branches known to no longer work due to changes in the comma codebase will be appended with -deprecated so it will be obvious they will not install or work correctly.

</details>


---

<details><summary><h3>💭 Join our Discord</h3></summary>

---

Join the official #ford channel at the sunnypilot Discord server to stay up to date with all the latest features and be a part of shaping the future of bluepilot!
* [sunnypilot Discord server](https://discord.sunnypilot.com)

</details>

<details><summary><h3>🌞 What is bluepilot?</h3></summary>

---

[bluepilot](https://github.com/bluepilotdev/bluepilot) is a fork of the hugely popular SunnyPilot project for the Comma3 and Comma3X.  The goal of BluePilot is to develop, test, and stage Ford specific enhancements, validating them before submission to the SunnyPilot team for inclusion in the parent project.  BluePilot is always based upon sunnypilot's master-devbranch.

**BluePilot bp-5.0** is based on **SunnyPilot v2025.003.000** and includes all upstream sunnypilot features plus Ford-specific enhancements. This release runs on AGNOS 13.1 and brings significant improvements to the UI, settings management, and onroad experience.

### Upstream SunnyPilot Features
BluePilot includes **all** features from the upstream SunnyPilot project. For a complete list of sunnypilot features and changes:
* **[CHANGELOG_SP.md](CHANGELOG_SP.md)** - Complete sunnypilot changelog with all upstream features
* **[README_SP.md](README_SP.md)** - Full sunnypilot documentation and feature descriptions

Key upstream features include: MADS (Modular Assistive Driving System), Neural Network Lateral Control (NNLC), Dynamic Experimental Control (DEC), Speed Limit Assist (SLA), Intelligent Cruise Button Management (ICBM, not yet available for Ford vehicles), Smart Cruise Control Map & Vision (SCC-M / SCC-V), Driving Model Manager with 86+ models, sunnylink integration, and much more.

</details>

<details><summary><h3>⛔ Prohibited Safety Modifications</h3></summary>

---

All [official sunnypilot branches](https://github.com/sunnyhaibin/sunnypilot/branches) strictly adhere to [comma.ai's safety policy](https://github.com/commaai/openpilot/blob/master/docs/SAFETY.md). Any changes that go against this policy will result in your fork and your device being banned from both comma.ai and sunnypilot channels. This same stipulation applies to all bluepilot instances as well.

The following changes are a **VIOLATION** of this policy and **ARE NOT** included in any sunnypilot branches:
* Driver Monitoring:
    * ❌ "Nerfing" or reducing monitoring parameters.
* Panda safety:
    * ❌ No preventing disengaging of <ins>**LONGITUDINAL CONTROL**</ins> (acceleration/brake) on brake pedal press.
    * ❌ No auto re-engaging of <ins>**LONGITUDINAL CONTROL**</ins> (acceleration/brake) on brake pedal release.
    * ❌ No disengaging on ACC MAIN in OFF state.

</details>


<details><summary><h3>⚒ Installation</h3></summary>

* bluepilot not installed
  1. [Factory reset/uninstall](https://github.com/commaai/openpilot/wiki/FAQ#how-can-i-reset-the-device) the previous software if you have another software/fork installed.
  2. After factory reset/uninstall and upon reboot, select `Custom Software` when given the option.
  3. Input the installation URL based on the desired branch. Example: ```installer.comma.ai/BluePilotDev/bp-5.0``` (note: `https://` is not required on the comma three)
  4. Complete the rest of the installation following the onscreen instructions.

* bluepilot already installed and you installed a version after 0.8.17?
  1. On the comma three, go to `Settings` ▶️ `Software`.
  2. At the `Download` option, press `CHECK`. This will fetch the list of latest branches from sunnypilot.
  3. At the `Target Branch` option, press `SELECT` to open the Target Branch selector.
  4. Scroll to select the desired branch


Requires further assistance with software installation? Join the [sunnypilot Discord server](https://discord.sunnypilot.com) and message us in the `#ford` channel.

  </details>

<details><summary><h3>🚗 BluePilot Specific Features - bp-5.0</h3></summary>

---

## What's New in bp-5.0

BluePilot 5.0 is a **major update** based on SunnyPilot v2025.003.000 (AGNOS 13.1) with significant improvements to the UI, settings management, and onroad experience.

### User Interface & Experience
* **Completely redesigned settings menu** - Reorganized into focused panels (Device, Display, Network, Vehicle, Toggles, Cruise, Steering, Developer, Visuals) for better navigation
* **Enhanced BluePilot Sidebar** - WiFi status with SSID and signal strength, improved network info card, removed constant fan animation (now shows memory usage only)
* **Improved Onroad Rendering** - Enhanced lane lines, road edges, and path rendering with glow effects and smoother curve tracking
* **Routes Panel (Beta)** - View dashcam footage directly on the device with video playback, web-based routes viewer for logs and cereal data
* **Brightness Control System** - Perceptual brightness correction for better viewing experience with more responsive adjustments
* **Model Info & Drive Stats Widgets** - Real-time onroad display of model information and enhanced drive statistics

### Software & Management
* **New Software Panel** - Integrated updater with branch management, model selection interface, git manager integration, and improved power management
* **Models Panel** - Easy switching between different driving models without reinstalling branches
* **Developer Tools** - Customizable debug panel with adjustable settings, conditional building, crash detection system with better error reporting

### Web Interface & Data Management
* **Routes Web Interface** - Full-featured web dashboard accessible at `http://<device-ip>:8088`
  * Browse and search all recorded routes with GPS metadata
  * Interactive route map with GPS coordinates and path visualization
  * Real-time metrics: speed, distance, duration, and segment information
  * Individual camera video exports (front, wide, driver) with progress tracking
  * Direct qlog/rlog downloads for CAN bus and sensor data analysis
  * Detailed log descriptions explaining what data each file contains
  * Automatic multi-segment file concatenation for seamless data access
* **Enhanced Data Export** - Simplified export system replacing ZIP compression
  * Individual camera downloads with descriptive filenames
  * Real-time progress tracking for video generation
  * No compression overhead - faster exports
  * qlog: Control commands, steering angles, CAN bus messages, lateral/longitudinal plans
  * rlog: Camera metadata, model predictions, radar tracks, IMU data, GPS coordinates

### Vehicle Features
* **Brake Status Indicator** - Now attempts to use brake light CAN signal when available for more accurate display
* **Radar Overlay** - Speed display matches system units (mph/kph)
* **Stop Sign Overlay** - Better positioning, enhanced visual effects, improved detection logic
* **Hybrid Drive Battery Gauge** - More accurate battery percentage calculations with fixed scaling
* **Option to Bypass BluePilot Lateral Controls** - Added for testing and diagnostic purposes

### Ford-Specific Lateral Control
In addition to all sunnypilot features, BluePilot incorporates the following Ford-specific enhancements:

* **Improved Ford Longitudinal Controls** - Logic to adjust stock OpenPilot single acceleration signal into separate gas and brake signals for smoother long control
* **Anti-Windup in Turns** - Resets EPAS back to zero when human turn is detected, preventing wind-up and fighting after straightening
* **OEM Style Lateral Control Logic** - Complete rewrite matching OEM EPAS behavior with curvature blending, curvature_rate integration, path_offset and path_angle variables
* **Improved Lane Change Logic** - Further improvements to fix overshoot issues from older logic

### BluePilot Settings & Tuning

The following settings are available in the BluePilot menu (after completing one drive in a Ford vehicle):

**Display & Visual Settings:**
* Disable GPS Alert
* Show Animated Steer Angle Icon
* Show Brake Status (now uses CAN signal when available)
* Custom Model Path Color
* Show Radar Lead Vehicle Overview
* Show Hybrid Electric Data Overlays
* Show Hybrid Battery Data Overlay
* Hybrid Drive Gauge Size
* Show Blindspot Indicators
* Show Stop Indicator Overlay
* Show Wide Camera at Low Speed

**Vehicle Integration:**
* Show Hands Free UI (Blue Cruise dash for supported digital dashes)
* Send Lane Departure Signals

**Lateral Control Tuning:**
* Enable Human Turn Detection
* Lane Change Factor
* Use Custom Tuning Profile (Auto-selected based on CAN/CANFD)
* Predicted Curvature Blend Ratio Low (Default: CANFD=0.65, CAN=0.4)
* Predicted Curvature Blend Ratio High (Default: CANFD=0.4, CAN=0.2)
* Enable Advanced Lane Positioning
* Enable Legacy Style Lanefull Mode
* In Lane Offset
* Low Curvature PID Gain (Default: CANFD=3.0, CAN=5.0)
* Bypass BluePilot Lateral Controls (for testing)

### Performance & Stability
* Refactored renderer for better performance
* Integrated lead tracking and stop detection into ModelRendererBP
* Enhanced frame state updates
* Better lane line mapping using model transform
* Thread safety improvements throughout UI
* Multiple stability fixes and bug fixes

### Known Issues
* Routes Panel video playback is in beta and may have performance issues on some devices

For complete details on all changes, see [CHANGELOG.md](CHANGELOG.md) or the [BP_CHANGES.json](BP_CHANGES.json) file.

</details>

<details><summary><h3>📗 How To's</h3></summary>

---

How-To instructions can be found in [HOW-TOS.md](https://github.com/sunnyhaibin/openpilot/blob/(!)README/HOW-TOS.md).

</details>

<details><summary><h3>🏆 Special Thanks</h3></summary>

---

* [twilsonco](https://github.com/twilsonco/openpilot)

</details>

<details><summary><h3>📊 User Data</h3></summary>

---

By default, sunnypilot/bluepilot uploads the driving data to comma servers. You can also access your data through [comma connect](https://connect.comma.ai/).

sunnypilot/bluepilot is open source software. The user is free to disable data collection if they wish to do so.

sunnypilot/bluepilot logs the road-facing camera, CAN, GPS, IMU, magnetometer, thermal sensors, crashes, and operating system logs.
The driver-facing camera is only logged if you explicitly opt-in in settings. The microphone is not recorded.

By using this software, you understand that use of this software or its related services will generate certain types of user data, which may be logged and stored at the sole discretion of comma. By accepting this agreement, you grant an irrevocable, perpetual, worldwide right to comma for the use of this data.

</details>

<details><summary><h3>Licensing</h3></summary>

openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.

Any user of this software shall indemnify and hold harmless comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.

**THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.
YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.
NO WARRANTY EXPRESSED OR IMPLIED.**

</details>

<details><summary><h3>Support sunnypilot</h3></summary>
<h3>💰 Support sunnypilot</h3>

---

If you find any of the features useful, consider becoming a [patron on Patreon](https://www.patreon.com/sunnyhaibin) or a [sponsor on GitHub](https://github.com/sponsors/sunnyhaibin) to support future feature development and improvements.


By becoming a patron/sponsor, you will gain access to exclusive content, early access to new features, and the opportunity to directly influence the project's development.

<h3>Patreon</h3>

<a href="https://www.patreon.com/sunnyhaibin">
  <img src="https://user-images.githubusercontent.com/47793918/244128051-bc7e913e-a196-4455-926e-23aec9a4bd3b.png" alt="Become a Patron" width="300" style="max-width: 100%; height: auto;">
</a>
<br>

<h3>GitHub Sponsor</h3>

<a href="https://github.com/sponsors/sunnyhaibin">
  <img src="https://user-images.githubusercontent.com/47793918/244135584-9800acbd-69fd-4b2b-bec9-e5fa2d85c817.png" alt="Become a Sponsor" width="300" style="max-width: 100%; height: auto;">
</a>
<br>

<h3>PayPal</h3>

<a href="https://paypal.me/sunnyhaibin0850" target="_blank">
<img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="PayPal this" title="PayPal - The safer, easier way to pay online!" border="0" />
</a>
<br></br>
</details>

<details><summary><h3>🔧 Technical Documentation</h3></summary>

---

### Backend Architecture

BluePilot's backend is organized into modular components for maintainability:

```
bluepilot/backend/
├── bp_portal.py             # Main HTTP server (BluePilot Portal)
├── config.py                # Configuration and constants
├── handlers/                # Request handlers
│   ├── log_downloads.py     # qlog/rlog download handlers
│   └── __init__.py
├── params/                  # Parameter management
│   ├── params_manager.py    # Parameter CRUD operations
│   ├── params_watcher.py    # Real-time parameter watching
│   └── __init__.py
├── routes/                  # Route processing
│   ├── scanner.py           # Route discovery
│   ├── segments.py          # Segment management
│   ├── preprocessor.py      # Route data preprocessing
│   └── processing.py        # GPS and metrics calculation
├── video/                   # Video export
│   ├── export.py            # Individual camera export with FFmpeg
│   └── remux.py             # Video remuxing utilities
├── core/                    # Core utilities
├── utils/                   # Helper functions
├── realtime/                # WebSocket broadcasting
├── cache/                   # Cache management
└── network/                 # Network utilities
```

### API Endpoints

**Route Management:**
- `GET /api/routes` - List all routes with pagination
- `GET /api/route/{route_base}` - Get specific route details
- `GET /api/route/{route_base}/camera-sizes` - Get camera and log file sizes

**Video Export:**
- `POST /api/video-export/{route_base}/{camera}` - Start video export
- `GET /api/video-export/{route_base}/{camera}/status` - Check export progress
- `GET /api/download/route/{route_base}/{camera}` - Download exported video

**Log Downloads:**
- `GET /api/download/qlog/{route_base}` - Download qlog (concatenated if multi-segment)
- `GET /api/download/rlog/{route_base}` - Download rlog (concatenated if multi-segment)

### Development

**Testing:**
```bash
# Test backend imports
python3 bluepilot/backend/test_backend_import.py

# Test modular components
python3 bluepilot/backend/test_modules_only.py

# Run local server for testing
python3 bluepilot/test_web_routes.py
```

**Frontend Development:**
```bash
cd bluepilot/web
npm install
npm run dev      # Development server
npm run build    # Production build
```

For detailed cleanup and refactoring notes, see:
- [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md) - Complete cleanup documentation
- [BACKEND_CLEANUP_CHECKLIST.md](BACKEND_CLEANUP_CHECKLIST.md) - Backend refactoring checklist

</details>


<span>-</span> BluePilotDev Team
