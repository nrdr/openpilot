# Engineering and Workspace Instructions

## Project Naming

- The official project name is `nrdr`, always lowercase; never capitalize it.
- Use lowercase naming in documentation, UI labels, release notes, comments, generated text, and all project references across branches and repositories.
- Do not rename existing identifiers or modify functionality solely to enforce this convention.

## Repository and branches

- Use `C:\Openpilot Workspace\openpilot` for routine development.
- `nrdr-development` is the primary development branch. Established release branches are `nrdr-nightly`, `nrdr-clean`, and `nrdr-staging`.
- Do not create branches or working copies unless explicitly necessary and authorized.
- Never create additional repository clones, experimental directories, or temporary worktrees directly under `C:\`.
- Keep temporary build artifacts in designated build/cache locations or the system temporary directory.
- Never delete existing folders or repositories without the user's approval.

## Engineering approach

- Prefer the simplest correct implementation consistent with the existing architecture.
- Avoid unnecessary abstractions, redundant checks, speculative safeguards, and unrelated refactoring.
- Preserve existing safety-critical behavior and unrelated user changes.

## Task Tracking

- Before starting a development task, consult `TASKS.md` for relevant context.
- After completing meaningful work, update the corresponding task's status and next action.
- Do not treat discussions, proposals, or investigations as completed implementations.
- Do not automatically begin work on unrelated pending tasks.
- Keep task updates concise and focused on actual progress.
- If `TASKS.md` does not exist, do not create it unless explicitly requested.

## Publishing and deployment

- Merge, push, or deploy only with explicit instructions.
- Do not modify release branches without explicit instructions.

## Release Management and Build Workflow

The primary development branch is `nrdr-development`.

The established release branches are:

- `nrdr-nightly`
- `nrdr-staging`
- `nrdr-clean`

The existing release script is `release/build_prebuilt.sh`.

### Ownership

- Release builds, branch synchronization, and deployment are user-controlled operations.
- Never execute `release/build_prebuilt.sh` unless I explicitly instruct you to run it.
- Never automatically build, publish, push, or deploy release branches.
- Do not recreate the release script's functionality through alternative commands.
- Do not introduce additional build scripts, release workflows, or validation pipelines unless requested.

### Development

- Make requested changes in the existing development environment.
- Perform only the verification relevant to the code being changed.
- Do not run full release builds to validate ordinary development changes.
- Do not perform speculative release checks or unrelated testing.
- Do not modify the release script unless explicitly requested.

### Handoff

When development work is complete:

1. Briefly summarize the changes.
2. Report any relevant tests performed.
3. Clearly identify whether changes are committed or uncommitted.
4. Leave release execution to me.

Do not automatically proceed into release preparation, building, or deployment.

### User Control

If I ask how to perform a release, explain the existing workflow and provide the appropriate commands for me to execute manually.

Do not execute those commands on my behalf unless I explicitly request execution.

## Standing PTM Testing investigation workflow

- Within the ongoing Clarity/PTM Testing investigation, the user authorizes justified investigation, implementation, parameter changes, commits, pushes, development deployment and verification on the Comma Four through `nrdr-development`. Do not repeatedly request publication permission for work already in this scope.
- Keep normal PTM, unrelated work and release branches unchanged. This authorization does not authorize `release/build_prebuilt.sh` or any automatic release build. Perform deployment/restarts only while parked and disengaged, with a recoverable baseline; confirm current vehicle state before each deployment session.
- Preserve steering safety enforcement and driver-override protections. Use the simplest adequate existing tuning adjustment before adding gates, filters or state. Keep expressly fixed variables (currently the final output filter in the unwind-release comparison) unchanged.
- Consult actual Biscuit-Labs/openpilot `Honda-PTM-Testing` implementation, tools and relevant diffs, not commit titles alone. Record useful source revisions, paths, reproducible commands, assumptions and limitations in the existing investigation notes; do not transfer another Honda's numerical tune without Clarity measurements.
- Run applicable quantitative tuning tools on meaningful baseline/candidate datasets, with consistent selections and configurations. Explain specific incompatibilities and justified alternatives. Distinguish measured, estimated, inherited and unknown quantities, including CAN-yaw and steering-ratio dependencies.
- Move offline findings to the next justified measurable experiment. Full-controller replay with recorded feedback is not a prediction of changed vehicle behavior. If causality remains unresolved, deploy targeted instrumentation and request the particular supervised collection that would discriminate hypotheses; do not make arbitrary behavior changes.
- For each experiment, preserve exact revision/submodule revisions, controller selection, parameters, logging configuration, prediction/rejection criteria, verification and rollback. Parameter-only experiments need no artificial source commit. Give a practical collection plan covering comparable ordinary maneuvers, model/speed/direction, preceding and subsequent history, interventions, stop/revert criteria and required logs.
- On receipt of logs, compare against the recorded prediction, include driver impressions and contradictory evidence, and decide keep/refine/revert. Update the relevant `TASKS.md` entry and investigation notes; distinguish ready-to-test, observed improvement and representative validation. Do not declare a road improvement from command-only replay or an offline report alone.
