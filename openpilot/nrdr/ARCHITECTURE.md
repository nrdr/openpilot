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
- The opendbc boundary should eventually receive typed Honda configuration from
  openpilot rather than importing openpilot's Params implementation.

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
  layouts, generated schema, translations, and edit rules.
- The remaining Step 3 controls and Steps 4 through 6 remain pending.

1. Add the first-class package, typed parameter catalog, generated registry
   artifacts, tests, and compatibility forwarding with no behavior change.
2. Move NRDR-owned parameter defaults, profiles, snapshots, and versioned
   migrations into `params`; retain temporary forwarding imports.
3. Make native UI and Sunnylink consume shared parameter metadata while keeping
   custom layouts handwritten.
4. Move existing NRDR implementations into domain folders under `features` and
   reduce their openpilot call sites to hooks.
5. Replace direct opendbc Params reads with typed configuration passed across
   the car-interface boundary.
6. Remove compatibility modules only after downstream imports and deployed
   branches have completed the migration.

Each step should preserve outputs, pass focused characterization tests, and be
small enough to revert independently.  Controller reorganization and tuning
changes should never share a commit.
