"""
Módulo para gerenciamento do bot do Telegram
"""
import os
import logging
from telegram import Bot
from telegram.error import TelegramError
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramBotManager:
    """Gerenciador do bot do Telegram para envio de sinais"""

    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        self.bot = None

        if self.token:
            try:
                self.bot = Bot(token=self.token)
                logger.info("[OK] Bot do Telegram inicializado")
            except Exception as e:
                logger.error(f"[ERRO] Erro ao inicializar bot: {str(e)}")
        else:
            logger.warning("[!] Token do Telegram nao configurado")

    async def send_signal_async(self, signal):
        """Envia sinal de forma assíncrona"""
        if not self.bot or not self.channel_id:
            logger.warning("[!] Bot ou canal nao configurado")
            return False

        try:
            message = self.format_signal_message(signal)
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            logger.info(f"[*] Sinal enviado para Telegram: {signal['signal']}")
            return True

        except TelegramError as e:
            logger.error(f"[ERRO] Erro ao enviar para Telegram: {str(e)}")
            return False

    def send_signals(self, signals):
        """Envia lista de sinais para o Telegram"""
        if not signals:
            logger.info("[*] Nenhum sinal para enviar")
            return

        successful_sends = 0

        for signal in signals:
            # Garantir que signal é um dict com campos esperados
            if not isinstance(signal, dict):
                logger.warning(f"[!] Sinal ignorado (formato inválido): {type(signal)}")
                continue

            # Normalizar campos obrigatórios com valores padrão
            signal.setdefault('game', 'Double')
            signal.setdefault('signal', 'Unknown')
            signal.setdefault('message', '')
            signal.setdefault('confidence', 0.0)
            signal.setdefault('timestamp', datetime.now())

            # Filtra sinais com confiança mínima
            try:
                conf_val = float(signal.get('confidence', 0))
            except Exception:
                conf_val = 0.0

            if conf_val >= 0.65:
                try:
                    # Executar método async de forma síncrona
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    message = self.format_signal_message(signal)
                    loop.run_until_complete(
                        self.bot.send_message(
                            chat_id=self.channel_id,
                            text=message,
                            parse_mode='HTML',
                            disable_web_page_preview=True
                        )
                    )
                    loop.close()
                    
                    logger.info(f"[*] Sinal enviado para Telegram: {signal.get('signal')}")

                    successful_sends += 1
                    import time
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"[ERRO] Erro ao enviar para Telegram: {str(e)}")

        logger.info(f"[*] Total de sinais enviados: {successful_sends}/{len(signals)}")

    def format_signal_message(self, signal):
        """Formata mensagem do sinal para Telegram com diferenciação por jogo"""
        game = signal.get('game', 'Double')
        
        # Diferenciar por jogo
        if game == 'Crash':
            return self._format_crash_signal(signal)
        else:
            return self._format_double_signal(signal)
    
    def _format_crash_signal(self, signal):
        """Formata mensagem específica para Crash"""
        confidence = signal.get('confidence', 0)
        confidence_text = self._get_confidence_level(confidence)
        strategies = signal.get('strategies_passed', 0)
        timestamp = signal.get('timestamp', datetime.now())
        
        # Emoji baseado no tipo de sinal
        signal_emoji = "🔴" if signal['signal'] == 'Vermelho' else "⚫" if signal['signal'] == 'Preto' else "⚪"
        confidence_emoji = "🔥" if confidence >= 0.85 else "✅" if confidence >= 0.75 else "⚠️"
        
        message = f"""
╔════════════════════════════════════════╗
║     🎮 ALERTA DE SINAL - CRASH 🎮      ║
╚════════════════════════════════════════╝

{signal_emoji} <b>PREVISÃO:</b> {signal['signal']}

<b>📊 ANÁLISE:</b>
   Confiança: {confidence_emoji} <b>{confidence_text}</b> ({confidence:.1%})
   Estratégias: <b>{strategies}/6</b> validadas
   Multiplicador esperado: <b>1.5x - 2.5x</b>

<b>⏰ TIMING:</b>
   Horário: {timestamp.strftime('%H:%M:%S')}
   Data: {timestamp.strftime('%d/%m/%Y')}

<b>💡 RECOMENDAÇÃO:</b>
   • Comece com aposta pequena
   • Controle seu risco
   • Máximo {self._get_bet_recommendation(confidence)} de seu bankroll

<b>⚠️ DISCLAIMER:</b>
<i>Apostas envolvem risco alto. Jogue responsavelmente.</i>
"""
        return message.strip()
    
    def _format_double_signal(self, signal):
        """Formata mensagem específica para Double"""
        confidence = signal.get('confidence', 0)
        confidence_text = self._get_confidence_level(confidence)
        strategies = signal.get('strategies_passed', 0)
        timestamp = signal.get('timestamp', datetime.now())
        
        # Emoji baseado no tipo de sinal
        signal_emoji = "🔴" if signal['signal'] == 'Vermelho' else "⚫" if signal['signal'] == 'Preto' else "⚪"
        confidence_emoji = "🔥" if confidence >= 0.85 else "✅" if confidence >= 0.75 else "⚠️"
        
        # Odds do Double
        odds_text = "1.90x" if signal['signal'] in ['Vermelho', 'Preto'] else "14.00x" if signal['signal'] == 'Branco' else "1.90x"
        
        message = f"""
╔════════════════════════════════════════╗
║    🎲 ALERTA DE SINAL - DOUBLE 🎲      ║
╚════════════════════════════════════════╝

{signal_emoji} <b>PREVISÃO:</b> {signal['signal']}

<b>📊 ANÁLISE:</b>
   Confiança: {confidence_emoji} <b>{confidence_text}</b> ({confidence:.1%})
   Estratégias: <b>{strategies}/6</b> validadas
   Odds da aposta: <b>{odds_text}</b>

<b>⏰ TIMING:</b>
   Horário: {timestamp.strftime('%H:%M:%S')}
   Data: {timestamp.strftime('%d/%m/%Y')}

<b>💡 RECOMENDAÇÃO:</b>
   • Cores têm odds de 1.90x
   • Branco paga 14.00x (risco maior)
   • Máximo {self._get_bet_recommendation(confidence)} de seu bankroll

<b>⚠️ DISCLAIMER:</b>
<i>Apostas envolvem risco. Jogue responsavelmente.</i>
"""
        return message.strip()
    
    def _get_confidence_level(self, confidence):
        """Converte confiança em nível descritivo"""
        if confidence >= 0.90:
            return "MUITO ALTA"
        elif confidence >= 0.80:
            return "ALTA"
        elif confidence >= 0.70:
            return "MÉDIA"
        elif confidence >= 0.60:
            return "MODERADA"
        else:
            return "BAIXA"
    
    def _get_bet_recommendation(self, confidence):
        """Recomenda % do bankroll baseado na confiança"""
        if confidence >= 0.90:
            return "5%"
        elif confidence >= 0.80:
            return "4%"
        elif confidence >= 0.70:
            return "3%"
        elif confidence >= 0.60:
            return "2%"
        else:
            return "1%"

    async def test_connection(self):
        """Testa conexão com o Telegram"""
        if not self.bot or not self.channel_id:
            return False

        try:
            chat = await self.bot.get_chat(self.channel_id)
            logger.info(f"[OK] Conexao testada com sucesso: {chat.title}")
            return True
        except TelegramError as e:
            logger.error(f"[ERRO] Erro ao testar conexao: {str(e)}")
            return False