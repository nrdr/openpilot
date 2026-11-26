"""Check saved 39990-TEG-A010 raw files. No vehicle or Panda connection."""
import argparse
import hashlib
import os
from pathlib import Path


FLASH_BYTES = 384 * 1024
SRAM_BYTES = 64 * 1024


def check_file(path: Path, size: int) -> bytes:
  if not path.is_file():
    raise ValueError(f"{path}: not a regular file")
  with path.open("rb") as f:
    actual = os.fstat(f.fileno()).st_size
    if actual != size:
      raise ValueError(f"{path}: {actual:,} bytes; expected exactly {size:,}")
    data = f.read(size + 1)
  if len(data) != size:
    raise ValueError(f"{path}: size changed while reading; check the finished file")
  print(f"{path}: {size:,} bytes (size OK); SHA-256 {hashlib.sha256(data).hexdigest()}")
  if data.count(data[:1]) == size:
    print(f"Warning: every byte in {path} is 0x{data[0]:02x}; size alone does not establish useful contents.")
  return data


def main(argv=None) -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("flash", type=Path, help="saved raw flash file, not an .rwd update package")
  parser.add_argument("sram", type=Path, help="saved raw SRAM file")
  parser.add_argument("--compare-flash", type=Path, help="optional second flash capture for a byte-for-byte comparison")
  args = parser.parse_args(argv)
  try:
    flash = check_file(args.flash, FLASH_BYTES)
    check_file(args.sram, SRAM_BYTES)
    if args.compare_flash is not None:
      if args.compare_flash.samefile(args.flash):
        raise ValueError("comparison refers to the same file; supply a separate flash capture")
      if flash != check_file(args.compare_flash, FLASH_BYTES):
        raise ValueError("flash captures differ")
      print("Flash captures are byte-for-byte identical.")
  except (OSError, ValueError) as e:
    print(f"Check failed: {e}")
    return 1
  print("Expected TEG file sizes confirmed. This does not authenticate firmware or verify the ECU memory map.")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
