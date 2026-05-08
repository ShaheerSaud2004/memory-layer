from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID

from app.models.enums import MemoryClass, MemoryType


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    workspace_name: str = Field(min_length=1, max_length=255)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MemoryCreate(BaseModel):
    content: str
    memory_type: MemoryType
    memory_class: MemoryClass = MemoryClass.semantic
    metadata: dict | None = None
    source_ref: str | None = None
    importance_score: float = 0.5
    recency_boost: float = 0.0
    tag_names: list[str] = []


class MemoryUpdate(BaseModel):
    content: str | None = None
    memory_type: MemoryType | None = None
    memory_class: MemoryClass | None = None
    metadata: dict | None = None
    importance_score: float | None = None
    recency_boost: float | None = None


class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    memory_type: str
    memory_class: str
    content: str
    metadata: dict | None = Field(
        default=None,
        validation_alias="metadata_",
        serialization_alias="metadata",
    )
    importance_score: float
    created_at: object


class SearchIn(BaseModel):
    query: str
    limit: int = 20
    memory_types: list[str] | None = None
    tag_names: list[str] | None = None


class SearchHit(BaseModel):
    id: UUID
    content: str
    score: float
    memory_type: str
    memory_class: str | None = None


class GraphNode(BaseModel):
    id: str
    label: str


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str


class AgentCreateIn(BaseModel):
    name: str
    description: str | None = None


class AgentOut(BaseModel):
    id: UUID
    name: str
    api_key: str | None = None


class OptimizerRunOut(BaseModel):
    job_id: UUID
    status: str
