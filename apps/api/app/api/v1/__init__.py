from fastapi import APIRouter

from app.api.v1 import agents, auth, billing, memories, optimizer

api_router = APIRouter(prefix="/v1")
api_router.include_router(auth.router)
api_router.include_router(billing.router)
api_router.include_router(memories.router)
api_router.include_router(agents.router)
api_router.include_router(optimizer.router)
