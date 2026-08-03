"""
LeadFlow - Automação: Envio de WhatsApp
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from src.services.whatsapp_bot import WhatsAppBot
from src.database import SessionLocal
from src.models.lead import Lead
from src.models.mensagem import Mensagem


class EnviadorWhatsApp:
    """Gerencia envio de mensagens via WhatsApp"""

    def __init__(self):
        self.bot = WhatsAppBot()
        self.delay_entre_envios = 5  # segundos

    async def enviar_para_lead(self, lead_id: str, mensagem: str) -> dict:
        """Envia mensagem pra um lead específico"""
        db = SessionLocal()

        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return {"erro": "Lead não encontrado"}

            if not lead.whatsapp:
                return {"erro": "Lead não tem WhatsApp"}

            # Verifica se número tem WhatsApp
            check = await self.bot.check_number(lead.whatsapp)
            if not check or not check[0].get("exists"):
                return {"erro": "Número não tem WhatsApp"}

            # Envia mensagem
            resultado = await self.bot.send_message(
                phone=lead.whatsapp,
                message=mensagem,
            )

            # Atualiza mensagem no banco
            msg = db.query(Mensagem).filter(
                Mensagem.lead_id == lead_id,
                Mensagem.conteudo == mensagem,
            ).first()

            if msg:
                msg.status = "enviada"
                msg.enviado_em = datetime.utcnow()
                msg.metadata = {**(msg.metadata or {}), "evolution_response": resultado}

            # Atualiza lead
            lead.ultimo_contato = datetime.utcnow()
            lead.status = "contatado"

            db.commit()

            return {
                "lead": lead.nome,
                "telefone": lead.whatsapp,
                "status": "enviada",
                "evolution_id": resultado.get("key", {}).get("id"),
            }

        except Exception as e:
            db.rollback()
            return {"erro": str(e)}
        finally:
            db.close()

    async def enviar_lote(
        self,
        status_lead: str = "novo",
        limite: int = 10,
        delay: int = 5,
    ) -> list:
        """Envia mensagens em lote"""
        db = SessionLocal()
        resultados = []

        try:
            # Busca leads com mensagens pendentes
            leads = (
                db.query(Lead)
                .filter(
                    Lead.status == status_lead,
                    Lead.whatsapp.isnot(None),
                )
                .order_by(Lead.score.desc())
                .limit(limite)
                .all()
            )

            for lead in leads:
                # Busca última mensagem não enviada
                msg = (
                    db.query(Mensagem)
                    .filter(
                        Mensagem.lead_id == lead.id,
                        Mensagem.status == "enviada",
                        Mensagem.metadata["gerado_por"].astext == "ia",
                    )
                    .order_by(Mensagem.created_at.desc())
                    .first()
                )

                if msg:
                    resultado = await self.enviar_para_lead(
                        str(lead.id),
                        msg.conteudo,
                    )
                    resultados.append(resultado)

                    # Delay entre envios
                    await asyncio.sleep(delay)

            return resultados

        finally:
            db.close()

    async def verificar_status_envios(self) -> dict:
        """Verifica status de todas as mensagens enviadas"""
        db = SessionLocal()

        try:
            total = db.query(Mensagem).filter(Mensagem.tipo == "texto").count()
            enviadas = db.query(Mensagem).filter(Mensagem.status == "enviada").count()
            entregues = db.query(Mensagem).filter(Mensagem.status == "entregue").count()
            lidas = db.query(Mensagem).filter(Mensagem.status == "lida").count()
            erros = db.query(Mensagem).filter(Mensagem.status == "erro").count()

            return {
                "total": total,
                "enviadas": enviadas,
                "entregues": entregues,
                "lidas": lidas,
                "erros": erros,
                "taxa_entrega": round((entregues + lidas) / max(enviadas, 1) * 100, 2),
                "taxa_leitura": round(lidas / max(enviadas, 1) * 100, 2),
            }

        finally:
            db.close()


async def main():
    """Execução standalone"""
    enviador = EnviadorWhatsApp()

    # Verifica status
    status = await enviador.verificar_status_envios()
    print(f"📊 Status: {status}")

    # Envia lote
    resultados = await enviador.enviar_lote(status_lead="novo", limite=5)
    print(f"✅ Enviados: {len(resultados)}")


if __name__ == "__main__":
    asyncio.run(main())
