import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import BaseModelMixin

if TYPE_CHECKING:
    from app.models.memory import MemoryTag
    from app.models.tenant import Tenant


class Tag(Base, BaseModelMixin):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_tag_tenant_name"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    tenant: Mapped["Tenant"] = relationship(back_populates="tags")
    memory_links: Mapped[List["MemoryTag"]] = relationship(back_populates="tag")

