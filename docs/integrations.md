# Vercel, Clerk, and Discord

The **product** is two services:

| Piece | Where it runs | Role |
|-------|----------------|------|
| **This Next.js app** | **Vercel** (`apps/web`) | Marketing, login, Clerk UI, dashboard UI, billing UI |
| **FastAPI + Postgres + Redis** | **Your host** (Fly, Railway, Render, VPS, K8s, …) | `/v1/*` API, embeddings, RLS, Stripe webhooks |

You cannot put Postgres inside the Next build. Point **`NEXT_PUBLIC_API_URL`** at the **public HTTPS URL** of your API. On the API host, set **`CORS_ORIGINS`** to your Vercel URLs.

---

## Vercel (Next.js · root directory `apps/web`)

### One-time

1. Import the GitHub repo: [vercel.com/new](https://vercel.com/new).
2. **Root Directory:** **`apps/web`** (critical for this monorepo).
3. **Framework preset:** Next.js.
4. **Build:** `npm run build` (default). **Output:** default (`.next`).
5. Deploy. Every push to `main` (or your production branch) redeploys.

### Environment variables (Vercel → Project → Settings → Environment Variables)

Add for **Production** and **Preview** as appropriate:

| Name | Value example | Required |
|------|----------------|----------|
| `NEXT_PUBLIC_API_URL` | `https://api.yourdomain.com` | **Yes** for a working console |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_live_…` or `pk_test_…` | If you use Clerk pages |
| `CLERK_SECRET_KEY` | `sk_live_…` or `sk_test_…` | If you use Clerk (server) |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | `pk_live_…` | Optional (Stripe.js / future) |

**Do not** put `CLERK_SECRET_KEY` in `NEXT_PUBLIC_*`.

After changing env vars, **redeploy** (Deployments → … → Redeploy) so clients pick up new `NEXT_PUBLIC_*` values.

### Copy-paste checklist (API side, not Vercel)

On the machine that runs **FastAPI**, set at least:

- `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `MASTER_KEY`
- `CORS_ORIGINS` — include your **custom domain** and any fixed Vercel host you use, comma-separated
- **`CORS_INCLUDE_VERCEL_APP_HOST=true`** (optional) — allows **`https://*.vercel.app`** (all preview + `.vercel.app` production) without listing each URL. Still set **`CORS_ORIGINS`** for `www.` / apex.
- Stripe: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PRO` if you use billing

See also [`.env.example`](.env.example) and [you-provide.md](you-provide.md).

### Verify after deploy

Open **`https://<your-vercel-app>/status`**. It calls `/api/health-proxy`, which hits **`NEXT_PUBLIC_API_URL/healthz`** from the server. Green = API reachable from Vercel.

---

## Fly.io (API container)

Repo includes **[`fly.toml`](../fly.toml)** at the **monorepo root** using **`docker/Dockerfile.api`**.

1. [Install flyctl](https://fly.io/docs/hands-on/install-flyctl/) and `fly auth login`.
2. Edit **`fly.toml`** `app = "..."` to a unique name (or run `fly launch` and merge config).
3. Provision **Postgres (pgvector)** + **Redis** (Fly, Neon, Upstash, …).
4. `fly secrets set DATABASE_URL="postgresql+psycopg://..." REDIS_URL="redis://..." JWT_SECRET="..." MASTER_KEY="..." CORS_ORIGINS="https://yourdomain.com" CORS_INCLUDE_VERCEL_APP_HOST=true` (+ Stripe/OpenAI as needed).
5. `fly deploy` — set Vercel **`NEXT_PUBLIC_API_URL`** to **`https://<app>.fly.dev`** (or custom domain on Fly).

---

## Clerk (production + preview)

1. [Clerk Dashboard](https://dashboard.clerk.com/) → your application.
2. Add **Frontend API / authorized origins / redirect URLs** for:
   - `https://<project>.vercel.app`
   - Your custom domain (if any)
   - Local dev: `http://localhost:3000` or `http://127.0.0.1:3000`
3. Use matching **`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`** / **`CLERK_SECRET_KEY`** in Vercel for that environment.

**Note:** Clerk sign-in and **email/JWT workspace login** are separate today; the dashboard uses the **JWT** from `/login` until you add a Clerk→API bridge.

---

## Discord (push to `main` → GitHub Action)

1. Discord channel → **Integrations → Webhooks** → create webhook → copy URL.
2. GitHub repo → **Settings → Secrets and variables → Actions** → **`DISCORD_WEBHOOK_URL`**.
3. Push to `main`. Workflow [`.github/workflows/discord-notify.yml`](../.github/workflows/discord-notify.yml) posts a short message (skipped if secret missing).

If the webhook leaks, delete and recreate it in Discord.

---

## Optional: Vercel ↔ Discord without GitHub

Use a **Vercel Deployment Webhook** to a worker, or a third-party connector. The Action above is the smallest path if you already use GitHub.
