# EPS tools

Standalone tooling for reading, validating, and flashing Honda/Acura EPS
firmware (`.rwd`). Works on the current opendbc layout — no panda-submodule or
`selfdrive.car` dependencies.

Credit to mmmorks for the original flasher scripts, and to
[RiskyBiscuit-arc](https://github.com/RiskyBiscuit-arc) for updating them to the
current opendbc layout and adding the safety checks.

> **Disclaimer:** Flashing EPS firmware can damage or permanently brick your
> power-steering ECU. **You alone are responsible for your EPS and your vehicle,
> and you use these tools entirely at your own risk** — no warranty of any kind,
> express or implied. Always validate the image (`check_rwd.py`) and do a dry run
> before flashing.

```
eps_tools/
  eps-update.py     UDS .rwd flasher (validate + erase/program over CAN)
  check_rwd.py      offline .rwd checksum validator (stdlib only)
  eps-diag.py       EPS CAN liveness/diagnostic (sniff, UDS ping, part number)
  rwd_format/       vendored Python-3 .rwd container parser (0x5A/0x31)
  rwd/              checksum-validated firmware images + upstreaming guidelines
```

Run the scripts **from this folder** so `rwd_format` resolves; `opendbc`/`panda`
come from the openpilot install (prefix with `PYTHONPATH=/data/openpilot` if you
hit import errors).

## How to flash

1. Make sure the comma power is connected to the car's OBD2 port.
2. With the car **OFF**, stop openpilot over SSH:
   ```
   pkill -f openpilot
   ```
3. Put the car in full **accessory mode** (ignition ON, engine OFF). Turn off the
   A/C to avoid draining the battery.
4. **Dry run first** — validates the image and walks the UDS/security flow but
   aborts *before* any mutating action:
   ```
   cd eps_tools
   python3 eps-update.py rwd/REPLACE_WITH_YOUR_FIRMWARE.rwd -b 1
   ```
   When it aborts before performing mutating actions, that's your sign it's ready.
5. **Flash for real** once you're committed:
   ```
   python3 eps-update.py rwd/REPLACE_WITH_YOUR_FIRMWARE.rwd -b 1 --danger
   ```
   You'll see warnings/errors on the dash while it flashes — that's normal. When
   it reaches "Resetting ECU" with no traceback, turn the car off. Done.

Example:
```
python3 eps-update.py rwd/39990-TLA-A040-linear-max.rwd -b 1 --danger
```

### `--skip-checksum` (not recommended)
If a firmware isn't covered by the checksum checker, you can add `--skip-checksum`.
**Be careful — flashing a `.rwd` with invalid checksums can brick the EPS.** Only
use it on an image you trust.
```
python3 eps-update.py rwd/SOME_FIRMWARE.rwd -b 1 --skip-checksum --danger
```

## Verify it worked
Turn the car back on and move the wheel by hand — any power-steering assist means
the flash succeeded. To confirm over CAN:
```
python3 eps-diag.py -b 1
```

## If a flash fails / crashes
Don't panic — **the EPS is not permanently bricked.** The flash erases before it
writes, so a crash mid-flash leaves the EPS erased: no power-steering assist until
it's flashed properly. Just run the same `--danger` command again; you may need to
power-cycle the car and/or the comma a few times before it lets you redo a failed
flash. Keep a verified `stock` `.rwd` on hand as the recovery image.

**Flash from a persistent copy** (e.g. `/data/media/0/eps_tools/`), not from
`/data/openpilot` — the comma updater deletes untracked files there, which could
pull the image/parser out from under a flash.

## Validate an image offline
```
python3 check_rwd.py rwd/39990-TLA-A040-linear-max.rwd
python3 check_rwd.py rwd/*.rwd
```

See `rwd/README.md` for the firmware images and upstreaming guidelines (a mod may
only be added alongside a verified stock recovery image).
