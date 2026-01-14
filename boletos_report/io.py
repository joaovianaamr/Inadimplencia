"""
Leitura de arquivos CSV e preparação de dados.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def read_csv_file(file_path: str, encoding: str = "utf-8-sig") -> pd.DataFrame:
    """
    Lê um arquivo CSV e retorna DataFrame.
    
    Args:
        file_path: Caminho do arquivo CSV
        encoding: Encoding do arquivo (default: utf-8-sig)
        
    Returns:
        DataFrame com os dados
    """
    logger.info(f"Lendo arquivo: {file_path}")
    
    try:
        # Tentar ler com encoding especificado
        df = pd.read_csv(
            file_path,
            encoding=encoding,
            dtype=str,  # Ler tudo como string primeiro
            na_values=['', 'NULL', 'null', 'None', 'N/A', 'n/a'],
            keep_default_na=False
        )
        
        logger.info(f"Arquivo lido com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
        return df
    
    except UnicodeDecodeError:
        logger.warning(f"Erro de encoding com {encoding}, tentando latin-1...")
        try:
            df = pd.read_csv(
                file_path,
                encoding="latin-1",
                dtype=str,
                na_values=['', 'NULL', 'null', 'None', 'N/A', 'n/a'],
                keep_default_na=False
            )
            logger.info(f"Arquivo lido com latin-1: {len(df)} linhas")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {file_path}: {e}")
            raise
    
    except Exception as e:
        logger.error(f"Erro ao ler arquivo {file_path}: {e}")
        raise


def find_csv_files(input_path: str) -> List[str]:
    """
    Encontra todos os arquivos CSV em um diretório ou retorna o arquivo único.
    
    Args:
        input_path: Caminho para arquivo CSV ou diretório
        
    Returns:
        Lista de caminhos de arquivos CSV
    """
    path = Path(input_path)
    
    if path.is_file():
        if path.suffix.lower() == '.csv':
            return [str(path)]
        else:
            logger.warning(f"Arquivo {input_path} não é CSV, ignorando")
            return []
    
    if path.is_dir():
        csv_files = list(path.glob("*.csv"))
        csv_files.extend(path.glob("*.CSV"))
        csv_files = sorted([str(f) for f in csv_files])
        logger.info(f"Encontrados {len(csv_files)} arquivos CSV em {input_path}")
        return csv_files
    
    logger.error(f"Caminho não encontrado: {input_path}")
    return []


def load_all_csvs(input_path: str, encoding: str = "utf-8-sig") -> pd.DataFrame:
    """
    Carrega todos os CSVs de um diretório ou arquivo único e concatena.
    
    Args:
        input_path: Caminho para arquivo CSV ou diretório
        encoding: Encoding dos arquivos
        
    Returns:
        DataFrame concatenado com todos os dados
    """
    csv_files = find_csv_files(input_path)
    
    if not csv_files:
        raise ValueError(f"Nenhum arquivo CSV encontrado em: {input_path}")
    
    dataframes = []
    
    for csv_file in csv_files:
        try:
            df = read_csv_file(csv_file, encoding=encoding)
            # Adicionar coluna com origem do arquivo
            df['arquivo_origem'] = os.path.basename(csv_file)
            dataframes.append(df)
        except Exception as e:
            logger.error(f"Erro ao processar {csv_file}: {e}")
            continue
    
    if not dataframes:
        raise ValueError("Nenhum arquivo CSV foi carregado com sucesso")
    
    # Concatenar todos
    logger.info(f"Concatenando {len(dataframes)} DataFrames...")
    df_combined = pd.concat(dataframes, ignore_index=True)
    
    logger.info(f"Total de linhas após concatenação: {len(df_combined)}")
    
    return df_combined


def validate_required_columns(df: pd.DataFrame) -> List[str]:
    """
    Valida se as colunas obrigatórias estão presentes.
    
    Args:
        df: DataFrame a validar
        
    Returns:
        Lista de colunas faltantes (vazia se tudo ok)
    """
    required = [
        'banco',
        'nome_pagador',
        'status',
        'numero_seu',
        'numero_nosso',
        'data_vencimento',
        'dda',
        'valor'
    ]
    
    missing = [col for col in required if col not in df.columns]
    
    if missing:
        logger.warning(f"Colunas faltantes: {missing}")
        logger.info(f"Colunas disponíveis: {list(df.columns)}")
    
    return missing
