# Engineering and Workspace Instructions

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
