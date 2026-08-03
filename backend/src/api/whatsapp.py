"""
LeadFlow - API de WhatsApp (Evolution API)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.database import get_db
from src.models.mensagem import Mensagem
from src.models.lead import Lead
from src.schemas import MensagemCreate, MensagemResponse
from src.auth import get_current_user
from src.services.whatsapp_bot import WhatsAppBot

router = APIRouter()
whatsapp = WhatsAppBot()


@router.get("/status")
async def get_whatsapp_status():
    """Status da conexão WhatsApp"""
    return await whatsapp.get_status()


@router.post("/enviar", response_model=MensagemResponse)
async def enviar_mensagem(
    data: MensagemCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Envia mensagem via WhatsApp"""
    lead = db.query(Lead).filter(Lead.id == data.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    if not lead.whatsapp:
        raise HTTPException(status_code=400, detail="Lead não tem WhatsApp cadastrado")

    # Envia via Evolution API
    result = await whatsapp.send_message(
        phone=lead.whatsapp,
        message=data.conteudo,
        media_type=data.tipo,
    )

    # Salva no banco
    mensagem = Mensagem(
        lead_id=data.lead_id,
        usuario_id=user["id"],
        conteudo=data.conteudo,
        tipo=data.tipo,
        status="enviada",
        metadata={"evolution_id": result.get("id")},
    )
    db.add(mensagem)

    # Atualiza último contato do lead
    lead.ultimo_contato = datetime.utcnow()
    lead.engajamento = min(lead.engajamento + 10, 100)

    db.commit()
    db.refresh(mensagem)
    return mensagem


@router.get("/mensagens/{lead_id}", response_model=List[MensagemResponse])
async def get_mensagens(
    lead_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Histórico de mensagens do lead"""
    mensagens = (
        db.query(Mensagem)
        .filter(Mensagem.lead_id == lead_id)
        .order_by(Mensagem.enviado_em.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return mensagens


@router.post("/follow-up/{lead_id}")
async def enviar_follow_up(
    lead_id: UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Envia follow-up automático"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    # Busca última mensagem
    ultima_msg = (
        db.query(Mensagem)
        .filter(Mensagem.lead_id == lead_id)
        .order_by(Mensagem.enviado_em.desc())
        .first()
    )

    if not ultima_msg:
        raise HTTPException(status_code=400, detail="Lead não tem mensagens anteriores")

    # Gera follow-up via IA
    from src.services.ia_prospeccao import IAProspeccao
    ia = IAProspeccao()
    follow_up = await ia.gerar_follow_up(lead, ultima_msg.conteudo)

    # Envia mensagem
    result = await whatsapp.send_message(
        phone=lead.whatsapp,
        message=follow_up,
    )

    mensagem = Mensagem(
        lead_id=lead_id,
        usuario_id=user["id"],
        conteudo=follow_up,
        tipo="texto",
        status="enviada",
        mensagem_original_id=ultima_msg.id,
    )
    db.add(mensagem)
    db.commit()

    return {"message": "Follow-up enviado", "conteudo": follow_up}


@router.post("/webhook")
async def webhook_evolution(payload: dict, db: Session = Depends(get_db)):
    """Webhook pra receber atualizações da Evolution API"""
    event = payload.get("event")

    if event == "messages.upsert":
        # Mensagem recebida
        msg_data = payload.get("data", {})
        phone = msg_data.get("key", {}).get("remoteJid", "").replace("@s.whatsapp.net", "")

        # Busca lead pelo telefone
        lead = db.query(Lead).filter(Lead.whatsapp.like(f"%{phone}%")).first()
        if lead:
            # Salva mensagem recebida
            mensagem = Mensagem(
                lead_id=lead.id,
                conteudo=msg_data.get("message", {}).get("conversation", ""),
                tipo="texto",
                status="lida",
                resposta=True,
                metadata=msg_data,
            )
            db.add(mensagem)

            # Atualiza engajamento
            lead.engajamento = min(lead.engajamento + 20, 100)
            lead.ultimo_contato = datetime.utcnow()
            db.commit()

    elif event == "message-receipt.update":
        # Status de leitura
        receipt = payload.get("data", {})
        msg_id = receipt.get("key", {}).get("id")
        if msg_id:
            msg = db.query(Mensagem).filter(
                Mensagem.metadata["evolution_id"].astext == msg_id
            ).first()
            if msg:
                status = receipt.get("status")
                if status == "read":
                    msg.status = "lida"
                    msg.lido_em = datetime.utcnow()
                elif status == "delivered":
                    msg.status = "entregue"
                    msg.entregue_em = datetime.utcnow()
                db.commit()

    return {"status": "ok"}
