# Honda EPS firmware library

The [shared Google Drive library](https://drive.google.com/drive/folders/1Z4_axffop928ep2CAmaApmTjdKUQV4xW)
is the primary source of truth for firmware supplied by nrdr, unless the owner
explicitly specifies otherwise. The [Honda EPS status sheet](https://docs.google.com/spreadsheets/d/1edkzOjTJfXRjE9v0nHh0uVFfhPFSkYnI3sg0oVliRkU/edit)
links to these vehicle folders. Repository/controller reference hashes are not
authority to replace a Drive image with a different tune.

The November 15, 2026 audit checked all 17 vehicle folders and their PTM/stock
categories. [SOURCES.md](SOURCES.md) records the 30 downloaded current PTM/stock
artifacts, exact source links, and remaining discrepancies. [SHA256SUMS](SHA256SUMS)
pins those 53 artifacts and the separately owner-supplied Clarity AnglePTM build 05.

## Guided catalog

Run `python3 flash.py` over SSH from the repository root. The command-line helper offers an explicit
24-image menu: 11 PTM images and 13 stock-recovery images, filtered by the EPS
software IDs in each container. Old C020 and Clarity files remain stored but are
no longer menu choices. A valid checksum and matching header are not proof of
vehicle/controller compatibility.

| EPS family | Current PTM choice | Stock choices |
| --- | --- | --- |
| TBA-A030 Civic | Drive replacement, `55c37266` | 1 |
| TBA-C020 Civic | Drive replacement, `df67bf6f` | 1 |
| TBA-C120 Civic | Drive `15e63414`; controller-reference mismatch | 1 |
| TEG-A010 Civic | Drive `80fbd0e0`; controller-reference mismatch | None available |
| TGG-A020 Civic | No PTM file in Drive | 1 |
| TGG-A120 Civic | Added `6640806d` | 1 |
| TLA-A040 CR-V | Drive `26f5390b`; controller-reference mismatch | 1 |
| TLA-A220 CR-V | Added `2c992997` | 1 |
| TRW-A020 Clarity | ClarityMax September PTM (`9e2e9885`); separate AnglePTM 20261118 build 05 (`1fbf3b63`) | 1 |
| TXM-A040 Insight | Drive `833a41bf`; controller-reference mismatch | 1 |
| THR-A020 Odyssey | No PTM file in Drive | 1 added |
| TJB-A220 RDX | Added `68a6fdb4`; runtime PTM admission remains disabled | 2 added |
| TG7-A060 Pilot | No PTM file in Drive | 1 |

Missing PTM files are not fabricated or substituted with legacy tunes.

The November 18 AnglePTM image is a manual choice, paired with
[openpilot #34](https://github.com/nrdr/openpilot/pull/34) and
[opendbc #5](https://github.com/nrdr/opendbc/pull/5). Adding it does not flash
the EPS or select angle mode. Its header declares the `39990+TRW+A020` ID as
well as earlier Clarity IDs. The bundled stock and September PTM headers do
**not** declare the plus ID: do not assume they provide a verified rollback
from build 05. Container validation is not a bench test of steering or recovery.

Adding RDX firmware does not enable RDX lateral-control support. The four
controller-reference mismatches and Clarity payload changes need separate
calibration review; no runtime tuning changed in this audit.

## Reference-only files

- **T6Z-A110 Ridgeline:** offline validation supports the original exact
  four-ID profile and the donor's newer header layout. Flashing is still
  rejected: its V850 bootloader requires an FF00/FF01 sequence not implemented
  by this updater. Drive's PTM folder is empty.
- **TG7-A040 Pilot:** downloaded stock image passes offline LE32 validation.
  Its flashing procedure is unverified, so it is not selectable or accepted
  by the updater. Existing TG7-A060 support is retained.
- **TVA-A160/A340 Accord:** stock, PTM and PTM-lite images are retained for
  reference. They use the unsupported `0x31` format; do not feed them to the
  `0x5A` updater.
- **Legacy/testing images, Pilot 2X WIP and raw binaries:** preserved for
  research, excluded from the guided menu.

Drive contains additional legacy files and vehicle-specific scripts. They are
not imported as current PTM firmware, and attachment-provided scripts were not
executed. Current source availability is separate from flashing-protocol support.

## Validation

All 50 RWD containers pass their outer file checksum. All 43 `0x5A`
containers pass the applicable internal checks; the seven `0x31` references
are intentionally rejected. Three raw binaries are not RWD containers.

The offline checker, command-line helper and updater share validation from
[check_rwd.py](../check_rwd.py). This includes SH2A word sums, THR/TJB ROM CRCs
and monitor shadows, and the existing Pilot/T6Z LE32 layouts. Unknown layouts,
malformed containers and bad checksums fail before Panda access.
`--skip-checksum` no longer bypasses validation.

Quote paths containing spaces:

```bash
python3 check_rwd.py "rwd/39990-TRW-A020 (Honda Clarity)/Proper Torque Mod/ClarityMax-PTM-Latest-092826.rwd"
python3 check_rwd.py "rwd/**/*.rwd"
```

The recursive command includes unsupported Accord references, so its overall
nonzero exit is expected. Offline checks do not validate live flashing or
on-car steering performance.

## Adding or updating firmware

Use the Drive source unless explicitly directed otherwise. Preserve the exact
bytes, record the source link in `SOURCES.md` and full hash in `SHA256SUMS`,
and update the matching test fixtures. Changing an extension for discovery is
acceptable; modifying the payload is not part of catalog maintenance.
Adding a file to `GUIDED_FLASH_FILES` also requires supported validation,
EPS identity/seed lookup and an applicable flashing procedure.

The original historical import came from
`Modded Honda RWDs-20260828T042240Z-1-001.zip`
(SHA-256 `b36446d02ee5f67250495528881a2ea239c3df3a40b0c463be7bc9d9a9f8721b`).
Those retained files are references, not a newer source than Drive.
