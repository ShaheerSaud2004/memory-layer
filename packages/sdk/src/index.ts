export type MemoryType =
  | "conversation_segment"
  | "note"
  | "file_excerpt"
  | "task"
  | "summary"
  | "transcript"
  | "workflow";

export type MemoryClass = "episodic" | "semantic" | "procedural";

export type MemoryCreate = {
  content: string;
  memory_type: MemoryType;
  memory_class?: MemoryClass;
  metadata?: Record<string, unknown>;
  source_ref?: string;
  importance_score?: number;
  recency_boost?: number;
  tag_names?: string[];
};

export class MemoryLayerClient {
  constructor(
    private readonly baseUrl: string,
    private readonly getToken: () => string | null,
  ) {}

  private headers(json = false): HeadersInit {
    const h: Record<string, string> = {
      Authorization: `Bearer ${this.getToken() || ""}`,
    };
    if (json) h["Content-Type"] = "application/json";
    return h;
  }

  async createMemory(body: MemoryCreate) {
    const res = await fetch(`${this.baseUrl}/v1/memories`, {
      method: "POST",
      headers: this.headers(true),
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async searchMemories(query: string, limit = 20) {
    const res = await fetch(`${this.baseUrl}/v1/memories/search`, {
      method: "POST",
      headers: this.headers(true),
      body: JSON.stringify({ query, limit }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }
}
