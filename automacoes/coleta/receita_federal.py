"""
LeadFlow - Automação de Consulta Receita Federal (CNPJ)
"""

import asyncio
import httpx
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from src.database import SessionLocal
from src.models.empresa import Empresa
from src.models.lead import Lead


async def consultar_cnpj(cnpj: str) -> dict:
    """Consulta CNPJ na Receita Federal via BrasilAPI"""
    cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")

    if len(cnpj_limpo) != 14:
        print(f"❌ CNPJ inválido: {cnpj}")
        return {}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}",
                timeout=10.0,
            )

            if response.status_code != 200:
                print(f"❌ CNPJ não encontrado: {cnpj}")
                return {}

            data = response.json()

            return {
                "cnpj": data.get("cnpj"),
                "razao_social": data.get("razao_social"),
                "nome_fantasia": data.get("nome_fantasia"),
                "cidade": data.get("municipio"),
                "estado": data.get("uf"),
                "bairro": data.get("bairro"),
                "logradouro": data.get("logradouro"),
                "numero": data.get("numero"),
                "cep": data.get("cep"),
                "telefone": data.get("ddd_telefone_1"),
                "email": data.get("email"),
                "situacao": data.get("situacao_cadastral"),
                "data_abertura": data.get("data_inicio_atividade"),
                "cnae": data.get("cnae_fiscal_descricao"),
                "natureza_juridica": data.get("natureza_juridica"),
                "capital_social": data.get("capital_social"),
            }

    except Exception as e:
        print(f"❌ Erro ao consultar CNPJ: {e}")
        return {}


async def importar_empresa_cnpj(cnpj: str) -> dict:
    """Importa empresa por CNPJ pra base de dados"""
    dados = await consultar_cnpj(cnpj)
    if not dados:
        return {"erro": "CNPJ não encontrado"}

    db = SessionLocal()

    try:
        # Verifica se já existe
        empresa = db.query(Empresa).filter(Empresa.cnpj == dados["cnpj"]).first()
        if empresa:
            return {"mensagem": "Empresa já existe", "empresa_id": str(empresa.id)}

        # Cria empresa
        endereco = f"{dados.get('logradouro', '')}, {dados.get('numero', '')} - {dados.get('bairro', '')}"

        empresa = Empresa(
            cnpj=dados["cnpj"],
            razao_social=dados["razao_social"],
            nome_fantasia=dados.get("nome_fantasia") or dados["razao_social"],
            cidade=dados.get("cidade"),
            estado=dados.get("estado"),
            endereco=endereco,
            telefone=dados.get("telefone"),
            email=dados.get("email"),
            nicho=dados.get("cnae"),
        )
        db.add(empresa)
        db.commit()
        db.refresh(empresa)

        return {
            "mensagem": "Empresa importada com sucesso",
            "empresa_id": str(empresa.id),
            "razao_social": empresa.razao_social,
        }

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}
    finally:
        db.close()


async def importar_lote_cnpjs(cnpjs: list) -> dict:
    """Importa múltiplos CNPJs"""
    resultados = {
        "sucesso": [],
        "ja_existiam": [],
        "erros": [],
    }

    for cnpj in cnpjs:
        resultado = await importar_empresa_cnpj(cnpj)

        if resultado.get("erro"):
            resultados["erros"].append({"cnpj": cnpj, "erro": resultado["erro"]})
        elif resultado.get("mensagem") == "Empresa já existe":
            resultados["ja_existiam"].append(cnpj)
        else:
            resultados["sucesso"].append({
                "cnpj": cnpj,
                "empresa_id": resultado.get("empresa_id"),
            })

        # Delay entre consultas
        await asyncio.sleep(0.5)

    print(f"📊 Resultado:")
    print(f"   ✅ Importadas: {len(resultados['sucesso'])}")
    print(f"   ℹ️  Já existiam: {len(resultados['ja_existiam'])}")
    print(f"   ❌ Erros: {len(resultados['erros'])}")

    return resultados


async def buscar_por_cnae(cnae: str, cidade: str = None) -> list:
    """Busca empresas por CNAE (atividade econômica)"""
    # Nota: BrasilAPI não tem busca por CNAE
    # Alternativa: ReceitaWS ou ReceitaNet
    print("⚠️  Busca por CNAE requer API adicional (ReceitaWS/ReceitaNet)")
    return []


if __name__ == "__main__":
    # Teste com CNPJ exemplo
    asyncio.run(importar_empresa_cnpj("11222333000181"))
