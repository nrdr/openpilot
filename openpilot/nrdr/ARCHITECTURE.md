# NRDR architecture

## Why `openpilot/nrdr`

`openpilot/nrdr` is a sibling of `openpilot/sunnypilot`, not an operating-system
top-level package.  This gives NRDR visible ownership while retaining several
important properties:

1. It is included by the existing Python package configuration, which packages
   the `openpilot` namespace.
2. The release builder copies tracked source files and therefore includes this
   directory without a second release mechanism.
3. Imports remain unambiguous (`openpilot.nrdr`) and cannot collide with an
   unrelated globally installed package named `nrdr`.
4. Package placement adds no per-frame work.  Normal Python module caching means
   an import is resolved once for each process.

The move changes dependency ownership, not control behavior.  It must therefore
be incremental and backed by compatibility imports until consumers migrate.

## Dependency direction

The intended direction is:

```text
openpilot process -> NRDR hook -> NRDR feature -> immutable configuration
                                      ^
NRDR UI ------------------------------| (commands/settings only)

openpilot card setup -> SunnyPilot host composer -> typed immutable config -> opendbc
                                      ^
                         NRDR Honda/provider adapter
```

Rules for new code:

- Core openpilot files call a small NRDR hook or facade.
- Algorithms live in `features`, never in a hook or parameter declaration.
- Feature update loops do not instantiate `Params` or synchronously read the
  Params filesystem.  A process reads at initialization or receives an
  immutable snapshot refreshed outside its real-time loop.
- Parameter keys, defaults, bounds, and migrations have one owner under
  `params`.
- `params` must not import features, hooks, or UI.
- `features` must not import hooks or UI.
- UI can consume parameter metadata but cannot become the source of controller
  defaults.
- Opendbc receives a typed, immutable multi-brand configuration from the
  SunnyPilot host composer. NRDR supplies only its Honda/provider portion and
  does not own SunnyPilot's generic brand keys or defaults. Opendbc must not
  import openpilot's Params implementation or re-own NRDR defaults and
  persistence policy.

## Public surface

Only symbols re-exported by a package `__init__.py` are public.  Callers should
not depend on implementation modules when a public import exists.  The first
public surface is `openpilot.nrdr.params`, containing the generated
`NrdrParamKey` enum, a read-only source protocol, and the existing typed
conversion helpers.

Compatibility modules use explicit re-exports.  Wildcard exports, module alias
injection, and import-time feature initialization are intentionally avoided.

## Migration sequence

Current status on `nrdr-architecture-development`:

- Step 1 is complete.
- Step 2 is complete for NRDR-owned defaults, profiles, and snapshots. There is
  no NRDR-specific versioned migration to relocate yet. SunnyPilot-wide
  migrations remain with SunnyPilot rather than being relabeled as NRDR code.
- Step 3 has started with shared, catalog-validated metadata for the six
  low/standard/high-speed lateral P/I scale controls. Their native and
  Sunnylink adapters now consume one definition while preserving the existing
  generated schema, translations, and edit rules. Native NRDR settings, home,
  and on-road implementations now have canonical UI owners. NRDR Sunnylink
  macros and settings fragments also live under `openpilot.nrdr.ui`; the
  framework compiler merges them at explicit anchors and continues to own the
  generated consumer schema. Framework layout files retain only
  import/registration seams.
- Step 4 runtime implementation ownership is complete. Lateral, longitudinal, radar,
  driver-policy, service, and process-hook implementations live under
  `openpilot.nrdr`; offline lateral, steer-ratio, and radar tools live under
  `openpilot.nrdr.tools`. Former SunnyPilot modules and root commands are
  explicit compatibility facades, while production callers use canonical
  owners. The safety-critical EPS flashing implementation, parser, tests, and
  all firmware images now live under `openpilot.nrdr.tools.eps`. Root and former
  `eps_tools` command paths are launch-only compatibility surfaces. Every image
  is pinned by SHA-256 and validated without changing its bytes.
- Step 5 is complete. `openpilot.nrdr.car` owns only NRDR Honda startup
  conversion, live snapshots, and persistence callbacks. SunnyPilot's host
  adapter owns its pre-existing multi-brand keys/defaults and composes both
  portions before the car-interface seam passes immutable values to opendbc.
- The retired `NrdrLegacyDualBpSteerRatio` manual selector is a parameter
  tombstone. Its exact persistent/backup BOOL registry metadata and default of
  `1` remain generated for downgrade compatibility, but profile v14, live
  snapshots, controllers, analyzers, and settings UIs no longer consume it.
- The remaining Step 3 metadata and Step 6 remain pending.

1. Add the first-class package, typed parameter catalog, generated registry
   artifacts, tests, and compatibility forwarding with no behavior change.
2. Move NRDR-owned parameter defaults, profiles, snapshots, and versioned
   migrations into `params`; retain temporary forwarding imports.
3. Make native UI and Sunnylink consume shared parameter metadata while keeping
   custom layouts handwritten.
4. Move existing NRDR implementations into domain folders under `features`,
   offline utilities under `tools`, and reduce their openpilot call sites to
   hooks. Keep firmware flashing changes separate, byte-validated, and reachable
   through stable compatibility commands.
5. Replace direct opendbc Params reads with typed configuration passed across
   the car-interface boundary.
6. Remove compatibility modules only after downstream imports and deployed
   branches have completed the migration.

Each step should preserve outputs, pass focused characterization tests, and be
small enough to revert independently.  Controller reorganization and tuning
changes should never share a commit.
