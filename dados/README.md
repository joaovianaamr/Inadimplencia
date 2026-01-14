# Pasta de Dados

Esta pasta é destinada aos arquivos CSV de boletos que serão processados pelo sistema de análise de inadimplência.

## Como usar

1. **Coloque seus arquivos CSV aqui** - Você pode colocar um ou múltiplos arquivos CSV nesta pasta
2. **Execute o sistema** apontando para esta pasta:
   ```bash
   python -m boletos_report --input dados --output relatorios
   ```

## Formato esperado

Os arquivos CSV devem conter as seguintes colunas:

- `banco` - Nome do banco
- `mes_referencia` - Mês no formato YYYY-MM (ex: 2025-10) - opcional, será derivado se faltar
- `pena_agua` - Número da pena de água - opcional, será extraído do nome se faltar
- `nome_pagador` - Nome completo do pagador
- `status` - Status do boleto (ex: "PAGO NO DIA", "VENCIDO", "EM ABERTO")
- `numero_seu` - Número seu do boleto
- `numero_nosso` - Número nosso do boleto
- `data_vencimento` - Data no formato YYYY-MM-DD ou DD/MM/YYYY
- `dda` - "S" ou "N"
- `valor` - Valor do boleto (aceita formatos: "1.161,41", "1161,41", "1161.41")

## Exemplo

Veja o arquivo `exemplo_boletos.csv` na raiz do projeto como referência.
