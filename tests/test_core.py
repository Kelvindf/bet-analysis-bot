"""
Testes unitários - FASE 4
Cobertura das funções críticas
"""
import pytest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import (
    Signal, SignalType, GameType, SignalStatus,
    BlazeData, retry, cache, DataValidationError
)
from database import SignalRepository, init_db
from data_collection.validators import DataValidator


class TestCoreTypes:
    """Testes de tipos core"""
    
    def test_signal_creation(self):
        """Testa criação de Signal"""
        signal = Signal(
            id="test_001",
            game=GameType.DOUBLE,
            signal_type=SignalType.RED,
            confidence=0.85,
            timestamp=datetime.now()
        )
        
        assert signal.id == "test_001"
        assert signal.confidence == 0.85
        assert signal.status == SignalStatus.PENDING
    
    def test_signal_validation_confidence(self):
        """Testa validação de confiança"""
        with pytest.raises(ValueError):
            Signal(
                id="test_001",
                game=GameType.DOUBLE,
                signal_type=SignalType.RED,
                confidence=1.5,  # Inválido
                timestamp=datetime.now()
            )
    
    def test_signal_validation_strategies(self):
        """Testa validação de estratégias"""
        with pytest.raises(ValueError):
            Signal(
                id="test_001",
                game=GameType.DOUBLE,
                signal_type=SignalType.RED,
                confidence=0.85,
                timestamp=datetime.now(),
                strategies_passed=10  # Inválido (max 6)
            )
    
    def test_blaze_data_creation(self):
        """Testa criação de BlazeData"""
        data = BlazeData(
            id="blaze_001",
            game=GameType.DOUBLE,
            timestamp=datetime.now(),
            result="red",
            data={'color': 'red'}
        )
        
        assert data.game == GameType.DOUBLE
        assert data.valid == True


class TestDataValidation:
    """Testes de validação de dados"""
    
    def test_validate_blaze_data_valid(self):
        """Testa validação de dados válidos"""
        data = BlazeData(
            id="test_001",
            game=GameType.DOUBLE,
            timestamp=datetime.now(),
            result="red",
            data={'color': 'red'}
        )
        
        assert DataValidator.validate_blaze_data(data) == True
    
    def test_validate_blaze_data_invalid_id(self):
        """Testa rejeição de ID inválido"""
        data = BlazeData(
            id="",  # Inválido
            game=GameType.DOUBLE,
            timestamp=datetime.now(),
            result="red",
            data={'color': 'red'}
        )
        
        with pytest.raises(DataValidationError):
            DataValidator.validate_blaze_data(data)
    
    def test_validate_data_list(self):
        """Testa validação de lista"""
        valid_data = BlazeData(
            id="test_001",
            game=GameType.DOUBLE,
            timestamp=datetime.now(),
            result="red",
            data={'color': 'red'}
        )
        
        invalid_data = BlazeData(
            id="",
            game=GameType.DOUBLE,
            timestamp=datetime.now(),
            result="red",
            data={'color': 'red'}
        )
        
        valid, errors = DataValidator.validate_data_list([valid_data, invalid_data])
        
        assert len(valid) == 1
        assert len(errors) == 1
    
    def test_deduplicate(self):
        """Testa deduplicação"""
        data1 = BlazeData(
            id="dup_001",
            game=GameType.DOUBLE,
            timestamp=datetime.now(),
            result="red",
            data={}
        )
        
        data2 = BlazeData(
            id="dup_001",  # Duplicado
            game=GameType.DOUBLE,
            timestamp=datetime.now(),
            result="red",
            data={}
        )
        
        result = DataValidator.deduplicate([data1, data2])
        assert len(result) == 1
    
    def test_data_quality_check(self):
        """Testa análise de qualidade"""
        data_list = [
            BlazeData(
                id=f"test_{i}",
                game=GameType.DOUBLE,
                timestamp=datetime.now() - timedelta(minutes=i),
                result="red" if i % 2 == 0 else "black",
                data={'index': i}
            )
            for i in range(10)
        ]
        
        quality = DataValidator.check_data_quality(data_list)
        
        assert quality['total'] == 10
        assert quality['completeness'] > 0.9
        assert quality['quality_score'] > 0.8


class TestDatabase:
    """Testes de banco de dados"""
    
    def test_signal_repository_save_and_get(self, tmp_path):
        """Testa save e get de sinais"""
        db_path = str(tmp_path / "test.db")
        Session = init_db(db_path)
        repo = SignalRepository(Session)
        
        signal = Signal(
            id="db_test_001",
            game=GameType.DOUBLE,
            signal_type=SignalType.RED,
            confidence=0.85,
            timestamp=datetime.now()
        )
        
        repo.save(signal)
        retrieved = repo.get_by_id("db_test_001")
        
        assert retrieved is not None
        assert retrieved.confidence == 0.85
    
    def test_signal_verify_result(self, tmp_path):
        """Testa verificação de resultado"""
        db_path = str(tmp_path / "test.db")
        Session = init_db(db_path)
        repo = SignalRepository(Session)
        
        signal = Signal(
            id="verify_test",
            game=GameType.DOUBLE,
            signal_type=SignalType.RED,
            confidence=0.85,
            timestamp=datetime.now()
        )
        
        repo.save(signal)
        repo.verify_result("verify_test", won=True)
        
        retrieved = repo.get_by_id("verify_test")
        assert retrieved.status == SignalStatus.WIN


class TestDecorators:
    """Testes de decoradores"""
    
    def test_cache_decorator(self):
        """Testa cache"""
        call_count = 0
        
        @cache(ttl_seconds=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(5)
        
        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Chamado uma vez apenas (cache)
    
    def test_retry_decorator(self):
        """Testa retry"""
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def sometimes_fails():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RetryableError("Falha simulada")
            return "sucesso"
        
        result = sometimes_fails()
        
        assert result == "sucesso"
        assert call_count == 2


# Tests de integração
class TestIntegration:
    """Testes de integração"""
    
    def test_full_pipeline(self, tmp_path):
        """Testa pipeline completo"""
        db_path = str(tmp_path / "test.db")
        Session = init_db(db_path)
        repo = SignalRepository(Session)
        
        # Criar múltiplos sinais
        for i in range(5):
            signal = Signal(
                id=f"integration_test_{i}",
                game=GameType.DOUBLE,
                signal_type=SignalType.RED if i % 2 == 0 else SignalType.BLACK,
                confidence=0.80 + (i * 0.02),
                timestamp=datetime.now() - timedelta(minutes=i),
                strategies_passed=3
            )
            repo.save(signal)
        
        # Verificar alguns
        repo.verify_result("integration_test_0", won=True)
        repo.verify_result("integration_test_1", won=False)
        
        # Obter stats
        stats = repo.get_stats()
        
        assert stats['total'] >= 2
        assert stats['wins'] == 1
        assert stats['losses'] == 1


# Fixtures
@pytest.fixture
def sample_signal():
    """Fixture de sinal de teste"""
    return Signal(
        id="fixture_001",
        game=GameType.DOUBLE,
        signal_type=SignalType.RED,
        confidence=0.85,
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_blaze_data():
    """Fixture de dados Blaze"""
    return BlazeData(
        id="fixture_blaze_001",
        game=GameType.DOUBLE,
        timestamp=datetime.now(),
        result="red",
        data={'color': 'red'}
    )


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
