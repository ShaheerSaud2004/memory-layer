"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

const api = () => process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password123");
  const [workspace, setWorkspace] = useState("My workspace");
  const [mode, setMode] = useState<"login" | "register">("register");
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setError(null);
    const path = mode === "login" ? "/v1/auth/login" : "/v1/auth/register";
    const body =
      mode === "login"
        ? { email, password }
        : { email, password, workspace_name: workspace };
    const res = await fetch(`${api()}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      setError((await res.json().catch(() => ({})))?.detail || res.statusText);
      return;
    }
    const data = await res.json();
    localStorage.setItem("aml_token", data.access_token);
    router.push("/dashboard");
  }

  return (
    <main>
      <div className="card" style={{ maxWidth: 520, margin: "48px auto" }}>
        <h2 style={{ marginTop: 0 }}>{mode === "login" ? "Sign in" : "Create account"}</h2>
        {error ? (
          <pre
            style={{
              padding: 12,
              borderRadius: 10,
              border: "1px solid #3a2323",
              background: "#1b1010",
              color: "#ffb4b4",
              whiteSpace: "pre-wrap",
            }}
          >
            {typeof error === "string" ? error : JSON.stringify(error)}
          </pre>
        ) : null}
        <div style={{ display: "grid", gap: 10, marginTop: 12 }}>
          <label className="muted">
            Email
            <input style={{ width: "100%", marginTop: 6 }} value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label className="muted">
            Password
            <input
              style={{ width: "100%", marginTop: 6 }}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          {mode === "register" ? (
            <label className="muted">
              Workspace name
              <input
                style={{ width: "100%", marginTop: 6 }}
                value={workspace}
                onChange={(e) => setWorkspace(e.target.value)}
              />
            </label>
          ) : null}
          <div className="row">
            <button className="primary" type="button" onClick={() => void submit()}>
              Continue
            </button>
            <button className="ghost" type="button" onClick={() => setMode(mode === "login" ? "register" : "login")}>
              {mode === "login" ? "Need an account?" : "Have an account?"}
            </button>
          </div>
          <p className="muted" style={{ marginTop: 18, fontSize: 14, lineHeight: 1.5 }}>
            Or use Clerk (separate from API JWT — dashboard still needs the token above until backend links Clerk).
            <br />
            <Link href="/sign-in">Clerk sign in</Link>
            {" · "}
            <Link href="/sign-up">Clerk sign up</Link>
            {" · "}
            <Link href="/status">API status</Link>
          </p>
        </div>
      </div>
    </main>
  );
}
