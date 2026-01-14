"""
Testes para módulo de reincidência.
"""

import pytest
import pandas as pd
from datetime import datetime
from boletos_report.recurrence import (
    calculate_recurrence,
    get_top_recurrent_debtors
)


@pytest.fixture
def sample_df_recurrence():
    """Cria DataFrame com dados de reincidência."""
    data = {
        'banco': ['BANCO1'] * 5,
        'nome_pagador': ['JOAO SILVA'] * 3 + ['MARIA SANTOS'] * 2,
        'status': ['VENCIDO'] * 5,
        'valor_float': [100.0, 150.0, 200.0, 300.0, 400.0],
        'valor_valido': [True] * 5,
        'data_vencimento_dt': [
            datetime(2025, 10, 15),
            datetime(2025, 11, 15),
            datetime(2025, 12, 15),
            datetime(2025, 10, 20),
            datetime(2025, 11, 20)
        ],
        'data_valida': [True] * 5,
        'pena_agua': ['123'] * 3 + ['456'] * 2,
        'mes_referencia': ['2025-10', '2025-11', '2025-12', '2025-10', '2025-11'],
        'status_norm': ['VENCIDO'] * 5,
        'status_categoria': ['OPEN'] * 5,
        'person_id': ['123|JOAO SILVA'] * 3 + ['456|MARIA SANTOS'] * 2,
        'numero_nosso': ['N1', 'N2', 'N3', 'N4', 'N5'],
        'numero_seu': ['S1', 'S2', 'S3', 'S4', 'S5']
    }
    
    return pd.DataFrame(data)


class TestCalculateRecurrence:
    """Testes para calculate_recurrence."""
    
    def test_calculate_recurrence(self, sample_df_recurrence):
        """Testa cálculo de reincidência."""
        recurrence = calculate_recurrence(sample_df_recurrence)
        
        assert len(recurrence) == 2
        
        # JOAO aparece em 3 meses
        joao = recurrence[recurrence['person_id'] == '123|JOAO SILVA'].iloc[0]
        assert joao['meses_apareceu'] == 3
        assert joao['qtd_boletos_open'] == 3
        assert joao['soma_open'] == 450.0  # 100 + 150 + 200
        
        # MARIA aparece em 2 meses
        maria = recurrence[recurrence['person_id'] == '456|MARIA SANTOS'].iloc[0]
        assert maria['meses_apareceu'] == 2
        assert maria['qtd_boletos_open'] == 2


class TestGetTopRecurrentDebtors:
    """Testes para get_top_recurrent_debtors."""
    
    def test_get_top_recurrent_debtors(self, sample_df_recurrence):
        """Testa ranking de reincidentes."""
        top = get_top_recurrent_debtors(sample_df_recurrence, top_n=2)
        
        assert len(top) == 2
        assert top.iloc[0]['person_id'] == '123|JOAO SILVA'  # Mais reincidente
        assert top.iloc[0]['qtd_boletos_open'] == 3
