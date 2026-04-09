# Night Rider Linear EPS Fork

## Overview

This fork supports the Linear EPS firmware modification available for select Honda platforms.

Linearized EPS firmware alters the steering torque response characteristics. As a result, stock lateral tuning is not appropriate. This fork applies the required adjustments to support linear torque curves, along with additional refinements/QOL developed within the Honda Openpilot/Sunnypilot community.

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

The following configuration is recommended for optimal behavior with Linear EPS firmware.

### Model

- **Model:** POPv1 (known simply as POP) (Good lane positioning)
  - OPMv7 can be smoother but hugs more.
  - GWMv9 has been tried and tested, solid legacy model.
- **Live Learning Delay:** ON

---

### Steering

- **Enforce Torque Lateral Control:** ON

---

### Torque Control Settings

- **Version:** v0.0
  - Default provides very aggressive low speed performance but will be uncomfortable and jerky.
- **Self Tune:** OFF
- **Less Restrict Settings (Beta):** OFF
- **Enable Custom Tuning:** OFF
- **Manual Real-time Tuning:** OFF

These defaults ensure consistent behavior with linearized EPS firmware.

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
