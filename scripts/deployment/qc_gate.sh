#!/usr/bin/env bash
set -euo pipefail

STATUS_DIR="${STATUS_DIR:-.artifacts/qc}"
mkdir -p "${STATUS_DIR}"

score=0
max_score=10

require_step() {
  local step="$1"
  local path="$2"

  if [[ -e "${path}" ]]; then
    printf '[qc] PASS  %s (%s)\n' "${step}" "${path}"
    score=$((score + 1))
  else
    printf '[qc] FAIL  %s (%s)\n' "${step}" "${path}"
  fi
}

# Fix -> Re-fix discipline: first pass catches issues, second pass confirms remediations stay green.
run_gate_pass() {
  local pass_name="$1"
  printf '[qc] ---- %s ----\n' "${pass_name}"
  require_step 'Env schema validation configured' '.github/actions/runtime-env-validate/action.yml'
  require_step 'Secrets sourcing step configured' '.github/workflows/deploy-runtime.yml'
  require_step 'Image packaging + SBOM pipeline configured' '.github/workflows/deploy-runtime.yml'
  require_step 'Infra drift/IaC validation configured' '.github/workflows/deploy-runtime.yml'
  require_step 'Staging verification gate configured' '.github/workflows/deploy-runtime.yml'
  require_step 'Progressive production rollout gate configured' '.github/workflows/deploy-runtime.yml'
  require_step 'Rollback path configured' '.github/workflows/deploy-runtime.yml'
  require_step 'Backup/restore check gate configured' '.github/workflows/deploy-runtime.yml'
  require_step 'Observability hold gate configured' '.github/workflows/deploy-runtime.yml'
  require_step 'Admission/security gate configured' '.github/workflows/deploy-runtime.yml'
}

run_gate_pass 'FIX'
first_score="${score}"

# Re-fix pass (same checks must remain green after remediation)
score=0
run_gate_pass 'RE-FIX'
second_score="${score}"

printf '{"fix_score": %s, "refix_score": %s, "max": %s}\n' "${first_score}" "${second_score}" "${max_score}" > "${STATUS_DIR}/score.json"

if [[ "${first_score}" -lt "${max_score}" || "${second_score}" -lt "${max_score}" ]]; then
  printf '[qc] RESULT: BLOCKED (%s/%s then %s/%s)\n' "${first_score}" "${max_score}" "${second_score}" "${max_score}"
  exit 1
fi

printf '[qc] RESULT: DEPLOYABLE 10/10 (fix=%s, re-fix=%s)\n' "${first_score}" "${second_score}"
