"""
LeadFlow - Modelo de Lead
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, ARRAY, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=True)
    nome = Column(String(255), nullable=False)
    cargo = Column(String(100))
    email = Column(String(255))
    telefone = Column(String(20))
    whatsapp = Column(String(20))
    linkedin = Column(String(255))
    instagram = Column(String(255))
    score = Column(Integer, default=0)
    status = Column(String(50), default="novo")
    fonte = Column(String(100))
    tags = Column(ARRAY(Text))
    notas = Column(Text)
    responsavel_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    ultimo_contato = Column(DateTime)
    proximo_followup = Column(DateTime)
    engajamento = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    empresa = relationship("Empresa", back_populates="leads")
    mensagens = relationship("Mensagem", back_populates="lead")
    pipeline = relationship("Pipeline", back_populates="lead", uselist=False)
    propostas = relationship("Proposta", back_populates="lead")
    interacoes = relationship("Interacao", back_populates="lead")
