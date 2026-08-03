"""
LeadFlow - Automação: Exportação de Dados
"""

import csv
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from src.database import SessionLocal
from src.models.lead import Lead
from src.models.mensagem import Mensagem
from src.models.pipeline import Pipeline


class Exportador:
    """Exportação de dados pra CSV/Excel"""

    def __init__(self):
        os.makedirs("storage/exports", exist_ok=True)

    def exportar_leads_csv(self, status: str = None, filename: str = None) -> str:
        """Exporta leads pra CSV"""
        db = SessionLocal()

        try:
            query = db.query(Lead)
            if status:
                query = query.filter(Lead.status == status)

            leads = query.order_by(Lead.score.desc()).all()

            if not filename:
                filename = f"storage/exports/leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Nome", "Cargo", "Email", "Telefone", "WhatsApp",
                    "LinkedIn", "Instagram", "Score", "Status", "Fonte",
                    "Último Contato", "Criado em",
                ])

                for lead in leads:
                    writer.writerow([
                        lead.nome,
                        lead.cargo or "",
                        lead.email or "",
                        lead.telefone or "",
                        lead.whatsapp or "",
                        lead.linkedin or "",
                        lead.instagram or "",
                        lead.score,
                        lead.status,
                        lead.fonte or "",
                        lead.ultimo_contato.strftime("%d/%m/%Y %H:%M") if lead.ultimo_contato else "",
                        lead.created_at.strftime("%d/%m/%Y %H:%M"),
                    ])

            print(f"✅ {len(leads)} leads exportados pra {filename}")
            return filename

        finally:
            db.close()

    def exportar_pipeline_csv(self, filename: str = None) -> str:
        """Exporta pipeline pra CSV"""
        db = SessionLocal()

        try:
            pipeline_items = db.query(Pipeline).all()

            if not filename:
                filename = f"storage/exports/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Lead", "Etapa", "Valor", "Probabilidade",
                    "Previsão", "Motivo Perda", "Atualizado em",
                ])

                for item in pipeline_items:
                    writer.writerow([
                        item.lead.nome if item.lead else "N/A",
                        item.etapa,
                        float(item.valor or 0),
                        f"{item.probabilidade}%",
                        item.data_previsao.strftime("%d/%m/%Y") if item.data_previsao else "",
                        item.motivo_perda or "",
                        item.updated_at.strftime("%d/%m/%Y %H:%M"),
                    ])

            print(f"✅ Pipeline exportado pra {filename}")
            return filename

        finally:
            db.close()

    def exportar_mensagens_csv(self, lead_id: str = None, filename: str = None) -> str:
        """Exporta mensagens pra CSV"""
        db = SessionLocal()

        try:
            query = db.query(Mensagem)
            if lead_id:
                query = query.filter(Mensagem.lead_id == lead_id)

            mensagens = query.order_by(Mensagem.enviado_em.desc()).all()

            if not filename:
                filename = f"storage/exports/mensagens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Lead", "Conteúdo", "Tipo", "Status",
                    "Enviado em", "Lido em", "Resposta",
                ])

                for msg in mensagens:
                    writer.writerow([
                        msg.lead.nome if msg.lead else "N/A",
                        msg.conteudo[:200],
                        msg.tipo,
                        msg.status,
                        msg.enviado_em.strftime("%d/%m/%Y %H:%M"),
                        msg.lido_em.strftime("%d/%m/%Y %H:%M") if msg.lido_em else "",
                        "Sim" if msg.resposta else "Não",
                    ])

            print(f"✅ {len(mensagens)} mensagens exportadas pra {filename}")
            return filename

        finally:
            db.close()

    def gerar_relatorio_performance(self, periodo_dias: int = 30) -> dict:
        """Gera relatório de performance completo"""
        db = SessionLocal()

        try:
            from datetime import timedelta
            data_inicio = datetime.utcnow() - timedelta(days=periodo_dias)

            # Leads
            total_leads = db.query(Lead).count()
            leads_novos = db.query(Lead).filter(Lead.created_at >= data_inicio).count()
            leads_por_fonte = dict(
                db.query(Lead.fonte, Lead.count())
                .group_by(Lead.fonte)
                .all()
            )

            # Pipeline
            valor_total = db.query(Pipeline).with_entities(
                db.func.sum(Pipeline.valor)
            ).scalar() or 0

            leads_fechados = db.query(Pipeline).filter(
                Pipeline.etapa == "fechado",
                Pipeline.moved_at >= data_inicio,
            ).count()

            # Mensagens
            total_mensagens = db.query(Mensagem).filter(
                Mensagem.enviado_em >= data_inicio
            ).count()

            mensagens_respondidas = db.query(Mensagem).filter(
                Mensagem.enviado_em >= data_inicio,
                Mensagem.resposta == True,
            ).count()

            taxa_resposta = round((mensagens_respondidas / max(total_mensagens, 1)) * 100, 2)

            relatorio = {
                "periodo": f"Últimos {periodo_dias} dias",
                "gerado_em": datetime.utcnow().isoformat(),
                "leads": {
                    "total": total_leads,
                    "novos": leads_novos,
                    "por_fonte": leads_por_fonte,
                },
                "pipeline": {
                    "valor_total": float(valor_total),
                    "fechados": leads_fechados,
                    "taxa_conversao": round((leads_fechados / max(leads_novos, 1)) * 100, 2),
                },
                "mensagens": {
                    "total_enviadas": total_mensagens,
                    "respondidas": mensagens_respondidas,
                    "taxa_resposta": taxa_resposta,
                },
            }

            # Salva relatório
            import json
            filename = f"storage/exports/relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(relatorio, f, indent=2, default=str)

            print(f"✅ Relatório gerado: {filename}")
            return relatorio

        finally:
            db.close()


async def main():
    """Exporta todos os dados"""
    exportador = Exportador()

    print("📦 Exportando dados do LeadFlow...\n")

    exportador.exportar_leads_csv()
    exportador.exportar_pipeline_csv()
    exportador.exportar_mensagens_csv()
    exportador.gerar_relatorio_performance()

    print("\n✅ Exportação concluída!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
