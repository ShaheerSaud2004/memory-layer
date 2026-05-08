import Link from "next/link";
import "./landing.css";

export default function HomePage() {
  return (
    <div className="landing-root">
      <div className="lp-inner">
        <header className="lp-nav">
          <Link href="/" className="lp-mark">
            Memory Layer
          </Link>
          <nav className="lp-nav-links">
            <a href="#product">Product</a>
            <a href="#platform">Platform</a>
            <a href="#operators">Operators</a>
            <Link href="/login" className="lp-btn lp-btn-ghost">
              Sign in
            </Link>
            <Link href="/login" className="lp-btn lp-btn-primary">
              Open console
            </Link>
          </nav>
        </header>

        <section className="lp-hero">
          <div className="lp-hero-copy">
            <span className="lp-pill">Infrastructure, not a chatbot</span>
            <h1>Long-term memory your agents can actually retrieve.</h1>
            <p className="lp-lede">
              One persistent layer for preferences, project context, workflows, and transcripts. Hybrid search
              blends vectors with full-text, time, and importance so the right memory surfaces under load.
            </p>
            <div className="lp-hero-cta">
              <Link href="/login" className="lp-btn lp-btn-primary">
                Start in the console
              </Link>
              <Link href="/dashboard" className="lp-btn lp-btn-ghost">
                Dashboard
              </Link>
            </div>
            <p className="lp-trust">Postgres · pgvector · Row-level isolation · API-first</p>
          </div>

          <div className="lp-window" aria-hidden>
            <div className="lp-window-bar">
              <span className="lp-dot" />
              <span className="lp-dot" />
              <span className="lp-dot" />
              <span className="lp-window-title">workspace / hybrid retrieval</span>
            </div>
            <div className="lp-window-body">
              <div className="lp-mock-split">
                <div className="lp-mock-panel">
                  <div className="lp-mock-label">Incoming</div>
                  <div className="lp-mock-row">
                    <strong>Note</strong> · semantic
                    <br />
                    Ship retrieval as FTS + cosine + recency; tune weights per tenant.
                  </div>
                  <div className="lp-mock-row">
                    <strong>Transcript</strong> · episodic
                    <br />
                    Q2 planning call — decision: stay on pgvector in-cluster.
                  </div>
                </div>
                <div className="lp-mock-panel">
                  <div className="lp-mock-label">Ranked results</div>
                  <div className="lp-mock-row">
                    <span className="lp-score">0.842</span>
                    <strong>Chunk</strong> note / infra
                    <br />
                    …prefer pgvector for self-hosted hybrid retrieval.
                  </div>
                  <div className="lp-mock-row">
                    <span className="lp-score">0.791</span>
                    <strong>Summary</strong> meeting / strategy
                    <br />
                    …consolidated decisions from planning session.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="lp-section" id="product">
          <div className="lp-section-header">
            <h2>Built like data infrastructure, sold like a product.</h2>
            <p>
              The console is a thin layer on top of a real database model: typed memories, embeddings, edges,
              tags, and audit-friendly tenancy. That is what you need before you paste a logo on a pricing page.
            </p>
          </div>

          <div className="lp-showcase">
            <div>
              <p className="lp-caption">Memory graph</p>
              <div className="lp-window">
                <div className="lp-window-bar">
                  <span className="lp-dot" />
                  <span className="lp-dot" />
                  <span className="lp-dot" />
                  <span className="lp-window-title">graph / neighborhood</span>
                </div>
                <div className="lp-window-body">
                  <div className="lp-graph-dots">
                    <div className="lp-graph-node" />
                    <div className="lp-graph-line" />
                    <div className="lp-graph-node mid" />
                    <div className="lp-graph-line" />
                    <div className="lp-graph-node" />
                  </div>
                  <p style={{ fontSize: "0.8rem", color: "var(--lp-muted)", margin: 0, lineHeight: 1.5 }}>
                    Edges carry provenance: supersedes, derived_from, part_of. Your UI and agents stay honest about
                    what replaced what.
                  </p>
                </div>
              </div>
            </div>
            <div>
              <p className="lp-caption">Agent scopes</p>
              <div className="lp-window">
                <div className="lp-window-bar">
                  <span className="lp-dot" />
                  <span className="lp-dot" />
                  <span className="lp-dot" />
                  <span className="lp-window-title">agents / policy</span>
                </div>
                <div className="lp-window-body">
                  <div className="lp-mock-panel" style={{ background: "#0a0b0d" }}>
                    <div className="lp-mock-label">Service principal</div>
                    <div className="lp-mock-row">
                      <strong>deploy-bot</strong>
                      <br />
                      Read: <span style={{ color: "var(--lp-text)" }}>note, workflow</span> · Tags:{" "}
                      <span style={{ color: "var(--lp-text)" }}>infra, runbooks</span>
                      <br />
                      Write: off
                    </div>
                    <div className="lp-mock-row">
                      <strong>crm-sync</strong>
                      <br />
                      Read/write within <span style={{ color: "var(--lp-text)" }}>namespace: crm/*</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="lp-section" id="platform">
          <div className="lp-section-header">
            <h2>What ships in the repo today.</h2>
            <p>
              Honest scope: this is a strong MVP for a technical buyer or design partner. It is not yet a
              full B2B motion on its own.
            </p>
          </div>
          <div className="lp-bento">
            <article className="lp-bento-card span-7">
              <h3>In the box</h3>
              <p>
                FastAPI with OpenAPI, JWT and agent API keys, hybrid memory search, RLS-scoped Postgres, Next.js
                console with search and graph view, Docker Compose for local parity, TypeScript SDK stub.
              </p>
            </article>
            <article className="lp-bento-card span-5">
              <h3>Before you bill enterprises</h3>
              <p>
                You will still want billing (Stripe), org SSO (SAML/OIDC), usage metering, SOC2 narrative, backup
                / DR runbooks, and hardening review. We document that gap so you do not mistake MVP for
                procurement-ready.
              </p>
            </article>
            <article className="lp-bento-card span-6">
              <h3>API, not lock-in</h3>
              <p>
                Memories are yours in standard Postgres. Swap embedding models, add Pinecone later, or mirror to
                a warehouse without rewriting your product semantics.
              </p>
            </article>
            <article className="lp-bento-card span-6">
              <h3>One request</h3>
              <div className="lp-code">{`POST /v1/memories/search
Authorization: Bearer …
{ "query": "what did we decide about embeddings?", "limit": 10 }`}</div>
            </article>
          </div>
        </section>

        <section className="lp-section" id="operators">
          <div className="lp-section-header">
            <h2>For teams who outgrew prompt stuffing.</h2>
            <p>
              If your agents forget state across tickets, runs, and customer workspaces, you need a memory layer
              with retrieval you can explain — not a longer system prompt.
            </p>
          </div>
        </section>

        <footer className="lp-footer">
          <span>Memory Layer — persistent context for agents</span>
          <span>
            <Link href="/login">Console</Link>
            &nbsp;·&nbsp;
            <Link href="/dashboard">Dashboard</Link>
          </span>
        </footer>
      </div>
    </div>
  );
}
