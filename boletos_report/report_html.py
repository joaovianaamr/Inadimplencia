"""
Geração de relatório HTML com resumo executivo.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)


def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_number(value: float) -> str:
    """Formata número com separador de milhar."""
    return f"{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(value: float) -> str:
    """Formata percentual."""
    return f"{value:.2f}%"


def generate_html_report(
    metrics: Dict[str, Any],
    metrics_by_bank: pd.DataFrame,
    max_min_boleto: Dict[str, Any],
    temporal_df: pd.DataFrame,
    ranking_total: pd.DataFrame,
    ranking_recurrence: pd.DataFrame,
    debt_change: pd.DataFrame,
    data_quality: Dict[str, Any],
    status_classifier,
    df_clean: pd.DataFrame,
    output_dir: str,
    report_number: int
):
    """
    Gera relatório HTML completo.
    
    Args:
        metrics: Dicionário com métricas gerais
        metrics_by_bank: DataFrame com métricas por banco
        max_min_boleto: Dicionário com maior e menor boleto
        temporal_df: DataFrame com evolução temporal
        ranking_total: Ranking por dívida total
        ranking_recurrence: Ranking por reincidência
        debt_change: Mudanças mês a mês
        data_quality: Dicionário com métricas de qualidade
        status_classifier: Instância de StatusClassifier
        output_dir: Diretório de saída
    """
    logger.info("Gerando relatório HTML...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    html_content = []
    
    # Cabeçalho
    html_content.append("""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Inadimplência</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #d32f2f;
            border-bottom: 3px solid #d32f2f;
            padding-bottom: 10px;
        }
        h2 {
            color: #1976d2;
            margin-top: 30px;
            border-left: 4px solid #1976d2;
            padding-left: 15px;
        }
        h3 {
            color: #555;
            margin-top: 20px;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .kpi-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        .kpi-card.warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .kpi-card.success {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .kpi-card.danger {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        }
        .kpi-label {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        th {
            background-color: #1976d2;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge-danger {
            background-color: #d32f2f;
            color: white;
        }
        .badge-warning {
            background-color: #f57c00;
            color: white;
        }
        .badge-success {
            background-color: #388e3c;
            color: white;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #777;
            font-size: 12px;
        }
        .interactive-panel {
            background-color: #f8f9fa;
            border: 2px solid #1976d2;
            border-radius: 8px;
            padding: 20px;
            margin: 30px 0;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            align-items: center;
        }
        .search-box input {
            flex: 1;
            padding: 12px;
            border: 2px solid #1976d2;
            border-radius: 4px;
            font-size: 16px;
        }
        .search-box button {
            padding: 12px 24px;
            background-color: #1976d2;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        .search-box button:hover {
            background-color: #1565c0;
        }
        .removed-badge {
            background-color: #ff9800;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-left: 10px;
        }
        .debtor-row.removed {
            opacity: 0.5;
            text-decoration: line-through;
            background-color: #ffebee;
        }
        .remove-btn {
            background-color: #d32f2f;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .remove-btn:hover {
            background-color: #b71c1c;
        }
        .remove-btn:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        .kpi-value.dynamic {
            transition: all 0.3s ease;
        }
        .kpi-value.dynamic.updated {
            animation: pulse 0.5s;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        table#debtorsTable th {
            cursor: pointer;
            user-select: none;
            position: relative;
            padding-right: 25px;
        }
        table#debtorsTable th:hover {
            background-color: #e3f2fd;
        }
        table#debtorsTable th.sortable::after {
            content: ' ↕';
            position: absolute;
            right: 8px;
            opacity: 0.5;
            font-size: 12px;
            color: white;
        }
        table#debtorsTable th.sort-asc::after {
            content: ' ↑';
            opacity: 1;
            color: #ffeb3b;
            font-weight: bold;
        }
        table#debtorsTable th.sort-desc::after {
            content: ' ↓';
            opacity: 1;
            color: #ffeb3b;
            font-weight: bold;
        }
        table#debtorsTable td {
            white-space: nowrap;
        }
        table#debtorsTable td:nth-child(5) {
            text-align: right;
        }
        table#debtorsTable td:nth-child(6) {
            text-align: center;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Inadimplência</h1>
        <p><strong>Número do Relatório:</strong> relatorio_""" + str(report_number) + """</p>
        <p><strong>Data de geração:</strong> """ + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + """</p>
""")
    
    # Gráfico de Evolução da Dívida Total
    html_content.append("""
        <div style="background-color: white; border: 2px solid #1976d2; border-radius: 8px; padding: 25px; margin: 30px 0;">
            <h2 style="margin-top: 0; color: #1976d2; text-align: center;">📈 Evolução da Dívida Total ao Longo dos Meses</h2>
            <div style="position: relative; height: 400px; margin: 20px 0;">
                <canvas id="debtEvolutionChart"></canvas>
            </div>
            <div id="debtEvolutionValues" style="margin-top: 20px; text-align: center; font-size: 14px; color: #555;"></div>
        </div>
    """)
    
    # Painel Interativo de Baixa Manual
    html_content.append("""
        <div class="interactive-panel">
            <h2 style="margin-top: 0; color: #1976d2;">🔧 Baixa Manual de Inadimplência</h2>
            <p>Digite a pena de água para dar baixa manual (ex: pessoa já pagou mas ainda consta como em aberto).</p>
            <div class="search-box">
                <input type="text" id="penaInput" placeholder="Digite a pena de água (ex: 436)" />
                <button onclick="removerPena()">Dar Baixa</button>
                <button onclick="resetarBaixas()" style="background-color: #757575;">Resetar Todas</button>
            </div>
            <div id="removedPenas" style="margin-top: 10px;"></div>
        </div>
    """)
    
    # 1. KPIs Gerais (apenas OPEN)
    html_content.append("""
        <h2>1. Panorama Geral de Inadimplência</h2>
        <div class="kpi-grid">
""")
    
    html_content.append(f"""
            <div class="kpi-card warning">
                <div class="kpi-label">Total de Devedores Únicos</div>
                <div class="kpi-value dynamic" id="kpi-devedores">{format_number(metrics['total_devedores_unicos'])}</div>
            </div>
            <div class="kpi-card warning">
                <div class="kpi-label">Total de Boletos em Aberto</div>
                <div class="kpi-value dynamic" id="kpi-boletos">{format_number(metrics['total_boletos_em_aberto'])}</div>
            </div>
            <div class="kpi-card danger">
                <div class="kpi-label">Soma da Dívida em Aberto</div>
                <div class="kpi-value dynamic" id="kpi-divida">{format_currency(metrics['soma_divida_em_aberto'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Ticket Médio em Aberto</div>
                <div class="kpi-value dynamic" id="kpi-ticket">{format_currency(metrics['ticket_medio_em_aberto'])}</div>
            </div>
        </div>
""")
    
    # Estatísticas descritivas
    html_content.append("""
        <h3>Estatísticas Descritivas (Valores em Aberto)</h3>
        <table>
            <tr>
                <th>Métrica</th>
                <th>Valor</th>
            </tr>
""")
    
    html_content.append(f"""
            <tr><td>Média</td><td>{format_currency(metrics['valor_medio'])}</td></tr>
            <tr><td>Mediana</td><td>{format_currency(metrics['valor_mediana'])}</td></tr>
            <tr><td>Moda</td><td>{format_currency(metrics['valor_moda'])}</td></tr>
            <tr><td>Desvio Padrão</td><td>{format_currency(metrics['valor_desvio_padrao'])}</td></tr>
            <tr><td>Percentil 90</td><td>{format_currency(metrics['valor_p90'])}</td></tr>
            <tr><td>Percentil 95</td><td>{format_currency(metrics['valor_p95'])}</td></tr>
        </table>
""")
    
    # Maior e menor dívida individual
    html_content.append("""
        <h3>Maior e Menor Dívida Individual</h3>
        <table id="maxMinDebtTable">
            <tr>
                <th>Métrica</th>
                <th>Pena de Água</th>
                <th>Nome</th>
                <th>Valor</th>
            </tr>
""")
    
    if metrics['maior_divida_person_id']:
        html_content.append(f"""
            <tr id="maior-divida-row">
                <td><strong>Maior Dívida</strong></td>
                <td id="maior-divida-pena">{metrics['maior_divida_pena_agua']}</td>
                <td id="maior-divida-nome">{metrics['maior_divida_nome']}</td>
                <td id="maior-divida-valor">{format_currency(metrics['maior_divida_individual'])}</td>
            </tr>
""")
    
    if metrics['menor_divida_person_id']:
        html_content.append(f"""
            <tr id="menor-divida-row">
                <td><strong>Menor Dívida</strong></td>
                <td id="menor-divida-pena">{metrics['menor_divida_pena_agua']}</td>
                <td id="menor-divida-nome">{metrics['menor_divida_nome']}</td>
                <td id="menor-divida-valor">{format_currency(metrics['menor_divida_individual'])}</td>
            </tr>
""")
    
    html_content.append("</table>")
    
    # 2. Máximos e mínimos de boletos
    html_content.append("""
        <h2>2. Boletos com Maior e Menor Valor em Aberto</h2>
""")
    
    if max_min_boleto.get('boleto_open_max'):
        boleto_max = max_min_boleto['boleto_open_max']
        html_content.append(f"""
        <h3>Maior Boleto em Aberto</h3>
        <table>
            <tr><th>Campo</th><th>Valor</th></tr>
            <tr><td>Valor</td><td>{format_currency(boleto_max['valor'])}</td></tr>
            <tr><td>Nome</td><td>{boleto_max['nome']}</td></tr>
            <tr><td>Pena de Água</td><td>{boleto_max['pena_agua']}</td></tr>
            <tr><td>Vencimento</td><td>{boleto_max['vencimento'].strftime('%d/%m/%Y') if boleto_max['vencimento'] else 'N/A'}</td></tr>
            <tr><td>Banco</td><td>{boleto_max['banco']}</td></tr>
            <tr><td>Número Nosso</td><td>{boleto_max['numero_nosso']}</td></tr>
        </table>
""")
    
    if max_min_boleto.get('boleto_open_min'):
        boleto_min = max_min_boleto['boleto_open_min']
        html_content.append(f"""
        <h3>Menor Boleto em Aberto</h3>
        <table>
            <tr><th>Campo</th><th>Valor</th></tr>
            <tr><td>Valor</td><td>{format_currency(boleto_min['valor'])}</td></tr>
            <tr><td>Nome</td><td>{boleto_min['nome']}</td></tr>
            <tr><td>Pena de Água</td><td>{boleto_min['pena_agua']}</td></tr>
            <tr><td>Vencimento</td><td>{boleto_min['vencimento'].strftime('%d/%m/%Y') if boleto_min['vencimento'] else 'N/A'}</td></tr>
            <tr><td>Banco</td><td>{boleto_min['banco']}</td></tr>
            <tr><td>Número Nosso</td><td>{boleto_min['numero_nosso']}</td></tr>
        </table>
""")
    
    # 2.5. Análise por Banco
    html_content.append("""
        <h2>2.5. Análise de Inadimplência por Banco</h2>
""")
    
    if len(metrics_by_bank) > 0:
        html_content.append("""
        <h3>Métricas por Banco</h3>
        <table>
            <tr>
                <th>Banco</th>
                <th>Soma da Dívida</th>
                <th>Valor Médio</th>
                <th>Valor Mediana</th>
                <th>Desvio Padrão</th>
                <th>P90</th>
                <th>P95</th>
                <th>Qtd Boletos</th>
                <th>Qtd Devedores Únicos</th>
                <th>Ticket Médio</th>
            </tr>
""")
        for _, row in metrics_by_bank.iterrows():
            html_content.append(f"""
            <tr>
                <td><strong>{row['banco']}</strong></td>
                <td>{format_currency(row['soma_divida'])}</td>
                <td>{format_currency(row['valor_medio'])}</td>
                <td>{format_currency(row['valor_mediana'])}</td>
                <td>{format_currency(row['valor_desvio_padrao'])}</td>
                <td>{format_currency(row['valor_p90'])}</td>
                <td>{format_currency(row['valor_p95'])}</td>
                <td>{format_number(row['qtd_boletos'])}</td>
                <td>{format_number(row['qtd_devedores_unicos'])}</td>
                <td>{format_currency(row['ticket_medio'])}</td>
            </tr>
""")
        html_content.append("</table>")
        
        # Gráfico de barras por banco (soma da dívida)
        html_content.append("""
        <h3>Comparação de Dívida Total por Banco</h3>
        <p><em>Os valores estão ordenados do maior para o menor.</em></p>
        <table>
            <tr>
                <th>Banco</th>
                <th>Soma da Dívida</th>
                <th>% do Total</th>
            </tr>
""")
        total_geral = metrics_by_bank['soma_divida'].sum()
        for _, row in metrics_by_bank.iterrows():
            pct = (row['soma_divida'] / total_geral * 100) if total_geral > 0 else 0.0
            html_content.append(f"""
            <tr>
                <td><strong>{row['banco']}</strong></td>
                <td>{format_currency(row['soma_divida'])}</td>
                <td>{format_percent(pct)}</td>
            </tr>
""")
        html_content.append("</table>")
    else:
        html_content.append("<p>Nenhum dado disponível para análise por banco.</p>")
    
    # 3. Ranking de devedores
    html_content.append("""
        <h2>3. Ranking de Devedores</h2>
""")
    
    if len(ranking_total) > 0:
        html_content.append("""
        <h3>Top 10 por Dívida Total</h3>
        <table>
            <tr>
                <th>Rank</th>
                <th>Pena de Água</th>
                <th>Nome</th>
                <th>Dívida Total</th>
                <th>Status Mais Comum</th>
            </tr>
""")
        for _, row in ranking_total.iterrows():
            html_content.append(f"""
            <tr>
                <td>{int(row['rank'])}</td>
                <td>{row['pena_agua']}</td>
                <td>{row['nome'][:50]}{'...' if len(row['nome']) > 50 else ''}</td>
                <td>{format_currency(row['divida_total'])}</td>
                <td><span class="badge badge-danger">{row['status_mais_comum']}</span></td>
            </tr>
""")
        html_content.append("</table>")
    
    if len(ranking_recurrence) > 0:
        html_content.append("""
        <h3>Top 10 por Reincidência (Quantidade de Boletos)</h3>
        <table>
            <tr>
                <th>Rank</th>
                <th>Pena de Água</th>
                <th>Nome</th>
                <th>Qtd Boletos</th>
                <th>Meses Apareceu</th>
                <th>Dívida Total</th>
            </tr>
""")
        for _, row in ranking_recurrence.iterrows():
            html_content.append(f"""
            <tr>
                <td>{int(row['rank'])}</td>
                <td>{row['pena_agua']}</td>
                <td>{row['nome'][:50]}{'...' if len(row['nome']) > 50 else ''}</td>
                <td>{int(row['qtd_boletos_open'])}</td>
                <td>{int(row['meses_apareceu'])}</td>
                <td>{format_currency(row['soma_open'])}</td>
            </tr>
""")
        html_content.append("</table>")
    
    # 4. Evolução temporal
    html_content.append("""
        <h2>4. Evolução Temporal da Inadimplência</h2>
""")
    
    if len(temporal_df) > 0:
        html_content.append("""
        <table>
            <tr>
                <th>Mês</th>
                <th>Soma Dívida em Aberto</th>
                <th>Qtd Boletos em Aberto</th>
                <th>Qtd Devedores Únicos</th>
                <th>Valor Médio em Aberto</th>
            </tr>
""")
        for _, row in temporal_df.iterrows():
            html_content.append(f"""
            <tr>
                <td>{row['mes_referencia']}</td>
                <td>{format_currency(row['soma_divida_open'])}</td>
                <td>{format_number(row['qtd_boletos_open'])}</td>
                <td>{format_number(row['qtd_devedores_open_unicos'])}</td>
                <td>{format_currency(row['valor_medio_open'])}</td>
            </tr>
""")
        html_content.append("</table>")
    
    # 5. Pioras e melhoras
    html_content.append("""
        <h2>5. Pioras e Melhoras (Mudanças Mês a Mês)</h2>
""")
    
    if len(debt_change) > 0:
        top_pioras = debt_change.nlargest(10, 'delta')
        top_melhoras = debt_change.nsmallest(10, 'delta')
        
        html_content.append("""
        <h3>Top 10 Maiores Aumentos de Dívida</h3>
        <table>
            <tr>
                <th>Pena de Água</th>
                <th>Nome</th>
                <th>Mês Anterior</th>
                <th>Mês Atual</th>
                <th>Dívida Anterior</th>
                <th>Dívida Atual</th>
                <th>Delta</th>
                <th>% Delta</th>
            </tr>
""")
        for _, row in top_pioras.iterrows():
            html_content.append(f"""
            <tr>
                <td>{row['pena_agua']}</td>
                <td>{row['nome'][:40]}{'...' if len(row['nome']) > 40 else ''}</td>
                <td>{row['mes_anterior']}</td>
                <td>{row['mes_atual']}</td>
                <td>{format_currency(row['divida_mes_anterior'])}</td>
                <td>{format_currency(row['divida_mes_atual'])}</td>
                <td><span class="badge badge-danger">+{format_currency(row['delta'])}</span></td>
                <td>+{format_percent(row['pct_delta'])}</td>
            </tr>
""")
        html_content.append("</table>")
        
        html_content.append("""
        <h3>Top 10 Maiores Reduções de Dívida</h3>
        <table>
            <tr>
                <th>Pena de Água</th>
                <th>Nome</th>
                <th>Mês Anterior</th>
                <th>Mês Atual</th>
                <th>Dívida Anterior</th>
                <th>Dívida Atual</th>
                <th>Delta</th>
                <th>% Delta</th>
            </tr>
""")
        for _, row in top_melhoras.iterrows():
            html_content.append(f"""
            <tr>
                <td>{row['pena_agua']}</td>
                <td>{row['nome'][:40]}{'...' if len(row['nome']) > 40 else ''}</td>
                <td>{row['mes_anterior']}</td>
                <td>{row['mes_atual']}</td>
                <td>{format_currency(row['divida_mes_anterior'])}</td>
                <td>{format_currency(row['divida_mes_atual'])}</td>
                <td><span class="badge badge-success">{format_currency(row['delta'])}</span></td>
                <td>{format_percent(row['pct_delta'])}</td>
            </tr>
""")
        html_content.append("</table>")
    
    # 6. Qualidade de dados
    html_content.append("""
        <h2>6. Qualidade dos Dados</h2>
        <table>
            <tr>
                <th>Métrica</th>
                <th>Valor</th>
            </tr>
""")
    
    html_content.append(f"""
            <tr><td>Total de Linhas</td><td>{format_number(data_quality['total_linhas'])}</td></tr>
            <tr><td>Linhas com Valor Inválido</td><td>{format_number(data_quality['qtd_linhas_invalidas_valor'])} ({format_percent(data_quality['pct_linhas_invalidas_valor'])})</td></tr>
            <tr><td>Linhas com Data Inválida</td><td>{format_number(data_quality['qtd_linhas_invalidas_data'])} ({format_percent(data_quality['pct_linhas_invalidas_data'])})</td></tr>
            <tr><td>Duplicidades (Banco + Número Nosso)</td><td>{format_number(data_quality['duplicidades_banco_numero_nosso'])}</td></tr>
            <tr><td>Duplicidades (Banco + Número Seu)</td><td>{format_number(data_quality['duplicidades_banco_numero_seu'])}</td></tr>
        </table>
""")
    
    # Status desconhecidos
    unknown_statuses = status_classifier.get_unknown_statuses()
    if unknown_statuses:
        html_content.append("""
        <h3>Status Desconhecidos (Não Classificados)</h3>
        <p>Os seguintes status foram encontrados mas não foram classificados como PAGO ou EM ABERTO:</p>
        <ul>
""")
        for status in sorted(unknown_statuses):
            html_content.append(f"<li><code>{status}</code></li>")
        html_content.append("</ul>")
        html_content.append("<p><strong>Recomendação:</strong> Revise as regras de classificação usando --paid-status e --open-status.</p>")
    
    # 7. Lista Completa de Devedores em Aberto
    html_content.append("""
        <h2>7. Lista Completa de Devedores em Aberto</h2>
        <p><em>Lista completa ordenada por valor em aberto (maior para menor). Use para verificação se realmente estão em aberto.</em></p>
        <table id="debtorsTable">
            <thead>
            <tr>
                <th style="width: 50px;">Ação</th>
                <th class="sortable" data-sort="pena" data-type="number">Pena de Água</th>
                <th class="sortable" data-sort="nome" data-type="text">Nome</th>
                <th class="sortable" data-sort="banco" data-type="text">Banco</th>
                <th class="sortable sort-desc" data-sort="valor" data-type="number">Valor em Aberto</th>
                <th class="sortable" data-sort="qtd" data-type="number">Qtd Boletos</th>
                <th class="sortable" data-sort="mes" data-type="text">Meses</th>
            </tr>
            </thead>
            <tbody>
""")
    
    # Obter todos os devedores em aberto - uma linha por pena + mês
    df_open = df_clean[df_clean['status_categoria'] == 'OPEN'].copy()
    devedores_por_mes = pd.DataFrame()
    
    if len(df_open) > 0:
        # Agrupar por pena, nome, banco E mês para ter uma linha por mês
        devedores_por_mes = df_open.groupby(['pena_agua', 'nome_pagador', 'banco', 'mes_referencia']).agg({
            'valor_float': ['sum', 'count']
        }).reset_index()
        devedores_por_mes.columns = ['pena_agua', 'nome', 'banco', 'mes', 'valor_total', 'qtd_boletos']
        devedores_por_mes = devedores_por_mes.sort_values('valor_total', ascending=False)
        
        for _, row in devedores_por_mes.iterrows():
            # Criar ID único para esta combinação pena + mês
            unique_id = f"{row['pena_agua']}_{row['mes']}"
            html_content.append(f"""
            <tr class="debtor-row" data-pena="{row['pena_agua']}" data-mes="{row['mes']}" data-unique-id="{unique_id}" data-valor="{row['valor_total']}" data-qtd="{int(row['qtd_boletos'])}">
                <td>
                    <button class="remove-btn" onclick="removerPenaPorMes('{row['pena_agua']}', '{row['mes']}', event)" title="Dar baixa apenas deste mês">−</button>
                </td>
                <td data-value="{row['pena_agua']}"><strong>{row['pena_agua']}</strong></td>
                <td data-value="{repr(row['nome'])}">{row['nome']}</td>
                <td data-value="{repr(row['banco'])}">{row['banco']}</td>
                <td data-value="{row['valor_total']}">{format_currency(row['valor_total'])}</td>
                <td data-value="{int(row['qtd_boletos'])}">{int(row['qtd_boletos'])}</td>
                <td data-value="{repr(str(row['mes']))}">{row['mes']}</td>
            </tr>
""")
    else:
        html_content.append("<tr><td colspan='7'>Nenhum devedor em aberto encontrado.</td></tr>")
    
    html_content.append("</tbody></table>")
    
    # JavaScript para interatividade
    # Preparar dados temporais para o gráfico
    temporal_data_js = []
    if len(temporal_df) > 0:
        for _, row in temporal_df.iterrows():
            temporal_data_js.append(f"""            {{
                "mes": {repr(str(row['mes_referencia']))},
                "divida": {row['soma_divida_open']}
            }}""")
    
    html_content.append("""
    <script>
        // Dados temporais para o gráfico
        const temporalData = [
""")
    if temporal_data_js:
        html_content.append(',\n'.join(temporal_data_js))
    html_content.append("""
        ];
        
        // Dados originais
        const originalData = {
            devedores: """ + str(metrics['total_devedores_unicos']) + """,
            boletos: """ + str(metrics['total_boletos_em_aberto']) + """,
            divida: """ + str(metrics['soma_divida_em_aberto']) + """,
            ticket: """ + str(metrics['ticket_medio_em_aberto']) + """
        };
        
        // Dados dos devedores
        const devedoresData = {
""")
    
    # Adicionar dados dos devedores em formato JSON
    # Para busca por pena (remove todos os meses)
    devedores_agrupados = pd.DataFrame()
    if len(df_open) > 0:
        devedores_agrupados = df_open.groupby(['pena_agua', 'nome_pagador', 'banco']).agg({
            'valor_float': ['sum', 'count']
        }).reset_index()
        devedores_agrupados.columns = ['pena_agua', 'nome', 'banco', 'valor_total', 'qtd_boletos']
    
    if len(devedores_agrupados) > 0:
        devedores_json = []
        for _, row in devedores_agrupados.iterrows():
            devedores_json.append(f"""            "{row['pena_agua']}": {{
                "nome": {repr(row['nome'])},
                "banco": {repr(row['banco'])},
                "valor": {row['valor_total']},
                "qtd_boletos": {int(row['qtd_boletos'])}
            }}""")
        html_content.append(',\n'.join(devedores_json))
    
    html_content.append("""
        };
        
        // Dados dos devedores por mês (para remoção individual)
        const devedoresPorMesData = {
""")
    
    # Adicionar dados por pena + mês
    if len(devedores_por_mes) > 0:
        devedores_mes_json = []
        for _, row in devedores_por_mes.iterrows():
            unique_id = f"{row['pena_agua']}_{row['mes']}"
            devedores_mes_json.append(f"""            "{unique_id}": {{
                "pena": {repr(str(row['pena_agua']))},
                "nome": {repr(row['nome'])},
                "banco": {repr(row['banco'])},
                "mes": {repr(str(row['mes']))},
                "valor": {row['valor_total']},
                "qtd_boletos": {int(row['qtd_boletos'])}
            }}""")
        html_content.append(',\n'.join(devedores_mes_json))
    
    html_content.append("""
        };
        
        const removedPenas = new Set(); // Pena completa (todos os meses)
        const removedPenasPorMes = new Set(); // Pena + mês específico
        
        function formatCurrency(value) {
            return 'R$ ' + value.toFixed(2).replace('.', ',').replace(/\\B(?=(\\d{3})+(?!\\d))/g, '.');
        }
        
        function formatNumber(value) {
            return value.toLocaleString('pt-BR');
        }
        
        function updateMetrics() {
            let totalDevedores = originalData.devedores;
            let totalBoletos = originalData.boletos;
            let totalDivida = originalData.divida;
            
            // Remover penas completas (todos os meses)
            removedPenas.forEach(pena => {
                if (devedoresData[pena]) {
                    totalDevedores--;
                    totalBoletos -= devedoresData[pena].qtd_boletos;
                    totalDivida -= devedoresData[pena].valor;
                }
            });
            
            // Remover penas por mês específico (mas não se a pena completa já foi removida)
            removedPenasPorMes.forEach(uniqueId => {
                if (devedoresPorMesData[uniqueId]) {
                    const data = devedoresPorMesData[uniqueId];
                    // Só remove se a pena completa não foi removida
                    if (!removedPenas.has(data.pena)) {
                        totalBoletos -= data.qtd_boletos;
                        totalDivida -= data.valor;
                        // Verificar se ainda há outros meses para esta pena
                        let temOutrosMeses = false;
                        for (const [id, d] of Object.entries(devedoresPorMesData)) {
                            if (d.pena === data.pena && id !== uniqueId && !removedPenasPorMes.has(id) && !removedPenas.has(data.pena)) {
                                temOutrosMeses = true;
                                break;
                            }
                        }
                        // Se não há outros meses ativos para esta pena, reduzir contador de devedores
                        if (!temOutrosMeses) {
                            totalDevedores--;
                        }
                    }
                }
            });
            
            const ticketMedio = totalDevedores > 0 ? totalDivida / totalDevedores : 0;
            
            // Atualizar KPIs com animação
            const kpiDevedores = document.getElementById('kpi-devedores');
            const kpiBoletos = document.getElementById('kpi-boletos');
            const kpiDivida = document.getElementById('kpi-divida');
            const kpiTicket = document.getElementById('kpi-ticket');
            
            [kpiDevedores, kpiBoletos, kpiDivida, kpiTicket].forEach(el => {
                el.classList.add('updated');
                setTimeout(() => el.classList.remove('updated'), 500);
            });
            
            kpiDevedores.textContent = formatNumber(totalDevedores);
            kpiBoletos.textContent = formatNumber(totalBoletos);
            kpiDivida.textContent = formatCurrency(totalDivida);
            kpiTicket.textContent = formatCurrency(ticketMedio);
            
            // Atualizar maior e menor dívida
            updateMaxMinDebt();
        }
        
        function updateMaxMinDebt() {
            // Calcular valores atuais considerando remoções completas e por mês
            const valoresAtuais = {};
            
            // Inicializar com valores completos (não removidos)
            Object.entries(devedoresData).forEach(([pena, data]) => {
                if (!removedPenas.has(pena)) {
                    valoresAtuais[pena] = {
                        pena: pena,
                        nome: data.nome,
                        valor: data.valor
                    };
                }
            });
            
            // Subtrair valores removidos por mês
            removedPenasPorMes.forEach(uniqueId => {
                if (devedoresPorMesData[uniqueId]) {
                    const data = devedoresPorMesData[uniqueId];
                    if (!removedPenas.has(data.pena) && valoresAtuais[data.pena]) {
                        valoresAtuais[data.pena].valor -= data.valor;
                    }
                }
            });
            
            // Filtrar apenas os que ainda têm valor > 0
            const devedoresAtivos = Object.values(valoresAtuais)
                .filter(d => d.valor > 0);
            
            if (devedoresAtivos.length === 0) {
                // Se não há devedores ativos, limpar a tabela
                const maiorRow = document.getElementById('maior-divida-row');
                const menorRow = document.getElementById('menor-divida-row');
                if (maiorRow) maiorRow.style.display = 'none';
                if (menorRow) menorRow.style.display = 'none';
                return;
            }
            
            // Ordenar por valor
            devedoresAtivos.sort((a, b) => b.valor - a.valor);
            
            const maior = devedoresAtivos[0];
            const menor = devedoresAtivos[devedoresAtivos.length - 1];
            
            // Atualizar maior dívida
            const maiorPena = document.getElementById('maior-divida-pena');
            const maiorNome = document.getElementById('maior-divida-nome');
            const maiorValor = document.getElementById('maior-divida-valor');
            const maiorRow = document.getElementById('maior-divida-row');
            
            if (maiorPena && maiorNome && maiorValor && maiorRow) {
                maiorRow.style.display = '';
                maiorPena.textContent = maior.pena;
                maiorNome.textContent = maior.nome;
                maiorValor.textContent = formatCurrency(maior.valor);
                
                // Adicionar animação
                [maiorPena, maiorNome, maiorValor].forEach(el => {
                    el.style.transition = 'all 0.3s ease';
                    el.style.backgroundColor = '#fff3cd';
                    setTimeout(() => {
                        el.style.backgroundColor = '';
                    }, 500);
                });
            }
            
            // Atualizar menor dívida
            const menorPena = document.getElementById('menor-divida-pena');
            const menorNome = document.getElementById('menor-divida-nome');
            const menorValor = document.getElementById('menor-divida-valor');
            const menorRow = document.getElementById('menor-divida-row');
            
            if (menorPena && menorNome && menorValor && menorRow) {
                menorRow.style.display = '';
                menorPena.textContent = menor.pena;
                menorNome.textContent = menor.nome;
                menorValor.textContent = formatCurrency(menor.valor);
                
                // Adicionar animação
                [menorPena, menorNome, menorValor].forEach(el => {
                    el.style.transition = 'all 0.3s ease';
                    el.style.backgroundColor = '#fff3cd';
                    setTimeout(() => {
                        el.style.backgroundColor = '';
                    }, 500);
                });
            }
        }
        
        function removerPena(pena) {
            if (!pena) {
                const input = document.getElementById('penaInput');
                pena = input.value.trim();
                
                if (!pena) {
                    alert('Por favor, digite uma pena de água.');
                    return;
                }
            }
            
            if (!devedoresData[pena]) {
                alert('Pena de água não encontrada na lista de devedores em aberto.');
                const input = document.getElementById('penaInput');
                if (input) input.value = '';
                return;
            }
            
            if (removedPenas.has(pena)) {
                alert('Esta pena de água já foi removida.');
                const input = document.getElementById('penaInput');
                if (input) input.value = '';
                return;
            }
            
            removedPenas.add(pena);
            
            // Marcar linhas na tabela e desabilitar botão
            const rows = document.querySelectorAll(`tr[data-pena="${pena}"]`);
            rows.forEach(row => {
                row.classList.add('removed');
                const btn = row.querySelector('.remove-btn');
                if (btn) {
                    btn.disabled = true;
                    btn.style.opacity = '0.5';
                }
            });
            
            updateMetrics();
            updateRemovedList();
            
            const input = document.getElementById('penaInput');
            if (input) {
                input.value = '';
                input.focus();
            }
        }
        
        function removerPenaPorMes(pena, mes, event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // Salvar posição atual do scroll
            const scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
            
            const uniqueId = `${pena}_${mes}`;
            
            if (!devedoresPorMesData[uniqueId]) {
                alert('Registro não encontrado.');
                return false;
            }
            
            if (removedPenasPorMes.has(uniqueId)) {
                alert('Este mês já foi removido.');
                return false;
            }
            
            // Se a pena completa já foi removida, não pode remover por mês
            if (removedPenas.has(pena)) {
                alert('Esta pena já foi removida completamente.');
                return false;
            }
            
            removedPenasPorMes.add(uniqueId);
            
            // Marcar linha na tabela e desabilitar botão
            const row = document.querySelector(`tr[data-unique-id="${uniqueId}"]`);
            if (row) {
                row.classList.add('removed');
                const btn = row.querySelector('.remove-btn');
                if (btn) {
                    btn.disabled = true;
                    btn.style.opacity = '0.5';
                }
            }
            
            updateMetrics();
            updateRemovedList();
            
            // Restaurar posição do scroll
            setTimeout(() => {
                window.scrollTo(0, scrollPosition);
            }, 10);
            
            return false;
        }
        
        function resetarBaixas() {
            const totalBaixas = removedPenas.size + removedPenasPorMes.size;
            if (totalBaixas === 0) {
                alert('Nenhuma baixa para resetar.');
                return;
            }
            
            if (!confirm(`Deseja resetar todas as ${totalBaixas} baixa(s) manual(is)?`)) {
                return;
            }
            
            // Resetar penas completas
            removedPenas.forEach(pena => {
                const rows = document.querySelectorAll(`tr[data-pena="${pena}"]`);
                rows.forEach(row => {
                    row.classList.remove('removed');
                    const btn = row.querySelector('.remove-btn');
                    if (btn) {
                        btn.disabled = false;
                        btn.style.opacity = '1';
                    }
                });
            });
            
            // Resetar penas por mês
            removedPenasPorMes.forEach(uniqueId => {
                const row = document.querySelector(`tr[data-unique-id="${uniqueId}"]`);
                if (row) {
                    row.classList.remove('removed');
                    const btn = row.querySelector('.remove-btn');
                    if (btn) {
                        btn.disabled = false;
                        btn.style.opacity = '1';
                    }
                }
            });
            
            removedPenas.clear();
            removedPenasPorMes.clear();
            updateMetrics(); // Isso já chama updateMaxMinDebt()
            updateRemovedList();
        }
        
        function updateRemovedList() {
            const container = document.getElementById('removedPenas');
            
            if (removedPenas.size === 0 && removedPenasPorMes.size === 0) {
                container.innerHTML = '';
                return;
            }
            
            let html = '<p><strong>Penas removidas:</strong> ';
            const badges = [];
            
            // Adicionar penas completas
            removedPenas.forEach(pena => {
                const data = devedoresData[pena];
                badges.push(`<span class="removed-badge">${pena} (${data.nome.substring(0, 30)}${data.nome.length > 30 ? '...' : ''}) - TODOS OS MESES</span>`);
            });
            
            // Adicionar penas por mês
            removedPenasPorMes.forEach(uniqueId => {
                const data = devedoresPorMesData[uniqueId];
                badges.push(`<span class="removed-badge">${data.pena} (${data.nome.substring(0, 30)}${data.nome.length > 30 ? '...' : ''}) - ${data.mes}</span>`);
            });
            
            html += badges.join(' ') + '</p>';
            container.innerHTML = html;
        }
        
        // Permitir Enter no input
        document.getElementById('penaInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                removerPena();
            }
        });
        
        // Criar gráfico de evolução da dívida
        let debtChart = null;
        
        function initDebtChart() {
            const ctx = document.getElementById('debtEvolutionChart');
            if (!ctx || temporalData.length === 0) {
                return;
            }
            
            const meses = temporalData.map(d => d.mes);
            const valores = temporalData.map(d => d.divida);
            
            // Atualizar valores exibidos
            const valuesContainer = document.getElementById('debtEvolutionValues');
            if (valuesContainer) {
                let html = '<div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">';
                temporalData.forEach(d => {
                    html += `<div style="background-color: #f0f0f0; padding: 8px 15px; border-radius: 5px; border-left: 4px solid #1976d2;"><strong>${d.mes}:</strong> ${formatCurrency(d.divida)}</div>`;
                });
                html += '</div>';
                valuesContainer.innerHTML = html;
            }
            
            debtChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: meses,
                    datasets: [{
                        label: 'Dívida Total (R$)',
                        data: valores,
                        borderColor: '#d32f2f',
                        backgroundColor: 'rgba(211, 47, 47, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointBackgroundColor: '#d32f2f',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Evolução da Dívida Total por Mês',
                            font: {
                                size: 18,
                                weight: 'bold'
                            },
                            color: '#1976d2',
                            padding: 20
                        },
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                },
                                padding: 15
                            }
                        },
                        tooltip: {
                            enabled: true,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: {
                                size: 14,
                                weight: 'bold'
                            },
                            bodyFont: {
                                size: 13
                            },
                            padding: 12,
                            callbacks: {
                                label: function(context) {
                                    return 'Dívida: ' + formatCurrency(context.parsed.y);
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: 'Valor em R$',
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                },
                                color: '#555'
                            },
                            ticks: {
                                callback: function(value) {
                                    return formatCurrency(value);
                                },
                                font: {
                                    size: 12
                                }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Mês de Referência',
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                },
                                color: '#555'
                            },
                            ticks: {
                                font: {
                                    size: 12
                                }
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }
        
        // Inicializar gráfico quando a página carregar
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initDebtChart);
        } else {
            initDebtChart();
        }
        
        // Função de ordenação de tabela
        let currentSort = { column: 4, direction: 'desc' }; // Coluna 4 = Valor em Aberto (índice 0-based)
        
        function getCellValue(cell, sortType) {
            if (!cell) return sortType === 'number' ? 0 : '';
            
            const dataValue = cell.getAttribute('data-value');
            if (dataValue !== null) {
                if (sortType === 'number') {
                    return parseFloat(dataValue) || 0;
                } else {
                    return dataValue.trim().toLowerCase();
                }
            }
            
            // Fallback: parsear do texto
            if (sortType === 'number') {
                const text = cell.textContent.replace(/[^\\d,.-]/g, '').replace(',', '.');
                return parseFloat(text) || 0;
            } else {
                return cell.textContent.trim().toLowerCase();
            }
        }
        
        function sortTable(columnIndex, sortType) {
            const table = document.getElementById('debtorsTable');
            if (!table) return;
            
            const tbody = table.querySelector('tbody');
            if (!tbody) return;
            
            const rows = Array.from(tbody.querySelectorAll('tr.debtor-row'));
            const headers = table.querySelectorAll('thead th');
            const header = headers[columnIndex];
            
            if (!header || !header.classList.contains('sortable')) return;
            
            // Remover classes de ordenação de todos os cabeçalhos
            headers.forEach(th => {
                th.classList.remove('sort-asc', 'sort-desc');
            });
            
            // Determinar direção da ordenação: alterna entre asc e desc
            if (currentSort.column === columnIndex) {
                // Mesma coluna: alterna direção
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            } else {
                // Nova coluna: começa com asc
                currentSort.direction = 'asc';
            }
            currentSort.column = columnIndex;
            
            // Adicionar classe ao cabeçalho atual
            header.classList.add(currentSort.direction === 'asc' ? 'sort-asc' : 'sort-desc');
            
            // Ordenar linhas
            rows.sort((a, b) => {
                const aCell = a.cells[columnIndex];
                const bCell = b.cells[columnIndex];
                
                let aValue = getCellValue(aCell, sortType);
                let bValue = getCellValue(bCell, sortType);
                
                // Comparação principal
                let comparison = 0;
                if (aValue < bValue) {
                    comparison = -1;
                } else if (aValue > bValue) {
                    comparison = 1;
                }
                
                // Se valores são iguais e é Qtd Boletos (coluna 5) ou Meses (coluna 6), ordenar por Pena de Água (coluna 1)
                if (comparison === 0 && (columnIndex === 5 || columnIndex === 6)) {
                    const aPenaCell = a.cells[1];
                    const bPenaCell = b.cells[1];
                    const aPena = getCellValue(aPenaCell, 'number');
                    const bPena = getCellValue(bPenaCell, 'number');
                    
                    if (aPena < bPena) comparison = -1;
                    else if (aPena > bPena) comparison = 1;
                }
                
                // Aplicar direção da ordenação
                return currentSort.direction === 'asc' ? comparison : -comparison;
            });
            
            // Reordenar no DOM
            rows.forEach(row => tbody.appendChild(row));
        }
        
        // Adicionar event listeners aos cabeçalhos ordenáveis
        function initTableSorting() {
            const table = document.getElementById('debtorsTable');
            if (!table) return;
            
            const allHeaders = table.querySelectorAll('thead th');
            const sortableHeaders = table.querySelectorAll('thead th.sortable');
            
            sortableHeaders.forEach((header) => {
                // Encontrar o índice real da coluna (incluindo coluna Ação)
                let columnIndex = -1;
                for (let i = 0; i < allHeaders.length; i++) {
                    if (allHeaders[i] === header) {
                        columnIndex = i;
                        break;
                    }
                }
                
                if (columnIndex >= 0) {
                    header.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        const sortType = this.getAttribute('data-type') || 'text';
                        sortTable(columnIndex, sortType);
                    });
                }
            });
        }
        
        // Inicializar quando a página carregar
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initTableSorting);
        } else {
            initTableSorting();
        }
    </script>
    """)
    
    # Rodapé
    html_content.append("""
        <div class="footer">
            <p>Relatório gerado automaticamente pelo Sistema de Análise de Inadimplência</p>
            <p>Foco: Identificação e acompanhamento de devedores e inadimplência</p>
        </div>
    </div>
</body>
</html>
""")
    
    # Salvar arquivo
    output_file = output_path / f"relatorio_inadimplencia_{report_number}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
    
    logger.info(f"Relatório HTML gerado: {output_file}")
