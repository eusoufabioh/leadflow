"""
LeadFlow - Schemas Pydantic
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


# ============== USUÁRIO ==============

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    plano: Optional[str] = "starter"

class UsuarioResponse(BaseModel):
    id: UUID
    nome: str
    email: str
    plano: str
    ativo: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== EMPRESA ==============

class EmpresaCreate(BaseModel):
    cnpj: Optional[str] = None
    razao_social: str
    nome_fantasia: Optional[str] = None
    nicho: Optional[str] = None
    porte: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    site: Optional[str] = None
    instagram: Optional[str] = None
    linkedin: Optional[str] = None
    descricao: Optional[str] = None
    funcionarios: Optional[int] = None

class EmpresaResponse(EmpresaCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== LEAD ==============

class LeadCreate(BaseModel):
    empresa_id: Optional[UUID] = None
    nome: str
    cargo: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None
    fonte: Optional[str] = None
    tags: Optional[List[str]] = []
    notas: Optional[str] = None

class LeadUpdate(BaseModel):
    nome: Optional[str] = None
    cargo: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None
    score: Optional[int] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    notas: Optional[str] = None
    responsavel_id: Optional[UUID] = None

class LeadResponse(BaseModel):
    id: UUID
    empresa_id: Optional[UUID]
    nome: str
    cargo: Optional[str]
    email: Optional[str]
    telefone: Optional[str]
    whatsapp: Optional[str]
    linkedin: Optional[str]
    instagram: Optional[str]
    score: int
    status: str
    fonte: Optional[str]
    tags: Optional[List[str]]
    notas: Optional[str]
    responsavel_id: Optional[UUID]
    ultimo_contato: Optional[datetime]
    proximo_followup: Optional[datetime]
    engajamento: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== MENSAGEM ==============

class MensagemCreate(BaseModel):
    lead_id: UUID
    conteudo: str
    tipo: Optional[str] = "texto"

class MensagemResponse(BaseModel):
    id: UUID
    lead_id: UUID
    usuario_id: Optional[UUID]
    conteudo: str
    tipo: str
    status: str
    enviado_em: datetime
    entregue_em: Optional[datetime]
    lido_em: Optional[datetime]
    resposta: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== PIPELINE ==============

class PipelineCreate(BaseModel):
    lead_id: UUID
    etapa: Optional[str] = "lead"
    valor: Optional[float] = None
    data_previsao: Optional[date] = None
    probabilidade: Optional[int] = 0

class PipelineUpdate(BaseModel):
    etapa: Optional[str] = None
    valor: Optional[float] = None
    data_previsao: Optional[date] = None
    probabilidade: Optional[int] = None
    motivo_perda: Optional[str] = None

class PipelineResponse(BaseModel):
    id: UUID
    lead_id: UUID
    etapa: str
    responsavel_id: Optional[UUID]
    valor: Optional[float]
    moeda: str
    data_previsao: Optional[date]
    probabilidade: int
    motivo_perda: Optional[str]
    moved_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class PipelineMove(BaseModel):
    etapa: str
    motivo_perda: Optional[str] = None


# ============== PROPOSTA ==============

class PropostaCreate(BaseModel):
    lead_id: UUID
    titulo: str
    conteudo: Optional[str] = None
    valor: Optional[float] = None
    validade: Optional[date] = None

class PropostaResponse(BaseModel):
    id: UUID
    lead_id: UUID
    titulo: str
    conteudo: Optional[str]
    valor: Optional[float]
    pdf_url: Optional[str]
    status: str
    enviada_em: Optional[datetime]
    visualizada_em: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============== INTERAÇÃO ==============

class InteracaoCreate(BaseModel):
    lead_id: UUID
    tipo: str
    conteudo: Optional[str] = None
    duracao: Optional[int] = None

class InteracaoResponse(BaseModel):
    id: UUID
    lead_id: UUID
    usuario_id: Optional[UUID]
    tipo: str
    conteudo: Optional[str]
    duracao: Optional[int]
    data: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============== COLETA ==============

class ColetaGoogleMaps(BaseModel):
    nicho: str
    cidade: str
    estado: Optional[str] = None
    raio_km: Optional[int] = 10
    limite: Optional[int] = 50

class ColetaInstagram(BaseModel):
    hashtags: List[str]
    local: Optional[str] = None
    limite: Optional[int] = 50

class ColetaLinkedIn(BaseModel):
    cargo: str
    empresa: Optional[str] = None
    local: Optional[str] = None
    limite: Optional[int] = 50

class ColetaCNPJ(BaseModel):
    cnpj: str


# ============== IA ==============

class IAGerarMensagem(BaseModel):
    lead_id: UUID
    template_id: Optional[UUID] = None
    tom: Optional[str] = "profissional"  # profissional, casual, direto

class IAResponse(BaseModel):
    mensagem: str
    modelo: str
    tokens: int


# ============== RELATÓRIOS ==============

class DashboardMetrics(BaseModel):
    total_leads: int
    leads_novos_hoje: int
    pipeline_valor_total: float
    taxa_conversao: float
    mensagens_enviadas_hoje: int
    taxa_resposta: float
    leads_por_status: dict
    pipeline_por_etapa: dict
