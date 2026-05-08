import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.skipif(os.getenv("INTEGRATION") != "1", reason="INTEGRATION=1 required")


def test_register_login_memory_search_flow() -> None:
    c = TestClient(app)
    email = f"u-{uuid.uuid4().hex}@example.com"
    reg = c.post(
        "/v1/auth/register",
        json={"email": email, "password": "password123", "workspace_name": "ws"},
    )
    assert reg.status_code == 200, reg.text
    token = reg.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    m = c.post(
        "/v1/memories",
        headers=headers,
        json={
            "content": "We prefer pgvector for embeddings in Postgres.",
            "memory_type": "note",
            "memory_class": "semantic",
            "tag_names": ["infra"],
        },
    )
    assert m.status_code == 200, m.text

    s = c.post(
        "/v1/memories/search",
        headers=headers,
        json={"query": "pgvector embeddings", "limit": 5},
    )
    assert s.status_code == 200, s.text
    hits = s.json()
    assert isinstance(hits, list)
    assert len(hits) >= 1
