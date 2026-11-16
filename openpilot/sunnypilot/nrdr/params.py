"""Compatibility imports for the first-class NRDR parameter API.

New code should import from :mod:`openpilot.nrdr.params`.
"""

from openpilot.nrdr.params import NrdrParamKey, ParamReader, ParamValue, read_bool, read_float

__all__ = ("NrdrParamKey", "ParamReader", "ParamValue", "read_bool", "read_float")
