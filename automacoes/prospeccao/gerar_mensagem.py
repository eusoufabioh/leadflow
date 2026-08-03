"""
LeadFlow - Automação: Gerar Mensagem Personalizada
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from src.services.ia_prospeccao import IAProspeccao
from src.database import SessionLocal
from src.models.lead import Lead
from src.models.mensagem import Mensagem


async def gerar_mensagem_lead(lead_id: str, tom: str = "profissional") -> dict:
    """Gera mensagem personalizada pra um lead"""
    db = SessionLocal()
    ia = IAProspeccao()

    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"erro": "Lead não encontrado"}

        resultado = await ia.gerar_mensagem(lead=lead, tom=tom)

        # Salva como rascunho
        mensagem = Mensagem(
            lead_id=lead.id,
            conteudo=resultado["mensagem"],
            tipo="texto",
            status="enviada",  # Será atualizado quando enviar
            metadata={
                "modelo": resultado["modelo"],
                "tokens": resultado["tokens"],
                "tom": tom,
                "gerado_por": "ia",
            },
        )
        db.add(mensagem)
        db.commit()

        return {
            "lead": lead.nome,
            "mensagem": resultado["mensagem"],
            "modelo": resultado["modelo"],
            "tokens": resultado["tokens"],
        }

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}
    finally:
        db.close()


async def gerar_mensagens_lote(
    status: str = "novo",
    limite: int = 10,
    tom: str = "profissional",
) -> list:
    """Gera mensagens pra múltiplos leads"""
    db = SessionLocal()

    try:
        leads = (
            db.query(Lead)
            .filter(Lead.status == status, Lead.whatsapp.isnot(None))
            .order_by(Lead.score.desc())
            .limit(limite)
            .all()
        )

        resultados = []
        for lead in leads:
            resultado = await gerar_mensagem_lead(str(lead.id), tom)
            resultados.append(resultado)
            await asyncio.sleep(1)  # Rate limiting

        return resultados

    finally:
        db.close()


async def criar_ab_test_lead(lead_id: str, variacoes: int = 3) -> dict:
    """Cria variações de mensagem pra A/B test"""
    db = SessionLocal()
    ia = IAProspeccao()

    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return {"erro": "Lead não encontrado"}

        resultado = await ia.criar_ab_test(lead, variacoes)
        return {
            "lead": lead.nome,
            "variacoes": resultado["variacoes"],
        }

    finally:
        db.close()


if __name__ == "__main__":
    # Exemplo
    asyncio.run(gerar_mensagens_lote(status="novo", limite=5))
