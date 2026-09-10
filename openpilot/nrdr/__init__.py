"""First-class NRDR extension package.

Public integrations should import narrowly from the owning subpackage, for
example ``openpilot.nrdr.params``.  Keeping this module lightweight prevents an
unrelated NRDR feature from being initialized merely because the package was
discovered.
"""
