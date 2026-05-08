"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type ProxyPayload =
  | { ok: true; apiBase: string; status: number; health: unknown }
  | { ok: false; step: string; message?: string; hint?: string; apiBase?: string };

export default function StatusPage() {
  const [data, setData] = useState<ProxyPayload | null>(null);
  const [loading, setLoading] = useState(true);

  const publicApi = process.env.NEXT_PUBLIC_API_URL || "";
  const clerkPub = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || "";
  const stripePub = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || "";

  useEffect(() => {
    void (async () => {
      try {
        const res = await fetch("/api/health-proxy", { cache: "no-store" });
        setData((await res.json()) as ProxyPayload);
      } catch (e) {
        setData({
          ok: false,
          step: "client",
          message: e instanceof Error ? e.message : String(e),
        });
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  function mask(s: string, keep = 10) {
    if (!s) return "—";
    if (s.length <= keep) return "•••";
    return `${s.slice(0, keep)}…`;
  }

  return (
    <main style={{ maxWidth: 720, margin: "40px auto", padding: "0 20px" }}>
      <div className="row" style={{ justifyContent: "space-between", alignItems: "baseline" }}>
        <h1 style={{ margin: 0, fontSize: "1.65rem" }}>Deploy status</h1>
        <Link href="/">Home</Link>
      </div>
      <p className="muted" style={{ marginTop: 8 }}>
        Vercel runs this Next.js app only. Your <strong>FastAPI + Postgres</strong> API must be reachable at{" "}
        <code>NEXT_PUBLIC_API_URL</code> for the console to work end-to-end.
      </p>

      <div className="card" style={{ marginTop: 20 }}>
        <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>API reachability</h2>
        {loading ? <p className="muted">Checking…</p> : null}
        {!loading && data?.ok === true ? (
          <p style={{ color: "#7dffb3", margin: 0 }}>
            OK — <code>{data.apiBase}</code> returned {data.status} · {JSON.stringify(data.health)}
          </p>
        ) : null}
        {!loading && data && !("ok" in data && data.ok) ? (
          <div>
            <p style={{ color: "#ffb4b4", marginTop: 0 }}>{data.message ?? "API check failed"}</p>
            {"hint" in data && data.hint ? <p className="muted">{data.hint}</p> : null}
            {"step" in data && data.step ? (
              <p className="muted" style={{ fontSize: 13 }}>
                Step: <code>{data.step}</code>
              </p>
            ) : null}
          </div>
        ) : null}
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Browser env (masked)</h2>
        <ul className="muted" style={{ margin: 0, paddingLeft: 20, lineHeight: 1.8 }}>
          <li>
            <code>NEXT_PUBLIC_API_URL</code>: {publicApi ? <code>{publicApi}</code> : <strong style={{ color: "#ffb4b4" }}>missing</strong>}
          </li>
          <li>
            <code>NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY</code>: {mask(clerkPub)}
          </li>
          <li>
            <code>NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY</code>: {mask(stripePub)}
          </li>
        </ul>
        <p className="muted" style={{ fontSize: 13, marginBottom: 0, marginTop: 12 }}>
          Server-only secrets (Clerk secret, etc.) are set in Vercel but never appear here — that is expected.
        </p>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Docs</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          In your clone: <code>docs/integrations.md</code> — Vercel root <code>apps/web</code>, env vars, Clerk URLs,
          Discord webhook.
        </p>
      </div>
    </main>
  );
}
