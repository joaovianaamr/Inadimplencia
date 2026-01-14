"""
Cálculo de métricas de inadimplência: KPIs, rankings, estatísticas.
"""

import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def calculate_open_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula métricas gerais apenas para boletos em aberto (OPEN).
    
    Args:
        df: DataFrame com dados limpos e classificados
        
    Returns:
        Dicionário com métricas
    """
    # Filtrar apenas OPEN
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    
    if len(df_open) == 0:
        logger.warning("Nenhum boleto em aberto encontrado")
        return {
            'total_devedores_unicos': 0,
            'total_boletos_em_aberto': 0,
            'soma_divida_em_aberto': 0.0,
            'ticket_medio_em_aberto': 0.0,
            'valor_medio': 0.0,
            'valor_mediana': 0.0,
            'valor_moda': 0.0,
            'valor_desvio_padrao': 0.0,
            'valor_p90': 0.0,
            'valor_p95': 0.0,
            'maior_divida_individual': 0.0,
            'maior_divida_person_id': None,
            'maior_divida_nome': None,
            'maior_divida_pena_agua': None,
            'menor_divida_individual': 0.0,
            'menor_divida_person_id': None,
            'menor_divida_nome': None,
            'menor_divida_pena_agua': None,
        }
    
    # Valores válidos
    valores = df_open[df_open['valor_valido']]['valor_float']
    
    # Métricas básicas
    total_devedores_unicos = df_open['person_id'].nunique()
    total_boletos_em_aberto = len(df_open)
    soma_divida_em_aberto = valores.sum()
    ticket_medio_em_aberto = soma_divida_em_aberto / total_devedores_unicos if total_devedores_unicos > 0 else 0.0
    
    # Estatísticas descritivas
    valor_medio = valores.mean() if len(valores) > 0 else 0.0
    valor_mediana = valores.median() if len(valores) > 0 else 0.0
    valor_moda = valores.mode().iloc[0] if len(valores.mode()) > 0 else 0.0
    valor_desvio_padrao = valores.std() if len(valores) > 0 else 0.0
    valor_p90 = valores.quantile(0.90) if len(valores) > 0 else 0.0
    valor_p95 = valores.quantile(0.95) if len(valores) > 0 else 0.0
    
    # Maior e menor dívida individual (por pessoa)
    dividas_por_pessoa = df_open.groupby('person_id')['valor_float'].sum().sort_values(ascending=False)
    
    if len(dividas_por_pessoa) > 0:
        maior_person_id = dividas_por_pessoa.index[0]
        maior_divida = dividas_por_pessoa.iloc[0]
        maior_row = df_open[df_open['person_id'] == maior_person_id].iloc[0]
        
        menor_person_id = dividas_por_pessoa.index[-1]
        menor_divida = dividas_por_pessoa.iloc[-1]
        menor_row = df_open[df_open['person_id'] == menor_person_id].iloc[0]
    else:
        maior_person_id = None
        maior_divida = 0.0
        maior_row = None
        menor_person_id = None
        menor_divida = 0.0
        menor_row = None
    
    return {
        'total_devedores_unicos': int(total_devedores_unicos),
        'total_boletos_em_aberto': int(total_boletos_em_aberto),
        'soma_divida_em_aberto': float(soma_divida_em_aberto),
        'ticket_medio_em_aberto': float(ticket_medio_em_aberto),
        'valor_medio': float(valor_medio),
        'valor_mediana': float(valor_mediana),
        'valor_moda': float(valor_moda),
        'valor_desvio_padrao': float(valor_desvio_padrao),
        'valor_p90': float(valor_p90),
        'valor_p95': float(valor_p95),
        'maior_divida_individual': float(maior_divida),
        'maior_divida_person_id': maior_person_id,
        'maior_divida_nome': maior_row['nome_pagador'] if maior_row is not None else None,
        'maior_divida_pena_agua': maior_row['pena_agua'] if maior_row is not None else None,
        'menor_divida_individual': float(menor_divida),
        'menor_divida_person_id': menor_person_id,
        'menor_divida_nome': menor_row['nome_pagador'] if menor_row is not None else None,
        'menor_divida_pena_agua': menor_row['pena_agua'] if menor_row is not None else None,
    }


def calculate_open_metrics_by_bank(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas de inadimplência por banco.
    
    Args:
        df: DataFrame com dados limpos e classificados
        
    Returns:
        DataFrame com métricas por banco
    """
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    
    if len(df_open) == 0:
        return pd.DataFrame()
    
    # Agrupar por banco
    metrics_by_bank = df_open.groupby('banco').agg({
        'valor_float': ['sum', 'mean', 'median', 'std', 'count'],
        'person_id': 'nunique'
    }).reset_index()
    
    # Aplanar colunas
    metrics_by_bank.columns = [
        'banco',
        'soma_divida',
        'valor_medio',
        'valor_mediana',
        'valor_desvio_padrao',
        'qtd_boletos',
        'qtd_devedores_unicos'
    ]
    
    # Calcular ticket médio
    metrics_by_bank['ticket_medio'] = metrics_by_bank['soma_divida'] / metrics_by_bank['qtd_devedores_unicos']
    metrics_by_bank['ticket_medio'] = metrics_by_bank['ticket_medio'].fillna(0.0)
    
    # Preencher NaN em outras colunas
    metrics_by_bank['valor_medio'] = metrics_by_bank['valor_medio'].fillna(0.0)
    metrics_by_bank['valor_mediana'] = metrics_by_bank['valor_mediana'].fillna(0.0)
    metrics_by_bank['valor_desvio_padrao'] = metrics_by_bank['valor_desvio_padrao'].fillna(0.0)
    
    # Calcular percentis por banco
    percentis_by_bank = []
    for banco in metrics_by_bank['banco'].unique():
        banco_data = df_open[df_open['banco'] == banco]
        valores = banco_data[banco_data['valor_valido']]['valor_float']
        if len(valores) > 0:
            percentis_by_bank.append({
                'banco': banco,
                'valor_p90': valores.quantile(0.90),
                'valor_p95': valores.quantile(0.95)
            })
        else:
            percentis_by_bank.append({
                'banco': banco,
                'valor_p90': 0.0,
                'valor_p95': 0.0
            })
    
    percentis_df = pd.DataFrame(percentis_by_bank)
    metrics_by_bank = metrics_by_bank.merge(percentis_df, on='banco', how='left')
    
    # Preencher NaN nos percentis
    metrics_by_bank['valor_p90'] = metrics_by_bank['valor_p90'].fillna(0.0)
    metrics_by_bank['valor_p95'] = metrics_by_bank['valor_p95'].fillna(0.0)
    
    # Ordenar por soma da dívida (maior primeiro)
    metrics_by_bank = metrics_by_bank.sort_values('soma_divida', ascending=False)
    
    return metrics_by_bank


def get_max_min_boleto_open(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Encontra boleto OPEN com maior e menor valor.
    
    Args:
        df: DataFrame com dados limpos
        
    Returns:
        Dicionário com informações do maior e menor boleto
    """
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    df_open_valid = df_open[df_open['valor_valido']].copy()
    
    if len(df_open_valid) == 0:
        return {
            'boleto_open_max': None,
            'boleto_open_min': None,
        }
    
    idx_max = df_open_valid['valor_float'].idxmax()
    idx_min = df_open_valid['valor_float'].idxmin()
    
    row_max = df_open_valid.loc[idx_max]
    row_min = df_open_valid.loc[idx_min]
    
    return {
        'boleto_open_max': {
            'valor': float(row_max['valor_float']),
            'nome': row_max['nome_pagador'],
            'pena_agua': row_max['pena_agua'],
            'vencimento': row_max['data_vencimento_dt'],
            'banco': row_max['banco'],
            'numero_nosso': row_max['numero_nosso'],
        },
        'boleto_open_min': {
            'valor': float(row_min['valor_float']),
            'nome': row_min['nome_pagador'],
            'pena_agua': row_min['pena_agua'],
            'vencimento': row_min['data_vencimento_dt'],
            'banco': row_min['banco'],
            'numero_nosso': row_min['numero_nosso'],
        }
    }


def calculate_temporal_evolution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula evolução temporal mês a mês da inadimplência.
    
    Args:
        df: DataFrame com dados limpos
        
    Returns:
        DataFrame com métricas por mês
    """
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    
    if len(df_open) == 0:
        return pd.DataFrame()
    
    # Agrupar por mes_referencia
    temporal = df_open.groupby('mes_referencia').agg({
        'valor_float': ['sum', 'mean', 'count'],
        'person_id': 'nunique'
    }).reset_index()
    
    temporal.columns = [
        'mes_referencia',
        'soma_divida_open',
        'valor_medio_open',
        'qtd_boletos_open',
        'qtd_devedores_open_unicos'
    ]
    
    temporal = temporal.sort_values('mes_referencia')
    
    return temporal


def calculate_debt_change_month_over_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula mudanças de dívida mês a mês (piora/melhora).
    
    Args:
        df: DataFrame com dados limpos
        
    Returns:
        DataFrame com delta de dívida por pessoa entre meses consecutivos
    """
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    
    if len(df_open) == 0:
        return pd.DataFrame()
    
    # Dívida por pessoa por mês
    divida_por_mes = df_open.groupby(['person_id', 'mes_referencia'])['valor_float'].sum().reset_index()
    divida_por_mes.columns = ['person_id', 'mes_referencia', 'divida_mes']
    
    # Ordenar por pessoa e mês
    divida_por_mes = divida_por_mes.sort_values(['person_id', 'mes_referencia'])
    
    # Calcular delta mês a mês
    changes = []
    
    for person_id in divida_por_mes['person_id'].unique():
        person_data = divida_por_mes[divida_por_mes['person_id'] == person_id].sort_values('mes_referencia')
        
        if len(person_data) < 2:
            continue
        
        for i in range(1, len(person_data)):
            mes_anterior = person_data.iloc[i-1]
            mes_atual = person_data.iloc[i]
            
            divida_anterior = mes_anterior['divida_mes']
            divida_atual = mes_atual['divida_mes']
            delta = divida_atual - divida_anterior
            pct_delta = (delta / divida_anterior * 100) if divida_anterior > 0 else 0.0
            
            # Buscar informações da pessoa
            person_row = df_open[df_open['person_id'] == person_id].iloc[0]
            
            changes.append({
                'person_id': person_id,
                'pena_agua': person_row['pena_agua'],
                'nome': person_row['nome_pagador'],
                'mes_anterior': mes_anterior['mes_referencia'],
                'mes_atual': mes_atual['mes_referencia'],
                'divida_mes_anterior': divida_anterior,
                'divida_mes_atual': divida_atual,
                'delta': delta,
                'pct_delta': pct_delta,
            })
    
    if not changes:
        return pd.DataFrame()
    
    changes_df = pd.DataFrame(changes)
    
    return changes_df


def get_top_debtors_by_total_debt(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Ranking de devedores por dívida total.
    
    Args:
        df: DataFrame com dados limpos
        top_n: Número de top devedores
        
    Returns:
        DataFrame com ranking
    """
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    
    if len(df_open) == 0:
        return pd.DataFrame()
    
    ranking = df_open.groupby('person_id').agg({
        'valor_float': 'sum',
        'pena_agua': 'first',
        'nome_pagador': 'first',
        'status_norm': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None,
    }).reset_index()
    
    ranking.columns = ['person_id', 'divida_total', 'pena_agua', 'nome', 'status_mais_comum']
    ranking = ranking.sort_values('divida_total', ascending=False).head(top_n)
    ranking['rank'] = range(1, len(ranking) + 1)
    
    return ranking[['rank', 'person_id', 'pena_agua', 'nome', 'divida_total', 'status_mais_comum']]


def calculate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula métricas de qualidade dos dados.
    
    Args:
        df: DataFrame com dados limpos
        
    Returns:
        Dicionário com métricas de qualidade
    """
    total_linhas = len(df)
    
    # Linhas inválidas
    qtd_linhas_invalidas_valor = (~df['valor_valido']).sum()
    qtd_linhas_invalidas_data = (~df['data_valida']).sum()
    
    # Duplicidades suspeitas
    # Duplicado por (banco, numero_nosso)
    dup_nosso = df.groupby(['banco', 'numero_nosso']).size()
    dup_nosso_count = (dup_nosso > 1).sum()
    dup_nosso_examples = df[df.set_index(['banco', 'numero_nosso']).index.isin(
        dup_nosso[dup_nosso > 1].index
    )].head(10)[['banco', 'numero_nosso', 'nome_pagador', 'valor_float', 'data_vencimento_dt']].to_dict('records')
    
    # Duplicado por (banco, numero_seu, data_vencimento, valor)
    dup_seu = df.groupby(['banco', 'numero_seu', 'data_vencimento_dt', 'valor_float']).size()
    dup_seu_count = (dup_seu > 1).sum()
    dup_seu_examples = df[df.set_index(['banco', 'numero_seu', 'data_vencimento_dt', 'valor_float']).index.isin(
        dup_seu[dup_seu > 1].index
    )].head(10)[['banco', 'numero_seu', 'nome_pagador', 'valor_float', 'data_vencimento_dt']].to_dict('records')
    
    return {
        'total_linhas': int(total_linhas),
        'qtd_linhas_invalidas_valor': int(qtd_linhas_invalidas_valor),
        'qtd_linhas_invalidas_data': int(qtd_linhas_invalidas_data),
        'pct_linhas_invalidas_valor': float(qtd_linhas_invalidas_valor / total_linhas * 100) if total_linhas > 0 else 0.0,
        'pct_linhas_invalidas_data': float(qtd_linhas_invalidas_data / total_linhas * 100) if total_linhas > 0 else 0.0,
        'duplicidades_banco_numero_nosso': int(dup_nosso_count),
        'duplicidades_banco_numero_seu': int(dup_seu_count),
        'exemplos_dup_nosso': dup_nosso_examples,
        'exemplos_dup_seu': dup_seu_examples,
    }
