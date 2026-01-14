# Sistema de Análise de Inadimplência

Sistema completo em Python para análise de inadimplência a partir de arquivos CSV de boletos. O objetivo é **identificar e acompanhar devedores**, reincidência, valores em aberto e risco, **não arrecadação**.

## 📋 Características

- ✅ Leitura de múltiplos arquivos CSV
- ✅ Classificação inteligente de status (pago vs em aberto)
- ✅ Cálculo de métricas de inadimplência
- ✅ Análise de reincidência de devedores
- ✅ Evolução temporal mês a mês
- ✅ Identificação de pioras e melhoras
- ✅ Relatórios HTML completos
- ✅ Exportação para CSV e XLSX
- ✅ Gráficos de visualização (PNG)
- ✅ Validação e relatório de qualidade de dados

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Passos

1. **Clone ou baixe o projeto:**
```bash
cd analiseDevedores
```

2. **Crie um ambiente virtual (recomendado):**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual:**

   **Windows:**
   ```bash
   venv\Scripts\activate
   ```

   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

4. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

## 📖 Uso

### Forma Básica

```bash
python -m boletos_report --input dados.csv --output relatorios
```

### Forma Avançada

```bash
python -m boletos_report \
    --input ./dados \
    --output ./relatorios \
    --format html,xlsx,csv \
    --top 20 \
    --paid-status "PAGO NO DIA,PAGO,LIQUIDADO,BAIXADO" \
    --open-status "A VENCER / VENCIDO,VENCIDO,EM ABERTO"
```

### Parâmetros

| Parâmetro | Descrição | Obrigatório | Padrão |
|-----------|-----------|-------------|--------|
| `--input` | Arquivo CSV único ou diretório com CSVs | ✅ Sim | - |
| `--output` | Diretório de saída | ✅ Sim | - |
| `--format` | Formatos: html,csv,xlsx,pdf | Não | html,csv |
| `--top` | Número de top devedores nos rankings | Não | 10 |
| `--encoding` | Encoding dos CSVs | Não | utf-8-sig |
| `--paid-status` | Status considerados PAGOS (vírgula) | Não | Padrão |
| `--open-status` | Status considerados EM ABERTO (vírgula) | Não | Padrão |
| `--verbose` | Modo verboso (DEBUG) | Não | - |

## 📁 Formato do CSV de Entrada

O CSV deve conter as seguintes colunas:

| Coluna | Tipo | Descrição | Obrigatória |
|--------|------|-----------|-------------|
| `banco` | string | Nome do banco | ✅ |
| `mes_referencia` | string | Mês no formato YYYY-MM (ex: 2025-10) | ⚠️ (derivado se faltar) |
| `pena_agua` | string | Número da pena de água | ⚠️ (extraído se faltar) |
| `nome_pagador` | string | Nome completo do pagador | ✅ |
| `status` | string | Status do boleto | ✅ |
| `numero_seu` | string | Número seu do boleto | ✅ |
| `numero_nosso` | string | Número nosso do boleto | ✅ |
| `data_vencimento` | string | Data no formato YYYY-MM-DD ou DD/MM/YYYY | ✅ |
| `dda` | string | "S" ou "N" | ✅ |
| `valor` | string/float | Valor do boleto | ✅ |

### Exemplo de CSV

```csv
banco,mes_referencia,pena_agua,nome_pagador,status,numero_seu,numero_nosso,data_vencimento,dda,valor
BANCO1,2025-10,436,MELQUESEDEQUE ANTONIO CAXEADO,A VENCER / VENCIDO,12345,67890,2025-10-15,N,1.161,41
BANCO2,2025-10,789,JOAO SILVA,PAGO NO DIA,23456,78901,2025-10-16,S,500.00
```

### Observações Importantes

- **pena_agua**: Se não estiver no CSV, será extraído do início do `nome_pagador` (ex: "436MELQUESEDEQUE..." → pena_agua="436")
- **mes_referencia**: Se não estiver no CSV, será derivado de `data_vencimento`
- **valor**: Aceita formatos brasileiros: "1.161,41", "1161,41", "1161.41"
- **data_vencimento**: Aceita YYYY-MM-DD ou DD/MM/YYYY

## 📊 Saídas Geradas

### 1. Relatório HTML (`relatorio_inadimplencia.html`)

Relatório executivo completo com:

- **Panorama Geral**: KPIs de inadimplência
- **Estatísticas Descritivas**: Média, mediana, percentis, etc.
- **Maior e Menor Dívida**: Individual e por boleto
- **Rankings**: Top devedores por dívida total e reincidência
- **Evolução Temporal**: Mês a mês
- **Pioras e Melhoras**: Mudanças de dívida
- **Qualidade de Dados**: Validações e duplicidades

### 2. Arquivos CSV/XLSX

- `open_summary_overall.csv` - Resumo geral (apenas boletos em aberto)
- `open_summary_by_bank.csv` - Resumo por banco
- `open_summary_by_month.csv` - Resumo por mês
- `open_summary_by_bank_month.csv` - Resumo por banco e mês
- `debtors_ranking_by_total_debt.csv` - Ranking por dívida total
- `debtors_ranking_by_recurrence.csv` - Ranking por reincidência
- `debtors_recurrence_detail.csv` - Detalhes de reincidência
- `debt_change_month_over_month.csv` - Mudanças mês a mês
- `top10_pioras.csv` - Top 10 maiores aumentos
- `top10_melhoras.csv` - Top 10 maiores reduções
- `data_quality_report.csv` - Relatório de qualidade

### 3. Gráficos PNG (`charts/`)

- `time_series_open_debt_total.png` - Evolução da dívida total
- `time_series_open_debtors_count.png` - Evolução de devedores únicos
- `time_series_open_bills_count.png` - Evolução de boletos em aberto
- `time_series_open_mean_value.png` - Evolução do valor médio
- `bar_top10_debtors_total.png` - Top 10 por dívida total
- `bar_top10_debtors_recurrence.png` - Top 10 reincidentes
- `boxplot_open_values_by_month.png` - Distribuição por mês
- `hist_open_values.png` - Histograma de valores

## 🔍 Classificação de Status

### Status Padrão Considerados PAGOS

- `PAGO NO DIA`
- `PAGO`
- `LIQUIDADO`
- `BAIXADO`
- `QUITADO`
- `PAGO EM DIA`

### Status Padrão Considerados EM ABERTO

- `A VENCER / VENCIDO`
- `VENCIDO`
- `EM ABERTO`
- `ABERTO`
- `A VENCER`
- `PENDENTE`

### Customização

Você pode customizar as listas usando `--paid-status` e `--open-status`:

```bash
python -m boletos_report \
    --input dados.csv \
    --output relatorios \
    --paid-status "PAGO NO DIA,QUITADO" \
    --open-status "VENCIDO,EM ABERTO"
```

**Importante**: Status não classificados aparecerão no relatório de qualidade para revisão.

## 🧪 Testes

Execute os testes unitários:

```bash
pytest tests/
```

Com cobertura:

```bash
pytest tests/ --cov=boletos_report --cov-report=html
```

## 📝 Estrutura do Projeto

```
analiseDevedores/
├── boletos_report/
│   ├── __init__.py
│   ├── cli.py              # Interface de linha de comando
│   ├── io.py               # Leitura de arquivos CSV
│   ├── cleaning.py         # Limpeza e conversão de dados
│   ├── status_rules.py     # Classificação de status
│   ├── metrics.py          # Cálculo de métricas
│   ├── recurrence.py       # Análise de reincidência
│   ├── charts.py           # Geração de gráficos
│   ├── report_html.py      # Geração de relatório HTML
│   ├── export.py           # Exportação CSV/XLSX
│   └── utils.py            # Utilitários gerais
├── tests/
│   ├── __init__.py
│   ├── test_cleaning.py
│   ├── test_status_rules.py
│   ├── test_metrics.py
│   └── test_recurrence.py
├── requirements.txt
└── README.md
```

## ⚠️ Regras de Negócio

### Definição de "Em Aberto / Devendo"

- **PAGO**: Apenas status claramente de pagamento (ex: "PAGO NO DIA", "LIQUIDADO")
- **DEVENDO**: Qualquer outro status (ex: "VENCIDO", "EM ABERTO", "A VENCER / VENCIDO")

### Identificação de Pessoa

- **person_id**: `{pena_agua}|{nome_normalizado}`
- Nome normalizado: trim, uppercase, remoção de acentos, redução de espaços

### Duplicidades

O sistema identifica duplicidades suspeitas por:
- `(banco, numero_nosso)` repetido
- `(banco, numero_seu, data_vencimento, valor)` repetido

**Não apaga automaticamente**: apenas marca e reporta no relatório de qualidade.

## 🐛 Solução de Problemas

### Erro de Encoding

Se houver erro ao ler CSVs, tente:

```bash
python -m boletos_report --input dados.csv --output relatorios --encoding latin-1
```

### Status Desconhecidos

Se aparecerem status desconhecidos no relatório:

1. Verifique o relatório HTML na seção "Qualidade dos Dados"
2. Adicione os status às listas usando `--paid-status` ou `--open-status`

### Dados Inválidos

O sistema não quebra com dados inválidos. Eles são:
- Registrados no relatório de qualidade
- Ignorados nos cálculos (mas contabilizados nas métricas de qualidade)

## 📄 Licença

Este projeto é de uso interno. Consulte a documentação da organização para mais detalhes.

## 🤝 Contribuindo

Para contribuir:

1. Crie uma branch para sua feature
2. Implemente testes
3. Execute `pytest` para garantir que tudo passa
4. Faça commit e push

## 📧 Suporte

Para dúvidas ou problemas, consulte a documentação ou entre em contato com a equipe de desenvolvimento.

---

**Lembrete**: Este sistema foca em **inadimplência e devedores**, não em arrecadação. A terminologia sempre reflete isso.
