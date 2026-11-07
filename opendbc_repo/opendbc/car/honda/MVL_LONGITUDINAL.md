# Honda MVL priority longitudinal contract

MVL mode selects the pinned MVL longitudinal command law for Honda openpilot
longitudinal control. It is not a claim that the whole controller, every CAN
field, or the qualified Clarity development brake path is identical to MVL.
This is offline-validated software, not a vehicle validation or deployment.

## Source pins

- MVL root: `376c44b5731b2655e5c2f301b73c9729eb499e91`.
- Its actual `opendbc_repo` gitlink:
  `3fec9a418a659de31d7b1f494193161697a35071`.
- The newer remote branch identified as `770d317` is not the baseline.
  In particular, MVL mode deliberately uses the pinned Bosch stopping-counter
  condition, without the newer `self.accel <= 0.0` guard. Thus the stopping
  bit can be set while the stopping ramp still produces positive acceleration.
  A dedicated differential test records this behavior; it is not being
  presented as an independently validated improvement.
- Legacy-OFF reference: `2320f7e4ff87eb52ed27567d9ab8e87b2f58a939`, the last
  controller before the engine-braking overlay.

The complete reference sources in `tests/mvl_reference/*.py.txt` are frozen
Git blobs, not generated from the new implementation. The tests verify their
canonical Git SHA-1 hashes and execute the original controller's entire
`update()`, original CAN builders, original interceptor, original helpers,
and original parameter definitions in isolated namespaces. There is no Git
fetch, host Params object, filesystem learner writer, or vehicle I/O.
The oracle substitutes in-memory parameter storage and disables the unrelated
EPS-mod adapter. Its only source-expression accommodation is an integer cast
in the lateral display speed-band format for newer NumPy. Common current
packing, schemas, and platform-state objects are used on both sides.

## Startup and host ownership

`HondaFlags.MVL_LONGITUDINAL = 131072` is a command-law flag, not a Panda
safety flag. `HondaCarConfig.mvl_longitudinal: bool = False` is an immutable
startup input. The host builds it from `HondaLiveLearningGas`; the host's
default-ON policy is separate from this boundary's conservative default.

`_configure_params` selects MVL only with openpilot longitudinal enabled and
stock longitudinal not enforced. MVL suppresses both PCM custom-mode flags.
`_get_params_sp` clears MVL for stock longitudinal or disabled openpilot
longitudinal, but retains it for gas interceptors and Bosch. The controller
latches the effective mode at construction. Effective learning remains ON
throughout an MVL drive even when the saved parameter changes; the UI must
require a parked restart.

The host's `mvl_longitudinal_enabled(CP)` policy requires Honda, openpilot
longitudinal, and the flag. Host NRDR longitudinal tuning must be disabled
under that policy; brand/UI eligibility alone is not sufficient.

Personality contract:

- Aggressive, Standard, and Relaxed use the pinned MVL profiles completely,
  including following profiles/distances, acceleration, and jerk. Their custom
  settings must be locked in the UI. NRDR profile files/tune files must not
  influence them.
- Econ alone retains its custom longer following distance and gentler
  acceleration/jerk.

Personality generation, following-distance policy, UI locks, planner/longcontrol
gains, and config adapters live in the parent repository. The nested tests
compare identical host actuator requests; they do not certify parent planner
or personality behavior. There are no personality-specific alternate command
laws in this controller.

## Longitudinal behavior selected by MVL

The extracted routines own preparation, PCM launch/recovery and command
calculation, Bosch/interceptor learners, brake computation, and persistence.
Lateral, HUD, radar ownership, and transport integration remain in the existing
controller.

- PCM uses donor multiband gas/speed learners, governor/coast/saturation gates,
  feedforward model and sensitivity, speed PID, wind learning, launch templates,
  recovery windows, brake feedback, stop ramp, and command curves. The Civic
  reference/allowance path, held-wire observer, ECU-matched ramps/deadband, PCM
  constraints, wind-credit trial, and configurable wind disabling do not run
  in this mode.
- Bosch uses donor low-speed brake PID, gas-factor/wind-factor/gas-alpha
  learning, model-specific learning rates, gas mapping and ramp, and stopping
  counter. The NRDR `LongGasLearner` is neither constructed nor called.
- Ordinary interceptors use donor gas/wind learning and no-learn window,
  measured low-speed multiplier, 0.004/send gas rise, Nidec brake gain and stop
  ramp. NRDR Roen acceleration limits, full-brake-authority overrides, and
  configurable stopping rate cannot alter them.
- Donor longitudinal parameter values are installed on each controller
  instance. This prevents previous fingerprints or the legacy manual-Accord
  class-global curve override from contaminating a new MVL controller.
  Interface acceleration limits, integral gains, and actuator delays are
  compared against the frozen donor.
- EngineBrakeFade and all controller overlay/freshness/washout dependencies
  are removed in both modes. The helper and its feature tests are retired.
  Old CC_SP fields remain unused for serialization compatibility; setting
  them cannot change CAN output.

OFF retains the pre-engine-braking legacy controller behavior. Differential
tests compare complete CAN messages and actuator feedback for PCM modes,
Bosch, and interceptors, with live learning both OFF and ON.

## Explicit differences from the pinned donor

### Host parameter storage and startup policy

The donor directly reads Params and owns a paced writer thread. Here all
reads/writes cross the existing host provider using logical names such as
`gas_alpha_low`, never raw `HondaGasAlphaLowParams`. Every gas/speed band
is checked against the independently listed host key contract. Persistence
snapshots are compared after mapping back to the donor's original keys.
No saved values are deleted, renamed, migrated, or reset by this change.
The donor's existing in-memory numerical bounds/default guards remain; these
are not a new on-disk reset procedure. Host finite-value handling and writer
scheduling remain host-owned.

The startup flag and frozen effective learner-enabled state are additions to
the donor. Per-instance curve isolation also replaces its class-global
fingerprint side effects; the selected curve for each supported platform is
the donor curve.

### Qualified Clarity interceptor hardware

This is a deliberate, non-parity hardware exception, not a donor feature and
not an Econ personality rule. It applies only when
`clarity_braking.qualified(CP, CP_SP)` matches the explicit Clarity hybrid,
interceptor, safety-model/parameter combination. Merely identifying a Clarity
or detecting an interceptor does not enable it. The existing off-device
development configuration/safety qualification is unchanged.

Retained local behavior:

- Nonlinear hybrid brake conversion, including the low-speed linear floor
  and 320-count cap, instead of donor generic 0–255 conversion.
- The calibrated brake path instead of donor Nidec brake gain learning and
  0.00042/send stopping ramp.
- Existing 1.0 brake-fraction/s rise and 0.33 standstill hold.
- Zero PCM speed with the calibrated coasting PCM-gas allowance; zero
  allowance when propulsion is not permitted.
- Existing cancel/driver-override release, propulsion inhibition during
  service braking/hold/AEB, and the dashboard code-252 hold avoidance.
- Interceptor learning inhibition when this hardware relinquishes propulsion.

Those adaptations retain the existing hardware brake scale and hold response;
blindly applying the generic donor brake ramp would change that response.
The generic donor gas multiplier and gas/wind learners otherwise remain in use.
Separate tests cover the retained 97-count standstill hold and override/AEB
propulsion inhibition. They are compatibility tests, not donor parity tests.
Ordinary Clarity PCM and non-qualified interceptor configurations do run the
independent donor differential replay.

### Feedback and preserved integration

Actuator feedback retains the current physical-unit fields. The donor
overloads speed/gas/brake/torqueOutputCan with learner diagnostics on some
paths; those diagnostic overloads are not imported.

Existing lateral control, EPS handling, HUD customization and CMBS/alert
policy, camera messages, radar ownership/relay handoff, and transport
compatibility are retained. Consequently whole-controller CAN byte parity is
not claimed in MVL mode. Differential tests compare complete longitudinal
brake/gas/ACC packets for normal alerts and the PCM propulsion/launch fields
inside ACC_HUD. Custom HUD and alert fields are intentionally outside that
comparison.

The existing Bosch non-finite compensated-force guard remains in the CAN
builder. For finite inputs the gas/brake classification matches the donor.
Panda/safety source and limits, stock-AEB arbitration, and the existing
qualified-hardware safety configuration are unchanged. No new safety
authority is requested by the MVL flag.

## Offline validation

Run the self-contained differential/contract suite explicitly:

```sh
pytest opendbc/car/honda/tests/test_mvl_priority.py -q
```

Broader controller regressions:

```sh
pytest opendbc/car/honda/tests opendbc/sunnypilot/car/honda/tests -q
```

Use a complete isolated native checkout for the existing Honda safety suite
and parent integration tests. Include new/untracked source and fixture files
when overlaying an archive; no donor Git objects are needed. Tests use
in-memory providers and must not connect to an active vehicle checkout or
production parameter directory.

Known baseline failure: the existing
`test_mvl_sync::test_civic_positive_plan_keeps_speed_lead_with_poisoned_alpha`
expects +0.35 m/s but unmodified nested HEAD `634f4354e` and this legacy path
both produce -4.8 m/s. Its first-tick experimental shaping is outside this
MVL-mode change; the legacy law has not been changed to make that assertion
pass.
