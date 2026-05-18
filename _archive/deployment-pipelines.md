# Deployment Pipelines (B1-P05)

This repository implements an end-to-end runtime + infrastructure deployment pipeline via `.github/workflows/deploy-runtime.yml`.

## Included pipelines

1. **Runtime packaging**
   - Builds runtime image
   - Pushes immutable image tag based on branch + commit SHA
   - Generates SBOM artifact
2. **Infra tooling packaging (`docker/infra`)**
   - Builds infra utility image with `terraform`, `kubectl`, `helm`, `yq`
   - Pushes immutable image tag based on branch + commit SHA
3. **Environment deployment flow**
   - `dev` deployment + schema validation + IaC validation
   - `staging` deployment + smoke/integration/synthetic checks + QC gate
   - `prod` manual approval + progressive rollout + rollback/backup/observability gates

## QC discipline (Fix → Re-fix → 10/10)

The gate script `scripts/deployment/qc_gate.sh` executes two full passes:

- **Fix pass**: validates all mandatory deployment controls exist.
- **Re-fix pass**: reruns same controls to ensure remediations are durable.

Release is blocked unless both passes score **10/10**.

## Deployable end-to-end criteria

The implementation is considered deployable when:

- Runtime env schema validation is wired for each environment.
- Runtime and infra images are packageable and publishable.
- Staging verification and production progressive rollout are enforced.
- Rollback, backup/restore, and observability hold steps are present.
- QC gate blocks release when any required step is missing.
