"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

const api = () => process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Status = {
  plan: string;
  subscription_status: string | null;
  stripe_customer_id: string | null;
};

async function readErrorBody(res: Response): Promise<string> {
  const text = await res.text();
  try {
    const j = JSON.parse(text) as { detail?: unknown };
    if (j.detail == null) return text || res.statusText;
    if (typeof j.detail === "string") return j.detail;
    return JSON.stringify(j.detail);
  } catch {
    return text || res.statusText;
  }
}

export default function BillingPage() {
  const token = useMemo(() => (typeof window !== "undefined" ? localStorage.getItem("aml_token") : null), []);
  const [status, setStatus] = useState<Status | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);

  const loadStatus = useCallback(async () => {
    if (!token) return;
    const res = await fetch(`${api()}/v1/billing/status`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      setErr(await readErrorBody(res));
      return;
    }
    setErr(null);
    setStatus(await res.json());
  }, [token]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const p = new URLSearchParams(window.location.search);
    if (p.get("success") === "1") {
      setBanner("Checkout complete — updating your plan (may take a few seconds)…");
    } else if (p.get("canceled") === "1") {
      setBanner("Checkout was canceled. You can try again anytime.");
    }
  }, []);

  useEffect(() => {
    void loadStatus();
  }, [loadStatus]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const p = new URLSearchParams(window.location.search);
    if (p.get("success") !== "1" || !token) return;
    let n = 0;
    const id = window.setInterval(() => {
      n += 1;
      void loadStatus();
      if (n >= 5) window.clearInterval(id);
    }, 2000);
    const clean = window.setTimeout(() => {
      window.history.replaceState({}, "", "/billing");
      window.clearInterval(id);
    }, 12000);
    return () => {
      window.clearInterval(id);
      window.clearTimeout(clean);
    };
  }, [token, loadStatus]);

  async function startCheckout() {
    if (!token) return;
    setBusy(true);
    setErr(null);
    try {
      const res = await fetch(`${api()}/v1/billing/checkout-session`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });
      if (!res.ok) {
        setErr(await readErrorBody(res));
        return;
      }
      const data = (await res.json()) as { url: string };
      window.location.href = data.url;
    } finally {
      setBusy(false);
    }
  }

  if (!token) {
    return (
      <main>
        <div className="card">
          <p>
            No token found. Please <Link href="/login">sign in</Link>.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <div>
          <h2 style={{ margin: "0 0 6px" }}>Billing</h2>
          <div className="muted">Pro unlocks API agents and the memory optimizer. Login stays email + JWT.</div>
        </div>
        <Link href="/dashboard">Dashboard</Link>
      </div>

      {banner ? (
        <div className="card" style={{ marginTop: 14, border: "1px solid #2a3f5c", background: "#121a28" }}>
          {banner}
        </div>
      ) : null}

      {err ? <pre style={{ color: "#ffb4b4", whiteSpace: "pre-wrap", marginTop: 12 }}>{err}</pre> : null}

      <div className="card" style={{ marginTop: 18 }}>
        <h3 style={{ marginTop: 0 }}>Current plan</h3>
        {status ? (
          <ul className="muted" style={{ margin: 0, paddingLeft: 18 }}>
            <li>
              Plan: <strong>{status.plan}</strong>
            </li>
            <li>Subscription: {status.subscription_status ?? "—"}</li>
            <li>Stripe customer: {status.stripe_customer_id ?? "—"}</li>
          </ul>
        ) : (
          <p className="muted">Loading…</p>
        )}
        <p className="muted" style={{ fontSize: 13, marginTop: 12 }}>
          Checkout requires workspace owner or admin. After payment, webhooks update this tenant to <code>pro</code>.
        </p>
        <button className="primary" type="button" style={{ marginTop: 14 }} disabled={busy} onClick={() => void startCheckout()}>
          {busy ? "Redirecting…" : "Upgrade to Pro (Stripe Checkout)"}
        </button>
      </div>
    </main>
  );
}
