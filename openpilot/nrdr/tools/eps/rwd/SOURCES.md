# Google Drive firmware audit — November 15, 2026

Primary source: [shared firmware library](https://drive.google.com/drive/folders/1Z4_axffop928ep2CAmaApmTjdKUQV4xW),
linked from the [Honda EPS status sheet](https://docs.google.com/spreadsheets/d/1edkzOjTJfXRjE9v0nHh0uVFfhPFSkYnI3sg0oVliRkU/edit).

All 17 vehicle folders and 28 direct category folders were listed. Current PTM
and clearly identified stock images were downloaded and hashed; legacy/WIP
files and vehicle-specific flashing scripts were not promoted to current images.
The table records 30 unique current artifacts, including unchanged local copies.
Full hashes for all retained assets are in [SHA256SUMS](SHA256SUMS).

### Clarity AnglePTM replacement — November 20, 2026

The owner supplied `39990+TRW+A020-AnglePTM-20261119-09.rwd` separately
from Drive. It replaces build 05 in the angle slot only. The unmodified RWD's
SHA-256 is `6fef0b9cd2a51e42b681befeba1a0d996b97618df2bbf52a4e3bafaca7b96d99`.
It matches both prefixes published in [opendbc #8](https://github.com/nrdr/opendbc/pull/8):
`6fef0b9c` for the RWD and `f8d6aee3` for the decoded binary with its
unpackaged leading region padded with `0xff`. That padding is not ECU readback data.

## Downloaded artifacts

Paths are relative to this directory. “Guided” means locally validated and
listed for the existing updater; it does not mean a flash or road test occurred.

| Local file | Drive source | SHA-256 prefix | Use |
| --- | --- | --- | --- |
| `39990-TBA-A030/Legacy and Stock/stock-39990-TBA-A030.rwd` | [stock-39990-TBA-A030.rwd](https://drive.google.com/file/d/1rl5RBN4fZWyqp-goteBIF-hdr8zUFWjv/view?usp=drivesdk) | `50aa2a555b44` | Guided |
| `39990-TBA-A030/Proper Torque Mod/39990-TBA,A030-PTM.rwd` | [39990-TBA,A030-PTM.rwd](https://drive.google.com/file/d/1AZTQza1DPKuuzNFmv4TR5lXHaFmE5g9m/view?usp=drivesdk) | `55c372662295` | Guided |
| `39990-TBA-C020 (2019 Honda Civic Sport)/Legacy and Stock/stock-39990-TBA-C020.rwd` | [stock-39990-TBA-C020.rwd](https://drive.google.com/file/d/1LChb56_ojc0BYwVZe4jkyFLEqD65Eshh/view?usp=drivesdk) | `ad30cbd9faad` | Guided |
| `39990-TBA-C020 (2019 Honda Civic Sport)/Proper Torque Mod/39990-TBA,C020-PTM.rwd` | [39990-TBA,C020-PTM.rwd](https://drive.google.com/file/d/1diU84Px_9c4yRJVMhJVn_jYDs9RpXHhJ/view?usp=drivesdk) | `df67bf6fa515` | Guided |
| `39990-TBA-C120/Legacy and Stock/stock-39990-TBA-C120.rwd` | [stock-39990-TBA-C120.rwd](https://drive.google.com/file/d/1G6pGm8_wIiv5eFEkPOLlgGAs1J0aj28I/view?usp=drivesdk) | `273726b6bbcf` | Guided |
| `39990-TBA-C120/Proper Torque Mod/39990-TBA,C120-PTM.rwd` | [39990-TBA,C120-PTM.rwd](https://drive.google.com/file/d/1WUXoF7OUWJUFDDM6LGpNJk2DrPS6koBI/view?usp=drivesdk) | `15e63414b313` | Guided |
| `39990-TEG-A010/Proper Torque Mod/39990-TEG,A010-PTM.rwd` | [39990-TEG,A010-PTM.rwd](https://drive.google.com/file/d/1yEelACXSGR0CThZ2TFkm-2SNqysCgBLT/view?usp=drivesdk) | `80fbd0e02345` | Guided |
| `39990-TG7-A040 (2016 Honda Pilot)/Legacy and Stock/39990-TG7-A040-STOCK.rwd` | [39990-TG7-A040-STOCK.rwd](https://drive.google.com/file/d/10GHzf08_QNwA8CVX0EH-RB75ju8robEx/view?usp=drivesdk) | `64ac87f422f3` | Reference: Pilot A040 |
| `39990-TG7-A060 (2019 Honda Pilot)/Legacy and Stock/39990-TG7-A060-STOCK.rwd` | [39990-TG7-A060-STOCK.rwd](https://drive.google.com/file/d/13GB5pEX5hUhgWcrJHEBzPMjN6i6go2Fh/view?usp=drivesdk) | `f13d6b28e60e` | Guided |
| `39990-TGG-A020/Legacy and Stock/stock-39990-TGG-A020-HatchbackSport.rwd` | [stock-39990-TGG-A020-HatchbackSport.rwd](https://drive.google.com/file/d/1ZF5Ca1uRP2dYA7ejqIoxFYfJ43IIGXhb/view?usp=drivesdk) | `9b43471586cd` | Guided |
| `39990-TGG-A120/Proper Torque Mod/39990-TGG,A120-PTM-20261016b.rwd` | [39990-TGG,A120-PTM-20261016b.rwd](https://drive.google.com/file/d/12_jEbYzXr_FjzNTDCA0FjJcw8kQI0BCp/view?usp=drivesdk) | `6640806da8a5` | Guided |
| `39990-TGG-A120/stock-39990-TGG-A120.rwd` | [stock-39990-TGG-A120.rwd](https://drive.google.com/file/d/11JdcMX9bflrulFuZukONOASyjIKCbZxm/view?usp=drivesdk) | `3780431a4700` | Guided |
| `39990-THR-A020 (Honda Odyssey)/Legacy and Stock/stock_39990-THR-A020.rwd` | [stock_39990-THR-A020.rwd](https://drive.google.com/file/d/1N4EzhbGdr0jR4yBEVi5P2BJQw3OHlt6s/view?usp=drivesdk) | `09604ecb9132` | Guided |
| `39990-TJB-A220 (Acura RDX)/Legacy and Stock/39990-TJB-A220 (Stock I-HDS File).rwd` | [39990-TJB-A220 (Stock I-HDS File).rwd](https://drive.google.com/file/d/15JROpp2FTt3sYWUscvdvaLaKKtZyjzMc/view?usp=drivesdk) | `d951de3c64d0` | Guided |
| `39990-TJB-A220 (Acura RDX)/Legacy and Stock/39990-TJB-A220-Stock.rwd` | [39990-TJB-A220-Stock.rwd](https://drive.google.com/file/d/1VHCiRhn8zpvw0PHKnKhja-mEpx2mhktt/view?usp=drivesdk) | `7895cace5ef2` | Guided |
| `39990-TJB-A220 (Acura RDX)/Proper Torque Mod/39990-TJB-A220-PTM-Keys.rwd` | [39990-TJB-A220-PTM-Keys.rwd](https://drive.google.com/file/d/1z-uVF0NqmpLw05eBUoORBJRePml8CC-a/view?usp=drivesdk) | `68a6fdb43e0b` | Guided |
| `39990-TLA-A040 - (Honda_CRV_5G)/Legacy and Stock/39990-TLA-A040-stock.rwd` | [39990-TLA-A040-stock.rwd](https://drive.google.com/file/d/14Xd31rB344K8sh-mvDK-VcyRzHjNJmq2/view?usp=drivesdk) | `f84968c6b2b1` | Guided |
| `39990-TLA-A040 - (Honda_CRV_5G)/Proper Torque Mod/39990-TLA-A040_Clarity_FF_tune_telemety_8cf8e537.rwd` | [39990-TLA-A040_Clarity_FF_tune_telemety_8cf8e537.rwd](https://drive.google.com/file/d/1UQm1PJ9vBxZrlchoAHWlLizsFkLJAuLp/view?usp=drivesdk) | `26f5390b654a` | Guided |
| `39990-TLA-A220 (2021 Honda CR-V)/Legacy and Stock/39990-TLA-A220-stock.rwd` | [39990-TLA-A220-stock.rwd](https://drive.google.com/file/d/1JutRnCCLNcaWy0ACf6l8Q0WxtjB9fPhm/view?usp=drivesdk) | `70d38d2e72a8` | Guided |
| `39990-TLA-A220 (2021 Honda CR-V)/Proper Torque Mod/39990-TLA,A220-PTM-20261016b.rwd` | [39990-TLA,A220-PTM-20261016b.rwd](https://drive.google.com/file/d/1ogQFge5yYAVcAdkHv1qLRODJiugkFSD1/view?usp=drivesdk) | `2c99299725fa` | Guided |
| `39990-TRW-A020 (Honda Clarity)/Legacy and Stock/39990-TRW-A020 (stock).rwd` | [39990-TRW-A020 (stock).rwd](https://drive.google.com/file/d/1vlSzpspX47bPkrrdqZuL4ZsYwKOi8sFQ/view?usp=drivesdk) | `d08a7f5c18ea` | Guided |
| `39990-TRW-A020 (Honda Clarity)/Proper Torque Mod/ClarityMax-PTM-Latest-092826.rwd` | [ClarityMax-PTM-Latest-092826](https://drive.google.com/file/d/1inzrNc447YYIvRRmGEeaZYSamm5Jg_6K/view?usp=drivesdk) | `9e2e98857a67` | Guided |
| `39990-TVA-A160 (Honda Accord)/Proper Torque Mod/39990-TVA,A160-V300-PTM.rwd` | [39990-TVA,A160-V300-PTM.rwd](https://drive.google.com/file/d/1Ei8IDShMzZQ8WdOdGeIcutz8cuMyQH3c/view?usp=drivesdk) | `42f562c069d3` | Reference: x31 |
| `39990-TVA-A160 (Honda Accord)/Proper Torque Mod/39990-TVA,A160-V37A-PTM-lite.rwd` | [39990-TVA,A160-V37A-PTM-lite.rwd](https://drive.google.com/file/d/1WOAnaIQknOLMDMqmAnMez-Dvz-EXXIRz/view?usp=drivesdk) | `af57a2365a17` | Reference: x31 |
| `39990-TVA-A160 (Honda Accord)/Stock/39990-TVA-A160-V9B-Stock.rwd` | [39990-TVA-A160-V9B-Stock.rwd](https://drive.google.com/file/d/1j9qRiocK1v4KHWhBVXalYjY5opBuNaag/view?usp=drivesdk) | `7ad6d49d4a97` | Reference: x31 |
| `39990-TVA-A340 (2021 Honda Accord)/Proper Torque Mod/39990-TVA,A340-V300-PTM.rwd` | [39990-TVA,A340-V300-PTM.rwd](https://drive.google.com/file/d/1zgd2xV_kLXEpnQLHpCMwZg4AI23E6Dj-/view?usp=drivesdk) | `2819a6f2d197` | Reference: x31 |
| `39990-TVA-A340 (2021 Honda Accord)/Proper Torque Mod/39990-TVA,A340-V37A-PTM-lite.rwd` | [39990-TVA,A340-V37A-PTM-lite.rwd](https://drive.google.com/file/d/1Dpvnw7XK1kbWBai-axtm7_Vl2RVomMkc/view?usp=drivesdk) | `e7728d58a129` | Reference: x31 |
| `39990-TVA-A340 (2021 Honda Accord)/Stock/39990-TVA-A340-STOCK.rwd` | [39990-TVA-A340-STOCK.rwd](https://drive.google.com/file/d/1OFEECeZO3jNIXbs6gQdmpiVSHtlLhEwt/view?usp=drivesdk) | `0965a24c7729` | Reference: x31 |
| `39990-TXM-A040 (2019-2022 Honda Insight)/Legacy and Stock/TXM-A040-STOCK.rwd` | [TXM-A040-STOCK.rwd](https://drive.google.com/file/d/1zi6qjKc-1lEhnhKyCmZUwhx8gHl3OX7V/view?usp=drivesdk) | `834a2fc06e62` | Guided |
| `39990-TXM-A040 (2019-2022 Honda Insight)/Proper Torque Mod/39990-TXM,A040-PTM.rwd` | [39990-TXM,A040-PTM.rwd](https://drive.google.com/file/d/1FlQpn5Wv_AMyIf-eekZcfUg5Btewc4eR/view?usp=drivesdk) | `833a41bf9c3a` | Guided |

## Reconciliation

- Civic A030 replaces the same-path older asset. Civic C020 and Clarity now use
  the newer Drive filenames; their previous files remain reference-only.
- Civic TGG-A120, CR-V A220, RDX, Odyssey stock, Clarity stock, Pilot A040 stock,
  and Accord PTM/stock additions fill previously missing catalog entries.
- Drive's extensionless `ClarityMax-PTM-Latest-092826` was saved with `.rwd`
  appended; its bytes are unchanged. Compared with the previous bundled
  Clarity PTM, headers are identical and 22 decrypted bytes differ: 18 within
  flash addresses `0x1396e–0x13bed`, plus four checksum bytes. The semantic
  effect of those 18 bytes is unverified; no controller retuning was done.
- The root and PTM-folder copies of TGG-A120 have identical bytes
  (`6640806d...`); only the PTM-folder copy is catalogued.
- Odyssey THR-A020, Ridgeline T6Z-A110, Pilot TG7-A060 and Civic TGG-A020 PTM
  folders were empty. TEG-A010 has no clearly identified stock image.
- Accord x31 and Ridgeline FF00/FF01 programming need their own verified
  protocol support. Pilot A040 is also held reference-only. No such transport
  was implemented or enabled.

## Firmware versus controller references

Drive remains authoritative for the offered image. The following current Drive
files do **not** match the firmware hashes documented for the present PTM
controller calibration in [firmware_controller_profiles.md](../../../docs/firmware_controller_profiles.md):

| Family | Drive SHA-256 prefix | Controller reference prefix |
| --- | --- | --- |
| TEG-A010 | `80fbd0e0` | `04147917` |
| TBA-C120 | `15e63414` | `9261b8db` |
| TXM-A040 | `833a41bf` | `7ba37432` |
| TLA-A040 | `26f5390b` | `2e6a8802` |

These four images were already bundled and were re-downloaded unchanged. Do not
claim calibration parity from their filenames or silently substitute a donor
file. Obtain an updated authoritative Drive image or explicitly review the
firmware/controller pairing before treating these as synchronized.

The new A030, C020, TGG-A120 and CR-V A220 images match the recorded reference
hash prefixes. RDX matches donor `68a6fdb4`, but nrdr's runtime RDX PTM admission
remains disabled. This audit changes neither controller numbers nor admission.

## Validation provenance and limits

ROM CRC, THR/TJB monitor-shadow, parser and newer T6Z checks are adapted from
[Biscuit-Labs `2f4bda7aed`](https://github.com/Biscuit-Labs/openpilot/commit/2f4bda7aed9a864a90c08fbb377852d9acdc4644),
not from untrusted Drive scripts. Existing nrdr Pilot A060 LE32 checks and
legacy T6Z header/identity checks are retained. The updater now shares these
checks instead of silently skipping unfamiliar lengths.

Verification is offline: file hashes, checksums, corruption rejection,
identity/seed lookups and SSH catalog selection. No Panda connection, ECU flash
or runtime controller change was performed. These checks do not establish
successful on-car flashing or safe steering behavior.

## Full-memory dump inventory — November 17, 2026

Read-only inspection of this checkout found TEG-A010 and TRW-A020 RWD update
images, not verified complete readbacks of either owner's installed ECU.
All five matching containers parse to one 304 KiB flash block at `0x4000`,
length `0x4c000`, ending at `0x50000` exclusive. They contain neither the lower
`0x0000–0x3fff` region nor an SRAM snapshot. This address coverage alone does
not establish the ECU's complete memory layout. Raw binaries for other EPS
families are not evidence of a complete TEG/TRW dump.

`CarParams.carFw` and the guided helper's "current firmware" lookup contain
software identification responses, not firmware code. `eps-diag.py` checks
communication/software IDs; `eps-update.py` programs supplied images. Neither
implements a verified TEG/TRW flash-plus-SRAM acquisition procedure. opendbc
provides generic UDS memory-read/upload methods, but their presence does not
establish that these ECUs support them, which regions are accessible, or that
the required diagnostic session is non-disruptive. No live requests were made.

For the requested TEG research, obtain the donor's exact acquisition tool and
revision, memory ranges, expected file sizes, required ECU state and recovery
procedure before attempting a read. Independently confirm which image is
installed: the bundled TEG PTM file still hashes to `80fbd0e02345...`, whereas
the controller reference is `04147917...`. That discrepancy is an unresolved
pairing question, not proof of what is installed or of a steering defect.
