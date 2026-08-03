"""
LeadFlow - API de Relatórios
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional
from datetime import datetime, timedelta
import io
import csv

from src.database import get_db
from src.models.lead import Lead
from src.models.mensagem import Mensagem
from src.models.pipeline import Pipeline
from src.auth import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    periodo: Optional[int] = Query(30, description="Dias"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Dashboard com métricas principais"""
    data_inicio = datetime.utcnow() - timedelta(days=periodo)

    # Total de leads
    total_leads = db.query(func.count(Lead.id)).scalar()

    # Leads novos no período
    leads_novos = (
        db.query(func.count(Lead.id))
        .filter(Lead.created_at >= data_inicio)
        .scalar()
    )

    # Leads por status
    leads_por_status = (
        db.query(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .all()
    )

    # Pipeline por etapa
    pipeline_por_etapa = (
        db.query(
            Pipeline.etapa,
            func.count(Pipeline.id),
            func.sum(Pipeline.valor),
        )
        .group_by(Pipeline.etapa)
        .all()
    )

    # Valor total no pipeline
    valor_pipeline = db.query(func.sum(Pipeline.valor)).scalar() or 0

    # Leads fechados no período
    leads_fechados = (
        db.query(func.count(Pipeline.id))
        .filter(Pipeline.etapa == "fechado", Pipeline.moved_at >= data_inicio)
        .scalar()
    )

    # Mensagens enviadas no período
    mensagens_enviadas = (
        db.query(func.count(Mensagem.id))
        .filter(Mensagem.enviado_em >= data_inicio)
        .scalar()
    )

    # Taxa de resposta
    mensagens_respondidas = (
        db.query(func.count(Mensagem.id))
        .filter(Mensagem.enviado_em >= data_inicio, Mensagem.resposta == True)
        .scalar()
    )
    taxa_resposta = (mensagens_respondidas / max(mensagens_enviadas, 1)) * 100

    # Taxa de conversão
    taxa_conversao = (leads_fechados / max(leads_novos, 1)) * 100

    # Leads por dia (últimos 7 dias)
    leads_por_dia = db.execute(text("""
        SELECT DATE(created_at) as dia, COUNT(*) as total
        FROM leads
        WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY DATE(created_at)
        ORDER BY dia
    """)).fetchall()

    # Top leads por score
    top_leads = (
        db.query(Lead)
        .order_by(Lead.score.desc())
        .limit(5)
        .all()
    )

    return {
        "periodo_dias": periodo,
        "total_leads": total_leads,
        "leads_novos": leads_novos,
        "leads_fechados": leads_fechados,
        "valor_pipeline": float(valor_pipeline),
        "mensagens_enviadas": mensagens_enviadas,
        "taxa_resposta": round(taxa_resposta, 2),
        "taxa_conversao": round(taxa_conversao, 2),
        "leads_por_status": {s: c for s, c in leads_por_status},
        "pipeline_por_etapa": {e: {"total": c, "valor": float(v or 0)} for e, c, v in pipeline_por_etapa},
        "leads_por_dia": [{"dia": str(d), "total": t} for d, t in leads_por_dia],
        "top_leads": [
            {"id": str(l.id), "nome": l.nome, "score": l.score, "status": l.status}
            for l in top_leads
        ],
    }


@router.get("/conversao")
async def get_conversao(
    periodo: Optional[int] = Query(30),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Métricas de conversão por etapa"""
    data_inicio = datetime.utcnow() - timedelta(days=periodo)

    etapas = ["lead", "qualificado", "contato", "call", "proposta", "fechado"]
    conversao = {}

    for i, etapa in enumerate(etapas):
        total = (
            db.query(func.count(Pipeline.id))
            .filter(Pipeline.etapa == etapa)
            .scalar()
        )
        conversao[etapa] = total

    # Calcula taxas de conversão entre etapas
    taxas = {}
    for i in range(len(etapas) - 1):
        atual = conversao[etapas[i]]
        proximo = conversao[etapas[i + 1]]
        taxa = (proximo / max(atual, 1)) * 100
        taxas[f"{etapas[i]}_para_{etapas[i+1]}"] = round(taxa, 2)

    return {
        "etapas": conversao,
        "taxas_conversao": taxas,
        "taxa_geral": round((conversao.get("fechado", 0) / max(conversao.get("lead", 1), 1)) * 100, 2),
    }


@router.get("/exportar/leads")
async def exportar_leads_csv(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Exporta leads em CSV"""
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)

    leads = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Cargo", "Email", "Telefone", "WhatsApp", "Score", "Status", "Fonte", "Criado em"])

    for lead in leads:
        writer.writerow([
            lead.nome,
            lead.cargo,
            lead.email,
            lead.telefone,
            lead.whatsapp,
            lead.score,
            lead.status,
            lead.fonte,
            lead.created_at.strftime("%d/%m/%Y %H:%M"),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=leads_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@router.get("/exportar/pipeline")
async def exportar_pipeline_csv(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Exporta pipeline em CSV"""
    pipeline_items = db.query(Pipeline).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Lead", "Etapa", "Valor", "Probabilidade", "Previsão", "Responsável"])

    for item in pipeline_items:
        writer.writerow([
            item.lead.nome if item.lead else "N/A",
            item.etapa,
            float(item.valor or 0),
            item.probabilidade,
            item.data_previsao,
            str(item.responsavel_id),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=pipeline_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@router.get("/roi")
async def get_roi(
    periodo: Optional[int] = Query(30),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """ROI por campanha/fonte"""
    data_inicio = datetime.utcnow() - timedelta(days=periodo)

    roi_por_fonte = db.execute(text("""
        SELECT
            l.fonte,
            COUNT(*) as total_leads,
            COUNT(CASE WHEN p.etapa = 'fechado' THEN 1 END) as fechados,
            COALESCE(SUM(CASE WHEN p.etapa = 'fechado' THEN p.valor END), 0) as receita
        FROM leads l
        LEFT JOIN pipeline p ON p.lead_id = l.id
        WHERE l.created_at >= :data_inicio
        GROUP BY l.fonte
    """), {"data_inicio": data_inicio}).fetchall()

    return {
        "periodo_dias": periodo,
        "por_fonte": [
            {
                "fonte": row[0],
                "total_leads": row[1],
                "fechados": row[2],
                "receita": float(row[3]),
                "taxa_conversao": round((row[2] / max(row[1], 1)) * 100, 2),
            }
            for row in roi_por_fonte
        ],
    }
