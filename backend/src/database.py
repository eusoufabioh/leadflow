"""
LeadFlow - Database Connection
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://leadflow:leadflow@localhost:5432/leadflow")

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"⚠️  Erro ao conectar ao banco: {e}")
    engine = None
    SessionLocal = None

Base = declarative_base()


def get_db():
    """Dependency pra obter sessão do banco"""
    if SessionLocal is None:
        raise Exception("Banco de dados não configurado")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
