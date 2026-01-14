"""
Análise de reincidência: devedores recorrentes, padrões mês a mês.
"""

import logging
from typing import Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_recurrence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula reincidência de devedores: quantos meses apareceram, quantos boletos, etc.
    
    Args:
        df: DataFrame com dados limpos (apenas OPEN)
        
    Returns:
        DataFrame com detalhes de reincidência por pessoa
    """
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    
    if len(df_open) == 0:
        return pd.DataFrame()
    
    # Agrupar por person_id
    recurrence = df_open.groupby('person_id').agg({
        'mes_referencia': ['nunique', lambda x: sorted(x.unique().tolist())],
        'valor_float': ['sum', 'mean', 'count'],
        'pena_agua': 'first',
        'nome_pagador': 'first',
        'status_norm': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None,
    }).reset_index()
    
    recurrence.columns = [
        'person_id',
        'meses_apareceu',
        'meses_lista',
        'soma_open',
        'media_open',
        'qtd_boletos_open',
        'pena_agua',
        'nome',
        'status_mais_comum'
    ]
    
    # Converter meses_lista para string para facilitar exportação
    recurrence['meses_lista'] = recurrence['meses_lista'].apply(lambda x: ', '.join(map(str, x)))
    
    return recurrence.sort_values('qtd_boletos_open', ascending=False)


def get_top_recurrent_debtors(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Ranking de devedores por reincidência (quantidade de boletos em aberto).
    
    Args:
        df: DataFrame com dados limpos
        top_n: Número de top reincidentes
        
    Returns:
        DataFrame com ranking
    """
    recurrence = calculate_recurrence(df)
    
    if len(recurrence) == 0:
        return pd.DataFrame()
    
    top = recurrence.sort_values('qtd_boletos_open', ascending=False).head(top_n)
    top['rank'] = range(1, len(top) + 1)
    
    return top[['rank', 'person_id', 'pena_agua', 'nome', 'qtd_boletos_open', 'meses_apareceu', 'soma_open', 'media_open', 'status_mais_comum']]


def calculate_recurrence_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula quantos devedores repetiram mês a mês.
    
    Args:
        df: DataFrame com dados limpos
        
    Returns:
        DataFrame com contagem de reincidentes por mês
    """
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    
    if len(df_open) == 0:
        return pd.DataFrame()
    
    # Para cada mês, contar quantos devedores já apareceram em meses anteriores
    meses_ordenados = sorted(df_open['mes_referencia'].unique())
    
    recurrence_by_month = []
    devedores_anteriores = set()
    
    for mes in meses_ordenados:
        devedores_mes_atual = set(df_open[df_open['mes_referencia'] == mes]['person_id'].unique())
        devedores_novos = devedores_mes_atual - devedores_anteriores
        devedores_reincidentes = devedores_mes_atual & devedores_anteriores
        
        recurrence_by_month.append({
            'mes_referencia': mes,
            'qtd_devedores_total': len(devedores_mes_atual),
            'qtd_devedores_novos': len(devedores_novos),
            'qtd_devedores_reincidentes': len(devedores_reincidentes),
            'pct_reincidentes': (len(devedores_reincidentes) / len(devedores_mes_atual) * 100) if len(devedores_mes_atual) > 0 else 0.0,
        })
        
        devedores_anteriores.update(devedores_mes_atual)
    
    return pd.DataFrame(recurrence_by_month)
