from __future__ import annotations

from uuid import UUID

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_public_db, require_roles
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.enums import MembershipRole
from app.models.tenant import Tenant
from app.models.user import User

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutIn(BaseModel):
    success_url: str | None = Field(default=None, max_length=2048)
    cancel_url: str | None = Field(default=None, max_length=2048)


class BillingStatusOut(BaseModel):
    plan: str
    subscription_status: str | None
    stripe_customer_id: str | None


@router.get("/status", response_model=BillingStatusOut)
def billing_status(
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_public_db),
) -> BillingStatusOut:
    tenant = db.get(Tenant, ctx.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="tenant not found")
    return BillingStatusOut(
        plan=tenant.plan,
        subscription_status=tenant.subscription_status,
        stripe_customer_id=tenant.stripe_customer_id,
    )


@router.post("/checkout-session")
def create_checkout_session(
    body: CheckoutIn,
    ctx: AuthContext = Depends(require_roles(MembershipRole.owner, MembershipRole.admin)),
    db: Session = Depends(get_public_db),
) -> dict[str, str]:
    settings = get_settings()
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing not configured: set STRIPE_SECRET_KEY",
        )
    if not settings.stripe_price_pro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing not configured: set STRIPE_PRICE_PRO (price_… id)",
        )

    stripe.api_key = settings.stripe_secret_key
    tenant = db.get(Tenant, ctx.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="tenant not found")

    user_email: str | None = None
    if ctx.user_id:
        u = db.get(User, ctx.user_id)
        if u:
            user_email = u.email

    if not tenant.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user_email,
            metadata={"tenant_id": str(tenant.id)},
        )
        tenant.stripe_customer_id = customer["id"]
        db.commit()

    success_url = body.success_url or settings.billing_success_url
    cancel_url = body.cancel_url or settings.billing_cancel_url
    if "{CHECKOUT_SESSION_ID}" not in success_url:
        sep = "&" if "?" in success_url else "?"
        success_url = f"{success_url}{sep}session_id={{CHECKOUT_SESSION_ID}}"

    session = stripe.checkout.Session.create(
        customer=tenant.stripe_customer_id,
        mode="subscription",
        line_items=[{"price": settings.stripe_price_pro, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"tenant_id": str(tenant.id)},
        subscription_data={"metadata": {"tenant_id": str(tenant.id)}},
        client_reference_id=str(tenant.id),
    )
    url = session.get("url")
    if not url:
        raise HTTPException(status_code=500, detail="Stripe did not return a checkout URL")
    return {"url": url}


def _sync_subscription_to_tenant(db: Session, sub: dict) -> None:
    tenant: Tenant | None = None
    tid = (sub.get("metadata") or {}).get("tenant_id")
    if tid:
        try:
            tenant = db.get(Tenant, UUID(str(tid)))
        except ValueError:
            tenant = None
    if tenant is None:
        cid = sub.get("customer")
        if cid:
            tenant = db.execute(
                select(Tenant).where(Tenant.stripe_customer_id == cid)
            ).scalar_one_or_none()
    if tenant is None:
        return

    tenant.stripe_subscription_id = sub.get("id")
    tenant.subscription_status = sub.get("status")
    st = sub.get("status") or ""
    if st in ("active", "trialing"):
        tenant.plan = "pro"
    elif st in ("canceled", "unpaid", "incomplete_expired", "paused"):
        tenant.plan = "free"
        tenant.stripe_subscription_id = None


@router.post("/webhook")
async def stripe_webhook(request: Request) -> dict[str, bool]:
    settings = get_settings()
    if not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured: STRIPE_WEBHOOK_SECRET",
        )

    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    if not sig:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload if isinstance(payload, (bytes, str)) else bytes(payload),
            sig,
            settings.stripe_webhook_secret,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload") from e
    except stripe.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature") from e

    db = SessionLocal()
    try:
        etype = event["type"]
        obj = event["data"]["object"]

        if etype == "checkout.session.completed":
            tid = (obj.get("metadata") or {}).get("tenant_id")
            sub_id = obj.get("subscription")
            if tid and sub_id:
                try:
                    tenant = db.get(Tenant, UUID(str(tid)))
                    if tenant:
                        tenant.stripe_subscription_id = sub_id
                        tenant.plan = "pro"
                        tenant.subscription_status = "active"
                except ValueError:
                    pass

        elif etype in ("customer.subscription.updated", "customer.subscription.created"):
            _sync_subscription_to_tenant(db, obj)

        elif etype == "customer.subscription.deleted":
            sub = obj
            tid = (sub.get("metadata") or {}).get("tenant_id")
            tenant: Tenant | None = None
            if tid:
                try:
                    tenant = db.get(Tenant, UUID(str(tid)))
                except ValueError:
                    tenant = None
            if tenant is None:
                cid = sub.get("customer")
                if cid:
                    tenant = db.execute(
                        select(Tenant).where(Tenant.stripe_customer_id == cid)
                    ).scalar_one_or_none()
            if tenant:
                tenant.plan = "free"
                tenant.subscription_status = "canceled"
                tenant.stripe_subscription_id = None

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return {"received": True}
