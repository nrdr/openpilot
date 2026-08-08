#!/usr/bin/env python3
"""
Guided EPS flash helper.

Steps it runs for you:
  1. Reads the car's current EPS firmware, scans .rwd images (in rwd/ and next to
     this script), and shows only ones compatible with your EPS — pre-validating
     each with check_rwd.py (flags any that fail). If none are compatible (or the
     car isn't fingerprinted yet), it asks before listing all images.
  2. Shows a numbered list; you pick one.
  3. Confirms the car is OFF, then stops openpilot (frees the panda), then
     prompts you to switch the car to accessory mode (ignition ON, engine OFF).
  4. Auto-detects the EPS CAN bus via live UDS probe of the selected .rwd's
     address (asks if ambiguous) unless --bus was passed.
  5. Offers a dry run (recommended) or skip (not recommended); --skip-dry-run
     bypasses that prompt. Confirms dry run reaches the safe abort when run.
  6. Asks for explicit confirmation (FLASH), then runs the real flash (--danger).
     On failure, offers retry (menu choice is enough — no second FLASH prompt).
  7. Post-flash menu: run eps-diag.py (loops back here), restore openpilot, or
     reboot the device.

Security-access delay: the EPS refuses the seed request with NRC 0x37 while its
delay timer runs (e.g. a settling window after power-up). Normal `flash.py` runs
handle this for you — eps-update.py retries the seed on a slow interval, and if the
default window elapses the dry run just asks whether to keep waiting. No flag needed.
--seed-timeout is only for unattended runs: it pins the window and skips that prompt.

Run from the eps_tools/ folder on the comma:
  python3 flash.py                     # normal use — auto bus + auto seed retry
  python3 flash.py --bus 0             # pin to a bus
  python3 flash.py --skip-dry-run      # skip dry-run prompt + dry run (not recommended)
  python3 flash.py --seed-timeout 600  # unattended: wait up to 10 min, no keep-waiting prompt
"""
import argparse
import contextlib
import glob
import io
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RWD_DIR = os.path.join(HERE, "rwd")
EPS_UPDATE = os.path.join(HERE, "eps-update.py")
DRY_RUN_OK_MARKER = "Safe mode: aborting before mutating actions"
REAL_CLIENT_MARKER = "Using real client"
# Printed by eps-update.py when the security-access seed stayed refused for the
# whole --seed-timeout window.
SEED_LOCKOUT_MARKER = "still refused"
# Normal-use seed-retry window (mirrors eps-update.py's DEFAULT_SEED_TIMEOUT_S) and
# how much longer each interactive "keep waiting?" extension waits.
DEFAULT_SEED_TIMEOUT_S = 120.0
SEED_EXTEND_S = 300.0
EPS_ADDR = 0x18DA30F1
DEFAULT_BUS = 1
PROBE_BUSES = (0, 1)

sys.path.insert(0, HERE)
import check_rwd  # noqa: E402  (reuse the validated checksum logic)


def subprocess_env():
    """opendbc/panda live in the openpilot root; rwd_format lives next to the script."""
    env = os.environ.copy()
    paths = [HERE, os.path.dirname(HERE)]
    if os.path.isdir("/data/openpilot"):
        paths.append("/data/openpilot")
    if env.get("PYTHONPATH"):
        paths.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(paths)
    return env


def validate(path):
    """True if the image passes check_rwd (run quietly)."""
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return bool(check_rwd.check(path))
    except Exception:
        return False


def find_images():
    files = set(glob.glob(os.path.join(RWD_DIR, "*.rwd")))
    files |= set(glob.glob(os.path.join(HERE, "*.rwd")))
    return sorted(files)


def norm_fw(s):
    """Normalize a part number for matching: '-'/',' interchangeable, strip NULs/space."""
    if isinstance(s, (bytes, bytearray)):
        s = bytes(s).decode("latin-1", "replace")
    return s.replace("-", ",").strip("\x00").strip()


def car_eps_fw():
    """EPS firmware string from CarParamsPersistent / CarParams, or None.

    Same source the nrdr settings UI uses: the EPS entry in CarParams.carFw.
    (Do not use CarFw.bus — Cap'n Proto UInt8 defaults to 0 when unset.)
    """
    try:
        from cereal import car
    except Exception:
        if os.path.isdir("/data/openpilot"):
            sys.path.append("/data/openpilot")
        try:
            from cereal import car
        except Exception:
            return None
    for p in ("/data/params/d/CarParamsPersistent", "/data/params/d/CarParams"):
        try:
            data = open(p, "rb").read()
        except OSError:
            continue
        try:
            with car.CarParams.from_bytes(data) as CP:
                for fw in CP.carFw:
                    if fw.ecu == "eps":
                        v = bytes(fw.fwVersion).decode("latin-1", "replace").strip("\x00").strip()
                        if v:
                            return v
        except Exception:
            continue
    return None


def rwd_supported_versions(path):
    """Normalized set of part numbers an .rwd supports (its header[3]); None if unparseable."""
    try:
        from rwd_format.x5a import x5a
        fw = x5a(open(path, "rb").read())
        return {norm_fw(bytes(v.value)) for v in fw.file_headers[3].values}
    except Exception:
        return None


def rwd_can_address(path):
    """UDS tester address from the .rwd (same as eps-update.get_can_address); None if unparseable."""
    try:
        import struct
        from rwd_format.x5a import x5a
        fw = x5a(open(path, "rb").read())
        return 0x18da00f1 | struct.unpack('!B', fw.file_headers[2].values[0].value)[0] << 8
    except Exception:
        return None


def probe_eps_buses(addr):
    """Live-probe buses 0/1 for Tester Present at addr. Return responding bus list.

    A negative UDS response still means the ECU is on that bus (same as eps-diag).
    """
    try:
        from panda import Panda
        from opendbc.car.structs import CarParams
        from opendbc.car.uds import UdsClient, NegativeResponseError
    except Exception as e:
        print(f"  Live bus probe unavailable ({e})")
        return []

    panda = None
    try:
        panda = Panda(disable_checks=True)
        panda.set_safety_mode(CarParams.SafetyModel.elm327)

        alive = []
        for bus in PROBE_BUSES:
            uds = UdsClient(panda, addr, bus=bus, timeout=1.5)
            try:
                uds.tester_present()
                alive.append(bus)
                print(f"  EPS responded on bus {bus}")
            except NegativeResponseError as e:
                alive.append(bus)
                print(f"  EPS on bus {bus} (negative response: {e})")
            except Exception:
                print(f"  No EPS response on bus {bus}")
        return alive
    except Exception as e:
        print(f"  Live bus probe: could not open/configure Panda ({e})")
        return []
    finally:
        # Always release USB so eps-update can open the Panda for dry run / flash.
        if panda is not None:
            try:
                panda.close()
            except Exception:
                pass


def ask_pick_bus(choices, default):
    """Prompt for a bus from choices. Empty input selects default."""
    choices = list(choices)
    if default not in choices:
        default = choices[0]
    label = "/".join(str(b) for b in choices)
    while True:
        raw = input(f"Select bus to flash [{label}] (default {default}): ").strip()
        if raw == "":
            return default
        try:
            bus = int(raw, 0)
        except ValueError:
            print("  Enter a bus number.")
            continue
        if bus not in choices:
            print(f"  Pick one of: {label}")
            continue
        return bus


def resolve_bus(cli_bus, rwd_path):
    """Pick the flash bus: --bus override, else live probe, else ask the user."""
    if cli_bus is not None:
        print(f"Using bus {cli_bus} (--bus override)")
        return cli_bus

    addr = rwd_can_address(rwd_path)
    if addr is None:
        addr = EPS_ADDR
        print(f"Could not read CAN address from .rwd — probing default 0x{addr:08X}")
    else:
        print(f"Probing for EPS bus (UDS 0x{addr:08X} from selected .rwd) ...")

    alive = probe_eps_buses(addr)
    if len(alive) == 1:
        print(f"Detected EPS on bus {alive[0]}")
        return alive[0]

    if len(alive) > 1:
        print(f"EPS responded on multiple buses: {', '.join(str(b) for b in alive)}")
        # Prefer the usual Honda default when both look alive (gateway echo, etc.).
        default = DEFAULT_BUS if DEFAULT_BUS in alive else alive[0]
        return ask_pick_bus(alive, default=default)

    print("Live probe found no EPS response on buses 0 or 1.")
    return ask_pick_bus(list(PROBE_BUSES), default=DEFAULT_BUS)


def stop_openpilot():
    # Stop the managed service and tear down the comma tmux session so openpilot
    # cannot respawn and reclaim the panda. Do NOT `pkill -f openpilot` — that
    # matches this script's argv when launched from a path containing "openpilot".
    print("Stopping openpilot to free the panda ...")
    subprocess.run(["sudo", "systemctl", "stop", "comma"], check=False)
    subprocess.run(
        ["tmux", "kill-session", "-t", "comma"],
        check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(2)
    status = subprocess.run(
        ["systemctl", "is-active", "comma"],
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    if status in ("active", "activating", "deactivating", "reloading"):
        sys.exit(
            f"Failed to stop openpilot (comma service is '{status}'). "
            "Run `sudo systemctl stop comma` manually and retry."
        )
    print("  done.\n")


def run_eps_update(rel_path, bus, skip_checksum, danger, seed_timeout=None):
    cmd = [sys.executable, EPS_UPDATE, rel_path, "-b", str(bus)]
    if skip_checksum:
        cmd.append("--skip-checksum")
    if danger:
        cmd.append("--danger")
    if seed_timeout is not None:
        cmd += ["--seed-timeout", str(seed_timeout)]
    return cmd


def restore_openpilot():
    print("\nRestoring openpilot (restarting the comma service) ...")
    subprocess.run("tmux kill-session -t comma 2>/dev/null; sudo systemctl restart comma",
                   shell=True, check=False)
    print("  Requested restart — openpilot should come up in ~30s. If not, reboot.")


def reboot_device():
    print("\nRebooting ...")
    subprocess.run(["sudo", "reboot"], check=False)


def exit_with_op_stopped(msg):
    """Abort after stop_openpilot(); offer to restore so the device isn't left dead."""
    print(msg)
    print("\nNote: openpilot is still stopped.")
    if input("Restore openpilot now? type 'yes': ").strip().lower() == "yes":
        restore_openpilot()
    else:
        print("Restore later with: sudo systemctl restart comma (or reboot).")
    sys.exit(1)


def post_flash_menu(env, bus, eps_addr=None):
    """After a flash: optionally run eps-diag (loops back), restore op, or reboot."""
    diag = os.path.join(HERE, "eps-diag.py")
    while True:
        print("\nWhat next?")
        print("  [1] Run eps-diag.py  — post-flash EPS check (returns here after)")
        print("  [2] Restore openpilot — it was stopped for flashing")
        print("  [3] Reboot the device (sudo reboot)")
        choice = input("Select 1/2/3 (q = leave openpilot stopped and exit): ").strip().lower()
        if choice == "1":
            print()
            # Pin to the bus/address we just flashed so the check matches the flash path.
            cmd = [sys.executable, diag, "-b", str(bus)]
            if eps_addr is not None:
                cmd += ["--addr", hex(eps_addr)]
            subprocess.run(cmd, env=env, cwd=HERE)
        elif choice == "2":
            restore_openpilot()
            return
        elif choice == "3":
            reboot_device()
            return
        elif choice in ("q", "quit", ""):
            print("Leaving openpilot stopped. Restore later with: sudo systemctl restart comma (or reboot).")
            return
        else:
            print("  Invalid choice — pick 1, 2, or 3.")


def choose_dry_run(skip_dry_run_flag):
    """Return True if a dry run should run. Flag bypasses the in-script prompt."""
    if skip_dry_run_flag:
        print("\nSkipping dry run (--skip-dry-run). Not recommended.")
        return False
    print("\nDry run validates the image and security flow, then aborts before erase.")
    print("Some EPS units lock security access after a dry run; skip only if you need to.")
    print("  [1] Run dry run first (recommended)")
    print("  [2] Skip dry run (not recommended)")
    choice = input("Select 1/2 [1]: ").strip() or "1"
    if choice == "2":
        print("Skipping dry run (not recommended).")
        return False
    if choice != "1":
        print("  Invalid choice — running dry run.")
    return True


def run_and_tee(cmd, env):
    """Run cmd, printing output as it arrives while capturing it for marker checks.

    The seed request can retry for minutes against an EPS security lockout, so the
    output has to stream — a captured run looks like a hang.
    """
    proc = subprocess.Popen(cmd, env=env, cwd=HERE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    lines = []
    for line in proc.stdout:
        print(line, end="", flush=True)
        lines.append(line)
    proc.wait()
    return proc.returncode, "".join(lines)


def run_dry_run(rel, bus, skip_checksum, env, name, seed_timeout=None):
    # seed_timeout None = normal use: fall back to eps-update.py's own default and
    # let an interactive lockout be handled by prompting to keep waiting, so plain
    # `flash.py` never needs a flag. An explicit --seed-timeout pins the window and
    # skips the prompt (for unattended runs).
    interactive = seed_timeout is None
    effective = DEFAULT_SEED_TIMEOUT_S if seed_timeout is None else seed_timeout
    while True:
        print(f"\n=== DRY RUN: {name} (validates + auth flow, stops before erase) ===\n")
        _, combined = run_and_tee(
            run_eps_update(rel, bus, skip_checksum, danger=False, seed_timeout=effective), env)
        # Mock UDS client also reaches the safe-abort marker; require a real Panda.
        if REAL_CLIENT_MARKER not in combined:
            exit_with_op_stopped(
                "\nDry run did NOT talk to a real Panda/EPS (mock client) — NOT flashing. "
                "Fix the Panda connection and retry."
            )
        if SEED_LOCKOUT_MARKER in combined:
            print(f"\nThe EPS security-access delay hasn't cleared after {effective:.0f}s.")
            print("This is the ECU's delay timer, not a bad image — waiting is the fix.")
            if interactive and input(
                    f"Keep waiting another {SEED_EXTEND_S:.0f}s? [Y/n]: ").strip().lower() in ("", "y", "yes"):
                effective = SEED_EXTEND_S
                continue
            exit_with_op_stopped(
                "\nStopping while the EPS delay is still active — NOT flashing.\n"
                "Leave the car in accessory mode (ignition off restarts the timer) and re-run."
            )
        if DRY_RUN_OK_MARKER not in combined:
            exit_with_op_stopped(
                "\nDry run did NOT reach the safe abort point — NOT flashing. Review the output above."
            )
        break
    print("Dry run OK — real client + safe abort (the traceback above is expected for a dry run).")
    print("Note: some EPS units lock security access briefly after a dry run.")
    print("If the real flash fails with a security/timeout error, wait or power-cycle, then retry.")


def run_real_flash(rel, bus, skip_checksum, env, name, seed_timeout=None):
    print(f"\n=== FLASHING: {name} (bus {bus}) ===\n")
    return subprocess.run(run_eps_update(rel, bus, skip_checksum, danger=True, seed_timeout=seed_timeout),
                          env=env, cwd=HERE).returncode


def flash_failure_menu(rel, bus, skip_checksum, env, name, rc, seed_timeout=None):
    """After a failed flash: retry (--danger only) or continue to post-flash menu.

    Choosing retry is enough confirmation — no second FLASH prompt.
    Returns the final return code.
    """
    while rc != 0:
        print(f"\nFlash process exited ({rc}).")
        print("FLASH FAILED or incomplete — EPS may need a recovery re-flash.")
        print("A security lockout after a dry run is common on some cars:")
        print("  wait a bit, power-cycle the car (OFF → accessory), then retry.")
        print("  [r] Retry flash (--danger only, no dry run)")
        print("  [m] Continue to post-flash menu")
        print("  [q] Quit (leave openpilot stopped)")
        choice = input("Select r/m/q: ").strip().lower()
        if choice == "r":
            rc = run_real_flash(rel, bus, skip_checksum, env, name, seed_timeout)
            if rc == 0:
                print(f"\nFlash process exited ({rc}).")
                print("Flash reported success (exit 0).")
                return rc
            continue
        if choice == "m":
            print("Continuing to post-flash menu without a successful flash.")
            return rc
        if choice in ("q", "quit"):
            exit_with_op_stopped("Leaving after failed flash — openpilot is still stopped.")
        print("  Invalid choice — pick r, m, or q.")
    return rc


def main():
    ap = argparse.ArgumentParser(description="Guided EPS flash helper")
    ap.add_argument("-b", "--bus", type=int, default=None,
                    help="CAN bus number (default: auto-detect; fallback 1)")
    ap.add_argument("--skip-dry-run", action="store_true",
                    help="Skip the dry-run prompt and dry run (not recommended)")
    ap.add_argument("--seed-timeout", type=float, default=None,
                    help="Seconds to keep retrying the security-access seed request while the "
                         "EPS reports a delay/lockout (passed to eps-update.py)")
    args = ap.parse_args()

    images = find_images()
    if not images:
        sys.exit(f"No .rwd files found in {RWD_DIR} or {HERE}")

    # Filter to images compatible with the car's current EPS firmware.
    car_fw = car_eps_fw()
    car_norm = norm_fw(car_fw) if car_fw else None
    if car_norm:
        print(f"Detected EPS firmware: {car_fw}")
        compatible = [f for f in images if (sv := rwd_supported_versions(f)) and car_norm in sv]
        if compatible:
            hidden = len(images) - len(compatible)
            extra = f"  ({hidden} incompatible image(s) hidden)" if hidden else ""
            print(f"Showing firmware compatible with your EPS{extra}:\n")
            shown = compatible
        else:
            print(f"\n!! No .rwd here is compatible with your EPS ({car_fw}).")
            if input("   Show ALL images and continue anyway? type 'yes': ").strip().lower() != "yes":
                sys.exit("Aborted.")
            print("\nAll firmware (compatibility NOT guaranteed — pre-validated):\n")
            shown = images
    else:
        print("Could not read the car's EPS firmware (not fingerprinted yet?). Showing all images.\n")
        shown = images

    rows = []
    for i, f in enumerate(shown):
        ok = validate(f)
        rows.append((f, ok))
        status = "valid ✓" if ok else "INVALID ✗  -> will need --skip-checksum (brick risk)"
        print(f"  [{i + 1:>2}] {os.path.basename(f):<44} {status}")

    sel = input("\nSelect a firmware number to flash (q to quit): ").strip()
    if sel.lower() in ("", "q", "quit"):
        sys.exit("Aborted.")
    try:
        idx = int(sel) - 1
    except ValueError:
        sys.exit("Invalid selection.")
    # Reject 0 and out-of-range: int("0")-1 == -1 would silently pick the last row.
    if idx < 0 or idx >= len(rows):
        sys.exit("Invalid selection.")
    path, ok = rows[idx]

    rel = os.path.relpath(path, HERE)
    name = os.path.basename(path)
    skip_checksum = not ok

    if not ok:
        print(f"\n!! {name} FAILED checksum validation.")
        print("!! It can only be flashed with --skip-checksum. A bad image can BRICK the EPS.")
        if input("   Type 'yes' to continue with this unvalidated image: ").strip().lower() != "yes":
            sys.exit("Aborted.")

    # Power sequence: kill openpilot with the car OFF, then switch to accessory
    # mode — so openpilot doesn't re-grab the panda when CAN comes alive.
    if input("\nConfirm the car is fully OFF (ignition off) — type 'yes': ").strip().lower() != "yes":
        sys.exit("Aborted — turn the car off first, then re-run.")
    stop_openpilot()
    input("Now switch the car to ACCESSORY mode (ignition ON, engine OFF, A/C off).\n"
          "Press Enter when the dash is on and ready: ")

    bus = resolve_bus(args.bus, path)
    eps_addr = rwd_can_address(path)
    env = subprocess_env()

    if choose_dry_run(args.skip_dry_run):
        run_dry_run(rel, bus, skip_checksum, env, name, args.seed_timeout)

    print(f"\n=== READY TO FLASH: {name} (bus {bus}) ===")
    print("Make sure the car is in accessory mode (ignition ON, engine OFF, A/C off).")
    print("If it crashes mid-flash, the EPS is recoverable: just run this again.")
    if input("Type 'FLASH' to commit the real flash (--danger): ").strip() != "FLASH":
        exit_with_op_stopped("Aborted — no flash performed.")

    rc = run_real_flash(rel, bus, skip_checksum, env, name, args.seed_timeout)
    if rc == 0:
        print(f"\nFlash process exited ({rc}).")
        print("Flash reported success (exit 0).")
    else:
        rc = flash_failure_menu(rel, bus, skip_checksum, env, name, rc, args.seed_timeout)

    post_flash_menu(env, bus, eps_addr=eps_addr)
    sys.exit(rc)


if __name__ == "__main__":
    main()
