"""
LeadFlow - API de Leads
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from src.database import get_db
from src.models.lead import Lead
from src.models.empresa import Empresa
from src.models.pipeline import Pipeline
from src.schemas import LeadCreate, LeadUpdate, LeadResponse
from src.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[LeadResponse])
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    score_min: Optional[int] = None,
    fonte: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Lista leads com filtros"""
    query = db.query(Lead)

    if status:
        query = query.filter(Lead.status == status)
    if score_min:
        query = query.filter(Lead.score >= score_min)
    if fonte:
        query = query.filter(Lead.fonte == fonte)
    if search:
        query = query.filter(
            (Lead.nome.ilike(f"%{search}%"))
            | (Lead.email.ilike(f"%{search}%"))
            | (Lead.telefone.ilike(f"%{search}%"))
        )

    leads = query.order_by(Lead.score.desc()).offset(skip).limit(limit).all()
    return leads


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Busca lead por ID"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return lead


@router.post("/", response_model=LeadResponse, status_code=201)
async def create_lead(
    data: LeadCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Cria novo lead"""
    # Verifica se empresa existe se informada
    if data.empresa_id:
        empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")

    lead = Lead(**data.model_dump(), responsavel_id=user["id"])
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Cria entrada no pipeline automaticamente
    pipeline_entry = Pipeline(lead_id=lead.id, etapa="lead", responsavel_id=user["id"])
    db.add(pipeline_entry)
    db.commit()

    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    data: LeadUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Atualiza lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, key, value)

    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Deleta lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    db.delete(lead)
    db.commit()
    return None


@router.get("/{lead_id}/historico")
async def get_lead_historico(
    lead_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Histórico completo do lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    return {
        "lead": lead,
        "mensagens": lead.mensagens,
        "interacoes": lead.interacoes,
        "propostas": lead.propostas,
        "pipeline": lead.pipeline,
    }
