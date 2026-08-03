"""
LeadFlow - Modelo de Empresa
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from src.database import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cnpj = Column(String(14), unique=True)
    razao_social = Column(String(255))
    nome_fantasia = Column(String(255))
    nicho = Column(String(100))
    porte = Column(String(50))
    cidade = Column(String(100))
    estado = Column(String(2))
    endereco = Column(Text)
    telefone = Column(String(20))
    email = Column(String(255))
    site = Column(String(255))
    instagram = Column(String(255))
    linkedin = Column(String(255))
    descricao = Column(Text)
    funcionarios = Column(Integer)
    faturamento_estimado = Column(Numeric(15, 2))
    data_fundacao = Column(Date)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    leads = relationship("Lead", back_populates="empresa")
