"""
Exportação de dados para CSV, XLSX e PDF.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def export_to_csv(df: pd.DataFrame, output_path: str):
    """
    Exporta DataFrame para CSV.
    
    Args:
        df: DataFrame a exportar
        output_path: Caminho do arquivo de saída
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logger.info(f"CSV exportado: {output_path}")


def export_to_xlsx(df: pd.DataFrame, output_path: str, sheet_name: str = "Sheet1"):
    """
    Exporta DataFrame para XLSX.
    
    Args:
        df: DataFrame a exportar
        output_path: Caminho do arquivo de saída
        sheet_name: Nome da planilha
    """
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Se arquivo já existe, adicionar nova planilha
        if output_file.exists():
            with pd.ExcelWriter(output_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"XLSX exportado: {output_path} (planilha: {sheet_name})")
    
    except ImportError:
        logger.error("openpyxl não está instalado. Instale com: pip install openpyxl")
        raise
    except Exception as e:
        logger.error(f"Erro ao exportar XLSX: {e}")
        raise


def export_all_summaries(
    df: pd.DataFrame,
    temporal_df: pd.DataFrame,
    ranking_total: pd.DataFrame,
    ranking_recurrence: pd.DataFrame,
    recurrence_detail: pd.DataFrame,
    debt_change: pd.DataFrame,
    data_quality: dict,
    output_dir: str,
    formats: List[str]
):
    """
    Exporta todos os resumos em CSV e/ou XLSX.
    
    Args:
        df: DataFrame com dados limpos
        temporal_df: DataFrame com evolução temporal
        ranking_total: Ranking por dívida total
        ranking_recurrence: Ranking por reincidência
        recurrence_detail: Detalhes de reincidência
        debt_change: Mudanças mês a mês
        data_quality: Dicionário com métricas de qualidade
        output_dir: Diretório de saída
        formats: Lista de formatos ('csv', 'xlsx')
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Resumo geral (apenas OPEN)
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    
    if 'csv' in formats:
        export_to_csv(df_open, str(output_path / 'open_summary_overall.csv'))
    
    if 'xlsx' in formats:
        export_to_xlsx(df_open, str(output_path / 'open_summary_overall.xlsx'), 'Geral')
    
    # Resumo por banco
    if len(df_open) > 0:
        by_bank = df_open.groupby('banco').agg({
            'valor_float': ['sum', 'mean', 'count'],
            'person_id': 'nunique'
        }).reset_index()
        by_bank.columns = ['banco', 'soma_divida', 'valor_medio', 'qtd_boletos', 'qtd_devedores']
        by_bank = by_bank.sort_values('soma_divida', ascending=False)
        
        if 'csv' in formats:
            export_to_csv(by_bank, str(output_path / 'open_summary_by_bank.csv'))
        if 'xlsx' in formats:
            export_to_xlsx(by_bank, str(output_path / 'open_summary_by_bank.xlsx'), 'Por Banco')
    
    # Resumo por mês
    if len(temporal_df) > 0:
        if 'csv' in formats:
            export_to_csv(temporal_df, str(output_path / 'open_summary_by_month.csv'))
        if 'xlsx' in formats:
            export_to_xlsx(temporal_df, str(output_path / 'open_summary_by_month.xlsx'), 'Por Mês')
    
    # Resumo por banco e mês
    if len(df_open) > 0:
        by_bank_month = df_open.groupby(['banco', 'mes_referencia']).agg({
            'valor_float': ['sum', 'mean', 'count'],
            'person_id': 'nunique'
        }).reset_index()
        by_bank_month.columns = ['banco', 'mes_referencia', 'soma_divida', 'valor_medio', 'qtd_boletos', 'qtd_devedores']
        by_bank_month = by_bank_month.sort_values(['banco', 'mes_referencia'])
        
        if 'csv' in formats:
            export_to_csv(by_bank_month, str(output_path / 'open_summary_by_bank_month.csv'))
        if 'xlsx' in formats:
            export_to_xlsx(by_bank_month, str(output_path / 'open_summary_by_bank_month.xlsx'), 'Por Banco e Mês')
    
    # Rankings
    if len(ranking_total) > 0:
        if 'csv' in formats:
            export_to_csv(ranking_total, str(output_path / 'debtors_ranking_by_total_debt.csv'))
        if 'xlsx' in formats:
            export_to_xlsx(ranking_total, str(output_path / 'debtors_ranking_by_total_debt.xlsx'), 'Ranking Dívida')
    
    if len(ranking_recurrence) > 0:
        if 'csv' in formats:
            export_to_csv(ranking_recurrence, str(output_path / 'debtors_ranking_by_recurrence.csv'))
        if 'xlsx' in formats:
            export_to_xlsx(ranking_recurrence, str(output_path / 'debtors_ranking_by_recurrence.xlsx'), 'Ranking Reincidência')
    
    # Detalhes de reincidência
    if len(recurrence_detail) > 0:
        if 'csv' in formats:
            export_to_csv(recurrence_detail, str(output_path / 'debtors_recurrence_detail.csv'))
        if 'xlsx' in formats:
            export_to_xlsx(recurrence_detail, str(output_path / 'debtors_recurrence_detail.xlsx'), 'Reincidência')
    
    # Mudanças mês a mês
    if len(debt_change) > 0:
        # Top 10 pioras
        top_pioras = debt_change.nlargest(10, 'delta')[['person_id', 'pena_agua', 'nome', 'mes_anterior', 'mes_atual', 
                                                         'divida_mes_anterior', 'divida_mes_atual', 'delta', 'pct_delta']]
        # Top 10 melhoras
        top_melhoras = debt_change.nsmallest(10, 'delta')[['person_id', 'pena_agua', 'nome', 'mes_anterior', 'mes_atual',
                                                            'divida_mes_anterior', 'divida_mes_atual', 'delta', 'pct_delta']]
        
        if 'csv' in formats:
            export_to_csv(debt_change, str(output_path / 'debt_change_month_over_month.csv'))
            export_to_csv(top_pioras, str(output_path / 'top10_pioras.csv'))
            export_to_csv(top_melhoras, str(output_path / 'top10_melhoras.csv'))
        if 'xlsx' in formats:
            export_to_xlsx(debt_change, str(output_path / 'debt_change_month_over_month.xlsx'), 'Mudanças')
            export_to_xlsx(top_pioras, str(output_path / 'top10_pioras.xlsx'), 'Top 10 Pioras')
            export_to_xlsx(top_melhoras, str(output_path / 'top10_melhoras.xlsx'), 'Top 10 Melhoras')
    
    # Relatório de qualidade
    quality_df = pd.DataFrame([{
        'metrica': k,
        'valor': v
    } for k, v in data_quality.items() if not isinstance(v, list)])
    
    if 'csv' in formats:
        export_to_csv(quality_df, str(output_path / 'data_quality_report.csv'))
    if 'xlsx' in formats:
        export_to_xlsx(quality_df, str(output_path / 'data_quality_report.xlsx'), 'Qualidade')
    
    logger.info("Todos os resumos exportados")
