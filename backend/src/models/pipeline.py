"""
LeadFlow - Modelo de Pipeline
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.database import Base


class Pipeline(Base):
    __tablename__ = "pipeline"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), unique=True, nullable=False)
    etapa = Column(String(50), default="lead")
    responsavel_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    valor = Column(Numeric(15, 2))
    moeda = Column(String(3), default="BRL")
    data_previsao = Column(Date)
    probabilidade = Column(Integer, default=0)
    motivo_perda = Column(String)
    moved_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lead = relationship("Lead", back_populates="pipeline")
