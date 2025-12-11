"""
Testes para módulo de análise
"""
import pytest
import pandas as pd
from src.analysis.statistical_analyzer import StatisticalAnalyzer

class TestStatisticalAnalyzer:
    """Testes para o analisador estatístico"""

    def test_analyzer_initialization(self):
        """Testa inicialização do analisador"""
        analyzer = StatisticalAnalyzer()
        assert analyzer is not None
        assert analyzer.min_confidence == 0.65

    def test_signal_generation(self):
        """Testa geração de sinais"""
        analyzer = StatisticalAnalyzer()

        # Dados de teste
        test_data = {
            'crash': pd.DataFrame({
                'crash_point': [1.5, 1.3, 1.2, 1.4, 1.1, 1.6, 1.2, 1.3, 1.1, 1.4],
                'timestamp': pd.date_range('2023-01-01', periods=10, freq='T')
            })
        }

        analysis_results = analyzer.analyze_patterns(test_data)
        signals = analyzer.generate_signals(analysis_results)

        assert isinstance(signals, list)