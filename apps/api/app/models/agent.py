import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import BaseModelMixin

if TYPE_CHECKING:
    from app.models.tenant import Tenant


class Agent(Base, BaseModelMixin):
    __tablename__ = "agents"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    tenant: Mapped["Tenant"] = relationship()
    scopes: Mapped[List["AgentMemoryScope"]] = relationship(
        back_populates="agent", cascade="all, delete-orphan"
    )


class AgentMemoryScope(Base, BaseModelMixin):
    __tablename__ = "agent_memory_scopes"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    memory_types = mapped_column(JSONB, nullable=True)
    tag_names = mapped_column(JSONB, nullable=True)
    namespace_prefix: Mapped[str | None] = mapped_column(String(128), nullable=True)
    can_write: Mapped[bool] = mapped_column(default=False, nullable=False)

    agent: Mapped["Agent"] = relationship(back_populates="scopes")
