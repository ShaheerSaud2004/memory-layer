from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_tenant_db, require_pro_subscription, require_roles
from app.graphs.optimizer import run_optimizer
from app.models.enums import MembershipRole, OptimizerStatus
from app.models.ingestion import OptimizerJob
from app.schemas.api import OptimizerRunOut

router = APIRouter(prefix="/optimizer", tags=["optimizer"])


@router.post("/run", response_model=OptimizerRunOut)
def run_optimize(
    ctx: AuthContext = Depends(require_roles(MembershipRole.owner, MembershipRole.admin)),
    _: AuthContext = Depends(require_pro_subscription()),
    db: Session = Depends(get_tenant_db),
) -> OptimizerRunOut:
    job = OptimizerJob(tenant_id=ctx.tenant_id, status=OptimizerStatus.pending)  # type: ignore[arg-type]
    db.add(job)
    db.flush()
    run_optimizer(db, tenant_id=ctx.tenant_id, job_id=job.id)  # type: ignore[arg-type]
    db.refresh(job)
    return OptimizerRunOut(job_id=job.id, status=job.status.value)


@router.get("/jobs/{job_id}")
def get_job(
    job_id: UUID,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_tenant_db),
):
    from fastapi import HTTPException

    j = db.get(OptimizerJob, job_id)
    if j is None:
        raise HTTPException(status_code=404, detail="not_found")
    return {"id": str(j.id), "status": j.status.value, "result": j.result_summary}
