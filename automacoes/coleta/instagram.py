"""
LeadFlow - Automação de Coleta Instagram
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from src.services.coleta_leads import ColetaLeads


async def coletar_por_hashtags(
    hashtags: list,
    local: str = None,
    limite: int = 50,
):
    """Coleta leads por hashtags do Instagram"""
    print(f"📱 Iniciando coleta Instagram")
    print(f"   Hashtags: {', '.join(hashtags)}")
    if local:
        print(f"   Local: {local}")

    coleta = ColetaLeads()
    leads = await coleta.instagram(
        hashtags=hashtags,
        local=local,
        limite=limite,
    )

    print(f"✅ Coleta finalizada: {len(leads)} leads encontrados")
    return leads


async def coletar_nicho_completo(nicho: str, cidades: list = None):
    """Coleta leads de um nicho com hashtags relevantes"""

    # Mapeamento de nichos pra hashtags
    hashtags_por_nicho = {
        "restaurante": ["restaurante", "gastronomia", "foodie", "chef"],
        "academia": ["academia", "fitness", "treino", "personaltrainer"],
        "salao": ["salao", "cabelo", "beleza", "hairstylist"],
        "advocacia": ["advocacia", "advogado", "direito", "juridico"],
        "imobiliaria": ["imobiliaria", "imovel", "corretor", "imoveis"],
        "clinica": ["clinica", "saude", "medico", "dentista"],
        "escritorio": ["escritorio", "contabilidade", "contador", "consultoria"],
        "loja": ["loja", "ecommerce", "varejo", "moda"],
        "tecnologia": ["tecnologia", "startup", "software", "ti"],
        "marketing": ["marketing", "agencia", "publicidade", "mkt"],
    }

    hashtags = hashtags_por_nicho.get(nicho, [nicho])

    if cidades:
        # Adiciona cidade nas hashtags
        for cidade in cidades[:3]:
            hashtags.append(cidade.lower().replace(" ", ""))

    return await coletar_por_hashtags(
        hashtags=hashtags[:10],  # Limita a 10 hashtags
        local=cidades[0] if cidades else None,
        limite=50,
    )


if __name__ == "__main__":
    asyncio.run(coletar_por_hashtags(
        hashtags=["restaurante", "sp"],
        local="São Paulo",
        limite=10,
    ))
