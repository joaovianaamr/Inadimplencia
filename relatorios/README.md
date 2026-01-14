# Pasta de Relatórios

Esta pasta contém todos os relatórios gerados pelo sistema de análise de inadimplência.

## Conteúdo gerado

Quando você executar o sistema, os seguintes arquivos serão gerados aqui:

### Relatório Principal
- `relatorio_inadimplencia.html` - Relatório executivo completo em HTML

### Arquivos CSV/XLSX
- `open_summary_overall.csv` - Resumo geral (apenas boletos em aberto)
- `open_summary_by_bank.csv` - Resumo por banco
- `open_summary_by_month.csv` - Resumo por mês
- `open_summary_by_bank_month.csv` - Resumo por banco e mês
- `debtors_ranking_by_total_debt.csv` - Ranking por dívida total
- `debtors_ranking_by_recurrence.csv` - Ranking por reincidência
- `debtors_recurrence_detail.csv` - Detalhes de reincidência
- `debt_change_month_over_month.csv` - Mudanças mês a mês
- `top10_pioras.csv` - Top 10 maiores aumentos de dívida
- `top10_melhoras.csv` - Top 10 maiores reduções de dívida
- `data_quality_report.csv` - Relatório de qualidade dos dados

### Gráficos
- `charts/` - Pasta contendo todos os gráficos PNG gerados

## Como visualizar

1. **Relatório HTML**: Abra `relatorio_inadimplencia.html` em qualquer navegador
2. **CSVs**: Abra com Excel, LibreOffice ou qualquer editor de planilhas
3. **Gráficos**: Visualize os arquivos PNG na pasta `charts/`

## Limpeza

Os arquivos desta pasta são gerados automaticamente e podem ser deletados a qualquer momento. Execute o sistema novamente para regenerá-los.
