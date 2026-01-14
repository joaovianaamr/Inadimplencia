# Pasta de Relatórios

Esta pasta contém todos os relatórios gerados pelo sistema de análise de inadimplência, organizados em pastas por categoria.

## Estrutura Organizada

Os relatórios são organizados em pastas temáticas para facilitar a navegação:

### 📊 Relatório Principal
- `relatorio_inadimplencia.html` - Relatório executivo completo em HTML (na raiz)

### 📁 Pastas Organizadas

#### `resumo_geral/`
Resumo geral de todos os boletos em aberto:
- `open_summary_overall.csv`
- `open_summary_overall.xlsx`

#### `por_banco/`
Análises agrupadas por banco:
- `open_summary_by_bank.csv` - Resumo por banco
- `open_summary_by_bank.xlsx`
- `open_summary_by_bank_month.csv` - Resumo por banco e mês
- `open_summary_by_bank_month.xlsx`

#### `por_mes/`
Análises agrupadas por mês:
- `open_summary_by_month.csv` - Evolução temporal mês a mês
- `open_summary_by_month.xlsx`

#### `rankings/`
Rankings de devedores:
- `debtors_ranking_by_total_debt.csv` - Ranking por dívida total
- `debtors_ranking_by_total_debt.xlsx`
- `debtors_ranking_by_recurrence.csv` - Ranking por reincidência
- `debtors_ranking_by_recurrence.xlsx`

#### `reincidencia/`
Análise detalhada de reincidência:
- `debtors_recurrence_detail.csv` - Detalhes completos de reincidência
- `debtors_recurrence_detail.xlsx`

#### `mudancas/`
Análise de mudanças mês a mês:
- `debt_change_month_over_month.csv` - Todas as mudanças
- `debt_change_month_over_month.xlsx`
- `top10_pioras.csv` - Top 10 maiores aumentos de dívida
- `top10_pioras.xlsx`
- `top10_melhoras.csv` - Top 10 maiores reduções de dívida
- `top10_melhoras.xlsx`

#### `qualidade/`
Relatório de qualidade dos dados:
- `data_quality_report.csv` - Validações e duplicidades
- `data_quality_report.xlsx`

#### `charts/`
Gráficos de visualização (PNG):
- `time_series_open_debt_total.png` - Evolução da dívida total
- `time_series_open_debtors_count.png` - Evolução de devedores únicos
- `time_series_open_bills_count.png` - Evolução de boletos em aberto
- `time_series_open_mean_value.png` - Evolução do valor médio
- `bar_top10_debtors_total.png` - Top 10 por dívida total
- `bar_top10_debtors_recurrence.png` - Top 10 reincidentes
- `boxplot_open_values_by_month.png` - Distribuição por mês
- `hist_open_values.png` - Histograma de valores

## Como visualizar

1. **Relatório HTML**: Abra `relatorio_inadimplencia.html` em qualquer navegador
2. **CSVs/XLSX**: Navegue pelas pastas organizadas e abra os arquivos com Excel, LibreOffice ou qualquer editor de planilhas
3. **Gráficos**: Visualize os arquivos PNG na pasta `charts/`

## Limpeza

Os arquivos desta pasta são gerados automaticamente e podem ser deletados a qualquer momento. Execute o sistema novamente para regenerá-los na mesma estrutura organizada.
