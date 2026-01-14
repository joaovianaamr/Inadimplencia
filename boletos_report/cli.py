"""
Interface de linha de comando (CLI) para o sistema de análise de inadimplência.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from boletos_report.io import load_all_csvs, validate_required_columns
from boletos_report.cleaning import clean_dataframe
from boletos_report.status_rules import StatusClassifier
from boletos_report.metrics import (
    calculate_open_metrics,
    calculate_open_metrics_by_bank,
    get_max_min_boleto_open,
    calculate_temporal_evolution,
    calculate_debt_change_month_over_month,
    get_top_debtors_by_total_debt,
    calculate_data_quality
)
from boletos_report.recurrence import (
    calculate_recurrence,
    get_top_recurrent_debtors,
    calculate_recurrence_by_month
)
from boletos_report.charts import generate_all_charts
from boletos_report.report_html import generate_html_report
from boletos_report.export import export_all_summaries

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description='Sistema de Análise de Inadimplência - Gera relatórios de devedores a partir de CSVs de boletos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python -m boletos_report --input dados.csv --output relatorios
  python -m boletos_report --input ./dados --output ./relatorios --format html,xlsx,csv --top 20
  python -m boletos_report --input dados/ --output relatorios/ --format html,csv --paid-status "PAGO NO DIA,PAGO"
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Caminho para arquivo CSV único ou diretório contendo CSVs'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Diretório de saída (será criado se não existir)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        default='html,csv',
        help='Formatos de saída separados por vírgula: html,csv,xlsx,pdf (default: html,csv)'
    )
    
    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='Número de top devedores nos rankings (default: 10)'
    )
    
    parser.add_argument(
        '--encoding',
        type=str,
        default='utf-8-sig',
        help='Encoding dos arquivos CSV (default: utf-8-sig)'
    )
    
    parser.add_argument(
        '--paid-status',
        type=str,
        default=None,
        help='Lista de status considerados como PAGOS, separados por vírgula (ex: "PAGO NO DIA,PAGO,LIQUIDADO")'
    )
    
    parser.add_argument(
        '--open-status',
        type=str,
        default=None,
        help='Lista de status considerados como EM ABERTO, separados por vírgula (ex: "VENCIDO,EM ABERTO")'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Modo verboso (DEBUG logging)'
    )
    
    return parser.parse_args()


def main():
    """Função principal."""
    args = parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 60)
    logger.info("Sistema de Análise de Inadimplência")
    logger.info("=" * 60)
    
    # Validar entrada
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Caminho de entrada não encontrado: {args.input}")
        sys.exit(1)
    
    # Criar diretório de saída com numeração sequencial
    base_output = Path(args.output)
    base_output.mkdir(parents=True, exist_ok=True)
    
    # Encontrar o próximo número disponível
    existing_reports = []
    for item in base_output.iterdir():
        if item.is_dir() and item.name.startswith("relatorio_"):
            # Tentar extrair o número do nome
            try:
                # Formato: relatorio_1, relatorio_2, etc.
                if item.name.startswith("relatorio_"):
                    num_str = item.name.replace("relatorio_", "")
                    # Verificar se é um número
                    if num_str.isdigit():
                        existing_reports.append(int(num_str))
            except (ValueError, AttributeError):
                continue
    
    # Encontrar o próximo número disponível
    if existing_reports:
        next_number = max(existing_reports) + 1
    else:
        next_number = 1
    
    # Criar pasta com número sequencial
    output_path = base_output / f"relatorio_{next_number}"
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Diretório de saída: {output_path}")
    logger.info(f"Relatório criado: relatorio_{next_number}")
    
    # Parse formatos
    formats = [f.strip().lower() for f in args.format.split(',')]
    valid_formats = {'html', 'csv', 'xlsx', 'pdf'}
    formats = [f for f in formats if f in valid_formats]
    
    if not formats:
        logger.warning("Nenhum formato válido especificado. Usando: html,csv")
        formats = ['html', 'csv']
    
    logger.info(f"Formatos de saída: {', '.join(formats)}")
    
    # Parse status lists
    paid_status_list = None
    if args.paid_status:
        paid_status_list = [s.strip() for s in args.paid_status.split(',')]
        logger.info(f"Status PAGOS customizados: {paid_status_list}")
    
    open_status_list = None
    if args.open_status:
        open_status_list = [s.strip() for s in args.open_status.split(',')]
        logger.info(f"Status EM ABERTO customizados: {open_status_list}")
    
    try:
        # 1. Carregar dados
        logger.info("=" * 60)
        logger.info("ETAPA 1: Carregando arquivos CSV...")
        logger.info("=" * 60)
        df = load_all_csvs(args.input, encoding=args.encoding)
        logger.info(f"Total de linhas carregadas: {len(df)}")
        
        # Validar colunas obrigatórias
        missing_cols = validate_required_columns(df)
        if missing_cols:
            logger.warning(f"Colunas faltantes: {missing_cols}")
            logger.warning("O processamento continuará, mas pode haver erros.")
        
        # 2. Classificador de status
        logger.info("=" * 60)
        logger.info("ETAPA 2: Inicializando classificador de status...")
        logger.info("=" * 60)
        status_classifier = StatusClassifier(
            paid_status_list=paid_status_list,
            open_status_list=open_status_list
        )
        
        # 3. Limpeza e normalização
        logger.info("=" * 60)
        logger.info("ETAPA 3: Limpando e normalizando dados...")
        logger.info("=" * 60)
        df_clean = clean_dataframe(df, status_classifier)
        logger.info(f"Total de linhas após limpeza: {len(df_clean)}")
        
        # Contar categorias
        if 'status_categoria' in df_clean.columns:
            status_counts = df_clean['status_categoria'].value_counts()
            logger.info("Distribuição de status:")
            for status, count in status_counts.items():
                logger.info(f"  {status}: {count}")
        
        # 4. Calcular métricas
        logger.info("=" * 60)
        logger.info("ETAPA 4: Calculando métricas de inadimplência...")
        logger.info("=" * 60)
        metrics = calculate_open_metrics(df_clean)
        metrics_by_bank = calculate_open_metrics_by_bank(df_clean)
        max_min_boleto = get_max_min_boleto_open(df_clean)
        temporal_df = calculate_temporal_evolution(df_clean)
        debt_change = calculate_debt_change_month_over_month(df_clean)
        ranking_total = get_top_debtors_by_total_debt(df_clean, top_n=args.top)
        data_quality = calculate_data_quality(df_clean)
        
        logger.info(f"Total de devedores únicos: {metrics['total_devedores_unicos']}")
        logger.info(f"Total de boletos em aberto: {metrics['total_boletos_em_aberto']}")
        logger.info(f"Soma da dívida em aberto: R$ {metrics['soma_divida_em_aberto']:,.2f}")
        
        # 5. Análise de reincidência
        logger.info("=" * 60)
        logger.info("ETAPA 5: Analisando reincidência...")
        logger.info("=" * 60)
        recurrence_detail = calculate_recurrence(df_clean)
        ranking_recurrence = get_top_recurrent_debtors(df_clean, top_n=args.top)
        recurrence_by_month = calculate_recurrence_by_month(df_clean)
        
        logger.info(f"Total de devedores reincidentes: {len(recurrence_detail)}")
        
        # 6. Gerar gráficos
        if 'html' in formats or 'pdf' in formats:
            logger.info("=" * 60)
            logger.info("ETAPA 6: Gerando gráficos...")
            logger.info("=" * 60)
            generate_all_charts(
                df_clean,
                temporal_df,
                ranking_total,
                ranking_recurrence,
                str(output_path)
            )
        
        # 7. Gerar relatório HTML
        if 'html' in formats:
            logger.info("=" * 60)
            logger.info("ETAPA 7: Gerando relatório HTML...")
            logger.info("=" * 60)
            generate_html_report(
                metrics,
                metrics_by_bank,
                max_min_boleto,
                temporal_df,
                ranking_total,
                ranking_recurrence,
                debt_change,
                data_quality,
                status_classifier,
                str(output_path)
            )
        
        # 8. Exportar resumos
        if 'csv' in formats or 'xlsx' in formats:
            logger.info("=" * 60)
            logger.info("ETAPA 8: Exportando resumos...")
            logger.info("=" * 60)
            export_all_summaries(
                df_clean,
                temporal_df,
                ranking_total,
                ranking_recurrence,
                recurrence_detail,
                debt_change,
                data_quality,
                str(output_path),
                formats
            )
        
        # 9. Resumo final
        logger.info("=" * 60)
        logger.info("PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        logger.info("=" * 60)
        logger.info(f"Relatórios gerados em: {output_path}")
        logger.info(f"  - HTML: {output_path / 'relatorio_inadimplencia.html'}")
        if 'csv' in formats or 'xlsx' in formats:
            logger.info(f"  - CSVs/XLSX: {output_path}")
        logger.info(f"  - Gráficos: {output_path / 'charts'}")
        
        # Avisos
        unknown_statuses = status_classifier.get_unknown_statuses()
        if unknown_statuses:
            logger.warning(f"Status desconhecidos encontrados: {len(unknown_statuses)}")
            logger.warning("Revise o relatório HTML para detalhes e ajuste as regras de classificação se necessário.")
        
        if data_quality['qtd_linhas_invalidas_valor'] > 0 or data_quality['qtd_linhas_invalidas_data'] > 0:
            logger.warning("Foram encontradas linhas com dados inválidos. Verifique o relatório de qualidade.")
    
    except Exception as e:
        logger.error(f"Erro durante processamento: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
