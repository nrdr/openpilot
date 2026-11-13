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
