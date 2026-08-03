"""
LeadFlow - Utilitários de CNPJ
"""

import re
from typing import Optional


def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ"""
    # Remove caracteres especiais
    cnpj = re.sub(r'[^0-9]', '', cnpj)

    # Verifica tamanho
    if len(cnpj) != 14:
        return False

    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False

    # Validação do primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cnpj[12]) != digito1:
        return False

    # Validação do segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cnpj[13]) != digito2:
        return False

    return True


def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ: XX.XXX.XXX/XXXX-XX"""
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def limpar_cnpj(cnpj: str) -> str:
    """Remove formatação do CNPJ"""
    return re.sub(r'[^0-9]', '', cnpj)


def extrair_cnpj_de_texto(texto: str) -> Optional[str]:
    """Extrai CNPJ de um texto"""
    # Pattern pra CNPJ formatado ou não
    patterns = [
        r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',  # Formatado
        r'\d{14}',  # Só números
    ]

    for pattern in patterns:
        match = re.search(pattern, texto)
        if match:
            cnpj = limpar_cnpj(match.group())
            if validar_cnpj(cnpj):
                return cnpj

    return None


def cnpj_para_int(cnpj: str) -> int:
    """Converte CNPJ pra inteiro"""
    return int(limpar_cnpj(cnpj))


def int_para_cnpj(numero: int) -> str:
    """Converte inteiro pra CNPJ formatado"""
    cnpj = str(numero).zfill(14)
    return formatar_cnpj(cnpj)
