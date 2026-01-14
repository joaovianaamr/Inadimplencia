"""
Testes para módulo de limpeza de dados.
"""

import pytest
from datetime import datetime
import pandas as pd
from boletos_report.cleaning import (
    parse_valor,
    parse_data,
    extract_pena_agua_from_name,
    derive_mes_referencia,
    remove_duplicates_by_pena_month
)


class TestParseValor:
    """Testes para parse_valor."""
    
    def test_parse_valor_brasileiro_com_ponto_e_virgula(self):
        """Testa formato brasileiro: 1.161,41"""
        valor, sucesso = parse_valor("1.161,41")
        assert sucesso is True
        assert abs(valor - 1161.41) < 0.01
    
    def test_parse_valor_sem_ponto_milhar(self):
        """Testa formato: 1161,41"""
        valor, sucesso = parse_valor("1161,41")
        assert sucesso is True
        assert abs(valor - 1161.41) < 0.01
    
    def test_parse_valor_ponto_decimal(self):
        """Testa formato: 1161.41"""
        valor, sucesso = parse_valor("1161.41")
        assert sucesso is True
        assert abs(valor - 1161.41) < 0.01
    
    def test_parse_valor_inteiro(self):
        """Testa valor inteiro."""
        valor, sucesso = parse_valor("1000")
        assert sucesso is True
        assert abs(valor - 1000.0) < 0.01
    
    def test_parse_valor_float(self):
        """Testa valor já como float."""
        valor, sucesso = parse_valor(1161.41)
        assert sucesso is True
        assert abs(valor - 1161.41) < 0.01
    
    def test_parse_valor_invalido(self):
        """Testa valor inválido."""
        valor, sucesso = parse_valor("abc")
        assert sucesso is False
        assert valor == 0.0
    
    def test_parse_valor_none(self):
        """Testa valor None."""
        valor, sucesso = parse_valor(None)
        assert sucesso is False
        assert valor == 0.0


class TestParseData:
    """Testes para parse_data."""
    
    def test_parse_data_iso_format(self):
        """Testa formato ISO: YYYY-MM-DD"""
        data, sucesso = parse_data("2025-10-15")
        assert sucesso is True
        assert isinstance(data, datetime)
        assert data.year == 2025
        assert data.month == 10
        assert data.day == 15
    
    def test_parse_data_brasileiro_format(self):
        """Testa formato brasileiro: DD/MM/YYYY"""
        data, sucesso = parse_data("15/10/2025")
        assert sucesso is True
        assert isinstance(data, datetime)
        assert data.year == 2025
        assert data.month == 10
        assert data.day == 15
    
    def test_parse_data_brasileiro_com_hifen(self):
        """Testa formato: DD-MM-YYYY"""
        data, sucesso = parse_data("15-10-2025")
        assert sucesso is True
        assert isinstance(data, datetime)
    
    def test_parse_data_datetime_object(self):
        """Testa datetime já como objeto."""
        dt = datetime(2025, 10, 15)
        data, sucesso = parse_data(dt)
        assert sucesso is True
        assert data == dt
    
    def test_parse_data_invalido(self):
        """Testa data inválida."""
        data, sucesso = parse_data("invalid")
        assert sucesso is False
        assert data is None
    
    def test_parse_data_none(self):
        """Testa data None."""
        data, sucesso = parse_data(None)
        assert sucesso is False
        assert data is None


class TestExtractPenaAgua:
    """Testes para extração de pena_agua."""
    
    def test_extract_pena_agua_com_digitos(self):
        """Testa extração quando nome começa com dígitos."""
        pena, nome = extract_pena_agua_from_name("436MELQUESEDEQUE ANTONIO CAXEADO")
        assert pena == "436"
        assert nome == "MELQUESEDEQUE ANTONIO CAXEADO"
    
    def test_extract_pena_agua_com_espacos(self):
        """Testa extração com espaços."""
        pena, nome = extract_pena_agua_from_name("  123  NOME COMPLETO")
        assert pena == "123"
        assert nome == "NOME COMPLETO"
    
    def test_extract_pena_agua_sem_digitos(self):
        """Testa quando não há dígitos no início."""
        pena, nome = extract_pena_agua_from_name("NOME SEM DIGITOS")
        assert pena is None
        assert nome == "NOME SEM DIGITOS"
    
    def test_extract_pena_agua_vazio(self):
        """Testa string vazia."""
        pena, nome = extract_pena_agua_from_name("")
        assert pena is None
        assert nome == ""


class TestDeriveMesReferencia:
    """Testes para derive_mes_referencia."""
    
    def test_derive_mes_referencia_datetime(self):
        """Testa derivação a partir de datetime."""
        dt = datetime(2025, 10, 15)
        mes = derive_mes_referencia(dt)
        assert mes == "2025-10"
    
    def test_derive_mes_referencia_timestamp(self):
        """Testa derivação a partir de pd.Timestamp."""
        ts = pd.Timestamp("2025-10-15")
        mes = derive_mes_referencia(ts)
        assert mes == "2025-10"
    
    def test_derive_mes_referencia_none(self):
        """Testa com None."""
        mes = derive_mes_referencia(None)
        assert mes is None


class TestRemoveDuplicatesByPenaMonth:
    """Testes para remoção de duplicatas de pena_agua no mesmo mês."""
    
    def test_remove_duplicates_same_month(self):
        """Testa remoção de duplicatas no mesmo mês."""
        df = pd.DataFrame({
            'pena_agua': ['436', '436', '789', '123'],
            'mes_referencia': ['2025-10', '2025-10', '2025-10', '2025-11'],
            'valor_float': [100.0, 200.0, 300.0, 400.0],
            'status_categoria': ['OPEN', 'PAID', 'OPEN', 'OPEN']
        })
        
        result = remove_duplicates_by_pena_month(df)
        
        # Deve manter apenas uma ocorrência de pena 436 no mês 2025-10
        # Prioriza OPEN e maior valor, então deve manter a primeira (OPEN, 100.0)
        assert len(result) == 3
        assert len(result[result['pena_agua'] == '436']) == 1
        assert len(result[result['pena_agua'] == '789']) == 1
        assert len(result[result['pena_agua'] == '123']) == 1
    
    def test_remove_duplicates_different_months(self):
        """Testa que duplicatas em meses diferentes não são removidas."""
        df = pd.DataFrame({
            'pena_agua': ['436', '436', '436'],
            'mes_referencia': ['2025-10', '2025-11', '2025-12'],
            'valor_float': [100.0, 200.0, 300.0],
            'status_categoria': ['OPEN', 'OPEN', 'OPEN']
        })
        
        result = remove_duplicates_by_pena_month(df)
        
        # Deve manter todas as ocorrências pois são em meses diferentes
        assert len(result) == 3
        assert len(result[result['pena_agua'] == '436']) == 3
    
    def test_remove_duplicates_prioritize_open(self):
        """Testa que status OPEN é priorizado."""
        df = pd.DataFrame({
            'pena_agua': ['436', '436'],
            'mes_referencia': ['2025-10', '2025-10'],
            'valor_float': [100.0, 200.0],
            'status_categoria': ['PAID', 'OPEN']  # OPEN deve ser mantido
        })
        
        result = remove_duplicates_by_pena_month(df)
        
        # Deve manter apenas uma ocorrência, priorizando OPEN
        assert len(result) == 1
        assert result.iloc[0]['status_categoria'] == 'OPEN'
        assert result.iloc[0]['valor_float'] == 200.0
    
    def test_remove_duplicates_invalid_pena(self):
        """Testa que linhas com pena_agua inválida não são processadas."""
        df = pd.DataFrame({
            'pena_agua': ['436', '436', '', None, 'nan'],
            'mes_referencia': ['2025-10', '2025-10', '2025-10', '2025-10', '2025-10'],
            'valor_float': [100.0, 200.0, 300.0, 400.0, 500.0],
            'status_categoria': ['OPEN', 'OPEN', 'OPEN', 'OPEN', 'OPEN']
        })
        
        result = remove_duplicates_by_pena_month(df)
        
        # Deve remover duplicata válida (436) mas manter inválidas
        assert len(result) == 4  # 1 válida + 3 inválidas
        assert len(result[result['pena_agua'] == '436']) == 1
