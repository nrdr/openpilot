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
  flash.py          guided flash: stop op -> pick image -> dry run -> --danger
  eps-update.py     UDS .rwd flasher (validate + erase/program over CAN)
  check_rwd.py      offline .rwd checksum validator (stdlib only)
  eps-diag.py       EPS CAN liveness/diagnostic (sniff, UDS ping, part number)
  rwd_format/       vendored Python-3 .rwd container parser (0x5A/0x31)
  rwd/              checksum-validated firmware images + upstreaming guidelines
```

Run the scripts **from this folder** so `rwd_format` resolves; `opendbc`/`panda`
come from the openpilot install (prefix with `PYTHONPATH=/data/openpilot` if you
hit import errors).

## Guided flash (recommended)

`flash.py` walks the whole thing for you: reads the car's current EPS firmware
and lists only the `.rwd` images compatible with it (with their checksum status),
lets you pick one, auto-detects the EPS CAN bus via a live UDS probe of the
selected image's address (asks if more than one bus responds), offers a dry run,
and only flashes after you confirm. If nothing matches your EPS (or the car isn't
fingerprinted yet) it asks before listing all images. Images that fail validation
are flagged and flashed with `--skip-checksum` (with an extra warning).

```bash
cd eps_tools
python3 flash.py                 # auto-detect bus (fallback default 1)
python3 flash.py --bus 0         # pin to a bus
python3 flash.py --skip-dry-run  # skip dry-run prompt + dry run (not recommended)
python3 flash.py --seed-timeout 600  # wait up to 10 min for a security lockout to clear
```

It confirms the car is OFF, stops openpilot, then prompts you to switch to
accessory mode (ignition ON, engine OFF) before bus detect / dry run / flash.

**Dry run:** by default you get an in-script choice — run dry run first
(recommended) or skip (not recommended). Some EPS units lock security access
after a dry run; if the real flash then fails with a timeout/security error,
`flash.py` offers a retry menu (choosing retry is enough — no second `FLASH`
prompt). `--skip-dry-run` bypasses the prompt and skips the dry run entirely.

After the flash it offers a menu: run `eps-diag.py` as a post-flash check (which
loops back to the menu), restore openpilot (it was stopped for flashing), or
reboot. The manual steps below are the same flow if you'd rather run each
command yourself.

## How to flash (manual)

1. Make sure the comma power is connected to the car's OBD2 port.
2. With the car **OFF**, stop openpilot over SSH:
   ```
   pkill -f openpilot
   ```
3. Put the car in full **accessory mode** (ignition ON, engine OFF). Turn off the
   A/C to avoid draining the battery.
4. **Dry run first** — validates the image and walks the UDS/security flow but
   aborts *before* any mutating action (`eps-update.py` defaults to bus **1**):
   ```
   cd eps_tools
   python3 eps-update.py rwd/REPLACE_WITH_YOUR_FIRMWARE.rwd -b 1
   ```
   When it aborts before performing mutating actions, that's your sign it's ready.
   **Note:** some cars lock security access after a dry run. If the real flash
   then fails, wait / power-cycle (OFF → accessory) and retry `--danger`, or skip
   the dry run on a subsequent attempt. See
   [Security-access lockout](#security-access-lockout-nrc-0x37) below.
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

`eps-update.py` is the power-user flasher: you pass `-b` explicitly (default **1**).
Bus auto-detect lives only in `flash.py`.

### Security-access lockout (NRC 0x37)

If a run dies with:

```
NegativeResponseError: SECURITY_ACCESS - required time delay not expired
```

the image and the CAN setup are fine — reading the software ID and entering the
extended session already succeeded. The EPS is refusing to hand out an unlock
seed because its security-access delay timer is running (typically a settling
window enforced after power-up).

**You do not need any flags for this.** A normal `flash.py` run already retries:
`eps-update.py` re-requests the seed every 10s for up to 120s and reports how long
the unlock took (so you learn your car's actual delay), and if 120s isn't enough
the dry run simply asks whether to keep waiting another 5 minutes:

```
The EPS security-access delay hasn't cleared after 120s.
This is the ECU's delay timer, not a bad image — waiting is the fix.
Keep waiting another 300s? [Y/n]:
```

`--seed-timeout N` is only for **unattended** runs (no operator to answer that
prompt): it pins the retry window to N seconds and skips the keep-waiting question.

```
python3 flash.py --seed-timeout 600                        # scripted, 10-min window
python3 eps-update.py rwd/YOUR_FIRMWARE.rwd -b 1 --seed-timeout 600  # raw flasher
```

Leave the car in accessory mode while it retries; turning the ignition off
restarts the timer. Only the *seed request* is retried — a rejected seed request
doesn't touch the attempt counter, but re-sending a **key** (NRC 0x35, invalid
key) increments it and restarts the delay, so that error is never retried.

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
python3 eps-diag.py          # checks buses 0 and 1 by default
python3 eps-diag.py -b 1     # pin to one bus
```

`eps-diag.py` reports which bus saw EPS activity and the detected part number when
available. For recovery it points you back to `flash.py` and choosing the **stock**
image for your EPS (it does not invent a specific `.rwd` filename).

## If a flash fails / crashes
Don't panic — **the EPS is not permanently bricked.** The flash erases before it
writes, so a crash mid-flash leaves the EPS erased: no power-steering assist until
it's flashed properly. Just run the same `--danger` command again (or retry from
`flash.py`'s failure menu); you may need to power-cycle the car and/or the comma a
few times before it lets you redo a failed flash. Keep a verified `stock` `.rwd`
on hand as the recovery image.

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
