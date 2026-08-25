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
├── params/    contracts, startup policy, profiles, snapshots, and typed access
├── features/  self-contained NRDR behavior
├── hooks/     small adapters called by openpilot processes
├── ui/        NRDR-owned presentation and settings integration
└── tests/     package and boundary tests
```

The separation is intentional:

- `params` owns names, types, startup defaults, validation, profiles, snapshots,
  and future NRDR-specific migrations.
- `features` owns algorithms.  Parameter mechanics do not belong here.
- `hooks` translates openpilot state into calls to NRDR features.  Hooks should
  remain small and contain no tuning algorithm.
- `ui` owns NRDR presentation.  Shared parameter metadata may be consumed here,
  while custom screen layout remains explicit.

The package exposes a lazy public API. Common readers use:

```python
from openpilot.nrdr.params import NrdrParamKey, ParamReader, read_bool, read_float
```

`ParamReader` deliberately exposes only `get`.  It can represent a startup
reader or an immutable snapshot without giving feature code permission to
write persistent state.  `read_bool` and `read_float` preserve the behavior of
the original NRDR helpers. `NrdrParamKey` gives consumers generated, typed key
names while remaining compatible with APIs that accept strings.

Existing modules under `openpilot/sunnypilot/nrdr` remain in place during the
incremental migration. Parameter defaults, handcrafted profiles, and live
snapshots now have canonical owners here; their old modules are explicit
forwarders so external users are not broken while production call sites move.

## Current migration status

- Complete: parameter catalog/generation, typed keys, startup defaults,
  handcrafted parameter profiles, and openpilot-process live snapshots.
- In progress: shared native/Sunnylink UI metadata. The first six lateral P/I
  scale controls now have one declarative owner with output-parity tests.
- Compatibility only: the old defaults, handcrafted-profile, and live-snapshot
  modules under `openpilot.sunnypilot.nrdr`.
- Pending: the remaining UI metadata, feature algorithms, hook implementations,
  UI ownership, and the typed opendbc configuration boundary.

SunnyPilot-wide migrations (including display and non-NRDR vehicle migrations)
remain owned by SunnyPilot. No NRDR-specific versioned migration exists yet;
the first one belongs here when it is introduced.

See [ARCHITECTURE.md](ARCHITECTURE.md) for dependency rules and the migration
sequence.
