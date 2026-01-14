"""
Limpeza e conversão de dados: valores, datas, extração de pena_agua, etc.
"""

import re
import logging
from datetime import datetime
from typing import Tuple, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def parse_valor(valor_str: any) -> Tuple[float, bool]:
    """
    Converte string de valor para float.
    Aceita formatos: "1.161,41", "1161,41", "1161.41", "1161"
    
    Args:
        valor_str: Valor como string ou número
        
    Returns:
        Tupla (valor_float, sucesso)
    """
    if pd.isna(valor_str) or valor_str is None:
        return (0.0, False)
    
    if isinstance(valor_str, (int, float)):
        return (float(valor_str), True)
    
    if not isinstance(valor_str, str):
        return (0.0, False)
    
    # Remove espaços e caracteres não numéricos exceto ponto e vírgula
    valor_clean = valor_str.strip().replace(" ", "")
    
    if not valor_clean:
        return (0.0, False)
    
    try:
        # Padrão: pode ter ponto como separador de milhar e vírgula como decimal
        # ou vírgula como separador de milhar e ponto como decimal
        # ou apenas número sem separadores
        
        # Se tem vírgula, assume formato brasileiro (1.234,56)
        if ',' in valor_clean:
            # Remove pontos (separadores de milhar)
            valor_clean = valor_clean.replace('.', '')
            # Substitui vírgula por ponto
            valor_clean = valor_clean.replace(',', '.')
        # Se tem apenas ponto, pode ser decimal ou milhar
        elif '.' in valor_clean:
            # Se tem mais de um ponto, assume que é separador de milhar
            if valor_clean.count('.') > 1:
                # Remove pontos (separadores de milhar)
                valor_clean = valor_clean.replace('.', '')
            # Caso contrário, mantém o ponto como decimal
        
        valor_float = float(valor_clean)
        return (valor_float, True)
    
    except (ValueError, AttributeError) as e:
        logger.debug(f"Erro ao converter valor '{valor_str}': {e}")
        return (0.0, False)


def parse_data(data_str: any) -> Tuple[Optional[datetime], bool]:
    """
    Converte string de data para datetime.
    Aceita formatos: YYYY-MM-DD e DD/MM/YYYY
    
    Args:
        data_str: Data como string
        
    Returns:
        Tupla (datetime_object, sucesso)
    """
    if pd.isna(data_str) or data_str is None:
        return (None, False)
    
    if isinstance(data_str, datetime):
        return (data_str, True)
    
    if isinstance(data_str, pd.Timestamp):
        return (data_str.to_pydatetime(), True)
    
    if not isinstance(data_str, str):
        return (None, False)
    
    data_clean = data_str.strip()
    
    if not data_clean:
        return (None, False)
    
    # Tentar formato YYYY-MM-DD
    try:
        dt = datetime.strptime(data_clean, "%Y-%m-%d")
        return (dt, True)
    except ValueError:
        pass
    
    # Tentar formato DD/MM/YYYY
    try:
        dt = datetime.strptime(data_clean, "%d/%m/%Y")
        return (dt, True)
    except ValueError:
        pass
    
    # Tentar formato DD-MM-YYYY
    try:
        dt = datetime.strptime(data_clean, "%d-%m-%Y")
        return (dt, True)
    except ValueError:
        pass
    
    logger.debug(f"Formato de data não reconhecido: '{data_str}'")
    return (None, False)


def extract_pena_agua_from_name(nome_pagador: str) -> Tuple[Optional[str], str]:
    """
    Extrai pena_agua do início do nome_pagador usando regex.
    Padrão: r"^\s*(\d+)\s*(.*)$"
    
    Args:
        nome_pagador: Nome do pagador que pode começar com dígitos
        
    Returns:
        Tupla (pena_agua, nome_limpo)
    """
    if pd.isna(nome_pagador) or not isinstance(nome_pagador, str):
        return (None, "")
    
    nome_clean = nome_pagador.strip()
    
    # Regex para extrair dígitos no início
    match = re.match(r"^\s*(\d+)\s*(.*)$", nome_clean)
    
    if match:
        pena_agua = match.group(1)
        nome_limpo = match.group(2).strip()
        return (pena_agua, nome_limpo)
    
    return (None, nome_clean)


def derive_mes_referencia(data_vencimento: datetime) -> Optional[str]:
    """
    Deriva mes_referencia (YYYY-MM) a partir de data_vencimento.
    
    Args:
        data_vencimento: Data de vencimento
        
    Returns:
        String no formato YYYY-MM ou None
    """
    if pd.isna(data_vencimento) or data_vencimento is None:
        return None
    
    if isinstance(data_vencimento, datetime):
        return data_vencimento.strftime("%Y-%m")
    
    if isinstance(data_vencimento, pd.Timestamp):
        return data_vencimento.strftime("%Y-%m")
    
    return None


def remove_duplicates_by_pena_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicatas de pena_agua no mesmo mês.
    Se uma pena aparecer múltiplas vezes no mesmo mes_referencia,
    mantém apenas a primeira ocorrência (priorizando status OPEN e maior valor).
    
    Args:
        df: DataFrame com dados limpos
        
    Returns:
        DataFrame sem duplicatas de pena_agua por mês
    """
    df = df.copy()
    
    # Filtrar apenas linhas com pena_agua e mes_referencia válidos
    # (não vazios, não None, não 'nan', não 'None')
    pena_str = df['pena_agua'].astype(str).str.strip()
    mes_str = df['mes_referencia'].astype(str).str.strip()
    
    mask_valido = (
        df['pena_agua'].notna() & 
        (pena_str != '') &
        (pena_str.lower() != 'nan') &
        (pena_str.lower() != 'none') &
        df['mes_referencia'].notna() &
        (mes_str != '') &
        (mes_str.lower() != 'nan') &
        (mes_str.lower() != 'none')
    )
    
    df_validos = df[mask_valido].copy()
    df_invalidos = df[~mask_valido].copy()
    
    if len(df_validos) == 0:
        logger.info("Nenhuma linha válida com pena_agua e mes_referencia para deduplicação")
        return df
    
    # Contar duplicatas antes da remoção
    duplicatas = df_validos.duplicated(subset=['pena_agua', 'mes_referencia'], keep=False)
    qtd_duplicatas = duplicatas.sum()
    
    if qtd_duplicatas > 0:
        logger.info(f"Encontradas {qtd_duplicatas} linhas com duplicatas de pena_agua no mesmo mês")
        
        # Ordenar para garantir consistência: priorizar OPEN, depois por valor decrescente
        # Criar coluna temporária para ordenação
        if 'status_categoria' in df_validos.columns:
            df_validos['_priority'] = df_validos['status_categoria'].map({'OPEN': 1, 'PAID': 2, 'OTHER': 3}).fillna(4)
            sort_cols = ['pena_agua', 'mes_referencia', '_priority', 'valor_float']
            ascending = [True, True, True, False]
        else:
            df_validos['_priority'] = 4  # Sem status, menor prioridade
            sort_cols = ['pena_agua', 'mes_referencia', 'valor_float']
            ascending = [True, True, False]
        
        df_validos = df_validos.sort_values(sort_cols, ascending=ascending)
        
        # Contar quantas linhas serão mantidas após remoção
        qtd_antes = len(df_validos)
        
        # Remover duplicatas mantendo a primeira (que agora é a priorizada)
        df_validos = df_validos.drop_duplicates(subset=['pena_agua', 'mes_referencia'], keep='first')
        
        # Remover coluna temporária
        df_validos = df_validos.drop(columns=['_priority'])
        
        qtd_depois = len(df_validos)
        qtd_removidas = qtd_antes - qtd_depois
        logger.info(f"Removidas {qtd_removidas} linhas duplicadas de pena_agua no mesmo mês")
    else:
        logger.info("Nenhuma duplicata de pena_agua no mesmo mês encontrada")
    
    # Reconcatenar linhas válidas (já deduplicadas) com inválidas
    if len(df_invalidos) > 0:
        df_final = pd.concat([df_validos, df_invalidos], ignore_index=True)
    else:
        df_final = df_validos
    
    logger.info(f"Total de linhas após remoção de duplicatas: {len(df_final)} (antes: {len(df)})")
    
    return df_final


def clean_dataframe(df: pd.DataFrame, status_classifier) -> pd.DataFrame:
    """
    Limpa e normaliza um DataFrame de boletos.
    
    Args:
        df: DataFrame com dados brutos
        status_classifier: Instância de StatusClassifier
        
    Returns:
        DataFrame limpo com colunas adicionais
    """
    df = df.copy()
    
    # Converter valores
    logger.info("Convertendo valores...")
    valor_results = df['valor'].apply(parse_valor)
    df['valor_float'] = [v[0] for v in valor_results]
    df['valor_valido'] = [v[1] for v in valor_results]
    
    # Converter datas
    logger.info("Convertendo datas...")
    data_results = df['data_vencimento'].apply(parse_data)
    df['data_vencimento_dt'] = [d[0] for d in data_results]
    df['data_valida'] = [d[1] for d in data_results]
    
    # Extrair pena_agua se faltar
    logger.info("Extraindo pena_agua...")
    if 'pena_agua' not in df.columns or df['pena_agua'].isna().all():
        df['pena_agua'] = None
    
    # Preencher pena_agua faltante a partir do nome
    mask_pena_faltante = df['pena_agua'].isna() | (df['pena_agua'].astype(str).str.strip() == "")
    if mask_pena_faltante.any():
        for idx in df[mask_pena_faltante].index:
            nome = df.loc[idx, 'nome_pagador']
            pena, nome_limpo = extract_pena_agua_from_name(nome)
            if pena:
                df.loc[idx, 'pena_agua'] = pena
                df.loc[idx, 'nome_pagador'] = nome_limpo
    
    # Converter pena_agua para string
    df['pena_agua'] = df['pena_agua'].astype(str).str.strip()
    
    # Derivar mes_referencia se faltar
    logger.info("Derivando mes_referencia...")
    if 'mes_referencia' not in df.columns:
        df['mes_referencia'] = None
    
    mask_mes_faltante = df['mes_referencia'].isna() | (df['mes_referencia'].astype(str).str.strip() == "")
    if mask_mes_faltante.any():
        for idx in df[mask_mes_faltante].index:
            data = df.loc[idx, 'data_vencimento_dt']
            if data:
                mes_ref = derive_mes_referencia(data)
                if mes_ref:
                    df.loc[idx, 'mes_referencia'] = mes_ref
    
    # Normalizar mes_referencia para YYYY-MM
    df['mes_referencia'] = df['mes_referencia'].astype(str).str.strip()
    
    # Classificar status
    logger.info("Classificando status...")
    status_results = df['status'].apply(status_classifier.classify)
    df['status_norm'] = [s[0] for s in status_results]
    df['status_categoria'] = [s[1] for s in status_results]
    
    # Criar person_id
    logger.info("Criando person_id...")
    from boletos_report.utils import create_person_id
    df['person_id'] = df.apply(
        lambda row: create_person_id(row['pena_agua'], row['nome_pagador']),
        axis=1
    )
    
    # Normalizar outros campos
    if 'banco' in df.columns:
        df['banco'] = df['banco'].astype(str).str.strip().str.upper()
    
    if 'nome_pagador' in df.columns:
        from boletos_report.utils import normalize_name
        df['nome_pagador_norm'] = df['nome_pagador'].apply(
            lambda x: normalize_name(x, remove_accents_flag=True)
        )
    
    # Remover duplicatas de pena_agua no mesmo mês
    logger.info("Removendo duplicatas de pena_agua no mesmo mês...")
    df = remove_duplicates_by_pena_month(df)
    
    return df
