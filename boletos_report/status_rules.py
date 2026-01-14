"""
Classificação e normalização de status de boletos.
Define regras para identificar boletos pagos vs em aberto.
"""

import re
import logging
from typing import Set, Tuple, Optional

logger = logging.getLogger(__name__)


class StatusClassifier:
    """
    Classificador de status de boletos.
    """
    
    def __init__(
        self,
        paid_status_list: Optional[list] = None,
        open_status_list: Optional[list] = None
    ):
        """
        Inicializa o classificador com listas de status.
        
        Args:
            paid_status_list: Lista de status considerados como pagos
            open_status_list: Lista de status considerados como em aberto
        """
        # Status padrão considerados como PAGOS
        self.default_paid = {
            "PAGO NO DIA",
            "PAGO",
            "LIQUIDADO",
            "BAIXADO",
            "QUITADO",
            "PAGO EM DIA"
        }
        
        # Status padrão considerados como EM ABERTO
        self.default_open = {
            "A VENCER / VENCIDO",
            "VENCIDO",
            "EM ABERTO",
            "ABERTO",
            "A VENCER",
            "VENCIDO",
            "PENDENTE"
        }
        
        # Normalizar listas fornecidas
        if paid_status_list:
            self.paid_status = {self.normalize_status(s) for s in paid_status_list}
        else:
            self.paid_status = self.default_paid.copy()
            
        if open_status_list:
            self.open_status = {self.normalize_status(s) for s in open_status_list}
        else:
            self.open_status = self.default_open.copy()
        
        # Status desconhecidos (não classificados)
        self.unknown_status: Set[str] = set()
    
    @staticmethod
    def normalize_status(status: str) -> str:
        """
        Normaliza um status: trim, uppercase, reduz espaços.
        
        Args:
            status: Status a normalizar
            
        Returns:
            Status normalizado
        """
        if not isinstance(status, str):
            return ""
        status = status.strip()
        status = re.sub(r'\s+', ' ', status)
        return status.upper()
    
    def is_paid(self, status: str) -> bool:
        """
        Verifica se um status indica pagamento.
        
        Args:
            status: Status a verificar
            
        Returns:
            True se for considerado pago
        """
        status_norm = self.normalize_status(status)
        if not status_norm:
            return False
        return status_norm in self.paid_status
    
    def is_open(self, status: str) -> bool:
        """
        Verifica se um status indica em aberto/devedor.
        
        Args:
            status: Status a verificar
            
        Returns:
            True se for considerado em aberto
        """
        status_norm = self.normalize_status(status)
        if not status_norm:
            return False
        return status_norm in self.open_status
    
    def classify(self, status: str) -> Tuple[str, str]:
        """
        Classifica um status e retorna (status_norm, categoria).
        
        Args:
            status: Status a classificar
            
        Returns:
            Tupla (status_normalizado, categoria) onde categoria é:
            - "PAID" se pago
            - "OPEN" se em aberto
            - "UNKNOWN" se não classificado
        """
        status_norm = self.normalize_status(status)
        
        if not status_norm:
            return ("", "UNKNOWN")
        
        if self.is_paid(status_norm):
            return (status_norm, "PAID")
        elif self.is_open(status_norm):
            return (status_norm, "OPEN")
        else:
            # Registrar status desconhecido
            if status_norm not in self.unknown_status:
                self.unknown_status.add(status_norm)
                logger.warning(f"Status desconhecido encontrado: '{status_norm}' (original: '{status}')")
            return (status_norm, "UNKNOWN")
    
    def get_unknown_statuses(self) -> Set[str]:
        """
        Retorna conjunto de status desconhecidos encontrados.
        
        Returns:
            Set de status normalizados não classificados
        """
        return self.unknown_status.copy()
