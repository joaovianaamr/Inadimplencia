"""
Utilitários gerais: normalização de texto, remoção de acentos, etc.
"""

import re
import unicodedata
import logging
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """
    Normaliza texto: trim, reduz espaços, uppercase.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text.upper()


def remove_accents(text: str) -> str:
    """
    Remove acentos de uma string.
    
    Args:
        text: Texto com acentos
        
    Returns:
        Texto sem acentos
    """
    if not isinstance(text, str):
        return ""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def normalize_name(name: str, remove_accents_flag: bool = True) -> str:
    """
    Normaliza nome completo: trim, reduz espaços, uppercase, opcionalmente remove acentos.
    
    Args:
        name: Nome a normalizar
        remove_accents_flag: Se True, remove acentos
        
    Returns:
        Nome normalizado
    """
    normalized = normalize_text(name)
    if remove_accents_flag:
        normalized = remove_accents(normalized)
    return normalized


def create_person_id(pena_agua: str, nome: str) -> str:
    """
    Cria um person_id único: pena_agua|nome_normalizado.
    
    Args:
        pena_agua: Número da pena de água
        nome: Nome do pagador
        
    Returns:
        person_id no formato "pena_agua|nome_normalizado"
    """
    pena_agua_str = str(pena_agua).strip() if pena_agua else ""
    nome_norm = normalize_name(nome, remove_accents_flag=True)
    return f"{pena_agua_str}|{nome_norm}"


def safe_float(value: any, default: float = 0.0) -> float:
    """
    Converte valor para float de forma segura.
    
    Args:
        value: Valor a converter
        default: Valor padrão em caso de erro
        
    Returns:
        Float ou default
    """
    if value is None:
        return default
    try:
        # Tentar usar pd.isna se for pandas object
        if hasattr(pd, 'isna') and pd.isna(value):
            return default
    except (TypeError, AttributeError):
        pass
    
    if isinstance(value, (int, float)):
        return float(value)
    
    return default
