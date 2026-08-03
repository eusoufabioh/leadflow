"""
LeadFlow - Modelo de Scoring de Leads
"""

import random
from typing import Dict, List


class LeadScorer:
    """Scoring de leads baseado em regras e IA"""

    # Pesos dos critérios
    PESOS = {
        "tamanho_empresa": 0.25,
        "engajamento": 0.25,
        "perfil_completo": 0.20,
        "interacao_recente": 0.15,
        "potencial_mercado": 0.15,
    }

    def calcular_score(self, lead_data: dict) -> Dict:
        """Calcula score baseado em múltiplos fatores"""
        scores = {}

        # 1. Tamanho da empresa
        scores["tamanho_empresa"] = self._score_tamanho(lead_data)

        # 2. Engajamento
        scores["engajamento"] = self._score_engajamento(lead_data)

        # 3. Perfil completo
        scores["perfil_completo"] = self._score_perfil(lead_data)

        # 4. Interação recente
        scores["interacao_recente"] = self._score_interacao(lead_data)

        # 5. Potencial de mercado
        scores["potencial_mercado"] = self._score_mercado(lead_data)

        # Score final ponderado
        score_final = sum(
            scores[k] * self.PESOS[k] for k in self.PESOS
        )

        # Classificação
        if score_final >= 80:
            classificacao = "quente"
        elif score_final >= 50:
            classificacao = "morno"
        else:
            classificacao = "frio"

        return {
            "score": round(score_final, 1),
            "classificacao": classificacao,
            "detalhes": scores,
            "recomendacao": self._gerar_recomendacao(score_final, classificacao),
        }

    def _score_tamanho(self, data: dict) -> float:
        """Score baseado no tamanho da empresa"""
        funcionarios = data.get("funcionarios", 0)

        if funcionarios >= 500:
            return 100
        elif funcionarios >= 100:
            return 80
        elif funcionarios >= 50:
            return 60
        elif funcionarios >= 10:
            return 40
        else:
            return 20

    def _score_engajamento(self, data: dict) -> float:
        """Score baseado no engajamento"""
        engajamento = data.get("engajamento", 0)

        # Normaliza pra 0-100
        return min(max(engajamento, 0), 100)

    def _score_perfil(self, data: dict) -> float:
        """Score baseado na completude do perfil"""
        campos = [
            "nome", "email", "telefone", "whatsapp",
            "linkedin", "instagram", "cargo",
        ]

        preenchidos = sum(1 for c in campos if data.get(c))
        return (preenchidos / len(campos)) * 100

    def _score_interacao(self, data: dict) -> float:
        """Score baseado em interações recentes"""
        dias_sem_contato = data.get("dias_sem_contato", 999)

        if dias_sem_contato <= 3:
            return 100
        elif dias_sem_contato <= 7:
            return 80
        elif dias_sem_contato <= 14:
            return 60
        elif dias_sem_contato <= 30:
            return 40
        else:
            return 20

    def _score_mercado(self, data: dict) -> float:
        """Score baseado no potencial de mercado"""
        nicho = data.get("nicho", "").lower()
        porte = data.get("porte", "").lower()

        # Nichos com alto potencial pra CRM
        nichos_quentes = ["tecnologia", "marketing", "consultoria", "saude", "educacao"]
        nichos_mornos = ["varejo", "industria", "servicos", "imobiliaria"]

        score_nicho = 50
        if any(n in nicho for n in nichos_quentes):
            score_nicho = 80
        elif any(n in nicho for n in nichos_mornos):
            score_nicho = 60

        # Porte
        score_porte = 50
        if porte in ["grande", "media"]:
            score_porte = 80
        elif porte == "pequena":
            score_porte = 50
        else:
            score_porte = 30

        return (score_nicho + score_porte) / 2

    def _gerar_recomendacao(self, score: float, classificacao: str) -> str:
        """Gera recomendação baseada no score"""
        if classificacao == "quente":
            return "Lead prioritário! Entrar em contato imediatamente. Considere call direta."
        elif classificacao == "morno":
            return "Lead com potencial. Nutrir com conteúdo e agendar call em 1-2 semanas."
        else:
            return "Lead frio. Adicionar em campanha de nurturing e reavaliar em 30 dias."
