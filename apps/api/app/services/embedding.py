import hashlib
import math
from typing import Sequence
from uuid import UUID

from openai import OpenAI

from app.core.config import get_settings
from app.models.memory import EMBED_DIM


def _fake_embedding(text: str) -> list[float]:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    out: list[float] = []
    for i in range(EMBED_DIM):
        b = h[i % len(h)]
        out.append((b / 255.0) * 2 - 1)
    # L2 normalize
    n = math.sqrt(sum(x * x for x in out)) or 1.0
    return [x / n for x in out]


def embed_texts(texts: Sequence[str]) -> tuple[list[list[float]], str]:
    settings = get_settings()
    if settings.openai_api_key:
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=list(texts),
        )
        return [d.embedding for d in resp.data], settings.openai_embedding_model
    return [_fake_embedding(t) for t in texts], "fake-local"
