"""
Testes para módulo de coleta de dados
"""
import pytest
import pandas as pd
from src.data_collection.blaze_client import BlazeDataCollector

class TestBlazeDataCollector:
    """Testes para o coletor de dados da Blaze"""

    def test_collector_initialization(self):
        """Testa inicialização do coletor"""
        collector = BlazeDataCollector()
        assert collector is not None
        assert collector.base_url == "https://blaze.com/api"

    def test_fallback_data_generation(self):
        """Testa geração de dados de fallback"""
        collector = BlazeDataCollector()

        crash_data = collector.get_fallback_crash_data()
        assert not crash_data.empty
        assert len(crash_data) == 50
        assert 'crash_point' in crash_data.columns

        double_data = collector.get_fallback_double_data()
        assert not double_data.empty
        assert len(double_data) == 50
        assert 'color' in double_data.columns

    def test_data_processing(self):
        """Testa processamento de dados"""
        collector = BlazeDataCollector()

        # Teste com dados de crash
        crash_data = collector.get_fallback_crash_data()
        processed_data = collector.calculate_derived_metrics(crash_data, 'crash_point')

        assert 'diff' in processed_data.columns
        assert 'moving_avg_5' in processed_data.columns