from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_tenant_db, require_pro_subscription, require_roles
from app.auth.agent_keys import generate_agent_api_key
from app.models.agent import Agent, AgentMemoryScope
from app.models.enums import MembershipRole
from app.schemas.api import AgentCreateIn, AgentOut

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentOut)
def create_agent(
    body: AgentCreateIn,
    ctx: AuthContext = Depends(require_roles(MembershipRole.owner, MembershipRole.admin)),
    _: AuthContext = Depends(require_pro_subscription()),
    db: Session = Depends(get_tenant_db),
) -> AgentOut:
    full, prefix, key_hash = generate_agent_api_key()
    agent = Agent(
        tenant_id=ctx.tenant_id,  # type: ignore[arg-type]
        name=body.name,
        description=body.description,
        key_prefix=prefix,
        key_hash=key_hash,
    )
    db.add(agent)
    db.flush()
    db.add(AgentMemoryScope(agent_id=agent.id, can_write=True))
    db.flush()
    return AgentOut(id=agent.id, name=agent.name, api_key=full)


@router.get("", response_model=list[AgentOut])
def list_agents(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_tenant_db),
) -> list[AgentOut]:
    rows = db.execute(select(Agent).order_by(Agent.created_at.desc())).scalars().all()
    return [AgentOut(id=a.id, name=a.name, api_key=None) for a in rows]


@router.delete("/{agent_id}", status_code=204, response_class=Response)
def delete_agent(
    agent_id: UUID,
    ctx: AuthContext = Depends(require_roles(MembershipRole.owner, MembershipRole.admin)),
    db: Session = Depends(get_tenant_db),
) -> Response:
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(agent)
    return Response(status_code=204)
