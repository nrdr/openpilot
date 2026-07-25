# nrdr / Honda openpilot — session handoff summary

## Who / project
- User: Brett (Discord "Aragon"). Maintains the **nrdr** openpilot/sunnypilot fork for Honda; ~6 years building the Honda community's EPS tooling.
- Cars: **Honda Clarity** (EPS `39990-TRW,A020`) and **2019 Honda Pilot Elite** (Nidec **V850** EPS `39990-TG7-A060`).
- Two comma devices in play: `comma-dd52d2a3` (AGNOS v11, used for the EPS flash) and `comma-7f347b24` (used Comma 3X, AGNOS v18.4 — the registration saga device).
- PC repos: `C:\Openpilot Workspace\openpilot` (superproject; `opendbc` is a symlink → `opendbc_repo/opendbc` submodule) and a separate clone `C:\Openpilot 2026\opendbc\opendbc`.

## Big wins this session
1. **First-ever V850 EPS firmware flash on the Pilot (TG7-A060)** — dumped, verified, patched (~2× LKAS authority + steer-to-standstill), dry-ran, flashed with `--danger`. Success.
2. **Fixed device registration** on the used Comma 3X across **Konik** (drives/device mgmt) and **Sunnylink** (settings sync) — ultimately by regenerating the device key.

## EPS firmware flash — reusable workflow (Nidec V850, TG7-A060)
Tools live in the openpilot tree; **`eps-update.py` is the EPS flasher** (NOT `honda-ecu-update.py`, which targets a TriCore/AURIX engine ECU — 4MB @ 0x80000000, CVN-based; wrong tool for EPS).

1. **Dump** (read-only). Runs on the comma over SSH. `pkill -f openpilot` FIRST (boardd owns the panda / floods the bus → timeouts):
   `python3 tools/uds-tool.py --can-id 0x30 --start-address 0x10000 --end-address 0x5FFFF --output /data/media/0/TG7-A060_stock.bin --bus 1`
   - Bus: **OBD2 = `--bus 1`**, camera-harness = bus 0 (EPS is on F-CAN; both reach it). `0x30` → CAN `0x18DA30F1`.
   - EPS imposes a **security lockout** ("required time delay not expired") after repeated failed attempts — wait / power-cycle.
   - I added a `tqdm` progress bar to `uds-tool.py` (it was silent; buffers whole image in RAM, writes only on success).
2. **Verify the dump**: 327,680 bytes (0x50000); internal checksums sum to 0 at block ends 0xA000/0x1D000/0x4FF00; app-id `39990-TG7-A060` present at 0x3438; patch-site "old" bytes match stock. (All passed.)
3. **Patch/wrap** with `tools/bin_to_rwd.py` — run **from the `tools/` dir** (it does `__import__("rwd-builder")`, resolves only there). Outputs land next to the input (`<name>.bin.enc`, `<name>.bin.rwd`); both runs share the output name so **rename between them**:
   - Stock restore: `python3 bin_to_rwd.py --input_bin 39990-TG7-A060_stock.bin --model 39990-TG7-A060` (no `--patch`)
   - Patched: same `+ --patch` (E4 LUT×2 authority + `min_speed` 0x14→0x01 / 0x0a→0x01 across all 5 lane_assist variants). Asserts stock bytes before patching = safety gate; recomputes checksums.
4. **Flash** (on the comma, from the flasher branch; deps `panda.format.x5a` + `tqdm` must be present):
   - Dry run: `python3 eps-update.py <PATCHED>.rwd -b 1` → green light is `Safe mode: aborting before mutating actions`.
   - Real: `... -b 1 --danger`. `pkill -f openpilot`, accessory mode (ign ON/engine OFF), stable power. Watch for `Resetting ECU` (no traceback), then turn car off.
   - Recovery: keep the raw `.bin` + a **stock `.rwd`** (from the no-`--patch` run); reflash it with `--danger` if needed.

## Registration architecture (learned the hard way)
- Device host is `API_HOST` env (`launch_env.sh`/`launch_openpilot.sh`): nrdr default **`https://api.konik.ai`** / `wss://athena.konik.ai`. The class is confusingly named `CommaConnectApi` but defaults to Konik. Clean branch reverts to comma via `build_prebuilt.sh`.
- **Konik** (`api.konik.ai` / dashboard `stable.konik.ai`) and **Sunnylink** (`stg.api.sunnypilot.ai`, staging) are **separate backends with separate dongles**. Konik = drives/device mgmt; Sunnylink = settings backup/sync (GitHub-paired).
- Pairing QR **bug**: `selfdrive/ui/widgets/pairing_dialog.py:38` (and `mici/widgets/pairing_dialog.py:36`) hardcode `https://connect.comma.ai/?pair={token}` — should be `stable.konik.ai/?pair={token}` (or a `CONNECT_HOST` env). Token itself is valid Konik; only the URL host is wrong. Workaround: build the `stable.konik.ai/?pair=<token>` URL manually and open it logged in.

## Used-device registration fix (comma-7f347b24)
- Symptom: Sunnylink "unregistered device"; Konik "bad request"; QR went to Comma Connect.
- Root causes found: (a) the pairing-QR host bug above; (b) a running daemon continuously **re-clobbers `DongleId` to `UnregisteredDevice`** when registration fails — must `pkill -f openpilot` before setting params or they won't stick; (c) an nrdr durable **`/persist/comma/dongle_id` mirror** restores stale dongles on boot; (d) the device's `/persist` RSA key is the **previous owner's**, bound on both backends → Sunnylink 409 "public key already in use."
- Konik fixed first: previous owner unpaired it → device is `173bc9c350a30d5d` ("Nidec Pilot") on the user's Konik account.
- Sunnylink couldn't be freed server-side (staging, no access) and the 173bc… trick 404'd there (separate backend). User chose to sacrifice the Konik identity → **regenerate the device key** (a new, unique key isn't "in use" anywhere).
- **Key regen procedure** (critical facts): openpilot does **NOT** auto-generate the key (`get_key_pair()` only reads `/persist/comma/id_rsa`+`.pub`; deleting = brick). So **write** a new key, don't delete. `/persist` is **read-only** → `sudo mount -o remount,rw /persist` and **verify** `mount | grep /persist` shows `rw` before proceeding (first attempt failed silently because the multi-line paste mangled and /persist stayed `ro`). Steps: remount rw → back up `id_rsa`/`.pub` to `.OLDBAK` → write new RSA-2048 via `cryptography` (private = PKCS#1/TraditionalOpenSSL PEM, public = SubjectPublicKeyInfo PEM) → `chown comma:comma` + `chmod 600/644` → `rm /persist/comma/dongle_id /persist/comma/sunnylink_dongle_id` → remount ro → clear `DongleId`/`SunnylinkDongleId`/`ApiCache_Device` params → reboot. New key → fresh registration on both → **Sunnylink registered**. Reversible via `.OLDBAK`.

## Code changes made this session (in `opendbc_repo` submodule unless noted)
- **honda/carcontroller.py**: pulled in MVL's changes — `brake_pid` → scalar `k_p=0.0, k_i=1.0`; `gas_error` float-wrap; (skipped MVL's `temp_errorlogging`/`temp_errorlogging2` debug channels that hijack `new_actuators.speed`/`torqueOutputCan`). Cruise sub-mode blink retimed (`1000ms→500ms` floor, quantized to the 10 Hz HUD send grid — old 100ms floor aliased). **Driver-override band-aid**: hardcoded `override_allowed = vEgo < 20*MPH_TO_MS`; above 20 mph retain 100% torque and never give way (gates the fade-down `and override_allowed` + adds `or not override_allowed` to `lkas_active`). No new param (precompiled-safe). **Still a local edit — commit/deploy to persist.**
- **honda/interface.py**: removed global `stoppingDecelRate=0.3`; CITY_7G if/else split (Nidec `else`: vEgoStopping 0.5, stoppingDecelRate 0.1, vEgoStarting=vEgoStopping).
- **tools/uds-tool.py** (openpilot repo): added `tqdm` dump progress bar.
- **sunnypilot/sunnylink/settings_ui.json**: broke the 3 learn toggles into a new top-of-section `nrdr_learned` "Learned Parameters" group (needs recompile via `compile_settings_ui.py`).
- Non-code deliverables produced: a multi-message Discord settings reference (`nrdr-discord-info-post.md`), a project masterplan checklist (`nrdr-project-masterplan.md`), an EPS flash runbook.

## Gotchas / lessons (don't repeat)
- Adding a `params_keys.h` key requires rebuilding `params_pyx` or it crash-loops with `UnknownKeyName` — hence hardcoding the 20mph band-aid instead of a new param.
- `pkill -f openpilot` before any panda/UDS work or param writes (boardd interferes).
- `/persist` is read-only; remount rw and verify it actually took.
- The sandbox/mount I used serves stale/NUL-corrupted copies of some files (the `C:\Openpilot 2026` clone especially) — the Read tool / the device are authoritative; git line counts over the mount are noisy (CRLF).
- `honda-ecu-update.py` ≠ `eps-update.py` (engine ECU vs EPS).

## Open items
- Commit/deploy the below-20mph override edit and the MVL carcontroller/interface changes to the branch the device builds from (`git fetch origin <branch> && git merge --ff-only origin/<branch>` to update just that branch on-device; note the updater resets `/data/openpilot` periodically).
- Recompile `settings_ui.json` for the Learned Parameters group.
- Fix the pairing-QR host bug permanently (or add `CONNECT_HOST`).
- Optionally clean up stale `173bc…` Konik/Sunnylink dashboard entries and the `/persist/comma/*.OLDBAK` key backups.
