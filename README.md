# AI Memory Layer

Production-oriented monorepo for persistent AI memory: FastAPI + Postgres (pgvector) + Redis + Next.js dashboard.

## Production and B2B readiness

**This codebase is a strong technical MVP** for builders and design partners. It is **not procurement-ready B2B SaaS** out of the box: you still need billing, enterprise identity, compliance narrative, ops, and scale controls for that story.

**Checklist (use as your roadmap):** [docs/go-to-market-readiness.md](docs/go-to-market-readiness.md) — billing, SSO, metering, compliance, runbooks, abuse/scale, support, and a suggested phase order.

**Secrets you must set (by environment):** [docs/you-provide.md](docs/you-provide.md).

---

## Quickstart (Docker)

```bash
cp .env.example .env
docker compose up --build
```

- API: [http://localhost:8000](http://localhost:8000) (OpenAPI: [/docs](http://localhost:8000/docs))
- Web: [http://localhost:3000](http://localhost:3000)

Register a workspace at `/login`, then open `/dashboard` to create and search memories.

## Local development (API + web)

Requires **Python 3.12+** (this repo is tested on **3.14** with `psycopg[binary]` and `pydantic>=2.12`).

1. Start Postgres + Redis via Docker Compose (`docker compose up postgres redis`).
2. Export `DATABASE_URL`, `JWT_SECRET` (32+ chars), `MASTER_KEY` (32+ chars).
3. API:

```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://memory:memory@localhost:5432/memory
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

4. Web:

```bash
cd apps/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

`npm run dev` picks a **free port** on `127.0.0.1` and prints the URL (avoids clashes when 3000/3001 are busy). Use `npm run dev:3000` for a fixed port. The API allows localhost on any port when `CORS_ALLOW_LOCALHOST_ANY_PORT=true` (default).

Open `/billing` (while signed in) to start Stripe Checkout. Configure `STRIPE_SECRET_KEY`, `STRIPE_PRICE_PRO` (a recurring Price id), and `STRIPE_WEBHOOK_SECRET` on the API; point the Stripe webhook to `https://<your-api-host>/v1/billing/webhook`. JWT login is unchanged.

**Deploy (Vercel + hosted API):** [docs/integrations.md](docs/integrations.md) — set Vercel **Root Directory** to `apps/web`, add **`NEXT_PUBLIC_API_URL`** (public HTTPS base of your FastAPI deployment), Clerk keys, redeploy after changing `NEXT_PUBLIC_*`. On the API host, add your `https://*.vercel.app` origins to **`CORS_ORIGINS`**. After deploy, open **`/status`** on the site to confirm **`/healthz`** is reachable from Vercel.

## Tests

```bash
cd apps/api
pytest -q
```

Set `INTEGRATION=1` and ensure Postgres is reachable via `DATABASE_URL` to run `tests/test_integration_memory.py`.

## Security notes

- Tenant isolation is enforced with Postgres RLS on memory data tables; API sets `SET LOCAL app.current_tenant_id` per request.
- JWT auth for users; agents use `X-API-Key`.
- Field-level encryption helpers live in `apps/api/app/services/crypto.py` (dev `MASTER_KEY`; use KMS in production).

See also [docs/architecture.md](docs/architecture.md) and [docs/api.md](docs/api.md).
