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
    derive_mes_referencia
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
