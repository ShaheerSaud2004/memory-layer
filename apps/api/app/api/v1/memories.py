from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_tenant_db
from app.graphs.ingest import run_ingest_pipeline
from app.models.agent import Agent, AgentMemoryScope
from app.models.enums import MemoryType
from app.models.memory import Memory, MemoryEmbedding, MemoryEdge, MemoryTag
from app.models.tag import Tag
from app.schemas.api import MemoryCreate, MemoryOut, MemoryUpdate, SearchHit, SearchIn
from app.services.embedding import embed_texts
from app.services.search import hybrid_memory_search

router = APIRouter(prefix="/memories", tags=["memories"])


def _agent_scopes(db: Session, ctx: AuthContext) -> list[AgentMemoryScope]:
    if not ctx.agent_id:
        return []
    agent = db.get(Agent, ctx.agent_id)
    if agent is None:
        return []
    return list(agent.scopes)


def _agent_can_write(scopes: list[AgentMemoryScope]) -> bool:
    if not scopes:
        return True
    return any(s.can_write for s in scopes)


def _memory_type_allowed(mem_type: MemoryType, scopes: list[AgentMemoryScope]) -> bool:
    if not scopes:
        return True
    allowed_any = False
    for s in scopes:
        if s.memory_types is None:
            allowed_any = True
            break
        if mem_type.value in (s.memory_types or []):
            allowed_any = True
            break
    return allowed_any


@router.post("", response_model=MemoryOut)
def create_memory(
    body: MemoryCreate,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_tenant_db),
) -> Memory:
    scopes = _agent_scopes(db, ctx)
    if ctx.agent_id and not _agent_can_write(scopes):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent cannot write")
    if not _memory_type_allowed(body.memory_type, scopes):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Memory type not allowed")

    mem = Memory(
        tenant_id=ctx.tenant_id,  # type: ignore[arg-type]
        memory_type=body.memory_type,
        memory_class=body.memory_class,
        content=body.content,
        metadata_=body.metadata,
        source_ref=body.source_ref,
        importance_score=body.importance_score,
        recency_boost=body.recency_boost,
    )
    db.add(mem)
    db.flush()

    chunks = run_ingest_pipeline(body.content)
    vectors, model = embed_texts(chunks)
    for idx, vec in enumerate(vectors):
        db.add(
            MemoryEmbedding(memory_id=mem.id, chunk_index=idx, model=model, embedding=vec)
        )

    for tname in body.tag_names:
        tag = db.execute(
            select(Tag).where(Tag.tenant_id == ctx.tenant_id, Tag.name == tname)
        ).scalar_one_or_none()
        if tag is None:
            tag = Tag(tenant_id=ctx.tenant_id, name=tname)  # type: ignore[arg-type]
            db.add(tag)
            db.flush()
        db.add(MemoryTag(memory_id=mem.id, tag_id=tag.id))

    db.flush()
    return mem


@router.get("", response_model=list[MemoryOut])
def list_memories(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_tenant_db),
    limit: int = 50,
) -> list[Memory]:
    stmt = select(Memory).order_by(Memory.created_at.desc()).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return list(rows)


@router.get("/{memory_id}", response_model=MemoryOut)
def get_memory(
    memory_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_tenant_db),
) -> Memory:
    m = db.get(Memory, memory_id)
    if m is None:
        raise HTTPException(status_code=404, detail="Not found")
    return m


@router.patch("/{memory_id}", response_model=MemoryOut)
def update_memory(
    memory_id: UUID,
    body: MemoryUpdate,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_tenant_db),
) -> Memory:
    m = db.get(Memory, memory_id)
    if m is None:
        raise HTTPException(status_code=404, detail="Not found")
    if body.content is not None:
        m.content = body.content
    if body.memory_type is not None:
        m.memory_type = body.memory_type
    if body.memory_class is not None:
        m.memory_class = body.memory_class
    if body.metadata is not None:
        m.metadata_ = body.metadata
    if body.importance_score is not None:
        m.importance_score = body.importance_score
    if body.recency_boost is not None:
        m.recency_boost = body.recency_boost
    db.flush()
    return m


@router.delete("/{memory_id}", status_code=204, response_class=Response)
def delete_memory(
    memory_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_tenant_db),
) -> Response:
    m = db.get(Memory, memory_id)
    if m is None:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(m)
    db.flush()
    return Response(status_code=204)


@router.post("/search", response_model=list[SearchHit])
def search_memories(
    body: SearchIn,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_tenant_db),
) -> list[SearchHit]:
    qvec, _ = embed_texts([body.query])
    rows = hybrid_memory_search(
        db,
        tenant_id=ctx.tenant_id,  # type: ignore[arg-type]
        query=body.query,
        query_embedding=qvec[0],
        limit=body.limit,
        memory_types=body.memory_types,
        tag_names=body.tag_names,
    )
    return [
        SearchHit(
            id=r["id"],
            content=r["content"],
            score=float(r["score"]),
            memory_type=str(r["memory_type"]),
            memory_class=str(r.get("memory_class")) if r.get("memory_class") is not None else None,
        )
        for r in rows
    ]


@router.get("/{memory_id}/graph")
def memory_graph(
    memory_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_tenant_db),
):
    edges = db.execute(
        select(MemoryEdge).where(
            (MemoryEdge.from_memory_id == memory_id) | (MemoryEdge.to_memory_id == memory_id)
        )
    ).scalars().all()
    nodes: dict[str, str] = {}
    out_edges: list[dict] = []

    def label(mid: UUID) -> str:
        m = db.get(Memory, mid)
        return (m.content[:80] + "…") if m and len(m.content) > 80 else (m.content if m else str(mid))

    for e in edges:
        nodes[str(e.from_memory_id)] = label(e.from_memory_id)
        nodes[str(e.to_memory_id)] = label(e.to_memory_id)
        out_edges.append(
            {"source": str(e.from_memory_id), "target": str(e.to_memory_id), "relation": e.relation.value}
        )
    return {"nodes": [{"id": k, "label": v} for k, v in nodes.items()], "edges": out_edges}
