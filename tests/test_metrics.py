"""
Testes para módulo de métricas.
"""

import pytest
import pandas as pd
from datetime import datetime
from boletos_report.metrics import (
    calculate_open_metrics,
    get_max_min_boleto_open,
    calculate_temporal_evolution
)
from boletos_report.status_rules import StatusClassifier


@pytest.fixture
def sample_df():
    """Cria DataFrame de exemplo para testes."""
    classifier = StatusClassifier()
    
    data = {
        'banco': ['BANCO1', 'BANCO1', 'BANCO2'],
        'nome_pagador': ['JOAO SILVA', 'MARIA SANTOS', 'PEDRO COSTA'],
        'status': ['VENCIDO', 'PAGO NO DIA', 'EM ABERTO'],
        'valor_float': [100.0, 200.0, 150.0],
        'valor_valido': [True, True, True],
        'data_vencimento_dt': [
            datetime(2025, 10, 15),
            datetime(2025, 10, 16),
            datetime(2025, 10, 17)
        ],
        'data_valida': [True, True, True],
        'pena_agua': ['123', '456', '789'],
        'mes_referencia': ['2025-10', '2025-10', '2025-10'],
        'status_norm': ['VENCIDO', 'PAGO NO DIA', 'EM ABERTO'],
        'status_categoria': ['OPEN', 'PAID', 'OPEN'],
        'person_id': ['123|JOAO SILVA', '456|MARIA SANTOS', '789|PEDRO COSTA'],
        'numero_nosso': ['N1', 'N2', 'N3'],
        'numero_seu': ['S1', 'S2', 'S3']
    }
    
    df = pd.DataFrame(data)
    return df


class TestCalculateOpenMetrics:
    """Testes para calculate_open_metrics."""
    
    def test_calculate_open_metrics_basic(self, sample_df):
        """Testa cálculo básico de métricas."""
        metrics = calculate_open_metrics(sample_df)
        
        assert metrics['total_devedores_unicos'] == 2  # JOAO e PEDRO
        assert metrics['total_boletos_em_aberto'] == 2
        assert metrics['soma_divida_em_aberto'] == 250.0  # 100 + 150
        assert metrics['ticket_medio_em_aberto'] == 125.0  # 250 / 2
    
    def test_calculate_open_metrics_empty(self):
        """Testa com DataFrame vazio."""
        df = pd.DataFrame()
        metrics = calculate_open_metrics(df)
        assert metrics['total_devedores_unicos'] == 0
        assert metrics['soma_divida_em_aberto'] == 0.0


class TestGetMaxMinBoletoOpen:
    """Testes para get_max_min_boleto_open."""
    
    def test_get_max_min_boleto_open(self, sample_df):
        """Testa obtenção de maior e menor boleto."""
        result = get_max_min_boleto_open(sample_df)
        
        assert result['boleto_open_max'] is not None
        assert result['boleto_open_min'] is not None
        assert result['boleto_open_max']['valor'] == 150.0  # PEDRO
        assert result['boleto_open_min']['valor'] == 100.0  # JOAO


class TestCalculateTemporalEvolution:
    """Testes para calculate_temporal_evolution."""
    
    def test_calculate_temporal_evolution(self, sample_df):
        """Testa evolução temporal."""
        temporal = calculate_temporal_evolution(sample_df)
        
        assert len(temporal) == 1
        assert temporal.iloc[0]['mes_referencia'] == '2025-10'
        assert temporal.iloc[0]['soma_divida_open'] == 250.0
        assert temporal.iloc[0]['qtd_boletos_open'] == 2
        assert temporal.iloc[0]['qtd_devedores_open_unicos'] == 2
