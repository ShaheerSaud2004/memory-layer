import re
from collections.abc import Generator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def _tenant_id_literal(tenant_id: UUID | str) -> str:
    s = str(tenant_id)
    UUID(s)
    if not re.fullmatch(r"[0-9a-fA-F\-]{36}", s):
        raise ValueError("invalid tenant id")
    return s


@contextmanager
def tenant_session(tenant_id) -> Generator[Session, None, None]:
    conn = engine.connect()
    trans = conn.begin()
    tid = _tenant_id_literal(tenant_id)
    conn.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": tid},
    )
    session = Session(bind=conn, autoflush=False, autocommit=False, future=True)
    try:
        yield session
        trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        session.close()
        conn.close()


def session_no_rls() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
