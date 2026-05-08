"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import ReactFlow, { Background, Controls, Edge, Node, ReactFlowProvider } from "reactflow";
import "reactflow/dist/style.css";

const api = () => process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type MemoryRow = {
  id: string;
  content: string;
  memory_type: string;
  memory_class: string;
  importance_score: number;
  created_at: string;
};

export default function DashboardPage() {
  const token = useMemo(() => (typeof window !== "undefined" ? localStorage.getItem("aml_token") : null), []);
  const [memories, setMemories] = useState<MemoryRow[]>([]);
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<{ id: string; content: string; score: number; memory_type: string }[]>([]);
  const [content, setContent] = useState("Remember: prefer pgvector for self-hosted hybrid retrieval.");
  const [memoryType, setMemoryType] = useState("note");
  const [memoryClass, setMemoryClass] = useState("semantic");
  const [selected, setSelected] = useState<string | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    void (async () => {
      const res = await fetch(`${api()}/v1/memories`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        setErr(await res.text());
        return;
      }
      setMemories(await res.json());
    })();
  }, [token]);

  useEffect(() => {
    if (!token || !selected) return;
    void (async () => {
      const res = await fetch(`${api()}/v1/memories/${selected}/graph`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = await res.json();
      setNodes(
        (data.nodes as { id: string; label: string }[]).map((n) => ({
          id: n.id,
          position: { x: Math.random() * 400, y: Math.random() * 250 },
          data: { label: n.label },
        }))
      );
      setEdges(
        (data.edges as { source: string; target: string; relation: string }[]).map((e, i) => ({
          id: `${e.source}-${e.target}-${i}`,
          source: e.source,
          target: e.target,
          label: e.relation,
        }))
      );
    })();
  }, [token, selected]);

  async function createMemory() {
    setErr(null);
    const res = await fetch(`${api()}/v1/memories`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content,
        memory_type: memoryType,
        memory_class: memoryClass,
        tag_names: ["product"],
      }),
    });
    if (!res.ok) {
      setErr(await res.text());
      return;
    }
    const m = await res.json();
    setMemories((prev) => [m, ...prev]);
  }

  async function search() {
    setErr(null);
    const res = await fetch(`${api()}/v1/memories/search`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: q, limit: 15 }),
    });
    if (!res.ok) {
      setErr(await res.text());
      return;
    }
    setHits(await res.json());
  }

  if (!token) {
    return (
      <main>
        <div className="card">
          <p>No token found. Please <Link href="/login">sign in</Link>.</p>
        </div>
      </main>
    );
  }

  return (
    <main>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <div>
          <h2 style={{ margin: "0 0 6px" }}>Workspace memories</h2>
          <div className="muted">Hybrid retrieval (FTS + vector) with tenant isolation + RLS.</div>
        </div>
        <div className="row" style={{ gap: 16 }}>
          <Link href="/billing">Billing</Link>
          <Link href="/login">Account</Link>
        </div>
      </div>

      {err ? (
        <pre style={{ color: "#ffb4b4", whiteSpace: "pre-wrap" }}>{err}</pre>
      ) : null}

      <div className="grid2" style={{ marginTop: 18 }}>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Create memory</h3>
          <textarea style={{ width: "100%", minHeight: 120 }} value={content} onChange={(e) => setContent(e.target.value)} />
          <div className="row" style={{ marginTop: 10 }}>
            <select value={memoryType} onChange={(e) => setMemoryType(e.target.value)}>
              <option value="note">note</option>
              <option value="task">task</option>
              <option value="summary">summary</option>
              <option value="conversation_segment">conversation_segment</option>
              <option value="transcript">transcript</option>
              <option value="workflow">workflow</option>
            </select>
            <select value={memoryClass} onChange={(e) => setMemoryClass(e.target.value)}>
              <option value="semantic">semantic</option>
              <option value="episodic">episodic</option>
              <option value="procedural">procedural</option>
            </select>
            <button className="primary" type="button" onClick={() => void createMemory()}>
              Save
            </button>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0 }}>Search</h3>
          <div className="row">
            <input style={{ flex: 1, minWidth: 220 }} value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ask your memory layer…" />
            <button className="primary" type="button" onClick={() => void search()}>
              Search
            </button>
          </div>
          <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
            {hits.map((h) => (
              <button
                key={h.id}
                className="ghost"
                type="button"
                style={{ textAlign: "left", padding: 12 }}
                onClick={() => setSelected(h.id)}
              >
                <div className="muted" style={{ fontSize: 12 }}>
                  score {h.score.toFixed(3)} · {h.memory_type}
                </div>
                <div>{h.content}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginTop: 0 }}>Recent</h3>
        <div style={{ display: "grid", gap: 10 }}>
          {memories.map((m) => (
            <div
              key={m.id}
              className="card"
              style={{ cursor: "pointer", background: selected === m.id ? "#171f33" : undefined }}
              onClick={() => setSelected(m.id)}
            >
              <div className="muted" style={{ fontSize: 12 }}>
                {m.memory_type} · {m.memory_class} · imp {m.importance_score}
              </div>
              <div>{m.content}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ marginTop: 16, height: 420 }}>
        <h3 style={{ marginTop: 0 }}>Graph neighborhood</h3>
        {selected ? (
          <div style={{ height: 340 }}>
            <ReactFlowProvider>
              <ReactFlow nodes={nodes} edges={edges} fitView>
                <Background />
                <Controls />
              </ReactFlow>
            </ReactFlowProvider>
          </div>
        ) : (
          <p className="muted">Select a memory to preview linked edges.</p>
        )}
      </div>
    </main>
  );
}
