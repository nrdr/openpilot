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
  4. Runs a dry run (no mutating actions) and confirms it reaches the safe abort.
  5. Asks for explicit confirmation, then runs the real flash (--danger).
  6. Post-flash menu: run eps-diag.py (loops back here), restore openpilot, or
     reboot the device.

Run from the eps_tools/ folder on the comma:
  python3 flash.py            # default CAN bus 1
  python3 flash.py --bus 0
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
    """The car's current EPS firmware string from CarParamsPersistent (None if unavailable).

    Same source the nrdr settings UI uses: the EPS entry in CarParams.carFw,
    captured when openpilot fingerprinted the car."""
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


def run_eps_update(rel_path, bus, skip_checksum, danger):
    cmd = [sys.executable, EPS_UPDATE, rel_path, "-b", str(bus)]
    if skip_checksum:
        cmd.append("--skip-checksum")
    if danger:
        cmd.append("--danger")
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


def post_flash_menu(env, bus):
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
            subprocess.run([sys.executable, diag, "-b", str(bus)], env=env, cwd=HERE)
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


def main():
    ap = argparse.ArgumentParser(description="Guided EPS flash helper")
    ap.add_argument("-b", "--bus", type=int, default=1, help="CAN bus number (default 1)")
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

    env = subprocess_env()

    print(f"\n=== DRY RUN: {name} (validates + auth flow, stops before erase) ===\n")
    res = subprocess.run(run_eps_update(rel, args.bus, not ok, danger=False),
                         env=env, cwd=HERE, capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)
    combined = res.stdout + res.stderr
    # Mock UDS client also reaches the safe-abort marker; require a real Panda.
    if REAL_CLIENT_MARKER not in combined:
        exit_with_op_stopped(
            "\nDry run did NOT talk to a real Panda/EPS (mock client) — NOT flashing. "
            "Fix the Panda connection and retry."
        )
    if DRY_RUN_OK_MARKER not in combined:
        exit_with_op_stopped(
            "\nDry run did NOT reach the safe abort point — NOT flashing. Review the output above."
        )
    print("Dry run OK — real client + safe abort (the traceback above is expected for a dry run).")

    print(f"\n=== READY TO FLASH: {name} ===")
    print("Make sure the car is in accessory mode (ignition ON, engine OFF, A/C off).")
    print("If it crashes mid-flash, the EPS is recoverable: just run this again.")
    if input("Type 'FLASH' to commit the real flash (--danger): ").strip() != "FLASH":
        exit_with_op_stopped("Aborted — no flash performed.")

    print()
    rc = subprocess.run(run_eps_update(rel, args.bus, not ok, danger=True), env=env, cwd=HERE).returncode
    print(f"\nFlash process exited ({rc}).")
    if rc != 0:
        print("FLASH FAILED or incomplete — EPS may need a recovery re-flash.")
        print("Note: a crash / non-zero exit mid-flash is recoverable — re-run flash.py to retry.")
    else:
        print("Flash reported success (exit 0).")

    post_flash_menu(env, args.bus)
    sys.exit(rc)


if __name__ == "__main__":
    main()
