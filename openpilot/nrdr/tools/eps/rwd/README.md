# Curated Honda EPS firmware library

This directory is the byte-for-byte firmware catalog imported from Brett's
`Modded Honda RWDs-20260828T042240Z-1-001.zip` archive. The outer archive's
SHA-256 is:

```text
b36446d02ee5f67250495528881a2ea239c3df3a40b0c463be7bc9d9a9f8721b
```

The source's model/category layout is preserved here, with trailing whitespace
removed from directory names so the paths work consistently on Windows and the
comma. There are 37 firmware artifacts: 33 named `.rwd` containers, one
extensionless Pilot work-in-progress container, and three raw `.bin` dumps.
`SHA256SUMS` pins every artifact recursively.

## What `flash.py` shows

The guided command deliberately shows only 15 reviewed choices:

- all seven files in a `Proper Torque Mod` directory; and
- eight `.rwd` recovery files whose filename clearly says `stock`.

Those choices are an explicit allowlist in `flash.py`. A valid checksum alone
does not make an old tune appropriate for a car, so files labelled legacy,
linear, max, spike, mod, testing, dated, or work in progress are not added to
the ordinary menu. The nested category path is displayed alongside every menu
choice so similarly named images are not confused.

Run the guided tool from the openpilot root:

```bash
python3 flash.py
```

## Guided catalog

| EPS family | Proper Torque Mod | clearly labelled stock recovery |
| --- | --- | --- |
| TBA-A030 | `Proper Torque Mod/39990-TBA,A030-PTM.rwd` | `Legacy and Stock/stock-39990-TBA-A030.rwd` |
| TBA-C020 | `Proper Torque Mod/39990-TBA,C020-Trk4000-PTM.rwd` | `Legacy and Stock/stock-39990-TBA-C020.rwd` |
| TBA-C120 | `Proper Torque Mod/39990-TBA,C120-PTM.rwd` | `Legacy and Stock/stock-39990-TBA-C120.rwd` |
| TEG-A010 | `Proper Torque Mod/39990-TEG,A010-PTM.rwd` | not present in the archive |
| TG7-A060 Pilot | not present in the archive | `Legacy and Stock/39990-TG7-A060-STOCK.rwd` |
| TGG-A020 | not present in the archive | `Legacy and Stock/stock-39990-TGG-A020-HatchbackSport.rwd` |
| TGG-A120 | not labelled as PTM in the archive | `stock-39990-TGG-A120.rwd` |
| TLA-A040 CR-V | `Proper Torque Mod/39990-TLA-A040_Clarity_FF_tune_telemety_8cf8e537.rwd` | `Legacy and Stock/39990-TLA-A040-stock.rwd` |
| TRW-A020 Clarity | `Proper Torque Mod/ClarityMax-PTM.rwd` | not present in the archive |
| TXM-A040 Insight | `Proper Torque Mod/39990-TXM,A040-PTM.rwd` | `Legacy and Stock/TXM-A040-STOCK.rwd` |

The archive included three empty category slots. No fake file or empty directory
was created for them:

- `39990-TG7-A060 (2019 Honda Pilot)/Proper Torque Mod`
- `39990-TGG-A020/Proper Torque Mod`
- `39990-TRW-A020 (Honda Clarity)/Legacy and Stock`

## Catalogued but not guided or approved for flashing

- **Legacy/testing x5A RWDs:** retained under their source paths for comparison
  and research. They are checksum-valid but are not automatically offered.
- **T6Z-A110:** the offline checker accepts only its exact four-ID group
  (T6Z-A110 plus TG7-A040/A030/A020), CAN address `0x18DA30F1`, all four
  `00 11 00 12 10 20` software secrets, key `01 02 03`, start `0x10000`, length
  `0x50000`, known checksum boundaries, and the decrypted T6Z identity. It
  prints a reference-only notice. The current `eps-update.py` intentionally
  rejects this identity, and `flash.py` never lists it. Offline validation is
  not flash approval.
- **TVA-A160:** the stock and 2x files use the different `0x31` container format.
  They are retained as reference material. `check_rwd.py`, `eps-update.py`, and
  the guided tool do not support or offer them.
- **Pilot 2X work in progress:** retained with its original extensionless name
  under `Work in Progress`; it is never discovered by the guided tool.
- **Raw `.bin` dumps:** retained for research and recovery analysis only. No EPS
  command discovers or flashes raw binaries.

Do not bypass these boundaries just because a file exists in the repository.
Hardware compatibility and a valid recovery procedure must be established
before any reference file becomes a guided choice.

## Integrity and offline validation

All 34 RWD/container artifacts pass their outer little-endian file checksum.
The full offline checker passes all 32 x5A containers: 30 ordinary `.rwd`
files, the one explicitly profiled T6Z `.rwd`, and the extensionless Pilot WIP.
The two x31 files are expected to be rejected by the x5A checker. Raw binaries
are not RWD containers.

Quote nested paths because several directory names contain spaces:

```bash
python3 check_rwd.py "rwd/39990-TBA-C120/Proper Torque Mod/39990-TBA,C120-PTM.rwd"
python3 check_rwd.py "rwd/39990-T6Z-A110/39990-T6Z-A110.rwd"
```

The root and historical `eps_tools/` launchers also expand recursive quoted
patterns such as `rwd/**/*.rwd`. That broad pattern includes the two unsupported
x31 reference files, so a nonzero overall result is expected.

## Deliberately excluded archive files

The following three attachment-borne documents/scripts are not firmware and
were not imported or executed:

- `39990-TVA-A160 (Honda Accord)/Flashing script and instructions via ssh/eps-update-tva.py`
- `39990-TVA-A160 (Honda Accord)/Flashing script and instructions via ssh/ONBOARDING.md`
- `39990-TXM-A040 (2019-2022 Honda Insight)/Legacy and Stock/readme.txt`

The TVA script describes an unverified flashing path outside the safe x5A tool,
and its onboarding text would conflict with the canonical root workflow. The
TXM note refers to a file that is not in the archive.

## Adding another image

Add real files only; never create placeholders for missing firmware. Preserve a
clear model/category path, record the exact SHA-256 in `SHA256SUMS`, validate the
container and decrypted firmware where supported, and document whether it is
guided or reference-only. Adding a file to the guided menu is a separate safety
decision and requires an explicit `GUIDED_FLASH_FILES` entry.
