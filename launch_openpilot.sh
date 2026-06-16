#!/usr/bin/env bash
export API_HOST=https://api.konik.ai
export ATHENA_HOST=wss://athena.konik.ai

# DEBUG SSH (mvl-testing throwaway branch ONLY) -- authorize Aragon7777 and enable SSH at the
# very top of boot, before `set -e` and before anything downstream (agnos_init, overlay,
# manager) that can wedge a fresh first boot. sshd is already up at the AGNOS level and reads
# its authorized key from /data/params/d/GithubSshKeys, so writing it here makes a stuck boot
# reachable for log capture. All best-effort; nothing here can block the boot.
# STRIP THIS before any public build (keep it off main/nightly/release).
mkdir -p /data/params/d 2>/dev/null || true
printf '%s' '1'          > /data/params/d/SshEnabled     2>/dev/null || true
printf '%s' 'Aragon7777' > /data/params/d/GithubUsername  2>/dev/null || true
printf '%s' 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC1Dv2NX9FCARm1XlSxe6h7hQG+I7eYqKNub1HRO11wCxFKM8hort9jNx0JQLJQrlWlf551bcH7xQU79Up7n3d0JwTpzIqgOhBRhLSwwHDPMZZUayrwN9YMbIlr6XgAkOIa+r+oSyX102Nf3s8Lfbvm/ZAKTUNHH/K15Q4+KXOrjqyDOtXStjQSaOoluNUpdpCIrng1aBgFwLWl3fiKCopV2pmpxmksvA9nT57vo/CBMlrB8onWZU+jrCyMjLxFQvdtAyuzqs5RLQB3leFOn+pnKbL2+ouTWVCM+iHLgSEW/aV67OT++dcOtWNOz5pO2TOLWwAqcFy23no3qJFw4WsdtVWupSI5++CkHd5IdR1vWRi9l92CA1K92dkLsnGkb0rLntmn7IwvqI2JYfCctcN62/zWnnVJh8p7+eBL+qAHcLRqCuI6pw2QPRhGvG2lN+TVSCMBxZ7PT84OSZmhd9y+gN5fy84GjYvYsrNgXxeglWu4L51FUE85kd27cYXDx5fdEJ1HXWerAE6vBlT/XNt33ZgD2wCAs7MCj8pivw2DSgtDXfTTf+Kl7V24rpoK8l1/f1QPHcU4/aW7Tad2t3bQkmmemIYtP+7HjXtaPjTaEsfhmCWpxlTKZeefrzNQpg1ZCr7BqoAaHKJWmQKqgiP6oUIZkwS9PdC8coRSJxk6Hw==' > /data/params/d/GithubSshKeys 2>/dev/null || true
sudo systemctl start ssh 2>/dev/null || sudo systemctl start sshd 2>/dev/null || true

set -euo pipefail
IFS=$'\n\t'

# On any failure, run the fallback launcher
trap 'exec ./launch_chffrplus.sh' ERR
C3_LAUNCH_SH="./sunnypilot/system/hardware/c3/launch_chffrplus.sh"

MODEL="$(tr -d '\0' < "/sys/firmware/devicetree/base/model")"
export MODEL

if [ "$MODEL" = "comma tici" ]; then
  # Force a failure if the launcher doesn't exist
  [ -x "$C3_LAUNCH_SH" ] || false

  # If it exists, run it
  exec "$C3_LAUNCH_SH"
fi

if is_device_runtime; then
  # Recreate local developer helpers after branch switches, reinstalls, or factory resets.
  if [[ -f "${DIR}/scripts/setup_dev_helpers.sh" ]]; then
    bash "${DIR}/scripts/setup_dev_helpers.sh" || true
  fi

  exec ./launch_chffrplus.sh "$@"
fi

exec ./launch_chffrplus.sh
