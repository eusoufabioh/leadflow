"""
LeadFlow - Modelo de Mensagem
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.database import Base


class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    conteudo = Column(Text, nullable=False)
    tipo = Column(String(20), default="texto")
    status = Column(String(20), default="enviada")
    enviado_em = Column(DateTime, default=datetime.utcnow)
    entregue_em = Column(DateTime)
    lido_em = Column(DateTime)
    resposta = Column(Boolean, default=False)
    mensagem_original_id = Column(UUID(as_uuid=True), ForeignKey("mensagens.id"))
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lead = relationship("Lead", back_populates="mensagens")
    respostas = relationship("Mensagem", backref="mensagem_original", remote_side=[id])
