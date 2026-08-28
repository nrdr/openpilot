# Device helpers

This directory owns NRDR's on-device repository helpers. The old paths under
`scripts/` remain as compatibility launchers.

The two helpers intentionally have different behavior:

- `opsync.sh` force-syncs the current branch and every submodule to the remote,
  discards local changes, and restarts the `comma` service.
- `setup_dev_helpers.sh` installs `/data/bin/opsync`, whose command performs a
  normal pull of the current branch and starts openpilot through `tools/op.sh`.

Do not consolidate these policies. The force-sync script is an explicit
recovery action; the installed command is the gentler everyday helper.
