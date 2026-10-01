"""Canonical authoring source for NRDR Sunnylink settings."""

from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent
MACRO_SOURCE = "_macros.yaml"
ITEM_SOURCE_FILES = ("items/device.yaml",)
PAGE_SOURCE_FILES = ("pages/cruise.yaml", "pages/software.yaml", "pages/steering.yaml")
SOURCE_FILES = (MACRO_SOURCE, *ITEM_SOURCE_FILES, *PAGE_SOURCE_FILES)


__all__ = ("ITEM_SOURCE_FILES", "MACRO_SOURCE", "PAGE_SOURCE_FILES", "SOURCE_FILES", "SOURCE_ROOT")
