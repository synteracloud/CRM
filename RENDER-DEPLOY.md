# Pakistan CRM — Render.com Deployment Guide (C4)

## One-Click Deploy via Blueprint

1. Go to **https://dashboard.render.com**
2. Click **New → Blueprint**
3. Connect your GitHub repo: `synteracloud/CRM`
4. Render detects `render.yaml` automatically
5. Click **Apply** — all 5 services are created on the **free plan**:
   - `crm-gateway` (Node.js web service)
   - `crm-services` (Python web service)
   - `crm-frontend` (static site)
   - `crm-postgres` (PostgreSQL, free = 256MB, 90-day expiry)
   - `crm-redis` (Redis, free = 25MB, 30-day expiry)

## Post-Deploy: Run Alembic Migrations

Once `crm-postgres` is created, run migrations via the Render shell:

1. In Render dashboard → `crm-services` → **Shell**
2. Run:
   ```bash
   cd /app
   alembic upgrade head
   ```
3. Verify: `alembic current` should show `0010 (head)`

## Post-Deploy: Seed Dev Data (optional)

In the Render shell for `crm-gateway`:
```bash
# The seed SQL must be run against the Render PostgreSQL
psql $DATABASE_URL -f seed_c1.sql
psql $DATABASE_URL -f seed_tenant_refs.sql
```

## Set GitHub Actions Variables (for CI/CD auto-deploy)

In your GitHub repo → **Settings → Environments**:

### staging environment
| Variable | Value |
|---|---|
| `RENDER_DEPLOY_HOOK_GATEWAY` | Render deploy hook URL for crm-gateway |
| `RENDER_DEPLOY_HOOK_SERVICES` | Render deploy hook URL for crm-services |
| `RENDER_STAGING_URL` | https://crm-gateway.onrender.com |

### production environment  
| Variable | Value |
|---|---|
| `RENDER_PROD_HOOK_GATEWAY` | Render production deploy hook URL |
| `RENDER_PROD_HOOK_SERVICES` | Render production deploy hook URL |

**To get deploy hook URLs:** Render dashboard → service → Settings → Deploy Hook → Copy URL

## C4 Gate Verification

Once deployed, run this from your local machine:
```bash
curl https://crm-gateway.onrender.com/health
# Expected: {"status":"ok","version":"1.0.0","uptime":...}
```

## Free Tier Limitations

| Service | Free Limit | Note |
|---|---|---|
| Web services | Sleep after 15min inactivity | First request after sleep takes ~30s |
| PostgreSQL | 256MB, expires 90 days | Upgrade to Starter ($7/mo) before expiry |
| Redis | 25MB, expires 30 days | Upgrade to Starter ($10/mo) before expiry |
| Static site | Always free | No limitation |

## Upgrade Path (before 90-day expiry)

In Render dashboard → service → Settings → Plan → change to **Starter**.
PostgreSQL Starter: $7/month | Redis Starter: $10/month | Web Starter: $7/month each.
