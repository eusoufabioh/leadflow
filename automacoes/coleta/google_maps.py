"""
LeadFlow - Automação de Coleta Google Maps
Execução standalone via Celery ou cron
"""

import asyncio
import sys
import os

# Adiciona path do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from src.services.coleta_leads import ColetaLeads
from src.database import SessionLocal
from src.models.lead import Lead
from src.models.empresa import Empresa


async def coletar_leads_google_maps(
    nicho: str,
    cidade: str,
    estado: str = None,
    raio_km: int = 10,
    limite: int = 50,
):
    """Coleta leads do Google Maps"""
    print(f"🔍 Iniciando coleta: {nicho} em {cidade}")
    print(f"   Raio: {raio_km}km | Limite: {limite} leads")

    coleta = ColetaLeads()
    leads = await coleta.google_maps(
        nicho=nicho,
        cidade=cidade,
        estado=estado,
        raio_km=raio_km,
        limite=limite,
    )

    print(f"✅ Coleta finalizada: {len(leads)} leads encontrados")

    for lead in leads:
        print(f"   → {lead['nome']}")

    return leads


async def coletar_varias_cidades(
    nicho: str,
    cidades: list,
    raio_km: int = 10,
    limite_por_cidade: int = 20,
):
    """Coleta leads em múltiplas cidades"""
    todos_leads = []

    for cidade_info in cidades:
        if isinstance(cidade_info, tuple):
            cidade, estado = cidade_info
        else:
            cidade = cidade_info
            estado = None

        leads = await coletar_leads_google_maps(
            nicho=nicho,
            cidade=cidade,
            estado=estado,
            raio_km=raio_km,
            limite=limite_por_cidade,
        )
        todos_leads.extend(leads)

        # Delay entre cidades pra não sobrecarregar API
        await asyncio.sleep(2)

    print(f"\n📊 Total: {len(todos_leads)} leads coletados em {len(cidades)} cidades")
    return todos_leads


if __name__ == "__main__":
    # Exemplo de uso
    asyncio.run(coletar_leads_google_maps(
        nicho="restaurante",
        cidade="São Paulo",
        estado="SP",
        raio_km=5,
        limite=10,
    ))
