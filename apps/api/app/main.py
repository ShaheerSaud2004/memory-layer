from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings

logger = logging.getLogger("uvicorn.error")

_WEAK_JWT = frozenset({"", "change-me"})


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.jwt_secret in _WEAK_JWT or len(settings.jwt_secret) < 16:
        logger.warning(
            "JWT_SECRET is missing, default, or very short. Set a long random value before production."
        )
    if settings.master_key in _WEAK_JWT or len(settings.master_key) < 16:
        logger.warning(
            "MASTER_KEY is missing, default, or very short. Use a strong key and plan KMS for B2B production."
        )
    yield


settings = get_settings()


def _cors_origin_regex() -> str | None:
    parts: list[str] = []
    if settings.cors_allow_localhost_any_port:
        parts.append(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$")
    if settings.cors_include_vercel_app_host:
        parts.append(r"^https://[^/]+\.vercel\.app$")
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    return "(?:" + ")|(?:".join(parts) + ")"


app = FastAPI(title="AI Memory Layer API", version="0.1.0", lifespan=lifespan)

_cors_kw: dict = {
    "allow_origins": settings.cors_origin_list,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
_cors_rx = _cors_origin_regex()
if _cors_rx:
    _cors_kw["allow_origin_regex"] = _cors_rx
app.add_middleware(CORSMiddleware, **_cors_kw)

app.include_router(api_router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health")
def health() -> dict[str, str]:
    return healthz()
