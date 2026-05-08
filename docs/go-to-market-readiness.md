# Go-to-market and production readiness

This document is the **honest boundary** between what this repository is today (a strong technical MVP) and what **procurement-grade B2B SaaS** typically requires. Use it as a working checklist, not marketing copy.

**Environment variables and accounts you must supply:** [you-provide.md](you-provide.md).

---

## What already works (design-partner / self-host MVP)

| Capability | Status |
|------------|--------|
| Workspace (tenant) model | Yes |
| Postgres RLS on memory-related tables | Yes |
| User JWT auth + agent API keys with scopes | Yes |
| Hybrid retrieval (vector + FTS + recency + importance) | Yes |
| Memory CRUD, tags, graph neighborhood API | Yes |
| Operator console (Next.js) | Yes |
| OpenAPI / Docker-oriented API | Yes |
| Field encryption helpers (dev-oriented; KMS path documented in architecture) | Partial |

---

## B2B SaaS gap checklist

Work through these before telling a Fortune 500 buyer you are “production SaaS” for their standard vendor process.

### 1. Billing and entitlements

- [ ] **Plans and packaging** — Free / Pro / Enterprise (or usage-based) defined on paper.
- [ ] **Payment provider** — Stripe (or equivalent): checkout, invoices, tax, dunning.
- [ ] **Entitlements** — Seat limits, API quotas, feature flags (e.g. SSO only on Enterprise) enforced in **code**, not sales slides.
- [ ] **Usage metering** — Counts you can bill on: API calls, memories stored, embedding tokens, search queries; stored in a billing-grade store with idempotency.

### 2. Identity and access (enterprise)

- [ ] **OIDC / SAML SSO** — Work with customer IdP (Okta, Azure AD, Google Workspace SAML).
- [ ] **Domain / email verification** — Optional claim flow for `company.com` → org.
- [ ] **SCIM provisioning** (usually Enterprise tier) — User/group sync into your app.
- [ ] **Org hierarchy** — Multiple workspaces per billing account, roles (owner / admin / member) with documented matrix.
- [ ] **Service account lifecycle** — Agent keys: rotation, expiry, last-used audit.

### 3. Security and compliance story

- [ ] **Threat model** — Written document: tenants, secrets, data at rest, supply chain.
- [ ] **Key management** — Customer DEK / KMS story (not a single `MASTER_KEY` in env).
- [ ] **Vulnerability process** — Disclosure email, SLA for patches, dependency scanning in CI.
- [ ] **SOC 2 Type II** (or equivalent) — If enterprise sales motion: roadmap + current controls mapping.
- [ ] **Data processing** — DPA template, subprocessors list, region / data residency if you promise it.
- [ ] **Customer audit logs** — Export or SIEM-friendly events beyond internal `audit_logs` (retention, immutability options).

### 4. Reliability and operations

- [ ] **SLA definition** — Uptime target and what is excluded; status page (e.g. Better Stack, Atlassian Statuspage).
- [ ] **Backups** — Automated Postgres backups; **tested** restore (quarterly drill logged).
- [ ] **Runbooks** — On-call: incident severity, rollback, comms template, who pages whom.
- [ ] **Observability** — Structured logs, metrics, tracing; per-tenant request IDs in support tickets.
- [ ] **Multi-region** — Only if you sell it: RPO/RTO, failover, and honest limits.

### 5. Scale and abuse

- [ ] **Rate limiting** — Per tenant / per API key; configurable limits by plan.
- [ ] **Load testing** — Baseline for search + ingest under concurrent load; document breaking points.
- [ ] **Async ingestion** — Queue (e.g. Redis, SQS) for large files / batch embed jobs; backpressure.
- [ ] **Cost controls** — Caps on embedding spend or LLM calls per tenant.

### 6. Product and support

- [ ] **Admin / support tools** — Read-only tenant lookup, impersonation with audit (if allowed by policy).
- [ ] **Documentation** — Deployment guide, API limits, security whitepaper stub.
- [ ] **Legal** — Terms of Service, Privacy Policy, acceptable use (even if v0).

---

## Suggested sequencing (pragmatic)

| Phase | Focus | Why |
|-------|--------|-----|
| **0 — Now** | Design partners on self-host or single-tenant managed | Prove retrieval + data model with real workloads. |
| **1 — Revenue gate** | Billing + plan enforcement + basic metering | Nothing else matters if you cannot charge cleanly. |
| **2 — Enterprise gate** | SSO + org model + audit log export | Unlocks mid-market and regulated pilots. |
| **3 — Trust gate** | SOC2 path, KMS, backup drills, status page | Unlocks procurement and security questionnaires. |
| **4 — Scale gate** | Queues, rate limits, load-tested SLOs | Survives hype and bad neighbors on shared infra. |

---

## How this repo relates to the checklist

- **Accelerates phase 0** — You can ship integrations and demos quickly.
- **Does not replace phases 1—to—4** — Those are product and company investments, not a few pull requests in a starter repo.

When the checklist above is mostly green **for the tier you sell**, you can credibly call the offering **B2B SaaS** at that tier. Until then, **“technical MVP + design-partner base”** is the accurate positioning.
