#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-qc}"
ROOT_DIR="${ROOT_DIR:-/workspace}"
INFRA_DIR="${INFRA_DIR:-${ROOT_DIR}/infra}"
K8S_DIR="${K8S_DIR:-${ROOT_DIR}/deployment/k8s}"

log() {
  printf '[infra-run] %s\n' "$*"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "Missing required command: $1"
    exit 1
  fi
}

validate_infra() {
  require_cmd terraform
  require_cmd helm
  require_cmd kubectl

  if [[ -d "${INFRA_DIR}" ]]; then
    log "Running terraform fmt and validate in ${INFRA_DIR}"
    terraform -chdir="${INFRA_DIR}" fmt -recursive -check
    terraform -chdir="${INFRA_DIR}" init -backend=false
    terraform -chdir="${INFRA_DIR}" validate
  else
    log "Skipping terraform checks (no ${INFRA_DIR} directory present)"
  fi

  if [[ -d "${K8S_DIR}" ]]; then
    log "Rendering kubernetes manifests from ${K8S_DIR}"
    find "${K8S_DIR}" -type f \( -name '*.yaml' -o -name '*.yml' \) -print0 | xargs -0 -r yq e '.' >/dev/null
  else
    log "Skipping kubernetes checks (no ${K8S_DIR} directory present)"
  fi
}

run_qc() {
  require_cmd bash
  local qc_script="${ROOT_DIR}/scripts/deployment/qc_gate.sh"
  if [[ ! -x "${qc_script}" ]]; then
    log "Missing executable QC script: ${qc_script}"
    exit 1
  fi
  "${qc_script}"
}

case "${MODE}" in
  validate)
    validate_infra
    ;;
  qc)
    validate_infra
    run_qc
    ;;
  *)
    log "Unknown mode '${MODE}'. Expected one of: validate, qc"
    exit 1
    ;;
esac
