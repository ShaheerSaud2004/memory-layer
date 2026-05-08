import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import BaseModelMixin

if TYPE_CHECKING:
    from app.models.membership import Membership
    from app.models.memory import Memory
    from app.models.tag import Tag


class Tenant(Base, BaseModelMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    plan: Mapped[str] = mapped_column(String(32), nullable=False, default="free", server_default="free")
    subscription_status: Mapped[str | None] = mapped_column(String(32), nullable=True)

    memberships: Mapped[List["Membership"]] = relationship(back_populates="tenant")
    memories: Mapped[List["Memory"]] = relationship(back_populates="tenant")
    tags: Mapped[List["Tag"]] = relationship(back_populates="tenant")


class TenantCrypto(Base):
    __tablename__ = "tenant_crypto"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True
    )
    encrypted_dek: Mapped[str] = mapped_column(Text, nullable=False)
    dek_nonce: Mapped[str] = mapped_column(String(64), nullable=False)
