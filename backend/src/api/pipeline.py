"""
LeadFlow - API de Pipeline (Kanban)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.database import get_db
from src.models.pipeline import Pipeline
from src.models.lead import Lead
from src.schemas import PipelineCreate, PipelineUpdate, PipelineResponse, PipelineMove
from src.auth import get_current_user

router = APIRouter()

ETAPAS = ["lead", "qualificado", "contato", "call", "proposta", "fechado"]


@router.get("/", response_model=List[dict])
async def get_pipeline(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Retorna pipeline completo organizado por etapas"""
    pipeline_items = (
        db.query(Pipeline)
        .options(joinedload(Pipeline.lead))
        .order_by(Pipeline.moved_at.desc())
        .all()
    )

    # Organiza por etapa
    result = {etapa: [] for etapa in ETAPAS}
    for item in pipeline_items:
        if item.etapa in result:
            result[item.etapa].append({
                "id": str(item.id),
                "lead_id": str(item.lead_id),
                "lead_nome": item.lead.nome if item.lead else None,
                "lead_score": item.lead.score if item.lead else 0,
                "lead_empresa": item.lead.empresa.nome_fantasia if item.lead and item.lead.empresa else None,
                "valor": float(item.valor) if item.valor else 0,
                "probabilidade": item.probabilidade,
                "data_previsao": item.data_previsao.isoformat() if item.data_previsao else None,
                "moved_at": item.moved_at.isoformat(),
            })

    return result


@router.get("/metrics")
async def get_pipeline_metrics(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Métricas do pipeline"""
    metrics = {}
    for etapa in ETAPAS:
        items = db.query(Pipeline).filter(Pipeline.etapa == etapa).all()
        metrics[etapa] = {
            "total": len(items),
            "valor_total": sum(float(i.valor or 0) for i in items),
            "probabilidade_media": sum(i.probabilidade or 0 for i in items) / max(len(items), 1),
        }

    total_valor = sum(m["valor_total"] for m in metrics.values())
    valor_ponderado = sum(
        m["valor_total"] * m["probabilidade_media"] / 100 for m in metrics.values()
    )

    return {
        "etapas": metrics,
        "valor_total_pipeline": total_valor,
        "valor_ponderado": valor_ponderado,
        "total_leads": sum(m["total"] for m in metrics.values()),
    }


@router.post("/", response_model=PipelineResponse, status_code=201)
async def create_pipeline_entry(
    data: PipelineCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Cria entrada no pipeline"""
    # Verifica se lead já está no pipeline
    existing = db.query(Pipeline).filter(Pipeline.lead_id == data.lead_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Lead já está no pipeline")

    entry = Pipeline(**data.model_dump(), responsavel_id=user["id"])
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/{pipeline_id}/mover")
async def move_pipeline(
    pipeline_id: UUID,
    data: PipelineMove,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Move lead entre etapas do pipeline"""
    entry = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada do pipeline não encontrada")

    if data.etapa not in ETAPAS:
        raise HTTPException(status_code=400, detail=f"Etapa inválida. Use: {ETAPAS}")

    entry.etapa = data.etapa
    entry.moved_at = datetime.utcnow()

    if data.etapa == "fechado":
        entry.probabilidade = 100
    if data.etapa == "perdido" or data.motivo_perda:
        entry.motivo_perda = data.motivo_perda

    # Atualiza status do lead
    lead = db.query(Lead).filter(Lead.id == entry.lead_id).first()
    if lead:
        status_map = {
            "lead": "novo",
            "qualificado": "qualificado",
            "contato": "contatado",
            "call": "qualificado",
            "proposta": "em_proposta",
            "fechado": "fechado",
        }
        lead.status = status_map.get(data.etapa, lead.status)

    db.commit()
    db.refresh(entry)
    return {"message": f"Lead movido para {data.etapa}", "entry": entry}


@router.delete("/{pipeline_id}", status_code=204)
async def delete_pipeline_entry(
    pipeline_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Remove entrada do pipeline"""
    entry = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")

    db.delete(entry)
    db.commit()
    return None
