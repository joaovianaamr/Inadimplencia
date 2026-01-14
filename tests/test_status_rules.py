"""
Testes para módulo de classificação de status.
"""

import pytest
from boletos_report.status_rules import StatusClassifier


class TestStatusClassifier:
    """Testes para StatusClassifier."""
    
    def test_normalize_status(self):
        """Testa normalização de status."""
        classifier = StatusClassifier()
        assert classifier.normalize_status("  pago no dia  ") == "PAGO NO DIA"
        assert classifier.normalize_status("vencido") == "VENCIDO"
        assert classifier.normalize_status("a   vencido") == "A VENCIDO"
    
    def test_is_paid_default(self):
        """Testa classificação de pagos com defaults."""
        classifier = StatusClassifier()
        assert classifier.is_paid("PAGO NO DIA") is True
        assert classifier.is_paid("PAGO") is True
        assert classifier.is_paid("LIQUIDADO") is True
        assert classifier.is_paid("VENCIDO") is False
    
    def test_is_open_default(self):
        """Testa classificação de em aberto com defaults."""
        classifier = StatusClassifier()
        assert classifier.is_open("VENCIDO") is True
        assert classifier.is_open("EM ABERTO") is True
        assert classifier.is_open("A VENCER / VENCIDO") is True
        assert classifier.is_open("PAGO NO DIA") is False
    
    def test_classify_paid(self):
        """Testa classificação como PAID."""
        classifier = StatusClassifier()
        status_norm, categoria = classifier.classify("PAGO NO DIA")
        assert categoria == "PAID"
        assert status_norm == "PAGO NO DIA"
    
    def test_classify_open(self):
        """Testa classificação como OPEN."""
        classifier = StatusClassifier()
        status_norm, categoria = classifier.classify("VENCIDO")
        assert categoria == "OPEN"
        assert status_norm == "VENCIDO"
    
    def test_classify_unknown(self):
        """Testa classificação como UNKNOWN."""
        classifier = StatusClassifier()
        status_norm, categoria = classifier.classify("STATUS DESCONHECIDO")
        assert categoria == "UNKNOWN"
        assert status_norm == "STATUS DESCONHECIDO"
        assert "STATUS DESCONHECIDO" in classifier.get_unknown_statuses()
    
    def test_custom_paid_status(self):
        """Testa status pagos customizados."""
        classifier = StatusClassifier(
            paid_status_list=["CUSTOM_PAGO", "OUTRO_PAGO"]
        )
        assert classifier.is_paid("CUSTOM_PAGO") is True
        assert classifier.is_paid("PAGO NO DIA") is False  # Não está na lista customizada
    
    def test_custom_open_status(self):
        """Testa status em aberto customizados."""
        classifier = StatusClassifier(
            open_status_list=["CUSTOM_ABERTO", "OUTRO_ABERTO"]
        )
        assert classifier.is_open("CUSTOM_ABERTO") is True
        assert classifier.is_open("VENCIDO") is False  # Não está na lista customizada
    
    def test_get_unknown_statuses(self):
        """Testa obtenção de status desconhecidos."""
        classifier = StatusClassifier()
        classifier.classify("STATUS1")
        classifier.classify("STATUS2")
        classifier.classify("PAGO NO DIA")  # Conhecido
        
        unknown = classifier.get_unknown_statuses()
        assert "STATUS1" in unknown
        assert "STATUS2" in unknown
        assert "PAGO NO DIA" not in unknown
