#!/usr/bin/env bash
# Zero-dependency installer for local pre-commit & pre-push AI security hooks.
# Usage:
#   bash cicd_與_安全檢查範本/install_git_hooks.sh          # Install hooks in existing git repo
#   bash cicd_與_安全檢查範本/install_git_hooks.sh --init   # Initialize git inside 期未/ safely, then install hooks

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
EXPECTED_FOLDER_NAME="期未"

if [[ "$(basename "${PROJECT_ROOT}")" != "${EXPECTED_FOLDER_NAME}" ]]; then
  echo "[ERROR] Expected project root named '${EXPECTED_FOLDER_NAME}', got: ${PROJECT_ROOT}"
  echo "Aborting so parent folders containing copyrighted textbook files are never initialized."
  exit 1
fi

if [[ "${1:-}" == "--init" ]]; then
  if [[ ! -d "${PROJECT_ROOT}/.git" ]]; then
    echo "[INFO] Initializing Git repository strictly inside: ${PROJECT_ROOT}"
    git -C "${PROJECT_ROOT}" init
  fi
fi

if [[ ! -d "${PROJECT_ROOT}/.git" ]]; then
  echo "[WARNING] No .git directory found in ${PROJECT_ROOT}."
  echo "Run with '--init' to initialize Git safely inside '期未/' ONLY:"
  echo "  bash cicd_與_安全檢查範本/install_git_hooks.sh --init"
  exit 1
fi

HOOKS_DIR="${PROJECT_ROOT}/.git/hooks"
mkdir -p "${HOOKS_DIR}"

cat > "${HOOKS_DIR}/pre-commit" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
echo "[pre-commit] Running Taigi NCM Secret, PII & Copyright Check..."
python3 "${REPO_ROOT}/cicd_與_安全檢查範本/pre_push_security_check.py" --strict-ci

if command -v gitleaks >/dev/null 2>&1; then
  echo "[pre-commit] Running gitleaks staged scan..."
  gitleaks protect --staged --config="${REPO_ROOT}/.gitleaks.toml" --redact
fi
HOOK

cat > "${HOOKS_DIR}/pre-push" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
echo "[pre-push] 1/2 Running full Security, PII & Copyright Audit..."
python3 "${REPO_ROOT}/cicd_與_安全檢查範本/pre_push_security_check.py" --strict-ci

echo "[pre-push] 2/2 Running AI Compliance & Diff Review..."
python3 "${REPO_ROOT}/cicd_與_安全檢查範本/ai_pr_reviewer.py" --diff-mode workspace --strict
HOOK

chmod +x "${HOOKS_DIR}/pre-commit" "${HOOKS_DIR}/pre-push"
chmod +x "${SCRIPT_DIR}/pre_push_security_check.py" "${SCRIPT_DIR}/ai_pr_reviewer.py" "${SCRIPT_DIR}/install_git_hooks.sh"

echo "[OK] Installed pre-commit and pre-push hooks in: ${HOOKS_DIR}"
echo "[TIP] Optional: If using Python pre-commit framework, run 'pre-commit install --hook-type pre-commit --hook-type pre-push'."
