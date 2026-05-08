from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass
class SearchWeights:
    semantic: float = 0.55
    keyword: float = 0.2
    recency: float = 0.15
    importance: float = 0.1


def _vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in vec) + "]"


def hybrid_memory_search(
    session: Session,
    *,
    tenant_id: UUID,
    query: str,
    query_embedding: list[float],
    limit: int = 20,
    memory_types: list[str] | None = None,
    tag_names: list[str] | None = None,
    weights: SearchWeights | None = None,
) -> list[dict[str, Any]]:
    w = weights or SearchWeights()
    vec_lit = _vector_literal(query_embedding)
    params: dict[str, Any] = {
        "qvec": vec_lit,
        "qtext": query,
        "limit": limit,
        "tenant": str(tenant_id),
    }
    type_filter = ""
    if memory_types:
        type_filter = "AND m.memory_type = ANY(:types)"
        params["types"] = memory_types
    tag_filter = ""
    if tag_names:
        tag_filter = """
          AND EXISTS (
            SELECT 1 FROM memory_tags mt
            JOIN tags t ON t.id = mt.tag_id
            WHERE mt.memory_id = m.id AND t.name = ANY(:tags)
          )
        """
        params["tags"] = tag_names

    sql = text(
        f"""
        WITH sims AS (
          SELECT me.memory_id,
                 MAX(1 - (me.embedding <=> CAST(:qvec AS vector))) AS sim
          FROM memory_embeddings me
          JOIN memories m ON m.id = me.memory_id
          WHERE m.tenant_id = CAST(:tenant AS uuid)
          {type_filter}
          {tag_filter}
          GROUP BY me.memory_id
        )
        SELECT
          m.id,
          m.content,
          m.memory_type,
          m.memory_class,
          m.metadata,
          m.importance_score,
          m.recency_boost,
          m.created_at,
          s.sim AS sim,
          ts_rank_cd(m.search_vector, plainto_tsquery('english', :qtext)) AS kw,
          EXTRACT(EPOCH FROM (now() - m.created_at)) / 86400.0 AS age_days,
          (
            :w_sem * GREATEST(s.sim, 0) +
            :w_kw * GREATEST(ts_rank_cd(m.search_vector, plainto_tsquery('english', :qtext)), 0) +
            :w_rec * exp(- (EXTRACT(EPOCH FROM (now() - m.created_at)) / 86400.0) / 30.0) +
            :w_imp * m.importance_score +
            m.recency_boost
          ) AS score
        FROM memories m
        JOIN sims s ON s.memory_id = m.id
        WHERE m.tenant_id = CAST(:tenant AS uuid)
        {type_filter}
        {tag_filter}
        ORDER BY score DESC
        LIMIT :limit
        """
    )
    params.update(
        {
            "w_sem": w.semantic,
            "w_kw": w.keyword,
            "w_rec": w.recency,
            "w_imp": w.importance,
        }
    )
    rows = session.execute(sql, params).mappings().all()
    return [dict(r) for r in rows]
