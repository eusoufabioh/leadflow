"""
LeadFlow - Serviço de Score de Leads
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from src.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class ScoreLeads:
    """Score de oportunidade baseado em múltiplos fatores"""

    # Pesos pra cada critério
    PESOS = {
        "tamanho_empresa": 25,
        "engajamento": 25,
        "perfil_completo": 20,
        "interacao_recente": 15,
        "potencial_mercado": 15,
    }

    async def calcular_score(self, lead) -> Dict:
        """Calcula score completo do lead"""
        detalhes = {}
        score_total = 0

        # 1. Tamanho da empresa (0-25)
        score_empresa = self._score_tamanho_empresa(lead)
        detalhes["tamanho_empresa"] = score_empresa
        score_total += score_empresa

        # 2. Engajamento (0-25)
        score_engajamento = self._score_engajamento(lead)
        detalhes["engajamento"] = score_engajamento
        score_total += score_engajamento

        # 3. Perfil completo (0-20)
        score_perfil = self._score_perfil_completo(lead)
        detalhes["perfil_completo"] = score_perfil
        score_total += score_perfil

        # 4. Interação recente (0-15)
        score_interacao = self._score_interacao_recente(lead)
        detalhes["interacao_recente"] = score_interacao
        score_total += score_interacao

        # 5. Potencial de mercado via IA (0-15)
        score_mercado = await self._score_potencial_mercado(lead)
        detalhes["potencial_mercado"] = score_mercado
        score_total += score_mercado

        # Classificação
        if score_total >= 80:
            classificacao = "quente"
        elif score_total >= 50:
            classificacao = "morno"
        else:
            classificacao = "frio"

        return {
            "score": min(score_total, 100),
            "detalhes": detalhes,
            "classificacao": classificacao,
        }

    def _score_tamanho_empresa(self, lead) -> int:
        """Score baseado no tamanho da empresa"""
        if not lead.empresa:
            return 5  # Sem empresa = baixo

        score = 0
        funcionarios = lead.empresa.funcionarios or 0

        # Porte da empresa
        if funcionarios >= 500:
            score = 25
        elif funcionarios >= 100:
            score = 20
        elif funcionarios >= 50:
            score = 15
        elif funcionarios >= 10:
            score = 10
        else:
            score = 5

        # Bonus se tem faturamento estimado
        if lead.empresa.faturamento_estimado:
            if lead.empresa.faturamento_estimado >= 10000000:  # 10M+
                score = min(score + 5, 25)
            elif lead.empresa.faturamento_estimado >= 1000000:  # 1M+
                score = min(score + 3, 25)

        return score

    def _score_engajamento(self, lead) -> int:
        """Score baseado no engajamento"""
        engajamento = lead.engajamento or 0

        if engajamento >= 80:
            return 25
        elif engajamento >= 60:
            return 20
        elif engajamento >= 40:
            return 15
        elif engajamento >= 20:
            return 10
        else:
            return 5

    def _score_perfil_completo(self, lead) -> int:
        """Score baseado na completude do perfil"""
        campos = [
            lead.nome,
            lead.email,
            lead.telefone,
            lead.whatsapp,
            lead.linkedin,
            lead.instagram,
            lead.cargo,
        ]

        preenchidos = sum(1 for c in campos if c)
        return int((preenchidos / len(campos)) * 20)

    def _score_interacao_recente(self, lead) -> int:
        """Score baseado em interações recentes"""
        if not lead.ultimo_contato:
            return 0

        dias_sem_contato = (datetime.utcnow() - lead.ultimo_contato).days

        if dias_sem_contato <= 3:
            return 15
        elif dias_sem_contato <= 7:
            return 12
        elif dias_sem_contato <= 14:
            return 8
        elif dias_sem_contato <= 30:
            return 5
        else:
            return 2

    async def _score_potencial_mercado(self, lead) -> int:
        """Score baseado no potencial de mercado via IA"""
        try:
            nicho = lead.empresa.nicho if lead.empresa else "geral"
            porte = lead.empresa.porte if lead.empresa else "desconhecido"
            cidade = lead.empresa.cidade if lead.empresa else ""

            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": """Analise o potencial de mercado deste lead pra uma solução de CRM/prospecção B2B.
Retorne APENAS um número de 0 a 15, onde:
- 0-5: Baixo potencial
- 6-10: Médio potencial
- 11-15: Alto potencial

Considere: nicho, porte, localização, probabilidade de precisar de CRM."""},
                    {"role": "user", "content": f"Nicho: {nicho}\nPorte: {porte}\nCidade: {cidade}"},
                ],
                max_tokens=10,
                temperature=0.3,
            )

            score = int(response.choices[0].message.content.strip())
            return min(max(score, 0), 15)

        except Exception:
            return 8  # Score médio default
