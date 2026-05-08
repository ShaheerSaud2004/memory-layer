import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import BaseModelMixin
from app.models.enums import IngestionStatus, OptimizerStatus


class IngestionJob(Base, BaseModelMixin):
    __tablename__ = "ingestion_jobs"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    status: Mapped[IngestionStatus] = mapped_column(
        Enum(IngestionStatus, name="ingestion_status", native_enum=False, length=32),
        nullable=False,
        default=IngestionStatus.pending,
    )
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class OptimizerJob(Base, BaseModelMixin):
    __tablename__ = "optimizer_jobs"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    status: Mapped[OptimizerStatus] = mapped_column(
        Enum(OptimizerStatus, name="optimizer_status", native_enum=False, length=32),
        nullable=False,
        default=OptimizerStatus.pending,
    )
    result_summary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
