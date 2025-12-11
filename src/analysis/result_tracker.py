"""
Sistema de Tracking de Resultados
Registra acertos/erros dos sinais enviados
"""
import json
import os
from datetime import datetime
from typing import Dict, List
import pandas as pd

class ResultTracker:
    def __init__(self, db_path='data/results_history.json'):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Garante que arquivo de histórico existe"""
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({'signals': [], 'stats': {}}, f)
    
    def save_signal(self, signal_data: Dict):
        """
        Salva sinal enviado para tracking posterior
        
        Args:
            signal_data: {
                'signal_id': 'xxx',
                'signal_type': 'Vermelho',
                'confidence': 0.85,
                'timestamp': datetime,
                'game': 'Double',
                'strategies_passed': 4
            }
        """
        data = self._load_db()
        
        signal_record = {
            'signal_id': signal_data.get('signal_id'),
            'signal_type': signal_data.get('signal_type'),
            'confidence': signal_data.get('confidence'),
            'timestamp': signal_data.get('timestamp').isoformat(),
            'game': signal_data.get('game', 'Double'),
            'strategies_passed': signal_data.get('strategies_passed', 0),
            'result': None,  # Será preenchido depois
            'verified_at': None
        }
        
        data['signals'].append(signal_record)
        self._save_db(data)
    
    def register_result(self, signal_id: str, won: bool):
        """
        Registra resultado de um sinal (acerto ou erro)
        
        Args:
            signal_id: ID do sinal
            won: True se acertou, False se errou
        """
        data = self._load_db()
        
        for signal in data['signals']:
            if signal['signal_id'] == signal_id and signal['result'] is None:
                signal['result'] = 'WIN' if won else 'LOSS'
                signal['verified_at'] = datetime.now().isoformat()
                break
        
        self._save_db(data)
        self._update_stats(data)
    
    def _update_stats(self, data: Dict):
        """Atualiza estatísticas globais"""
        verified = [s for s in data['signals'] if s['result'] is not None]
        
        if not verified:
            return
        
        wins = sum(1 for s in verified if s['result'] == 'WIN')
        losses = len(verified) - wins
        win_rate = wins / len(verified) if verified else 0
        
        # Stats por confiança
        by_confidence = {}
        for s in verified:
            conf_range = self._get_confidence_range(s['confidence'])
            if conf_range not in by_confidence:
                by_confidence[conf_range] = {'wins': 0, 'total': 0}
            
            by_confidence[conf_range]['total'] += 1
            if s['result'] == 'WIN':
                by_confidence[conf_range]['wins'] += 1
        
        data['stats'] = {
            'total_verified': len(verified),
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 3),
            'win_rate_pct': f"{win_rate * 100:.1f}%",
            'by_confidence': by_confidence,
            'last_updated': datetime.now().isoformat()
        }
        
        self._save_db(data)
    
    def _get_confidence_range(self, conf: float) -> str:
        """Agrupa confiança em ranges"""
        if conf >= 0.90:
            return '90-100%'
        elif conf >= 0.80:
            return '80-90%'
        elif conf >= 0.70:
            return '70-80%'
        else:
            return '< 70%'
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de acertos"""
        data = self._load_db()
        return data.get('stats', {})
    
    def get_pending_signals(self) -> List[Dict]:
        """Retorna sinais sem resultado registrado"""
        data = self._load_db()
        return [s for s in data['signals'] if s['result'] is None]
    
    def export_to_csv(self, output_path='data/results_export.csv'):
        """Exporta histórico para CSV"""
        data = self._load_db()
        df = pd.DataFrame(data['signals'])
        df.to_csv(output_path, index=False)
        return output_path
    
    def _load_db(self) -> Dict:
        with open(self.db_path, 'r') as f:
            return json.load(f)
    
    def _save_db(self, data: Dict):
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)