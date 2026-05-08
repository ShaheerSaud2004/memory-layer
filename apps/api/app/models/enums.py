import enum


class MembershipRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


class MemoryType(str, enum.Enum):
    conversation_segment = "conversation_segment"
    note = "note"
    file_excerpt = "file_excerpt"
    task = "task"
    summary = "summary"
    transcript = "transcript"
    workflow = "workflow"


class MemoryClass(str, enum.Enum):
    episodic = "episodic"
    semantic = "semantic"
    procedural = "procedural"


class EdgeRelation(str, enum.Enum):
    derived_from = "derived_from"
    supersedes = "supersedes"
    part_of = "part_of"
    tagged_by = "tagged_by"
    related_to = "related_to"


class IngestionStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class OptimizerStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
