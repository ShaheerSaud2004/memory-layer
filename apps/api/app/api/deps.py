from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import safe_decode
from app.db.session import SessionLocal, tenant_session
from app.models.agent import Agent
from app.models.enums import MembershipRole
from app.models.tenant import Tenant


class AuthContext:
    def __init__(
        self,
        *,
        user_id: UUID | None = None,
        tenant_id: UUID | None = None,
        role: str | None = None,
        agent_id: UUID | None = None,
    ) -> None:
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role
        self.agent_id = agent_id


def get_auth_context(
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> AuthContext:
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        payload = safe_decode(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        try:
            return AuthContext(
                user_id=UUID(payload["sub"]),
                tenant_id=UUID(payload["tenant_id"]),
                role=str(payload.get("role", "member")),
            )
        except (KeyError, ValueError) as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e

    if x_api_key:
        prefix = x_api_key[:12]
        db = SessionLocal()
        try:
            agent = db.execute(select(Agent).where(Agent.key_prefix == prefix)).scalar_one_or_none()
        finally:
            db.close()
        if agent is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
        from app.auth.agent_keys import verify_agent_api_key

        if not verify_agent_api_key(x_api_key, agent.key_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
        return AuthContext(agent_id=agent.id, tenant_id=agent.tenant_id, role="agent")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


def require_roles(*allowed: MembershipRole):
    roles = {r.value for r in allowed}
    roles.add("agent")

    def dep(ctx: Annotated[AuthContext, Depends(get_auth_context)]) -> AuthContext:
        if ctx.role == "agent":
            return ctx
        if ctx.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return ctx

    return dep


def get_tenant_db(ctx: Annotated[AuthContext, Depends(get_auth_context)]) -> Generator[Session, None, None]:
    if ctx.tenant_id is None:
        raise HTTPException(status_code=400, detail="tenant required")
    with tenant_session(ctx.tenant_id) as session:
        yield session


def require_pro_subscription():
    """Require paid plan for tenant-scoped user actions (agents may pass through for key issuance flows elsewhere)."""

    def dep(ctx: Annotated[AuthContext, Depends(get_auth_context)], db: Session = Depends(get_public_db)) -> AuthContext:
        if ctx.role == "agent":
            return ctx
        if ctx.tenant_id is None:
            raise HTTPException(status_code=400, detail="tenant required")
        tenant = db.get(Tenant, ctx.tenant_id)
        if tenant is None:
            raise HTTPException(status_code=404, detail="tenant not found")
        if tenant.plan == "enterprise":
            return ctx
        if tenant.plan != "pro":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={"code": "subscription_required", "current_plan": tenant.plan},
            )
        inactive = {"canceled", "unpaid", "incomplete_expired", "paused", "incomplete", "past_due"}
        if tenant.subscription_status in inactive:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={"code": "subscription_inactive", "status": tenant.subscription_status},
            )
        return ctx

    return dep


def get_public_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
