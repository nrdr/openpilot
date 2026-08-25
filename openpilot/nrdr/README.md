# NRDR

NRDR is a first-class openpilot extension package.  New NRDR-owned code belongs
here rather than under the SunnyPilot namespace.

Moving the package does not make the controller faster or slower.  Python
resolves these imports when a process starts; the directory depth is not part
of the on-road control loop.  The top-level location instead makes ownership
clear, removes the misleading implication that NRDR is an internal SunnyPilot
component, and gives contributors one obvious place to start.

## Package map

```text
openpilot/nrdr/
├── params/    parameter contracts and typed, read-only access
├── features/  self-contained NRDR behavior
├── hooks/     small adapters called by openpilot processes
├── ui/        NRDR-owned presentation and settings integration
└── tests/     package and boundary tests
```

The separation is intentional:

- `params` owns names, types, defaults, validation, profiles, and migrations.
- `features` owns algorithms.  Parameter mechanics do not belong here.
- `hooks` translates openpilot state into calls to NRDR features.  Hooks should
  remain small and contain no tuning algorithm.
- `ui` owns NRDR presentation.  Shared parameter metadata may be consumed here,
  while custom screen layout remains explicit.

The stable parameter-reader API is:

```python
from openpilot.nrdr.params import NrdrParamKey, ParamReader, read_bool, read_float
```

`ParamReader` deliberately exposes only `get`.  It can represent a startup
reader or an immutable snapshot without giving feature code permission to
write persistent state.  `read_bool` and `read_float` preserve the behavior of
the original NRDR helpers. `NrdrParamKey` gives consumers generated, typed key
names while remaining compatible with APIs that accept strings.

Existing modules under `openpilot/sunnypilot/nrdr` remain in place during the
incremental migration.  The old parameter-helper module forwards to this API,
so external users are not broken while production call sites move.

See [ARCHITECTURE.md](ARCHITECTURE.md) for dependency rules and the migration
sequence.
