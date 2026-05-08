# What you provide (keys & accounts)

Paste these into your **hosting env UI** (Vercel, Fly, Railway, etc.) or a **local `.env` / `apps/web/.env.local`** — never commit real secrets to git.

## Required for any real deployment

| Name | What it is | You get it from |
|------|------------|-----------------|
| `DATABASE_URL` | Postgres connection string (with `pgvector`) | Neon, RDS, Supabase, self-hosted |
| `JWT_SECRET` | Long random string (32+ chars) | `openssl rand -base64 48` |
| `MASTER_KEY` | Exactly 32+ chars for envelope crypto (replace with KMS later for B2B) | Generate locally; plan cloud KMS for prod |
| `API_PUBLIC_URL` | Public base URL of the API (`https://api.yourco.com`) | Your DNS / reverse proxy |
| `CORS_ORIGINS` | Comma-separated web origins allowed to call the API | Your Next.js URL(s) |
| `REDIS_URL` | Redis connection string | Upstash, ElastiCache, Docker |

## Web (Next.js)

| Name | What it is |
|------|------------|
| `NEXT_PUBLIC_API_URL` | Same as public API base URL the browser will call |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk **publishable** key (`pk_test_…` / `pk_live_…`) |
| `CLERK_SECRET_KEY` | Clerk **secret** (server-only; set in Vercel env, not exposed to browser) |

Clerk powers `/sign-in` and `/sign-up` (hash routing). The FastAPI **memory API** still uses **JWT** from `/login` until you add a Clerk→JWT bridge.

In the [Clerk Dashboard](https://dashboard.clerk.com/) set allowed origins / redirect URLs for your dev and prod web URLs.

## Optional: real embeddings & chat

| Name | What it is |
|------|------------|
| `OPENAI_API_KEY` | For embeddings + optional chat pipelines |
| `ANTHROPIC_API_KEY` | If you wire Anthropic in code paths that use it |

Without `OPENAI_API_KEY`, local/dev may use fallbacks; production search quality usually needs a key.

## Optional: Stripe (paid plans / Checkout)

| Name | What it is |
|------|------------|
| `STRIPE_SECRET_KEY` | `sk_test_…` or `sk_live_…` |
| `STRIPE_WEBHOOK_SECRET` | Signing secret from Stripe Dashboard for your webhook endpoint |
| `STRIPE_PRICE_PRO` | Price id (e.g. `price_…`) for the Pro subscription |
| `BILLING_SUCCESS_URL` / `BILLING_CANCEL_URL` | Where Checkout returns users (must match your web app URLs) |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | `pk_test_…` or `pk_live_…` (browser-safe; for Stripe.js if you add it) |

Webhook URL: `https://<your-api-host>/v1/billing/webhook`

## B2B / enterprise (later — not env vars alone)

- **SSO:** Auth0, WorkOS, Clerk Enterprise, etc. (account + app registration).
- **Compliance:** DPA, subprocessors, SOC2 program — legal + vendor choices, not a single API key.

## Accounts to create (checklist)

- [ ] Postgres host
- [ ] Redis host  
- [ ] DNS + TLS for API + web  
- [ ] Stripe (if billing) — **test mode first**  
- [ ] OpenAI (if real vectors)

See also [`.env.example`](../.env.example) for variable names and [go-to-market-readiness.md](go-to-market-readiness.md) for the full B2B gap list.
