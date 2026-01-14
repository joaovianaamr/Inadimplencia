"""
Geração de gráficos para visualização de inadimplência.
"""

import os
import logging
from pathlib import Path
from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

logger = logging.getLogger(__name__)

# Configurar estilo
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def save_chart(fig, output_dir: str, filename: str):
    """
    Salva gráfico em arquivo PNG.
    
    Args:
        fig: Figura do matplotlib
        output_dir: Diretório de saída
        filename: Nome do arquivo
    """
    output_path = Path(output_dir) / "charts"
    output_path.mkdir(parents=True, exist_ok=True)
    
    filepath = output_path / filename
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"Gráfico salvo: {filepath}")


def plot_time_series_open_debt_total(temporal_df: pd.DataFrame, output_dir: str):
    """
    Gráfico de linha: dívida total em aberto por mês.
    
    Args:
        temporal_df: DataFrame com evolução temporal
        output_dir: Diretório de saída
    """
    if len(temporal_df) == 0:
        logger.warning("Sem dados para gráfico de dívida total")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(temporal_df['mes_referencia'], temporal_df['soma_divida_open'], 
            marker='o', linewidth=2, markersize=8, color='#d32f2f')
    ax.set_xlabel('Mês de Referência', fontsize=12)
    ax.set_ylabel('Dívida Total em Aberto (R$)', fontsize=12)
    ax.set_title('Evolução da Dívida Total em Aberto', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    
    # Formatar eixo Y como moeda
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    
    plt.tight_layout()
    save_chart(fig, output_dir, 'time_series_open_debt_total.png')


def plot_time_series_open_debtors_count(temporal_df: pd.DataFrame, output_dir: str):
    """
    Gráfico de linha: quantidade de devedores únicos em aberto por mês.
    
    Args:
        temporal_df: DataFrame com evolução temporal
        output_dir: Diretório de saída
    """
    if len(temporal_df) == 0:
        logger.warning("Sem dados para gráfico de devedores")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(temporal_df['mes_referencia'], temporal_df['qtd_devedores_open_unicos'], 
            marker='s', linewidth=2, markersize=8, color='#f57c00')
    ax.set_xlabel('Mês de Referência', fontsize=12)
    ax.set_ylabel('Quantidade de Devedores Únicos', fontsize=12)
    ax.set_title('Evolução da Quantidade de Devedores Únicos', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    save_chart(fig, output_dir, 'time_series_open_debtors_count.png')


def plot_time_series_open_bills_count(temporal_df: pd.DataFrame, output_dir: str):
    """
    Gráfico de linha: quantidade de boletos em aberto por mês.
    
    Args:
        temporal_df: DataFrame com evolução temporal
        output_dir: Diretório de saída
    """
    if len(temporal_df) == 0:
        logger.warning("Sem dados para gráfico de boletos")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(temporal_df['mes_referencia'], temporal_df['qtd_boletos_open'], 
            marker='^', linewidth=2, markersize=8, color='#7b1fa2')
    ax.set_xlabel('Mês de Referência', fontsize=12)
    ax.set_ylabel('Quantidade de Boletos em Aberto', fontsize=12)
    ax.set_title('Evolução da Quantidade de Boletos em Aberto', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    save_chart(fig, output_dir, 'time_series_open_bills_count.png')


def plot_time_series_open_mean_value(temporal_df: pd.DataFrame, output_dir: str):
    """
    Gráfico de linha: média do valor em aberto por mês.
    
    Args:
        temporal_df: DataFrame com evolução temporal
        output_dir: Diretório de saída
    """
    if len(temporal_df) == 0:
        logger.warning("Sem dados para gráfico de média")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(temporal_df['mes_referencia'], temporal_df['valor_medio_open'], 
            marker='d', linewidth=2, markersize=8, color='#388e3c')
    ax.set_xlabel('Mês de Referência', fontsize=12)
    ax.set_ylabel('Valor Médio em Aberto (R$)', fontsize=12)
    ax.set_title('Evolução do Valor Médio em Aberto', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    
    # Formatar eixo Y como moeda
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.2f}'))
    
    plt.tight_layout()
    save_chart(fig, output_dir, 'time_series_open_mean_value.png')


def plot_bar_top10_debtors_total(ranking_df: pd.DataFrame, output_dir: str):
    """
    Gráfico de barras: top 10 devedores por dívida total.
    
    Args:
        ranking_df: DataFrame com ranking
        output_dir: Diretório de saída
    """
    if len(ranking_df) == 0:
        logger.warning("Sem dados para gráfico de ranking")
        return
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Limitar nomes para exibição
    nomes_display = ranking_df['nome'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
    
    bars = ax.barh(range(len(ranking_df)), ranking_df['divida_total'], color='#d32f2f')
    ax.set_yticks(range(len(ranking_df)))
    ax.set_yticklabels([f"{row['pena_agua']} - {nome}" for _, row, nome in zip(ranking_df.index, ranking_df.itertuples(), nomes_display)], fontsize=9)
    ax.set_xlabel('Dívida Total (R$)', fontsize=12)
    ax.set_title('Top 10 Devedores por Dívida Total', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Formatar eixo X como moeda
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    
    # Inverter eixo Y para maior no topo
    ax.invert_yaxis()
    
    plt.tight_layout()
    save_chart(fig, output_dir, 'bar_top10_debtors_total.png')


def plot_bar_top10_debtors_recurrence(recurrence_df: pd.DataFrame, output_dir: str):
    """
    Gráfico de barras: top 10 reincidentes (por quantidade de boletos).
    
    Args:
        recurrence_df: DataFrame com ranking de reincidência
        output_dir: Diretório de saída
    """
    if len(recurrence_df) == 0:
        logger.warning("Sem dados para gráfico de reincidência")
        return
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Limitar nomes para exibição
    nomes_display = recurrence_df['nome'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
    
    bars = ax.barh(range(len(recurrence_df)), recurrence_df['qtd_boletos_open'], color='#f57c00')
    ax.set_yticks(range(len(recurrence_df)))
    ax.set_yticklabels([f"{row['pena_agua']} - {nome}" for _, row, nome in zip(recurrence_df.index, recurrence_df.itertuples(), nomes_display)], fontsize=9)
    ax.set_xlabel('Quantidade de Boletos em Aberto', fontsize=12)
    ax.set_title('Top 10 Devedores por Reincidência', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Inverter eixo Y para maior no topo
    ax.invert_yaxis()
    
    plt.tight_layout()
    save_chart(fig, output_dir, 'bar_top10_debtors_recurrence.png')


def plot_boxplot_open_values_by_month(df: pd.DataFrame, output_dir: str):
    """
    Boxplot: distribuição de valores em aberto por mês.
    
    Args:
        df: DataFrame com dados limpos
        output_dir: Diretório de saída
    """
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    df_open_valid = df_open[df_open['valor_valido']].copy()
    
    if len(df_open_valid) == 0:
        logger.warning("Sem dados para boxplot")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    meses_ordenados = sorted(df_open_valid['mes_referencia'].unique())
    data_by_month = [df_open_valid[df_open_valid['mes_referencia'] == mes]['valor_float'].values 
                     for mes in meses_ordenados]
    
    bp = ax.boxplot(data_by_month, labels=meses_ordenados, patch_artist=True)
    
    # Colorir boxes
    for patch in bp['boxes']:
        patch.set_facecolor('#e1bee7')
        patch.set_alpha(0.7)
    
    ax.set_xlabel('Mês de Referência', fontsize=12)
    ax.set_ylabel('Valor em Aberto (R$)', fontsize=12)
    ax.set_title('Distribuição de Valores em Aberto por Mês', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='x', rotation=45)
    
    # Formatar eixo Y como moeda
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    
    plt.tight_layout()
    save_chart(fig, output_dir, 'boxplot_open_values_by_month.png')


def plot_hist_open_values(df: pd.DataFrame, output_dir: str):
    """
    Histograma: distribuição de valores em aberto.
    
    Args:
        df: DataFrame com dados limpos
        output_dir: Diretório de saída
    """
    df_open = df[df['status_categoria'] == 'OPEN'].copy()
    df_open_valid = df_open[df_open['valor_valido']].copy()
    
    if len(df_open_valid) == 0:
        logger.warning("Sem dados para histograma")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.hist(df_open_valid['valor_float'], bins=50, color='#5c6bc0', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Valor em Aberto (R$)', fontsize=12)
    ax.set_ylabel('Frequência', fontsize=12)
    ax.set_title('Distribuição de Valores em Aberto', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Formatar eixo X como moeda
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
    
    plt.tight_layout()
    save_chart(fig, output_dir, 'hist_open_values.png')


def generate_all_charts(df: pd.DataFrame, temporal_df: pd.DataFrame, 
                       ranking_total: pd.DataFrame, ranking_recurrence: pd.DataFrame,
                       output_dir: str):
    """
    Gera todos os gráficos.
    
    Args:
        df: DataFrame com dados limpos
        temporal_df: DataFrame com evolução temporal
        ranking_total: DataFrame com ranking por dívida total
        ranking_recurrence: DataFrame com ranking por reincidência
        output_dir: Diretório de saída
    """
    logger.info("Gerando gráficos...")
    
    plot_time_series_open_debt_total(temporal_df, output_dir)
    plot_time_series_open_debtors_count(temporal_df, output_dir)
    plot_time_series_open_bills_count(temporal_df, output_dir)
    plot_time_series_open_mean_value(temporal_df, output_dir)
    plot_bar_top10_debtors_total(ranking_total, output_dir)
    plot_bar_top10_debtors_recurrence(ranking_recurrence, output_dir)
    plot_boxplot_open_values_by_month(df, output_dir)
    plot_hist_open_values(df, output_dir)
    
    logger.info("Todos os gráficos gerados com sucesso")
