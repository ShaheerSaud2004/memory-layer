import re
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_public_db
from app.auth.security import create_access_token, hash_password, verify_password
from app.schemas.api import LoginIn, RegisterIn, TokenOut
from app.services.crypto import generate_dek, wrap_dek
from app.models.enums import MembershipRole
from app.models.membership import Membership
from app.models.tenant import Tenant, TenantCrypto
from app.models.user import User
from app.db.session import tenant_session

router = APIRouter(prefix="/auth", tags=["auth"])


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")[:64] or "workspace"
    return s


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, db: Session = Depends(get_public_db)) -> TokenOut:
    if db.execute(select(User).where(User.email == str(body.email))).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    base_slug = slugify(body.workspace_name)
    slug = base_slug
    for _ in range(10):
        if db.execute(select(Tenant).where(Tenant.slug == slug)).scalar_one_or_none() is None:
            break
        slug = f"{base_slug}-{uuid4().hex[:6]}"
    else:
        raise HTTPException(status_code=400, detail="Could not allocate workspace slug")

    user = User(email=str(body.email).lower(), hashed_password=hash_password(body.password))
    db.add(user)
    db.flush()

    tenant = Tenant(name=body.workspace_name, slug=slug)
    db.add(tenant)
    db.flush()

    db.add(
        Membership(
            user_id=user.id,
            tenant_id=tenant.id,
            role=MembershipRole.owner,
        )
    )
    db.commit()

    dek = generate_dek()
    enc, nonce = wrap_dek(dek, str(tenant.id))
    with tenant_session(tenant.id) as ts:
        ts.add(TenantCrypto(tenant_id=tenant.id, encrypted_dek=enc, dek_nonce=nonce))

    token = create_access_token(
        user_id=user.id, tenant_id=tenant.id, role=MembershipRole.owner.value
    )
    return TokenOut(access_token=token)


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_public_db)) -> TokenOut:
    user = db.execute(select(User).where(User.email == str(body.email).lower())).scalar_one_or_none()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    m = db.execute(
        select(Membership)
        .where(Membership.user_id == user.id)
        .order_by(Membership.created_at.asc())
    ).scalars().first()
    if m is None:
        raise HTTPException(status_code=400, detail="No workspace membership")
    token = create_access_token(user_id=user.id, tenant_id=m.tenant_id, role=m.role.value)
    return TokenOut(access_token=token)
