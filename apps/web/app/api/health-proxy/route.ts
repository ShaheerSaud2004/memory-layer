import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/**
 * Server-side reachability check to the FastAPI host (no browser CORS).
 * Use /status in the UI and after Vercel deploys.
 */
export async function GET() {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (!raw) {
    return NextResponse.json(
      {
        ok: false,
        step: "env",
        message:
          "NEXT_PUBLIC_API_URL is not set. In Vercel: Project → Settings → Environment Variables → add your public API base URL (no trailing slash).",
      },
      { status: 503 }
    );
  }

  const base = raw.replace(/\/$/, "");
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 10_000);
    const res = await fetch(`${base}/healthz`, { signal: ctrl.signal, cache: "no-store" });
    clearTimeout(timer);
    const text = await res.text();
    let health: unknown;
    try {
      health = JSON.parse(text) as unknown;
    } catch {
      health = text;
    }
    return NextResponse.json({
      ok: res.ok,
      apiBase: base,
      status: res.status,
      health,
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);
    return NextResponse.json(
      {
        ok: false,
        apiBase: base,
        step: "network",
        message,
        hint:
          "Host FastAPI separately (Docker, Fly.io, Railway, Render, etc.), expose HTTPS, then set NEXT_PUBLIC_API_URL. On the API, set CORS_ORIGINS to your Vercel preview + production URLs.",
      },
      { status: 502 }
    );
  }
}
