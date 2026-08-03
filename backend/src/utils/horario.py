"""
LeadFlow - Utilitários de Horário
"""

from datetime import datetime, time, timedelta
from typing import Optional, Tuple
import pytz


# Fuso horário de Brasília
BRASILIA_TZ = pytz.timezone("America/Sao_Paulo")


def agora_brasilia() -> datetime:
    """Retorna datetime atual no fuso de Brasília"""
    return datetime.now(BRASILIA_TZ)


def melhor_horario_envio(
    cargo: Optional[str] = None,
    nicho: Optional[str] = None,
) -> Tuple[int, int]:
    """Sugere melhor horário pra enviar mensagem baseado no cargo/nicho"""

    # Horários base por tipo de cargo
    horarios_cargo = {
        "ceo": (9, 11),       # CEOs preferem manhã
        "cto": (10, 12),      # Tech leads depois das 10
        "cfo": (8, 10),       # Financeiro cedo
        "diretor": (9, 11),
        "gerente": (10, 12),
        "head": (10, 12),
        "coordenador": (14, 16),
        "analista": (14, 16),
        "default": (10, 12),
    }

    # Ajuste por nicho
    horarios_nicho = {
        "saude": (7, 9),          # Profissionais de saúde cedo
        "educacao": (17, 19),     # Educadores à tarde/noite
        "varejo": (8, 10),        # Varejo cedo
        "tecnologia": (10, 12),   # Tech flexível
        "financeiro": (8, 10),    # Financeiro cedo
        "marketing": (10, 12),
        "juridico": (9, 11),
    }

    # Define horário base
    hora_inicio = 10
    hora_fim = 12

    if cargo:
        cargo_lower = cargo.lower()
        for key, (ini, fim) in horarios_cargo.items():
            if key in cargo_lower:
                hora_inicio, hora_fim = ini, fim
                break

    if nicho:
        nicho_lower = nicho.lower()
        for key, (ini, fim) in horarios_nicho.items():
            if key in nicho_lower:
                hora_inicio, hora_fim = ini, fim
                break

    return hora_inicio, hora_fim


def melhor_dia_semana() -> str:
    """Retorna melhor dia da semana pra contato"""
    hoje = datetime.now().weekday()

    # Evita sexta à tarde e fim de semana
    if hoje >= 4:  # Sexta ou depois
        return "terça-feira"

    dias = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira"]
    return dias[hoje]


def esta_no_horario_comercial(data: Optional[datetime] = None) -> bool:
    """Verifica se está no horário comercial"""
    if data is None:
        data = agora_brasilia()

    hora = data.hour
    dia_semana = data.weekday()

    # Segunda a sexta, 8h às 18h
    return dia_semana < 5 and 8 <= hora < 18


def proximo_horario_comercial(data: Optional[datetime] = None) -> datetime:
    """Retorna próximo horário comercial"""
    if data is None:
        data = agora_brasilia()

    # Se já está no horário comercial, retorna a mesma hora
    if esta_no_horario_comercial(data):
        return data

    # Se é fim de semana, vai pra segunda
    if data.weekday() >= 5:
        dias_ate_segunda = 7 - data.weekday()
        data = data + timedelta(days=dias_ate_segunda)
        return data.replace(hour=9, minute=0, second=0)

    # Se é antes das 8h
    if data.hour < 8:
        return data.replace(hour=9, minute=0, second=0)

    # Se é depois das 18h, vai pra próximo dia útil
    data = data + timedelta(days=1)
    if data.weekday() >= 5:
        dias_ate_segunda = 7 - data.weekday()
        data = data + timedelta(days=dias_ate_segunda)

    return data.replace(hour=9, minute=0, second=0)


def formatar_hora_brasilia(dt: datetime) -> str:
    """Formata datetime pra Brasília"""
    if dt.tzinfo is None:
        dt = BRASILIA_TZ.localize(dt)
    return dt.strftime("%d/%m/%Y %H:%M")


def calcular_tempo_resposta(enviado_em: datetime, resposta_em: datetime) -> str:
    """Calcula tempo de resposta em formato legível"""
    delta = resposta_em - enviado_em
    segundos = int(delta.total_seconds())

    if segundos < 60:
        return f"{segundos}s"
    elif segundos < 3600:
        minutos = segundos // 60
        return f"{minutos}min"
    elif segundos < 86400:
        horas = segundos // 3600
        return f"{horas}h"
    else:
        dias = segundos // 86400
        return f"{dias}d"
