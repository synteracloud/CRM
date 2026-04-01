# Runtime Deployment Specification (B0-P04)

## 1) Scope and Goals

This document defines a **fully deployable runtime specification** for the CRM platform, covering:

- Environment configuration
- Build/package strategy
- Deployment architecture
- Infrastructure model
- Quality-control (QC) gates for deploy readiness

The target outcome is a repeatable, secure, observable, and rollback-safe deployment across development, staging, and production.

---

## 2) Environment Configuration

## 2.1 Environment Matrix

| Environment | Purpose | Data Class | SLA/SLO Target | Change Policy |
|---|---|---|---|---|
| `local` | Developer workflows and feature validation | Synthetic/dev fixtures | Best effort | Direct local iteration |
| `dev` | Shared integration and CI validation | Non-production | 99.0% availability | Auto deploy from mainline |
| `staging` | Pre-prod release candidate verification | Production-like masked data | 99.5% availability | Promotion-based, approval gate |
| `prod` | Customer-facing runtime | Production data | 99.9% availability | Change window + progressive rollout |

## 2.2 Runtime Environment Variables

All variables are validated at startup. Any missing required variable causes fail-fast boot rejection.

### Core Runtime

- `NODE_ENV` = `production|development|test`
- `PORT` = listener port (default `3000`)
- `LOG_LEVEL` = `debug|info|warn|error`
- `SERVICE_NAME` = logical service identifier
- `SERVICE_VERSION` = semantic version/build SHA
- `REGION` = deployment region identifier

### Database & Storage

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `DB_POOL_MIN`, `DB_POOL_MAX`, `DB_STATEMENT_TIMEOUT_MS`
- `REDIS_URL`
- `OBJECT_STORAGE_BUCKET`
- `OBJECT_STORAGE_REGION`

### Security / Identity

- `JWT_ISSUER`
- `JWT_AUDIENCE`
- `JWT_PUBLIC_KEY_URL`
- `ENCRYPTION_KMS_KEY_ID`
- `SECRETS_PROVIDER` = `vault|ssm|k8s-secret`

### Messaging / Async

- `EVENT_BUS_BROKERS`
- `EVENT_BUS_CLIENT_ID`
- `EVENT_BUS_TOPIC_PREFIX`
- `DLQ_ENABLED` = `true|false`

### External Integrations

- `PAYMENTS_BASE_URL`, `PAYMENTS_API_KEY`
- `EMAIL_BASE_URL`, `EMAIL_API_KEY`
- `WEBHOOK_SIGNING_SECRET`

### Observability

- `OTEL_EXPORTER_OTLP_ENDPOINT`
- `OTEL_RESOURCE_ATTRIBUTES`
- `METRICS_NAMESPACE`
- `TRACE_SAMPLING_RATIO`
- `ERROR_TRACKING_DSN`

## 2.3 Configuration Sources and Precedence

Order of precedence (high → low):

1. Runtime secret manager injection
2. Environment variables set by orchestrator
3. Environment-specific config file (immutable artifact)
4. Built-in defaults (non-sensitive only)

Rules:

- Secrets **must never** be committed to source control.
- Sensitive values must originate from secret manager only.
- Startup performs schema validation and redacts secret fields in logs.

## 2.4 Secret Rotation Policy

- Keys and credentials rotate every 90 days (or provider policy, whichever is stricter).
- Dual-key overlap window required for zero-downtime rotation.
- Rotation runbook includes validation checks, rollback, and audit evidence.

---

## 3) Packaging

## 3.1 Build Artifacts

Primary deployable unit is an OCI container image per service:

- `ghcr.io/<org>/crm-<service>:<semver>-<gitsha>`
- Immutable tagging required (`<gitsha>`)
- `latest` tag prohibited for production promotions

Secondary artifacts:

- SBOM (`spdx` or `cyclonedx`)
- Provenance attestation (SLSA-compatible)
- Migration bundle for schema updates

## 3.2 Docker/Container Standards

- Multi-stage builds (builder + runtime)
- Non-root runtime user
- Read-only root filesystem (except explicitly mounted writable volumes)
- Distroless/minimal base image preferred
- Healthcheck endpoint required (`/health/live`, `/health/ready`)

## 3.3 CI Packaging Pipeline

1. Install dependencies with lockfile verification
2. Lint + unit tests + static analysis
3. Build artifact and generate checksums
4. Build image and run container security scan
5. Generate SBOM and provenance
6. Push image + attestations to registry
7. Publish release metadata manifest

Any failed step blocks promotion.

## 3.4 Versioning and Release Semantics

- Semantic versioning for release channels
- Commit SHA is source-of-truth traceability key
- Release metadata must include:
  - Git SHA
  - CI pipeline run ID
  - Dependency lock hash
  - Migration version(s)
  - Feature flag profile for rollout

---

## 4) Deployment Architecture

## 4.1 Topology

- **Control Plane**: CI/CD, registry, IaC state, secrets policy, release orchestration
- **Data Plane**: Kubernetes workloads, databases, cache, messaging, ingress, observability agents

Each environment is isolated by namespace/account boundary and network segmentation.

## 4.2 Deployment Strategy

Production deploy strategy is progressive:

1. Deploy to `staging`
2. Run smoke + integration + synthetic checks
3. Manual approval gate
4. Canary rollout in `prod` (5% → 25% → 50% → 100%)
5. Auto-halt on SLO regressions

Rollback triggers:

- Error rate increase beyond threshold
- Latency p95 regression beyond threshold
- Failed readiness/liveness probes
- Business KPI anomaly alerts

Rollback method:

- Helm/Kustomize release rollback to prior revision
- Database migration rollback only when migration marked reversible
- For non-reversible migrations: activate compatibility mode and forward-fix

## 4.3 Kubernetes Runtime Baseline

For each service:

- Deployment with at least 2 replicas (prod)
- PodDisruptionBudget
- HorizontalPodAutoscaler (CPU + custom metric)
- Resource requests/limits set
- Startup, liveness, readiness probes configured
- ServiceAccount with least privilege RBAC
- NetworkPolicy default deny + explicit allow
- ConfigMap (non-secret) + Secret (secret refs only)

## 4.4 Edge and Traffic Management

- Ingress controller with TLS termination
- WAF policies on public endpoints
- Rate limiting and burst control
- mTLS for east-west service communication (service mesh or equivalent)
- API gateway for external contract governance and authn/authz enforcement

## 4.5 Data Migration and Compatibility

Deployment with schema change follows expand/contract model:

1. Expand schema (backward compatible)
2. Deploy app using old + new schema
3. Backfill data asynchronously
4. Flip reads/writes via feature flag
5. Contract old schema in later release

No destructive migration in same release as first code usage.

---

## 5) Infrastructure Model

## 5.1 Layered Infra Blueprint

### Layer 0 — Foundation

- Cloud account/project hierarchy
- VPC/VNet, subnets (public/private), NAT, route tables
- DNS zones and certificate authority integration
- KMS/HSM root keys
- IAM federation and baseline roles

### Layer 1 — Platform Services

- Kubernetes cluster(s)
- Container registry
- Secret manager
- Managed PostgreSQL (HA) + read replica strategy
- Managed Redis (HA)
- Message bus/streaming platform
- Object storage

### Layer 2 — Traffic & Security

- API gateway
- Ingress/load balancers
- WAF and DDoS protections
- Security groups / firewall policy
- Service mesh (optional but recommended for mTLS and traffic policy)

### Layer 3 — Application Runtime

- CRM microservices and supporting workers
- Cron/scheduled jobs
- Event consumers/producers
- Feature flags/config service integration

### Layer 4 — Operations & Reliability

- Centralized logs
- Metrics + alerting
- Distributed tracing
- On-call routing/escalation
- Backups + disaster recovery automation
- Compliance/audit trails

## 5.2 High Availability / DR Targets

- Multi-AZ required for production data stores and cluster control plane
- RPO target: ≤ 15 minutes
- RTO target: ≤ 60 minutes
- PITR enabled for relational database
- Daily backup restore verification in non-prod
- Quarterly disaster recovery game day

## 5.3 IaC Requirements

- Infrastructure managed through Terraform/Pulumi (single source of truth)
- No manual console drift allowed
- Drift detection job runs daily
- Every infra change linked to code review and change record

## 5.4 Capacity and Cost Controls

- Baseline sizing per environment with headroom targets
- Autoscaling guardrails (min/max)
- Budget alarms per environment/service
- Scheduled scale-down for non-prod off-hours

---

## 6) Security, Compliance, and Access Controls

- Least-privilege IAM for humans and workloads
- SSO + MFA mandatory for privileged roles
- Runtime secrets retrieved at start and rotated without restart where supported
- Audit logs immutable and retained per policy
- Image signing verification enforced at admission controller
- Admission policies block privileged containers and missing resource limits

---

## 7) Observability and Operational Readiness

## 7.1 Golden Signals

Track and alert on:

- Latency (p50/p95/p99)
- Traffic (RPS, queue depth)
- Errors (5xx, business-level failures)
- Saturation (CPU, memory, connection pools)

## 7.2 SLO Policies

- Service-level SLOs defined per critical endpoint
- Error budget burn alerts (fast + slow burn)
- Deploy pipeline integrated with SLO gating to pause rollout

## 7.3 Runbooks

Required runbooks:

- Service startup failure
- Elevated latency/error rate
- Dependency outage (DB/Redis/message bus)
- Secret rotation failure
- Rollback execution
- Regional failover

---

## 8) End-to-End Deployment Workflow

1. Developer merges PR to protected main branch
2. CI validates and packages immutable artifact
3. Artifact signs + attestation generation
4. Auto deploy to dev
5. Promote to staging with test gates
6. Approve release
7. Progressive deploy to prod
8. Post-deploy verification and monitoring hold period
9. Release marked successful and evidence archived

Deployment evidence retained:

- Artifact digest
- SBOM and scan reports
- Test summaries
- Approval record
- Runtime SLO snapshot post-deploy

---

## 9) Quality Control (QC) — Fix → Re-fix → 10/10

## 9.1 QC Checklist

A release is deployable only if all items pass:

- Environment config schema validation is green
- Required secrets resolved in target environment
- Package integrity, signature, and provenance verified
- IaC plan/apply completed with no unmanaged drift
- Staging smoke/integration tests passed
- Canary analysis within SLO limits
- Rollback path verified and executable
- Backup/restore status healthy
- Alerts and dashboards active for service
- Security policy/admission checks passed

## 9.2 Scoring Rubric

- 0–4: Incomplete (deployment blocked)
- 5–7: Partially ready (remediation required)
- 8–9: Ready with minor risk acceptance
- 10: Fully deployable, all control layers validated

## 9.3 Remediation Loop

When QC score < 10:

1. **Fix**: address failed gate(s)
2. **Re-fix**: rerun failed + dependent checks after remediation
3. **10/10**: release only when all mandatory controls pass

Mandatory: No production release permitted under score < 10.

---

## 10) Deliverable Validation

This specification is considered complete when:

- All four required build areas are explicitly defined:
  - env config
  - packaging
  - deployment architecture
  - infra model
- Every infra layer from foundation to operations is present
- Deployment workflow includes promotion, rollback, and QC gates
- QC loop enforces fix → re-fix → 10/10 release discipline

