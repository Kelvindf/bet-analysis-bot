"""
Validadores de dados coletados
Garante qualidade dos dados antes de processar
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from core import BlazeData, DataValidationError

logger = logging.getLogger(__name__)


class DataValidator:
    """Validador de dados coletados"""
    
    @staticmethod
    def validate_blaze_data(data: BlazeData) -> bool:
        """
        Valida um registro BlazeData
        
        Args:
            data: Dados a validar
        
        Returns:
            True se válido
        
        Raises:
            DataValidationError se inválido
        """
        # Validar ID
        if not data.id or len(str(data.id)) < 2:
            raise DataValidationError(f"ID inválido: {data.id}")
        
        # Validar timestamp
        if not isinstance(data.timestamp, datetime):
            raise DataValidationError(f"Timestamp não é datetime: {data.timestamp}")
        
        if data.timestamp > datetime.now():
            raise DataValidationError(f"Timestamp no futuro: {data.timestamp}")
        
        if data.timestamp < datetime.now() - timedelta(days=7):
            raise DataValidationError(f"Timestamp muito antigo: {data.timestamp}")
        
        # Validar resultado
        if not data.result or len(str(data.result)) < 1:
            raise DataValidationError(f"Resultado vazio: {data.result}")
        
        # Validar price (se Crash)
        if data.price is not None:
            if not isinstance(data.price, (int, float)):
                raise DataValidationError(f"Price não é número: {data.price}")
            if data.price < 0.1 or data.price > 1000:
                raise DataValidationError(f"Price fora do range: {data.price}")
        
        # Validar dados JSON
        if not isinstance(data.data, dict):
            raise DataValidationError(f"Data não é dict: {type(data.data)}")
        
        return True
    
    @staticmethod
    def validate_data_list(data_list: List[BlazeData]) -> Tuple[List[BlazeData], List[str]]:
        """
        Valida lista de dados, retorna válidos e erros
        
        Args:
            data_list: Lista de BlazeData
        
        Returns:
            Tupla (válidos, erros)
        """
        valid = []
        errors = []
        
        for i, data in enumerate(data_list):
            try:
                DataValidator.validate_blaze_data(data)
                valid.append(data)
            except DataValidationError as e:
                errors.append(f"Record {i}: {str(e)}")
                logger.warning(f"Record {i} inválido: {e}")
        
        if errors:
            logger.warning(f"❌ {len(errors)}/{len(data_list)} registros inválidos")
        else:
            logger.info(f"✅ {len(valid)}/{len(data_list)} registros válidos")
        
        return valid, errors
    
    @staticmethod
    def check_data_quality(data_list: List[BlazeData]) -> Dict[str, Any]:
        """
        Analisa qualidade dos dados coletados
        
        Args:
            data_list: Lista de BlazeData
        
        Returns:
            Dicionário com métricas de qualidade
        """
        if not data_list:
            return {
                'total': 0,
                'quality_score': 0.0,
                'issues': ['Nenhum dado coletado']
            }
        
        issues = []
        
        # Verificar completude
        with_id = sum(1 for d in data_list if d.id)
        with_timestamp = sum(1 for d in data_list if d.timestamp)
        with_result = sum(1 for d in data_list if d.result)
        with_data = sum(1 for d in data_list if d.data)
        
        total = len(data_list)
        completeness = (with_id + with_timestamp + with_result + with_data) / (total * 4) if total > 0 else 0
        
        if completeness < 0.95:
            issues.append(f"Completude baixa: {completeness*100:.1f}%")
        
        # Verificar duplicatas
        ids = [d.id for d in data_list]
        duplicates = len(ids) - len(set(ids))
        if duplicates > 0:
            issues.append(f"{duplicates} registros duplicados")
        
        # Verificar timestamps
        if len(data_list) > 1:
            timestamps = sorted([d.timestamp for d in data_list])
            gaps = []
            for i in range(1, len(timestamps)):
                gap = (timestamps[i] - timestamps[i-1]).total_seconds()
                if gap > 300:  # Mais de 5 minutos
                    gaps.append(gap)
            
            if gaps:
                avg_gap = sum(gaps) / len(gaps)
                if avg_gap > 60:
                    issues.append(f"Grandes gaps entre timestamps (média: {avg_gap:.0f}s)")
        
        # Score de qualidade
        quality_score = (completeness * 0.4) + ((1 - min(duplicates / total, 1)) * 0.3) + (0.3 if not gaps else 0.15)
        
        return {
            'total': total,
            'completeness': completeness,
            'duplicates': duplicates,
            'quality_score': quality_score,
            'issues': issues,
            'status': 'OK' if quality_score > 0.85 else 'WARNING' if quality_score > 0.7 else 'ERROR'
        }
    
    @staticmethod
    def deduplicate(data_list: List[BlazeData]) -> List[BlazeData]:
        """
        Remove duplicatas baseado em ID
        
        Args:
            data_list: Lista com possíveis duplicatas
        
        Returns:
            Lista sem duplicatas
        """
        seen = set()
        unique = []
        
        for data in data_list:
            if data.id not in seen:
                seen.add(data.id)
                unique.append(data)
        
        if len(unique) < len(data_list):
            logger.info(f"🔄 Removidas {len(data_list) - len(unique)} duplicatas")
        
        return unique
