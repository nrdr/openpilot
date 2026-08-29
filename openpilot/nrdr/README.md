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
├── car/       NRDR Honda/provider portion of opendbc's typed configuration
├── params/    contracts, startup policy, profiles, snapshots, and typed access
├── features/  lateral, longitudinal, radar, driver-policy, and service behavior
├── hooks/     small adapters called by openpilot processes
├── tools/     offline analysis, release, device-helper, and EPS flashing tools
├── ui/        NRDR-owned settings, Sunnylink source, home, and on-road presentation
├── docs/      current references plus clearly labeled historical notes
└── tests/     package and boundary tests
```

The separation is intentional:

- `params` owns names, types, startup defaults, validation, profiles, snapshots,
  and future NRDR-specific migrations.
- `car` owns the narrow adapter that converts only NRDR's Honda configuration
  into immutable typed values. SunnyPilot owns the neutral multi-brand host
  composer and its pre-existing vehicle settings.
- `features` owns algorithms.  Parameter mechanics do not belong here.
- `hooks` translates openpilot state into calls to NRDR features.  Hooks should
  remain small and contain no tuning algorithm.
- `tools` owns offline analysis libraries, release tooling, and safety-reviewed
  device utilities. Compatibility entrypoints may retain old paths while the
  real implementations live in this canonical package.
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

Modules under `openpilot/sunnypilot/nrdr` remain temporarily for compatibility,
but they no longer own production implementations. They are explicit forwarders
to canonical NRDR owners so older branches and external imports keep working
while downstream consumers migrate.

## Current migration status

- Complete: parameter catalog/generation, typed keys, startup defaults,
  handcrafted profiles, and process-level live snapshots.
- Complete: lateral, longitudinal, radar, driver-policy, service, framework-hook,
  native settings, home, and on-road UI ownership. Framework callers retain only
  narrow import/call seams.
- Complete: offline lateral, steer-ratio, and radar reverse-engineering tool
  ownership, with old command paths retained as compatibility entrypoints.
- Complete: EPS flashing implementation, parser, validation tests, and all 15
  firmware images live under `openpilot.nrdr.tools.eps`. Root and historical
  `eps_tools` commands are thin launchers; the firmware manifest pins every
  shipped image byte-for-byte.
- Complete: device helper ownership, with the boot caller using the canonical
  setup script and the old script paths retained as thin launchers.
- Complete: NRDR Sunnylink macros and settings authoring fragments. The generic
  Sunnylink compiler merges them at explicit page, section, and item anchors;
  the generated consumer schema remains in Sunnylink's framework package.
- Complete: the typed openpilot-to-opendbc configuration boundary. Opendbc no
  longer reads openpilot Params; SunnyPilot composes its generic vehicle policy
  with NRDR's isolated Honda provider before passing immutable data across.
- In progress: shared native/Sunnylink UI metadata. The first six lateral P/I
  scale controls now have one declarative owner with output-parity tests.
- Compatibility only: the old defaults, handcrafted-profile, and live-snapshot
  modules and every former NRDR feature module under
  `openpilot.sunnypilot.nrdr`.
- Pending: the remaining shared UI metadata, downstream import migration, and
  eventual compatibility-facade retirement.

SunnyPilot-wide migrations (including display and non-NRDR vehicle migrations)
remain owned by SunnyPilot. No NRDR-specific versioned migration exists yet;
the first one belongs here when it is introduced.

See [ARCHITECTURE.md](ARCHITECTURE.md) for dependency rules and the migration
sequence, and [docs](docs/) for current and historical references.
