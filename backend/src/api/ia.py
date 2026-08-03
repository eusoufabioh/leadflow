"""
LeadFlow - API de IA
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.database import get_db
from src.models.lead import Lead
from src.schemas import IAGerarMensagem, IAResponse
from src.auth import get_current_user
from src.services.ia_prospeccao import IAProspeccao
from src.services.score_leads import ScoreLeads

router = APIRouter()
ia = IAProspeccao()
scorer = ScoreLeads()


@router.post("/gerar-mensagem", response_model=IAResponse)
async def gerar_mensagem(
    data: IAGerarMensagem,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Gera mensagem personalizada via IA"""
    lead = db.query(Lead).filter(Lead.id == data.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    resultado = await ia.gerar_mensagem(
        lead=lead,
        template_id=data.template_id,
        tom=data.tom,
    )

    return resultado


@router.post("/score/{lead_id}")
async def calcular_score(
    lead_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Calcula score do lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    score_data = await scorer.calcular_score(lead)

    # Atualiza lead
    lead.score = score_data["score"]
    db.commit()

    return {
        "lead_id": str(lead_id),
        "score": score_data["score"],
        "detalhes": score_data["detalhes"],
        "classificacao": score_data["classificacao"],
    }


@router.post("/qualificar/{lead_id}")
async def qualificar_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Qualifica lead via IA"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    resultado = await ia.qualificar_lead(lead)
    return resultado


@router.post("/melhor-horario/{lead_id}")
async def melhor_horario(
    lead_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Sugere melhor horário pra enviar mensagem"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    resultado = await ia.sugerir_horario(lead)
    return resultado


@router.post("/ab-test")
async def criar_ab_test(
    lead_id: UUID,
    variacoes: int = 3,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Cria variações de mensagem pra A/B test"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    resultado = await ia.criar_ab_test(lead, variacoes)
    return resultado
