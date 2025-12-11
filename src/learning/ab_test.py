"""
A/B Testing Framework - FASE 3, Tarefa 8

Comparação estatística entre versões do sistema

OBJETIVO:
    - Testar Versão A (controle) vs Versão B (tratamento)
    - Medir performance em: WR, ROI, drawdown
    - Validar com significância estatística
    - Fazer rollout gradual (10% → 50% → 100%)
    - Ganho esperado: +3-5% lucro

FLUXO:
    
    Sinal Gerado
        ├─ Versão A (Control): Sistema atual
        └─ Versão B (Test): Com otimizações
    
    Ambas versões executam aposta em paralelo
        ├─ Coletam dados
        ├─ Registram resultados
        └─ Acumulam métricas
    
    Análise Periódica:
        ├─ Calcular WR de cada versão
        ├─ Calcular ROI de cada versão
        ├─ Calcular drawdown de cada versão
        ├─ Teste estatístico (t-test ou chi-square)
        └─ Determinar vencedor
    
    Rollout Gradual:
        10% → Versão B em 10% das apostas
        20% → Versão B em 20% das apostas
        ...
        100% → Versão B em 100% (migração completa)

ESTATÍSTICA:
    
    Win Rate (Binomial):
        H0: p_A = p_B (mesma taxa de ganho)
        H1: p_A ≠ p_B (diferentes)
        Teste: Chi-square ou binomial test
        Significância: α = 0.05 (95% confiança)
    
    ROI (Contínuo):
        H0: μ_A = μ_B (mesmo retorno)
        H1: μ_A ≠ μ_B (diferentes)
        Teste: t-test independente
        Significância: α = 0.05
    
    Drawdown (Contínuo):
        H0: σ_A ≤ σ_B (A não é mais seguro)
        H1: σ_A > σ_B (A é mais seguro)
        Teste: Levene's test
        Significância: α = 0.05

ROLLOUT STRATEGY:
    
    Fase 1: Validação (min 100 amostras)
        └─ Coletar dados suficientes
    
    Fase 2: Análise (p-value < 0.05)
        └─ Versão B é melhor?
    
    Fase 3: Rollout (10% → 50% → 100%)
        ├─ 10% por 24h (monitorar)
        ├─ 50% por 48h (validar)
        └─ 100% (completo se OK)
    
    Fase 4: Monitoramento
        └─ Acompanhar continuamente

EXEMPLO:

    ab_test = ABTestManager()
    
    # Coletar dados
    while running:
        signal = generate_signal()
        
        # Versão A
        result_a = execute_version_a(signal)
        ab_test.record_result_a(result_a)
        
        # Versão B
        result_b = execute_version_b(signal)
        ab_test.record_result_b(result_b)
    
    # Análise periódica
    if ab_test.should_analyze():
        analysis = ab_test.analyze()
        print(f"Win Rate A: {analysis.wr_a:.1%}")
        print(f"Win Rate B: {analysis.wr_b:.1%}")
        print(f"p-value: {analysis.pvalue_wr:.4f}")
        print(f"B é melhor? {analysis.b_is_better}")
        
        if analysis.b_is_better and analysis.pvalue_wr < 0.05:
            print("→ Aumentar rollout de B")
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class RolloutPhase(Enum):
    """Fases do rollout gradual"""
    COLLECTION = "collection"      # Coletando dados (100% A, 0% B)
    ANALYSIS = "analysis"          # Analisando (100% A, 0% B)
    ROLLOUT_10 = "rollout_10"      # 90% A, 10% B
    ROLLOUT_25 = "rollout_25"      # 75% A, 25% B
    ROLLOUT_50 = "rollout_50"      # 50% A, 50% B
    ROLLOUT_75 = "rollout_75"      # 25% A, 75% B
    ROLLOUT_100 = "rollout_100"    # 0% A, 100% B
    COMPLETE = "complete"          # Migração concluída


@dataclass
class TestResult:
    """Resultado de uma aposta no A/B test"""
    bet_id: str
    version: str                    # 'A' ou 'B'
    result: str                     # 'WIN' ou 'LOSS'
    payout: float                   # Lucro/perda em %
    timestamp: datetime
    confidence: float               # Confiança da aposta


@dataclass
class AnalysisResult:
    """Resultado da análise A/B test"""
    timestamp: datetime
    
    # Versão A (controle)
    results_a: int                  # Total de apostas
    wins_a: int                     # Total de ganhos
    wr_a: float                     # Win Rate (%)
    roi_a: float                    # ROI médio
    std_a: float                    # Desvio padrão
    
    # Versão B (teste)
    results_b: int
    wins_b: int
    wr_b: float
    roi_b: float
    std_b: float
    
    # Testes estatísticos
    pvalue_wr: float                # p-value do teste de WR
    pvalue_roi: float               # p-value do teste de ROI
    confidence_level: float         # Confiança (95%, 99%, etc)
    
    # Conclusões
    b_is_better: bool               # B é melhor que A?
    significant: bool               # Diferença é significante?
    recommendation: str             # Recomendação de ação


class ABTestManager:
    """
    Gerenciador de A/B Testing
    
    Comparação estatística entre duas versões do sistema
    
    Exemplo:
        ab_test = ABTestManager(
            min_samples=100,
            significance_level=0.05,
            analysis_interval_hours=24
        )
        
        # Registrar resultados
        ab_test.record_result_a(result)
        ab_test.record_result_b(result)
        
        # Analisar
        if ab_test.should_analyze():
            analysis = ab_test.analyze()
            if analysis.b_is_better:
                ab_test.increase_rollout()
    """
    
    def __init__(self,
                 min_samples: int = 100,
                 significance_level: float = 0.05,
                 analysis_interval_hours: int = 24):
        """
        Args:
            min_samples: Mínimo de amostras antes de analisar
            significance_level: α para teste estatístico (default 0.05 = 95%)
            analysis_interval_hours: Intervalo entre análises (horas)
        """
        self.min_samples = min_samples
        self.significance_level = significance_level
        self.analysis_interval = timedelta(hours=analysis_interval_hours)
        
        # Resultados de cada versão
        self.results_a: List[TestResult] = []
        self.results_b: List[TestResult] = []
        
        # Histórico de análises
        self.analyses: List[AnalysisResult] = []
        
        # Controle de rollout
        self.current_phase = RolloutPhase.COLLECTION
        self.phase_history: Dict = {}
        self.last_analysis_time: Optional[datetime] = None
        
        # Configuração
        self.rollout_percentages = {
            RolloutPhase.COLLECTION: (100, 0),    # (% A, % B)
            RolloutPhase.ANALYSIS: (100, 0),
            RolloutPhase.ROLLOUT_10: (90, 10),
            RolloutPhase.ROLLOUT_25: (75, 25),
            RolloutPhase.ROLLOUT_50: (50, 50),
            RolloutPhase.ROLLOUT_75: (25, 75),
            RolloutPhase.ROLLOUT_100: (0, 100),
            RolloutPhase.COMPLETE: (0, 100),
        }
        
        logger.info(f"[AB-TEST] ABTestManager inicializado:")
        logger.info(f"  - Min Samples: {min_samples}")
        logger.info(f"  - Significance Level: {significance_level:.1%}")
        logger.info(f"  - Analysis Interval: {analysis_interval_hours}h")
    
    def record_result_a(self, result: TestResult):
        """Registra resultado para Versão A (controle)"""
        if result.version != 'A':
            result.version = 'A'
        
        self.results_a.append(result)
        logger.debug(f"[AB-TEST] Resultado A registrado: {result.bet_id} → {result.result}")
    
    def record_result_b(self, result: TestResult):
        """Registra resultado para Versão B (teste)"""
        if result.version != 'B':
            result.version = 'B'
        
        self.results_b.append(result)
        logger.debug(f"[AB-TEST] Resultado B registrado: {result.bet_id} → {result.result}")
    
    def should_analyze(self) -> bool:
        """Verifica se deve fazer análise"""
        # Mínimo de amostras
        if len(self.results_a) < self.min_samples or len(self.results_b) < self.min_samples:
            return False
        
        # Intervalo de tempo
        if self.last_analysis_time is None:
            return True  # Primeira análise
        
        elapsed = datetime.now() - self.last_analysis_time
        return elapsed > self.analysis_interval
    
    def analyze(self) -> AnalysisResult:
        """
        Analisa performance das duas versões
        
        Returns:
            AnalysisResult com conclusões e recomendações
        """
        # Validar dados
        if len(self.results_a) < self.min_samples or len(self.results_b) < self.min_samples:
            logger.warning(f"[AB-TEST] Amostras insuficientes para análise")
            return None
        
        # Calcular métricas Versão A
        wins_a = sum(1 for r in self.results_a if r.result == 'WIN')
        wr_a = wins_a / len(self.results_a)
        roi_a = np.mean([r.payout for r in self.results_a])
        std_a = np.std([r.payout for r in self.results_a])
        
        # Calcular métricas Versão B
        wins_b = sum(1 for r in self.results_b if r.result == 'WIN')
        wr_b = wins_b / len(self.results_b)
        roi_b = np.mean([r.payout for r in self.results_b])
        std_b = np.std([r.payout for r in self.results_b])
        
        # Testes estatísticos
        # 1. Win Rate (Chi-square test)
        contingency_table = np.array([
            [wins_a, len(self.results_a) - wins_a],
            [wins_b, len(self.results_b) - wins_b]
        ])
        chi2, pvalue_wr, dof, expected = stats.chi2_contingency(contingency_table)
        
        # 2. ROI (t-test independente)
        t_stat, pvalue_roi = stats.ttest_ind(
            [r.payout for r in self.results_a],
            [r.payout for r in self.results_b],
            equal_var=False  # Welch's t-test
        )
        
        # Determinar vencedor
        b_is_better = (wr_b > wr_a and roi_b > roi_a)
        significant = (pvalue_wr < self.significance_level)
        
        # Gerar recomendação
        recommendation = self._generate_recommendation(
            wr_a, wr_b, roi_a, roi_b,
            pvalue_wr, pvalue_roi,
            b_is_better, significant
        )
        
        # Criar resultado
        analysis = AnalysisResult(
            timestamp=datetime.now(),
            results_a=len(self.results_a),
            wins_a=wins_a,
            wr_a=wr_a,
            roi_a=roi_a,
            std_a=std_a,
            results_b=len(self.results_b),
            wins_b=wins_b,
            wr_b=wr_b,
            roi_b=roi_b,
            std_b=std_b,
            pvalue_wr=pvalue_wr,
            pvalue_roi=pvalue_roi,
            confidence_level=1.0 - self.significance_level,
            b_is_better=b_is_better,
            significant=significant,
            recommendation=recommendation
        )
        
        # Registrar análise
        self.analyses.append(analysis)
        self.last_analysis_time = datetime.now()
        
        logger.info(f"[AB-TEST] Análise concluída:")
        logger.info(f"  A: {wr_a:.1%} WR, {roi_a:.2f}% ROI")
        logger.info(f"  B: {wr_b:.1%} WR, {roi_b:.2f}% ROI")
        logger.info(f"  p-value (WR): {pvalue_wr:.4f}")
        logger.info(f"  B melhor? {b_is_better}, Significante? {significant}")
        logger.info(f"  Recomendação: {recommendation}")
        
        return analysis
    
    def _generate_recommendation(self, wr_a, wr_b, roi_a, roi_b,
                                pvalue_wr, pvalue_roi,
                                b_is_better, significant) -> str:
        """Gera recomendação baseada em análise"""
        
        if not b_is_better:
            return "Versão A é melhor - continuar com A"
        
        if significant and pvalue_wr < self.significance_level:
            return "B é melhor com significância - aumentar rollout para 10%"
        
        if b_is_better and pvalue_wr < 0.1:  # 90% confiança
            return "B provavelmente é melhor - aumentar rollout para 10%"
        
        if b_is_better:
            return "B parece melhor mas sem significância - continuar coletando dados"
        
        return "Continuar monitorando"
    
    def should_increase_rollout(self, analysis: Optional[AnalysisResult] = None) -> bool:
        """
        Verifica se deve aumentar rollout de B
        
        Critérios:
        1. B é melhor que A
        2. Diferença é estatisticamente significante (p < 0.05)
        3. ROI de B é consistentemente positivo
        """
        if analysis is None:
            if not self.analyses:
                return False
            analysis = self.analyses[-1]
        
        # Critério 1: B melhor em WR
        if analysis.wr_b <= analysis.wr_a:
            logger.warning(f"[AB-TEST] B não tem melhor WR ({analysis.wr_b:.1%} vs {analysis.wr_a:.1%})")
            return False
        
        # Critério 2: Significância estatística
        if analysis.pvalue_wr > self.significance_level:
            logger.warning(f"[AB-TEST] Diferença não significante (p={analysis.pvalue_wr:.4f})")
            return False
        
        # Critério 3: ROI positivo
        if analysis.roi_b < 0:
            logger.warning(f"[AB-TEST] ROI de B é negativo ({analysis.roi_b:.2f}%)")
            return False
        
        logger.info(f"[AB-TEST] Critérios para rollout atendidos")
        return True
    
    def increase_rollout(self) -> bool:
        """
        Aumenta o rollout de Versão B
        
        Returns:
            True se rollout foi aumentado
        """
        current_idx = list(RolloutPhase).index(self.current_phase)
        
        if current_idx >= len(RolloutPhase) - 1:
            logger.info(f"[AB-TEST] Rollout já em 100%")
            return False
        
        next_phase = list(RolloutPhase)[current_idx + 1]
        pct_a, pct_b = self.rollout_percentages[next_phase]
        
        self.current_phase = next_phase
        self.phase_history[next_phase.value] = datetime.now()
        
        logger.info(f"[AB-TEST] Rollout aumentado para {next_phase.value}: {pct_b}% B, {pct_a}% A")
        return True
    
    def decrease_rollout(self) -> bool:
        """
        Diminui o rollout de Versão B (rollback)
        
        Usado se B apresentar problemas
        """
        current_idx = list(RolloutPhase).index(self.current_phase)
        
        if current_idx <= 1:
            logger.warning(f"[AB-TEST] Não é possível diminuir rollout")
            return False
        
        prev_phase = list(RolloutPhase)[current_idx - 1]
        pct_a, pct_b = self.rollout_percentages[prev_phase]
        
        self.current_phase = prev_phase
        
        logger.warning(f"[AB-TEST] Rollout reduzido para {prev_phase.value}: {pct_b}% B, {pct_a}% A")
        return True
    
    def get_current_rollout(self) -> Tuple[int, int]:
        """Retorna percentual atual de (A%, B%)"""
        return self.rollout_percentages[self.current_phase]
    
    def get_status(self) -> Dict:
        """Retorna status atual do A/B test"""
        pct_a, pct_b = self.get_current_rollout()
        
        status = {
            'phase': self.current_phase.value,
            'rollout_a': pct_a,
            'rollout_b': pct_b,
            'results_a': len(self.results_a),
            'results_b': len(self.results_b),
            'can_analyze': self.should_analyze(),
            'analyses_completed': len(self.analyses)
        }
        
        if self.analyses:
            last_analysis = self.analyses[-1]
            status['last_analysis'] = {
                'timestamp': last_analysis.timestamp.isoformat(),
                'wr_a': f"{last_analysis.wr_a:.1%}",
                'wr_b': f"{last_analysis.wr_b:.1%}",
                'roi_a': f"{last_analysis.roi_a:.2f}%",
                'roi_b': f"{last_analysis.roi_b:.2f}%",
                'b_is_better': last_analysis.b_is_better,
                'pvalue': f"{last_analysis.pvalue_wr:.4f}"
            }
        
        return status
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """Retorna histórico de análises"""
        return [
            {
                'timestamp': a.timestamp.isoformat(),
                'wr_a': f"{a.wr_a:.1%}",
                'wr_b': f"{a.wr_b:.1%}",
                'roi_a': f"{a.roi_a:.2f}%",
                'roi_b': f"{a.roi_b:.2f}%",
                'pvalue_wr': f"{a.pvalue_wr:.4f}",
                'pvalue_roi': f"{a.pvalue_roi:.4f}",
                'b_is_better': a.b_is_better,
                'significant': a.significant,
                'recommendation': a.recommendation
            }
            for a in self.analyses[-limit:]
        ]


if __name__ == '__main__':
    # Exemplo de uso
    print("=" * 80)
    print("TESTE AB TESTING FRAMEWORK")
    print("=" * 80)
    
    ab_test = ABTestManager(min_samples=50)
    
    # Simular resultados
    import random
    
    print("\nSimulando 60 resultados para cada versão...")
    for i in range(60):
        # Versão A
        result_a = TestResult(
            bet_id=f"a_{i:03d}",
            version='A',
            result='WIN' if random.random() < 0.65 else 'LOSS',
            payout=19.0 if random.random() < 0.65 else -100.0,
            timestamp=datetime.now(),
            confidence=0.65 + random.random() * 0.25
        )
        ab_test.record_result_a(result_a)
        
        # Versão B (um pouco melhor)
        result_b = TestResult(
            bet_id=f"b_{i:03d}",
            version='B',
            result='WIN' if random.random() < 0.68 else 'LOSS',  # 3% melhor
            payout=19.0 if random.random() < 0.68 else -100.0,
            timestamp=datetime.now(),
            confidence=0.67 + random.random() * 0.25
        )
        ab_test.record_result_b(result_b)
    
    print(f"✓ {len(ab_test.results_a)} resultados de A")
    print(f"✓ {len(ab_test.results_b)} resultados de B")
    
    # Analisar
    if ab_test.should_analyze():
        print("\nAnalisando...")
        analysis = ab_test.analyze()
        
        print(f"\nResultados:")
        print(f"  Versão A: {analysis.wr_a:.1%} WR, {analysis.roi_a:.2f}% ROI")
        print(f"  Versão B: {analysis.wr_b:.1%} WR, {analysis.roi_b:.2f}% ROI")
        print(f"  p-value (WR): {analysis.pvalue_wr:.4f}")
        print(f"  Significância: {analysis.significant}")
        print(f"  B é melhor? {analysis.b_is_better}")
        print(f"\nRecomendação: {analysis.recommendation}")
        
        # Rollout
        if ab_test.should_increase_rollout(analysis):
            print("\n✓ Aumentando rollout...")
            ab_test.increase_rollout()
            pct_a, pct_b = ab_test.get_current_rollout()
            print(f"  Nova distribuição: {pct_a}% A, {pct_b}% B")
    
    # Status
    print("\n" + "=" * 80)
    print("STATUS FINAL")
    print("=" * 80)
    status = ab_test.get_status()
    print(json.dumps(status, indent=2, default=str))
    
    print("\n✅ TESTE AB TESTING CONCLUÍDO")
