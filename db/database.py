"""Connexion et session SQLAlchemy pour PostgreSQL."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config.settings import DATABASE_URL


connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    connect_args["connect_timeout"] = 2

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency injection pour FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cree toutes les tables."""
    Base.metadata.create_all(bind=engine)
