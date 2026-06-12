# Night Rider Linear EPS Fork

## Overview

This fork supports the Linear EPS firmware modification available for select Honda platforms.

Linearized EPS firmware alters the steering torque response characteristics. As a result, stock lateral tuning is not appropriate. This fork applies the required adjustments to support linear torque curves, along with additional refinements/QOL developed within the Honda Openpilot/Sunnypilot community.

---

## Recent Changes

- **Sunnylink support for all toggles & params** — every nrdr setting is now exposed on the Sunnylink website.
- **Live Long v2.0** — longitudinal stopping params (stop accel, planner stopping rate, vEgo stopping/starting) tunable live.
- **Live tuning UI overhaul** — tunable Low Pass Filter tau bands, live learned-params display, default labels, menu reorder, and the override LKAS relabel/behavior change.
- **UI crash fix + tuner polish** — fixed the vCruise speed-limit UI crash; 5% PID steps; 0.1 s override fade.
- **Live tuner fixes** — PID / longitudinal tune scale and Honda live params now actually apply; opendbc submodule repointed to nrdr.

---

## Supported Platforms

- Honda Civic (Nidec)
- Honda Civic (Bosch)
- Honda Clarity (Nidec)

Additional EPS firmware variants may be supported as they are validated.

---

## Installation

```
installer.comma.ai/nrdr/mvl-staging-03.03.2026
```

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
