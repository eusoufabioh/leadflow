"""
LeadFlow - Automação: Dashboard em Tempo Real
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from src.database import SessionLocal
from src.models.lead import Lead
from src.models.mensagem import Mensagem
from src.models.pipeline import Pipeline
from sqlalchemy import func


class DashboardService:
    """Dashboard com métricas em tempo real"""

    def get_metricas(self, periodo_dias: int = 30) -> dict:
        """Retorna métricas principais"""
        db = SessionLocal()
        data_inicio = datetime.utcnow() - timedelta(days=periodo_dias)

        try:
            # Total de leads
            total_leads = db.query(func.count(Lead.id)).scalar() or 0

            # Leads novos no período
            leads_novos = (
                db.query(func.count(Lead.id))
                .filter(Lead.created_at >= data_inicio)
                .scalar() or 0
            )

            # Leads por status
            leads_por_status = dict(
                db.query(Lead.status, func.count(Lead.id))
                .group_by(Lead.status)
                .all()
            )

            # Pipeline por etapa
            pipeline_dados = (
                db.query(
                    Pipeline.etapa,
                    func.count(Pipeline.id),
                    func.sum(Pipeline.valor),
                )
                .group_by(Pipeline.etapa)
                .all()
            )

            pipeline_por_etapa = {
                etapa: {"total": total, "valor": float(valor or 0)}
                for etapa, total, valor in pipeline_dados
            }

            # Valor total no pipeline
            valor_pipeline = sum(v["valor"] for v in pipeline_por_etapa.values())

            # Leads fechados no período
            leads_fechados = (
                db.query(func.count(Pipeline.id))
                .filter(Pipeline.etapa == "fechado", Pipeline.moved_at >= data_inicio)
                .scalar() or 0
            )

            # Mensagens enviadas
            mensagens_enviadas = (
                db.query(func.count(Mensagem.id))
                .filter(Mensagem.enviado_em >= data_inicio)
                .scalar() or 0
            )

            # Taxa de resposta
            mensagens_respondidas = (
                db.query(func.count(Mensagem.id))
                .filter(Mensagem.enviado_em >= data_inicio, Mensagem.resposta == True)
                .scalar() or 0
            )
            taxa_resposta = round((mensagens_respondidas / max(mensagens_enviadas, 1)) * 100, 2)

            # Leads por dia (últimos 7 dias)
            leads_por_dia = []
            for i in range(7):
                dia = datetime.utcnow() - timedelta(days=6 - i)
                count = (
                    db.query(func.count(Lead.id))
                    .filter(func.date(Lead.created_at) == dia.date())
                    .scalar() or 0
                )
                leads_por_dia.append({
                    "dia": dia.strftime("%d/%m"),
                    "total": count,
                })

            # Top 5 leads por score
            top_leads = (
                db.query(Lead)
                .order_by(Lead.score.desc())
                .limit(5)
                .all()
            )

            return {
                "periodo_dias": periodo_dias,
                "total_leads": total_leads,
                "leads_novos": leads_novos,
                "leads_fechados": leads_fechados,
                "valor_pipeline": valor_pipeline,
                "mensagens_enviadas": mensagens_enviadas,
                "taxa_resposta": taxa_resposta,
                "leads_por_status": leads_por_status,
                "pipeline_por_etapa": pipeline_por_etapa,
                "leads_por_dia": leads_por_dia,
                "top_leads": [
                    {"id": str(l.id), "nome": l.nome, "score": l.score, "status": l.status}
                    for l in top_leads
                ],
                "atualizado_em": datetime.utcnow().isoformat(),
            }

        finally:
            db.close()

    def get_conversao_etapas(self) -> dict:
        """Taxa de conversão entre etapas do pipeline"""
        db = SessionLocal()

        try:
            etapas = ["lead", "qualificado", "contato", "call", "proposta", "fechado"]
            contagem = {}

            for etapa in etapas:
                contagem[etapa] = db.query(func.count(Pipeline.id)).filter(
                    Pipeline.etapa == etapa
                ).scalar() or 0

            taxas = {}
            for i in range(len(etapas) - 1):
                atual = contagem[etapas[i]]
                proximo = contagem[etapas[i + 1]]
                taxa = round((proximo / max(atual, 1)) * 100, 2)
                taxas[f"{etapas[i]}_para_{etapas[i+1]}"] = taxa

            return {
                "etapas": contagem,
                "taxas": taxas,
                "taxa_geral": round(
                    (contagem.get("fechado", 0) / max(contagem.get("lead", 1), 1)) * 100, 2
                ),
            }

        finally:
            db.close()

    def get_performance_vendedores(self) -> list:
        """Performance por vendedor"""
        db = SessionLocal()

        try:
            from src.models.usuario import Usuario

            vendedores = (
                db.query(
                    Lead.responsavel_id,
                    func.count(Lead.id).label("total_leads"),
                    func.avg(Lead.score).label("score_medio"),
                )
                .filter(Lead.responsavel_id.isnot(None))
                .group_by(Lead.responsavel_id)
                .all()
            )

            resultado = []
            for resp_id, total, score_medio in vendedores:
                # Busca pipeline
                pipeline = (
                    db.query(
                        func.count(Pipeline.id).label("total"),
                        func.sum(Pipeline.valor).label("valor"),
                    )
                    .filter(Pipeline.responsavel_id == resp_id)
                    .first()
                )

                resultado.append({
                    "responsavel_id": str(resp_id),
                    "total_leads": total,
                    "score_medio": round(float(score_medio or 0), 1),
                    "pipeline_total": pipeline[0] if pipeline else 0,
                    "pipeline_valor": float(pipeline[1] or 0) if pipeline else 0,
                })

            return sorted(resultado, key=lambda x: x["pipeline_valor"], reverse=True)

        finally:
            db.close()


async def main():
    """Gera relatório do dashboard"""
    dashboard = DashboardService()

    print("📊 Gerando dashboard...")
    metricas = dashboard.get_metricas(30)

    print(f"\n{'='*50}")
    print(f"LEADFLOW - DASHBOARD ({metricas['periodo_dias']} dias)")
    print(f"{'='*50}")
    print(f"Total de Leads: {metricas['total_leads']}")
    print(f"Leads Novos: {metricas['leads_novos']}")
    print(f"Leads Fechados: {metricas['leads_fechados']}")
    print(f"Valor no Pipeline: R$ {metricas['valor_pipeline']:,.2f}")
    print(f"Mensagens Enviadas: {metricas['mensagens_enviadas']}")
    print(f"Taxa de Resposta: {metricas['taxa_resposta']}%")

    print(f"\n📈 Leads por Status:")
    for status, total in metricas['leads_por_status'].items():
        print(f"   {status}: {total}")

    print(f"\n🏆 Top Leads:")
    for lead in metricas['top_leads']:
        print(f"   {lead['nome']} (Score: {lead['score']})")


if __name__ == "__main__":
    asyncio.run(main())
