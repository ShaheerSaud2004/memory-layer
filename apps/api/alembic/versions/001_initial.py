"""initial schema with RLS

revision ID: 001_initial
Revises:
Create Date: 2026-05-07
"""

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("settings", postgresql.JSONB, nullable=True),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "tenant_crypto",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("encrypted_dek", sa.Text(), nullable=False),
        sa.Column("dek_nonce", sa.String(64), nullable=False),
    )

    op.create_table(
        "memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(32), nullable=False, server_default="member"),
    )
    op.create_index("ix_memberships_user_id", "memberships", ["user_id"])
    op.create_index("ix_memberships_tenant_id", "memberships", ["tenant_id"])
    op.create_unique_constraint("uq_membership_user_tenant", "memberships", ["user_id", "tenant_id"])

    op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
    )
    op.create_index("ix_tags_tenant_id", "tags", ["tenant_id"])
    op.create_unique_constraint("uq_tag_tenant_name", "tags", ["tenant_id", "name"])

    op.create_table(
        "memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("memory_type", sa.String(64), nullable=False),
        sa.Column("memory_class", sa.String(32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("source_ref", sa.String(512), nullable=True),
        sa.Column("importance_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("recency_boost", sa.Float(), nullable=False, server_default="0"),
        sa.Column("compressed_from_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("memories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_encrypted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_memories_tenant_id", "memories", ["tenant_id"])
    op.create_index("ix_memories_memory_type", "memories", ["memory_type"])
    op.create_index("ix_memories_memory_class", "memories", ["memory_class"])
    op.execute(
        """
        ALTER TABLE memories ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED
        """
    )
    op.execute("CREATE INDEX memories_fts ON memories USING GIN (search_vector)")

    op.create_table(
        "memory_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("memory_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("memories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
    )
    op.create_index("ix_memory_embeddings_memory_id", "memory_embeddings", ["memory_id"])
    op.create_unique_constraint("uq_memory_embedding_chunk", "memory_embeddings", ["memory_id", "chunk_index"])
    op.execute(
        "CREATE INDEX memory_embeddings_hnsw ON memory_embeddings USING hnsw (embedding vector_cosine_ops)"
    )

    op.create_table(
        "memory_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("from_memory_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("memories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_memory_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("memories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relation", sa.String(32), nullable=False),
    )
    op.create_index("ix_memory_edges_tenant_id", "memory_edges", ["tenant_id"])

    op.create_table(
        "memory_tags",
        sa.Column("memory_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("memories.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("key_prefix", sa.String(16), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False),
    )
    op.create_index("ix_agents_tenant_id", "agents", ["tenant_id"])
    op.create_index("ix_agents_key_prefix", "agents", ["key_prefix"])

    op.create_table(
        "agent_memory_scopes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("memory_types", postgresql.JSONB, nullable=True),
        sa.Column("tag_names", postgresql.JSONB, nullable=True),
        sa.Column("namespace_prefix", sa.String(128), nullable=True),
        sa.Column("can_write", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_agent_memory_scopes_agent_id", "agent_memory_scopes", ["agent_id"])

    for name in ("ingestion_jobs", "optimizer_jobs"):
        op.create_table(
            name,
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
            sa.Column("payload" if name == "ingestion_jobs" else "result_summary", postgresql.JSONB, nullable=True),
            sa.Column("error", sa.Text(), nullable=True),
        )
        op.create_index(f"ix_{name}_tenant_id", name, ["tenant_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_type", sa.String(32), nullable=False),
        sa.Column("actor_id", sa.String(64), nullable=True),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("resource", sa.String(128), nullable=True),
        sa.Column("details", postgresql.JSONB, nullable=True),
        sa.Column("ip", sa.String(64), nullable=True),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])

    for tbl in (
        "memories",
        "memory_edges",
        "tags",
        "agents",
        "ingestion_jobs",
        "optimizer_jobs",
        "audit_logs",
    ):
        op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {tbl}_tenant_isolation ON {tbl} FOR ALL USING ("
            f"tenant_id::text = current_setting('app.current_tenant_id', true)"
            f")"
        )

    op.execute("ALTER TABLE memory_embeddings ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY memory_embeddings_tenant_isolation ON memory_embeddings FOR ALL USING (
          EXISTS (
            SELECT 1 FROM memories m
            WHERE m.id = memory_embeddings.memory_id
            AND m.tenant_id::text = current_setting('app.current_tenant_id', true)
          )
        )
        """
    )

    op.execute("ALTER TABLE agent_memory_scopes ENABLE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY agent_memory_scopes_tenant_isolation ON agent_memory_scopes FOR ALL USING (
          EXISTS (
            SELECT 1 FROM agents a
            WHERE a.id = agent_memory_scopes.agent_id
            AND a.tenant_id::text = current_setting('app.current_tenant_id', true)
          )
        )
        """
    )

    op.execute(
        """
        ALTER TABLE memory_tags ENABLE ROW LEVEL SECURITY;
        CREATE POLICY memory_tags_via_memory ON memory_tags FOR ALL USING (
          EXISTS (
            SELECT 1 FROM memories m
            WHERE m.id = memory_tags.memory_id
            AND m.tenant_id::text = current_setting('app.current_tenant_id', true)
          )
        );
        """
    )

    op.execute(
        """
        ALTER TABLE tenant_crypto ENABLE ROW LEVEL SECURITY;
        CREATE POLICY tenant_crypto_isolation ON tenant_crypto FOR ALL USING (
            tenant_id::text = current_setting('app.current_tenant_id', true)
        );
        """
    )


def downgrade() -> None:
    for stmt in (
        "DROP POLICY IF EXISTS tenant_crypto_isolation ON tenant_crypto",
        "DROP POLICY IF EXISTS memory_tags_via_memory ON memory_tags",
        "DROP POLICY IF EXISTS audit_logs_tenant_isolation ON audit_logs",
        "DROP POLICY IF EXISTS optimizer_jobs_tenant_isolation ON optimizer_jobs",
        "DROP POLICY IF EXISTS ingestion_jobs_tenant_isolation ON ingestion_jobs",
        "DROP POLICY IF EXISTS agent_memory_scopes_tenant_isolation ON agent_memory_scopes",
        "DROP POLICY IF EXISTS agents_tenant_isolation ON agents",
        "DROP POLICY IF EXISTS memory_edges_tenant_isolation ON memory_edges",
        "DROP POLICY IF EXISTS memory_embeddings_tenant_isolation ON memory_embeddings",
        "DROP POLICY IF EXISTS memories_tenant_isolation ON memories",
        "DROP POLICY IF EXISTS tags_tenant_isolation ON tags",
    ):
        op.execute(stmt)

    op.execute("ALTER TABLE tenant_crypto DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE memory_tags DISABLE ROW LEVEL SECURITY")
    for tbl in (
        "audit_logs",
        "optimizer_jobs",
        "ingestion_jobs",
        "agent_memory_scopes",
        "agents",
        "memory_tags",
        "memory_edges",
        "memory_embeddings",
        "memories",
        "tags",
    ):
        op.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY")

    op.drop_table("audit_logs")
    op.drop_table("optimizer_jobs")
    op.drop_table("ingestion_jobs")
    op.drop_table("agent_memory_scopes")
    op.drop_table("agents")
    op.drop_table("memory_tags")
    op.drop_table("memory_edges")
    op.execute("DROP INDEX IF EXISTS memory_embeddings_hnsw")
    op.drop_table("memory_embeddings")
    op.execute("DROP INDEX IF EXISTS memories_fts")
    op.drop_table("memories")
    op.drop_table("tags")
    op.drop_table("memberships")
    op.drop_table("tenant_crypto")
    op.drop_table("users")
    op.drop_table("tenants")
