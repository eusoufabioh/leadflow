"""
LeadFlow - Automação: Follow-up Automático
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from src.services.ia_prospeccao import IAProspeccao
from src.services.whatsapp_bot import WhatsAppBot
from src.database import SessionLocal
from src.models.lead import Lead
from src.models.mensagem import Mensagem


class FollowUpBot:
    """Bot de follow-up automático"""

    # Configuração de tentativas
    TENTATIVAS = [
        {"dias": 3, "tom": "lembrete"},
        {"dias": 7, "tom": "valor"},
        {"dias": 14, "tom": "ultimo"},
    ]

    def __init__(self):
        self.ia = IAProspeccao()
        self.whatsapp = WhatsAppBot()

    async def verificar_follow_ups(self) -> list:
        """Verifica leads que precisam de follow-up"""
        db = SessionLocal()
        follow_ups = []

        try:
            # Busca leads com último contato > 3 dias
            data_limite = datetime.utcnow() - timedelta(days=3)

            leads = (
                db.query(Lead)
                .filter(
                    Lead.ultimo_contato <= data_limite,
                    Lead.ultimo_contato.isnot(None),
                    Lead.status.in_(["contatado", "qualificado"]),
                    Lead.whatsapp.isnot(None),
                )
                .order_by(Lead.ultimo_contato.asc())
                .all()
            )

            for lead in leads:
                dias_sem_contato = (datetime.utcnow() - lead.ultimo_contato).days

                # Determina tentativa
                tentativa = self._determinar_tentativa(dias_sem_contato)

                if tentativa:
                    follow_ups.append({
                        "lead": lead,
                        "dias_sem_contato": dias_sem_contato,
                        "tentativa": tentativa,
                    })

            return follow_ups

        finally:
            db.close()

    async def executar_follow_ups(self, limite: int = 10) -> list:
        """Executa follow-ups pendentes"""
        follow_ups = await self.verificar_follow_ups()
        resultados = []

        for item in follow_ups[:limite]:
            lead = item["lead"]
            tentativa = item["tentativa"]

            # Gera mensagem de follow-up
            ultima_msg = self._buscar_ultima_mensagem(lead.id)
            mensagem = await self.ia.gerar_follow_up(lead, ultima_msg or "")

            # Envia via WhatsApp
            resultado = await self.whatsapp.send_message(
                phone=lead.whatsapp,
                message=mensagem,
            )

            # Salva no banco
            db = SessionLocal()
            try:
                msg = Mensagem(
                    lead_id=lead.id,
                    conteudo=mensagem,
                    tipo="texto",
                    status="enviada",
                    mensagem_original_id=None,
                    metadata={
                        "tipo": "follow_up",
                        "tentativa": tentativa["tom"],
                        "dias_sem_contato": item["dias_sem_contato"],
                    },
                )
                db.add(msg)

                # Atualiza lead
                lead_db = db.query(Lead).filter(Lead.id == lead.id).first()
                if lead_db:
                    lead_db.ultimo_contato = datetime.utcnow()

                db.commit()

                resultados.append({
                    "lead": lead.nome,
                    "tentativa": tentativa["tom"],
                    "mensagem": mensagem[:100] + "...",
                })

            except Exception as e:
                db.rollback()
                print(f"Erro ao salvar follow-up: {e}")
            finally:
                db.close()

            # Delay entre envios
            await asyncio.sleep(5)

        return resultados

    def _determinar_tentativa(self, dias_sem_contato: int) -> dict:
        """Determina qual tentativa de follow-up usar"""
        for tentativa in reversed(self.TENTATIVAS):
            if dias_sem_contato >= tentativa["dias"]:
                return tentativa
        return None

    def _buscar_ultima_mensagem(self, lead_id) -> str:
        """Busca última mensagem do lead"""
        db = SessionLocal()
        try:
            msg = (
                db.query(Mensagem)
                .filter(Mensagem.lead_id == lead_id)
                .order_by(Mensagem.enviado_em.desc())
                .first()
            )
            return msg.conteudo if msg else ""
        finally:
            db.close()


async def main():
    """Execução standalone"""
    bot = FollowUpBot()

    print("🔄 Verificando follow-ups pendentes...")
    follow_ups = await bot.verificar_follow_ups()
    print(f"   {len(follow_ups)} leads precisam de follow-up")

    if follow_ups:
        print("\n📤 Executando follow-ups...")
        resultados = await bot.executar_follow_ups(limite=5)
        print(f"   {len(resultados)} follow-ups enviados")

        for r in resultados:
            print(f"   → {r['lead']}: {r['tentativa']}")


if __name__ == "__main__":
    asyncio.run(main())
