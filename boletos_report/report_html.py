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
    max_min_boleto: Dict[str, Any],
    temporal_df: pd.DataFrame,
    ranking_total: pd.DataFrame,
    ranking_recurrence: pd.DataFrame,
    debt_change: pd.DataFrame,
    data_quality: Dict[str, Any],
    status_classifier,
    output_dir: str
):
    """
    Gera relatório HTML completo.
    
    Args:
        metrics: Dicionário com métricas gerais
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
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Relatório de Inadimplência</h1>
        <p><strong>Data de geração:</strong> """ + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + """</p>
""")
    
    # 1. KPIs Gerais (apenas OPEN)
    html_content.append("""
        <h2>1. Panorama Geral de Inadimplência</h2>
        <div class="kpi-grid">
""")
    
    html_content.append(f"""
            <div class="kpi-card warning">
                <div class="kpi-label">Total de Devedores Únicos</div>
                <div class="kpi-value">{format_number(metrics['total_devedores_unicos'])}</div>
            </div>
            <div class="kpi-card warning">
                <div class="kpi-label">Total de Boletos em Aberto</div>
                <div class="kpi-value">{format_number(metrics['total_boletos_em_aberto'])}</div>
            </div>
            <div class="kpi-card danger">
                <div class="kpi-label">Soma da Dívida em Aberto</div>
                <div class="kpi-value">{format_currency(metrics['soma_divida_em_aberto'])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Ticket Médio em Aberto</div>
                <div class="kpi-value">{format_currency(metrics['ticket_medio_em_aberto'])}</div>
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
        <table>
            <tr>
                <th>Métrica</th>
                <th>Pena de Água</th>
                <th>Nome</th>
                <th>Valor</th>
            </tr>
""")
    
    if metrics['maior_divida_person_id']:
        html_content.append(f"""
            <tr>
                <td><strong>Maior Dívida</strong></td>
                <td>{metrics['maior_divida_pena_agua']}</td>
                <td>{metrics['maior_divida_nome']}</td>
                <td>{format_currency(metrics['maior_divida_individual'])}</td>
            </tr>
""")
    
    if metrics['menor_divida_person_id']:
        html_content.append(f"""
            <tr>
                <td><strong>Menor Dívida</strong></td>
                <td>{metrics['menor_divida_pena_agua']}</td>
                <td>{metrics['menor_divida_nome']}</td>
                <td>{format_currency(metrics['menor_divida_individual'])}</td>
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
    output_file = output_path / "relatorio_inadimplencia.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
    
    logger.info(f"Relatório HTML gerado: {output_file}")
