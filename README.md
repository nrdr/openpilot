# Night Rider Linear EPS Fork

## Overview

This fork supports the Linear EPS firmware modification available for select Honda platforms.

Linearized EPS firmware alters the steering torque response characteristics. As a result, stock lateral tuning is not appropriate. This fork applies the required adjustments to support linear torque curves, along with additional refinements/QOL developed within the Honda Openpilot/Sunnypilot community.

---

## Recent Changes

- **Tune Report with scoring & advice** — scan your drives on-device (or from Sunnylink) and get a 0–10 tuning score with plain-English findings and suggestions that name the exact slider to move. PID Tune Information shows your car's live kp/ki/kf.
- **Dynamic HUD (Cruise Button Sub-Mode)** — distance / set / resume presses first wake a blinking preview of your personality and set speed on the real dashboard; only presses during the preview act. Adjustable 5–60 s window.
- **Special panel** — Alternative Dashboard split into independent Speed (lead / GPS / cluster) and Distance (radar / velocity) designs that stay on the cluster permanently, Show Footage (QR a phone straight to your drive videos, roadside-ready), Clear Dashboard Fault Codes toggle, and dead-camera support that finally silences "Auto High Beam System Problem".
- **Sunnylink Remote Actions** — fire Force Update or a Tune Scan from the website and watch status come back; econ 4th personality now shows there too.
- **Per-device AGNOS** — comma 4 runs 18.4, C3X runs 18.3, C3 keeps its own lane; one branch safely serves all of them. Force Update drives the real updater chain end to end.

---

## Supported Platforms

- Honda Civic (Nidec)
- Honda Civic (Bosch)
- Honda Clarity (Nidec)
- Honda Pilot (Nidec, including dead/absent stock camera via Spoof Camera Messages)

Devices: comma 3, comma 3X, comma 4 (per-device AGNOS and UI handling). Additional EPS firmware variants may be supported as they are validated.

---

## Installation

```
installer.comma.ai/nrdr/nrdr-nightly
```

`nrdr-nightly` always tracks the latest build. Dated `nrdr-staging-MM.DD.YYYY` branches are frozen daily snapshots. `nrdr-clean` is the same build minus the konik-specific pieces — it uploads to comma's servers (connect.comma.ai) for those staying in the stock ecosystem.

---

## Recommended Device Configuration

- **Force Torque Controller:** OFF
- **NNLC:** OFF
- **Model:** PopV2
- **Live Learning Delay:** ON

---

## Steering Assist Activation Behavior

Configure steering assist activation according to preference:

### Activate on Every Startup
```
STEERING → CUSTOMIZE MADS → TOGGLE MADS WITH CRUISE MAIN: ON
```

### Activate Only After LKAS Button Press
```
STEERING → CUSTOMIZE MADS → TOGGLE MADS WITH CRUISE MAIN: OFF
```

---

## Drive Uploads

This fork routes drive uploads through:

```
stable.konik.ai
```

---

## Device Pairing / Offline Issues

If the device appears offline or cannot be paired, refer to:

https://community.sunnypilot.ai/t/using-stable-konik-or-any-other-hosted-routes/945

---

## Important Notes

- While running this fork, the device communicates with `stable.konik.ai` and does not connect to Comma servers.
- When switching to another fork, always perform a factory reset first.
  - This preserves your Comma Connect account.
  - It reduces the risk of pairing or account-related issues.

---

## Disclaimer

This fork is intended for use with compatible Linear EPS firmware. Users are responsible for ensuring the correct firmware is installed prior to use. Running this fork without the appropriate EPS firmware will result in incorrect lateral control behavior.
