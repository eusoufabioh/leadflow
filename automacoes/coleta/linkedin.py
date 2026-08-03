"""
LeadFlow - Automação de Coleta LinkedIn
Nota: LinkedIn não tem API pública. Este módulo usa proxy/RapidAPI.
"""

import asyncio
import httpx
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from src.config import settings
from src.database import SessionLocal
from src.models.lead import Lead


class LinkedInScraper:
    """Coleta de leads do LinkedIn via proxy"""

    def __init__(self):
        # RapidAPI LinkedIn
        self.api_url = "https://linkedin-data-api.p.rapidapi.com"
        self.api_key = getattr(settings, 'LINKEDIN_API_KEY', '')

    async def buscar_pessoas(
        self,
        cargo: str,
        empresa: str = None,
        local: str = None,
        limite: int = 50,
    ) -> list:
        """Busca pessoas por cargo"""
        if not self.api_key:
            print("⚠️  LinkedIn API key não configurada")
            return []

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "linkedin-data-api.p.rapidapi.com",
        }

        params = {
            "keyword": cargo,
            "start": 0,
        }

        if empresa:
            params["keyword"] += f" {empresa}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.apiUrl}/search/people",
                    headers=headers,
                    params=params,
                    timeout=30.0,
                )

                if response.status_code != 200:
                    print(f"Erro na API: {response.status_code}")
                    return []

                data = response.json()
                pessoas = data.get("data", [])[:limite]

                return [
                    {
                        "nome": p.get("fullName"),
                        "cargo": p.get("headline"),
                        "linkedin": p.get("profileUrl"),
                        "local": p.get("location"),
                        "empresa": p.get("company"),
                    }
                    for p in pessoas
                ]

        except Exception as e:
            print(f"Erro ao buscar LinkedIn: {e}")
            return []

    async def buscar_empresas(
        self,
        nicho: str,
        local: str = None,
        limite: int = 50,
    ) -> list:
        """Busca empresas por nicho"""
        if not self.api_key:
            print("⚠️  LinkedIn API key não configurada")
            return []

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "linkedin-data-api.p.rapidapi.com",
        }

        params = {
            "keyword": nicho,
            "start": 0,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/search/companies",
                    headers=headers,
                    params=params,
                    timeout=30.0,
                )

                if response.status_code != 200:
                    return []

                data = response.json()
                empresas = data.get("data", [])[:limite]

                return [
                    {
                        "nome": e.get("name"),
                        "linkedin": e.get("url"),
                        "funcionarios": e.get("employeeCount"),
                        "nicho": e.get("industry"),
                        "local": e.get("headquarter"),
                    }
                    for e in empresas
                ]

        except Exception as e:
            print(f"Erro ao buscar empresas: {e}")
            return []


async def coletar_leads_linkedin(
    cargo: str,
    empresa: str = None,
    local: str = None,
    limite: int = 50,
):
    """Coleta leads do LinkedIn"""
    print(f"🔗 Iniciando coleta LinkedIn")
    print(f"   Cargo: {cargo}")

    scraper = LinkedInScraper()
    pessoas = await scraper.buscar_pessoas(
        cargo=cargo,
        empresa=empresa,
        local=local,
        limite=limite,
    )

    # Salva no banco
    db = SessionLocal()
    leads_criados = []

    try:
        for pessoa in pessoas:
            lead = Lead(
                nome=pessoa["nome"],
                cargo=pessoa["cargo"],
                linkedin=pessoa["linkedin"],
                fonte="linkedin",
                notas=f"Empresa: {pessoa.get('empresa', 'N/A')} | Local: {pessoa.get('local', 'N/A')}",
            )
            db.add(lead)
            leads_criados.append(lead)

        db.commit()
        print(f"✅ {len(leads_criados)} leads importados")

    except Exception as e:
        db.rollback()
        print(f"Erro ao salvar: {e}")
    finally:
        db.close()

    return [{"id": str(l.id), "nome": l.nome} for l in leads_criados]


if __name__ == "__main__":
    asyncio.run(coletar_leads_linkedin(
        cargo="CTO",
        local="São Paulo",
        limite=10,
    ))
