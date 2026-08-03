"""
LeadFlow - Serviço de IA para Prospecção
"""

from openai import AsyncOpenAI
from typing import Optional, Dict, List
from datetime import datetime
from src.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class IAProspeccao:
    """IA especializada em prospecção B2B"""

    def __init__(self):
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS

    async def gerar_mensagem(
        self,
        lead,
        template_id: Optional[str] = None,
        tom: str = "profissional",
    ) -> Dict:
        """Gera mensagem personalizada pra cada lead"""
        # Carrega prompt base
        prompt = self._carregar_prompt("prospeccao")

        # Monta contexto do lead
        contexto = self._montar_contexto(lead)

        # Prompt final
        system_prompt = f"""Você é um especialista em prospecção B2B.
Gere uma mensagem personalizada de WhatsApp para este lead.

CONTEXTO DO LEAD:
{contexto}

TOM: {tom}

REGRAS:
- Máximo 500 caracteres
- Use emojis moderadamente
- Seja direto e específico
- Mencione algo específico da empresa/nicho do lead
- Inclua uma call-to-action clara
- Não use linguagem agressiva ou spam
"""

        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Gere a mensagem personalizada."},
            ],
            max_tokens=self.max_tokens,
            temperature=0.7,
        )

        mensagem = response.choices[0].message.content
        tokens = response.usage.total_tokens

        return {
            "mensagem": mensagem,
            "modelo": self.model,
            "tokens": tokens,
        }

    async def gerar_follow_up(self, lead, ultima_mensagem: str) -> str:
        """Gera mensagem de follow-up"""
        contexto = self._montar_contexto(lead)

        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"""Você é um especialista em prospecção B2B.
Gere uma mensagem de follow-up natural e não invasiva.

CONTEXTO DO LEAD:
{contexto}

ÚLTIMA MENSAGEM ENVIADA:
{ultima_mensagem}

REGRAS:
- Máximo 300 caracteres
- Seja educado e respeitoso
- Ofereça valor adicional
- Não pressione demais
"""},
                {"role": "user", "content": "Gere o follow-up."},
            ],
            max_tokens=500,
            temperature=0.7,
        )

        return response.choices[0].message.content

    async def qualificar_lead(self, lead) -> Dict:
        """Qualifica lead via IA"""
        contexto = self._montar_contexto(lead)

        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"""Analise este lead e classifique:

CONTEXTO:
{contexto}

Retorne um JSON com:
- qualificacao: "quente", "morno", "frio"
- score_sugerido: 0-100
- motivo: explicação breve
- melhor_abordagem: sugestão de como abordar
- melhor_horario: melhor dia/horário pra contato
"""},
                {"role": "user", "content": "Qualifique este lead."},
            ],
            max_tokens=500,
            temperature=0.3,
        )

        return {"analise": response.choices[0].message.content}

    async def sugerir_horario(self, lead) -> Dict:
        """Sugere melhor horário pra enviar mensagem"""
        contexto = self._montar_contexto(lead)

        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"""Baseado no perfil do lead, sugira o melhor horário pra enviar mensagem via WhatsApp.

CONTEXTO:
{contexto}

Retorne JSON com:
- dia_semana: melhor dia
- horario: melhor horário
- motivo: por que esse horário
"""},
                {"role": "user", "content": "Sugira o melhor horário."},
            ],
            max_tokens=300,
            temperature=0.5,
        )

        return {"horario_sugerido": response.choices[0].message.content}

    async def criar_ab_test(self, lead, variacoes: int = 3) -> Dict:
        """Cria variações de mensagem pra A/B test"""
        contexto = self._montar_contexto(lead)

        response = await client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"""Crie {variacoes} variações de mensagem de prospecção para A/B test.

CONTEXTO:
{contexto}

Cada variação deve ter uma abordagem diferente:
1. Abordagem direta/foco em resultado
2. Abordagem de conexão/relacionamento
3. Abordagem de curiosidade/pergunta

Retorne JSON com array de variações, cada uma com:
- abordagem: tipo de abordagem
- mensagem: texto da mensagem
"""},
                {"role": "user", "content": f"Crie {variacoes} variações."},
            ],
            max_tokens=1000,
            temperature=0.8,
        )

        return {"variacoes": response.choices[0].message.content}

    def _montar_contexto(self, lead) -> str:
        """Monta contexto do lead pra IA"""
        partes = [f"Nome: {lead.nome}"]

        if lead.cargo:
            partes.append(f"Cargo: {lead.cargo}")
        if lead.empresa:
            partes.append(f"Empresa: {lead.empresa.nome_fantasia or lead.empresa.razao_social}")
            if lead.empresa.nicho:
                partes.append(f"Nichoo: {lead.empresa.nicho}")
            if lead.empresa.porte:
                partes.append(f"Porte: {lead.empresa.porte}")
            if lead.empresa.cidade:
                partes.append(f"Cidade: {lead.empresa.cidade}")
            if lead.empresa.funcionarios:
                partes.append(f"Funcionários: {lead.empresa.funcionarios}")
        if lead.score:
            partes.append(f"Score atual: {lead.score}/100")
        if lead.fonte:
            partes.append(f"Fonte: {lead.fonte}")
        if lead.notas:
            partes.append(f"Notas: {lead.notas}")

        return "\n".join(partes)

    def _carregar_prompt(self, nome: str) -> str:
        """Carrega prompt do arquivo"""
        try:
            with open(f"ia/prompts/{nome}.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return ""
