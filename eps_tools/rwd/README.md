# EPS firmware images (`.rwd`)

Honda/Acura EPS firmware files for use with `eps-update.py` (in the repo root).
All files here were checksum-validated with `check_rwd.py` (file checksum +
decrypted firmware checksums all PASS).

Each model is kept as a **stock + modified pair** — `stock` is the factory
recovery image (flash this back if a flash fails), and the modified image is the
matching stabilized torque-table tune.

## Validate
```bash
python3 check_rwd.py rwd/<file>.rwd       # single
python3 check_rwd.py rwd/*.rwd            # all
```

## Flash (see ../README.md and ../eps-update.py)
Prefer the guided flasher: `python3 flash.py` (auto-detects bus, offers dry run).
For the manual path, always run a `--danger`-less dry run first (it stops before
erase; default bus is **1**), and flash from a persistent copy — the comma updater
wipes untracked files from `/data/openpilot`. Some cars lock security access after
a dry run; wait / power-cycle before `--danger`, or use `flash.py`'s skip/retry.

## Contents
| model | stock | modified |
|-------|-------|-----------|
| Honda CR-V 5G (39990-TLA-A040) | `39990-TLA-A040-stock.rwd` | `39990-TLA-A040-linear-max.rwd` |
| Honda Civic (39990-TBA-C120) | `39990-TBA-C120-stock.rwd` | `39990-TBA-C120-linear-max.rwd` |
| Honda Insight (39990-TXM-A040) | `39990-TXM-A040-stock.rwd` | `39990-TXM-A040-linear-max.rwd` |
| Honda Pilot (39990-TG7-A060) | `39990-TG7-A060_STOCK.rwd` | `39990-TG7-A060_2X.rwd` |

## Upstreaming guidelines

Rules for adding `.rwd` files to this branch / upstreaming them:

1. **Every file must validate.** It has to pass `check_rwd.py` (file checksum +
   decrypted firmware checksums) before it can be added.
2. **A stock `.rwd` may be added on its own.** Factory/recovery images are always
   welcome — more recovery coverage is strictly good.
3. **A linear-max (or any modified) variant may NOT be added alone.** It must be
   accompanied by a valid, verified **stock** `.rwd` for the same model, so there
   is always a factory image to flash back if a flash fails. No stock → no mod.
4. **Keep experimental work in a testing fork.** Anything still being tested or
   tuned (filter/rate variants, gain experiments, `*-test`, version-bumped
   tuning images, etc.) stays in a testing fork until it is proven stable on the
   car. Only stock images and stabilized linear-max variants belong here.

