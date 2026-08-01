#!/usr/bin/env bash
set -euo pipefail

DATA_BIN="/data/bin"
OPSYNC="${DATA_BIN}/opsync"
BASHRC="${HOME}/.bashrc"

mkdir -p "${DATA_BIN}"

cat > "${OPSYNC}" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

cd /data/openpilot

branch="$(git branch --show-current)"
if [[ -z "${branch}" ]]; then
  echo "Unable to determine current branch."
  exit 1
fi

echo "Pulling only current branch: ${branch}"
git pull origin "${branch}" --no-tags

echo "Starting openpilot..."
/data/openpilot/tools/op.sh start
SH

chmod +x "${OPSYNC}"

if [[ -f "${BASHRC}" ]]; then
  grep -qxF 'export PATH="/data/bin:$PATH"' "${BASHRC}" || echo 'export PATH="/data/bin:$PATH"' >> "${BASHRC}"
else
  echo 'export PATH="/data/bin:$PATH"' > "${BASHRC}"
fi

export PATH="/data/bin:${PATH}"