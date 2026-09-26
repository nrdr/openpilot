"""Compatibility facade for the canonical NRDR radar reverse-engineering CLI."""

from openpilot.nrdr.tools.radar_re.cli import TRUTH_CHANNELS, main, run


__all__ = ("TRUTH_CHANNELS", "main", "run")


if __name__ == "__main__":
    main()
