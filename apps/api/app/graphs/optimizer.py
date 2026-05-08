"""Memory optimizer job: scans old memories; MVP completes safely without destructive merges."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import OptimizerStatus
from app.models.ingestion import OptimizerJob
from app.models.memory import Memory


def run_optimizer(session: Session, *, tenant_id: UUID, job_id: UUID) -> dict[str, Any]:
    job = session.get(OptimizerJob, job_id)
    if job is None:
        raise ValueError("job not found")
    job.status = OptimizerStatus.running
    session.flush()

    total = session.execute(select(Memory).where(Memory.tenant_id == tenant_id)).scalars().all()
    job.status = OptimizerStatus.completed
    job.result_summary = {"tenant_id": str(tenant_id), "memory_count": len(total)}
    session.flush()
    return job.result_summary or {}
