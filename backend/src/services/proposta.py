"""
LeadFlow - Serviço de Propostas
"""

from openai import AsyncOpenAI
from typing import Optional, Dict
from datetime import datetime, timedelta
from src.config import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import io
import os

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class PropostaService:
    """Geração e gestão de propostas"""

    async def gerar_proposta(self, lead, usuario, valor: Optional[float] = None) -> Dict:
        """Gera proposta personalizada via IA"""
        # Resume a conversa do lead
        resumo = await self._resumir_conversa(lead)

        # Gera conteúdo da proposta
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": """Você é um especialista em vendas B2B.
Gere uma proposta comercial profissional e persuasiva.

A proposta deve ter:
1. Cabeçalho com dados da empresa
2. Introdução personalizada
3. Entendimento do problema/necessidade
4. Solução apresentada
5. Benefícios esperados
6. Valores e condições
7. Próximos passos

Seja profissional mas acessível. Use dados específicos do lead."""},
                {"role": "user", "content": f"""
LEAD:
Nome: {lead.nome}
Cargo: {lead.cargo}
Empresa: {lead.empresa.nome_fantasia if lead.empresa else 'N/A'}
Nichoo: {lead.empresa.nicho if lead.empresa else 'N/A'}
Porte: {lead.empresa.porte if lead.empresa else 'N/A'}

RESUMO DA CONVERSA:
{resumo}

VALOR PROPOSTO: R$ {valor or 'a definir'}

Gere o conteúdo completo da proposta em markdown.
"""},
            ],
            max_tokens=2000,
            temperature=0.7,
        )

        conteudo = response.choices[0].message.content

        # Gera PDF
        pdf_url = await self._gerar_pdf(conteudo, lead)

        return {
            "conteudo": conteudo,
            "pdf_url": pdf_url,
            "valor": valor,
            "modelo": settings.OPENAI_MODEL,
        }

    async def _resumir_conversa(self, lead) -> str:
        """Resume histórico de conversa do lead"""
        if not lead.mensagens:
            return "Sem histórico de conversa."

        # Pega últimas 10 mensagens
        mensagens = sorted(lead.mensagens, key=lambda m: m.enviado_em)[-10:]
        historico = "\n".join([
            f"[{m.enviado_em.strftime('%d/%m %H:%M')}] {'Lead' if m.resposta else 'Vendedor'}: {m.conteudo[:200]}"
            for m in mensagens
        ])

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Resuma esta conversa de prospecção em 3-5 pontos principais. Foque nas necessidades e objeções do lead."},
                    {"role": "user", "content": historico},
                ],
                max_tokens=500,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception:
            return "Resumo não disponível."

    async def _gerar_pdf(self, conteudo: str, lead) -> Optional[str]:
        """Gera PDF da proposta"""
        try:
            # Diretório de propostas
            os.makedirs("storage/propostas", exist_ok=True)

            filename = f"storage/propostas/proposta_{lead.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            # Cabeçalho
            c.setFont("Helvetica-Bold", 24)
            c.drawString(2 * cm, height - 3 * cm, "Proposta Comercial")

            c.setFont("Helvetica", 12)
            c.drawString(2 * cm, height - 4 * cm, f"Para: {lead.nome}")
            if lead.empresa:
                c.drawString(2 * cm, height - 4.5 * cm, f"Empresa: {lead.empresa.nome_fantasia}")
            c.drawString(2 * cm, height - 5 * cm, f"Data: {datetime.now().strftime('%d/%m/%Y')}")

            # Linha separadora
            c.line(2 * cm, height - 5.5 * cm, width - 2 * cm, height - 5.5 * cm)

            # Conteúdo
            y = height - 7 * cm
            for line in conteudo.split("\n"):
                if y < 3 * cm:
                    c.showPage()
                    y = height - 3 * cm

                # Limita linha
                if len(line) > 80:
                    line = line[:80] + "..."

                c.setFont("Helvetica", 10)
                c.drawString(2 * cm, y, line)
                y -= 0.5 * cm

            c.save()

            return filename

        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return None

    async def sugerir_follow_up(self, lead, proposta) -> Dict:
        """Sugere follow-up após envio de proposta"""
        dias_sem_resposta = (datetime.utcnow() - proposta.enviada_em).days if proposta.enviada_em else 0

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": f"""Sugira uma mensagem de follow-up para uma proposta enviada há {dias_sem_resposta} dias.
Seja educado, não pressione, e ofereça valor adicional."""},
                {"role": "user", "content": f"Lead: {lead.nome}\nEmpresa: {lead.empresa.nome_fantasia if lead.empresa else 'N/A'}"},
            ],
            max_tokens=300,
            temperature=0.7,
        )

        return {"mensagem": response.choices[0].message.content}
