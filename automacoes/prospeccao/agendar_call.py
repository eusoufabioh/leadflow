"""
LeadFlow - Automação: Agendamento de Calls
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
from src.models.interacao import Interacao


class AgendadorCall:
    """Agendamento automático de calls"""

    def __init__(self):
        self.ia = IAProspeccao()
        self.whatsapp = WhatsAppBot()

    async def sugerir_call(self, lead_id: str) -> dict:
        """Sugere agendamento de call pra um lead"""
        db = SessionLocal()

        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return {"erro": "Lead não encontrado"}

            # Verifica se lead está qualificado pra call
            if lead.score < 60:
                return {"erro": "Lead não qualificado pra call (score < 60)"}

            # Gera mensagem de convite
            response = await self.ia.gerar_mensagem(
                lead=lead,
                tom="profissional",
            )

            mensagem = f"""{response['mensagem']}

📅 Posso agendar uma call rápida de 15 minutos?
Responda com o melhor dia e horário pra você!"""

            return {
                "lead": lead.nome,
                "score": lead.score,
                "mensagem_sugerida": mensagem,
                "horarios_sugeridos": self._gerar_horarios(),
            }

        finally:
            db.close()

    async def enviar_convite_call(self, lead_id: str) -> dict:
        """Envia convite de call via WhatsApp"""
        db = SessionLocal()

        try:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return {"erro": "Lead não encontrado"}

            if not lead.whatsapp:
                return {"erro": "Lead não tem WhatsApp"}

            sugestao = await self.sugerir_call(lead_id)
            if sugestao.get("erro"):
                return sugestao

            # Envia mensagem
            resultado = await self.whatsapp.send_message(
                phone=lead.whatsapp,
                message=sugestao["mensagem_sugerida"],
            )

            # Registra interação
            interacao = Interacao(
                lead_id=lead.id,
                tipo="whatsapp",
                conteudo="Convite de call enviado",
                metadata={
                    "tipo": "convite_call",
                    "horarios_sugeridos": sugestao["horarios_sugeridos"],
                },
            )
            db.add(interacao)

            # Atualiza lead
            lead.ultimo_contato = datetime.utcnow()
            db.commit()

            return {
                "lead": lead.nome,
                "status": "convite_enviado",
                "mensagem": sugestao["mensagem_sugerida"][:100] + "...",
            }

        except Exception as e:
            db.rollback()
            return {"erro": str(e)}
        finally:
            db.close()

    async def processar_resposta_call(self, lead_id: str, resposta: str) -> dict:
        """Processa resposta do lead sobre agendamento"""
        # Usa IA pra interpretar resposta
        response = await self.ia.qualificar_lead(None)  # Simplificado

        # Palavras-chave de aceitação
        palavras_aceite = ["sim", "pode", "quando", "ok", "beleza", "vamos", "bora", "horário"]

        resposta_lower = resposta.lower()
        aceitou = any(p in resposta_lower for p in palavras_aceite)

        if aceitou:
            return {
                "status": "aceito",
                "acao": "agendar",
                "mensagem": "Ótimo! Vou agendar. Qual horário fica melhor pra você?",
            }
        else:
            return {
                "status": "pendente",
                "acao": "nurturing",
                "mensagem": "Sem problemas! Quando quiser conversar, é só me chamar.",
            }

    def _gerar_horarios(self) -> list:
        """Gera horários sugeridos pra call"""
        agora = datetime.now()
        horarios = []

        # Próximos 3 dias úteis
        dias = 0
        data = agora

        while len(horarios) < 3:
            data = data + timedelta(days=1)
            if data.weekday() < 5:  # Dias úteis
                horarios.append({
                    "data": data.strftime("%d/%m/%Y"),
                    "dia_semana": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"][data.weekday()],
                    "horarios": ["09:00", "10:00", "14:00", "15:00", "16:00"],
                })
                dias += 1

        return horarios


async def main():
    """Execução standalone"""
    agendador = AgendadorCall()

    # Busca leads qualificados
    db = SessionLocal()
    leads = (
        db.query(Lead)
        .filter(Lead.score >= 60, Lead.status == "qualificado", Lead.whatsapp.isnot(None))
        .limit(5)
        .all()
    )
    db.close()

    print(f"📞 {len(leads)} leads qualificados pra call")

    for lead in leads:
        resultado = await agendador.enviar_convite_call(str(lead.id))
        print(f"   → {lead.nome}: {resultado.get('status', resultado.get('erro'))}")
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
