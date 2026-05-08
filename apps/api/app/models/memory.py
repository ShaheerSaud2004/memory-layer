import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.base import Base
from app.models.base import BaseModelMixin
from app.models.enums import EdgeRelation, MemoryClass, MemoryType

if TYPE_CHECKING:
    from app.models.tag import Tag
    from app.models.tenant import Tenant


EMBED_DIM = 1536


class Memory(Base, BaseModelMixin):
    __tablename__ = "memories"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    memory_type: Mapped[MemoryType] = mapped_column(
        Enum(MemoryType, name="memory_type", native_enum=False, length=64),
        nullable=False,
        index=True,
    )
    memory_class: Mapped[MemoryClass] = mapped_column(
        Enum(MemoryClass, name="memory_class", native_enum=False, length=32),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    source_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    importance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    recency_boost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    compressed_from_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id", ondelete="SET NULL"), nullable=True
    )
    is_encrypted: Mapped[bool] = mapped_column(default=False, nullable=False)

    tenant: Mapped["Tenant"] = relationship(back_populates="memories")
    embeddings: Mapped[List["MemoryEmbedding"]] = relationship(
        back_populates="memory", cascade="all, delete-orphan"
    )
    tag_links: Mapped[List["MemoryTag"]] = relationship(
        back_populates="memory", cascade="all, delete-orphan"
    )


class MemoryEmbedding(Base):
    __tablename__ = "memory_embeddings"
    __table_args__ = (
        UniqueConstraint("memory_id", "chunk_index", name="uq_memory_embedding_chunk"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(nullable=False, default=0)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    embedding: Mapped[list] = mapped_column(Vector(EMBED_DIM), nullable=False)

    memory: Mapped["Memory"] = relationship(back_populates="embeddings")


class MemoryEdge(Base, BaseModelMixin):
    __tablename__ = "memory_edges"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    to_memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relation: Mapped[EdgeRelation] = mapped_column(
        Enum(EdgeRelation, name="edge_relation", native_enum=False, length=32),
        nullable=False,
    )


class MemoryTag(Base):
    __tablename__ = "memory_tags"

    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )

    memory: Mapped["Memory"] = relationship(back_populates="tag_links")
    tag: Mapped["Tag"] = relationship(back_populates="memory_links")
