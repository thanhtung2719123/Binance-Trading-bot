from typing import Dict, List
import pandas as pd
from .base_strategy import BaseStrategy

class DynamicTrendRider(BaseStrategy):
    def __init__(self):
        super().__init__("Dynamic Trend Rider")
        
    def setup_parameters(self):
        self.parameters = {
            'ema_fast': 12,
            'ema_slow': 26,
            'adx_threshold': 25,
            'rsi_oversold': 30,
            'rsi_overbought': 70
        }
        
    def get_required_indicators(self) -> List[str]:
        return [
            'EMA_12', 'EMA_26',
            'ADX', 'DI_plus', 'DI_minus',
            'RSI'
        ]
        
    def analyze(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        # Get indicator values
        ema_fast = indicators['trend']['EMA_12']
        ema_slow = indicators['trend']['EMA_26']
        adx = indicators['trend']['ADX']
        di_plus = indicators['trend']['DI_plus']
        di_minus = indicators['trend']['DI_minus']
        rsi = indicators['momentum']['RSI']
        
        # Get latest values
        current_ema_fast = ema_fast.iloc[-1]
        current_ema_slow = ema_slow.iloc[-1]
        current_adx = adx.iloc[-1]
        current_di_plus = di_plus.iloc[-1]
        current_di_minus = di_minus.iloc[-1]
        current_rsi = rsi.iloc[-1]
        
        # Analyze trend
        trend_strength = current_adx > self.parameters['adx_threshold']
        trend_direction = current_di_plus > current_di_minus
        
        # Generate signal
        signal = "NONE"
        if trend_strength:
            if trend_direction and current_rsi < self.parameters['rsi_oversold']:
                signal = "BUY"
            elif not trend_direction and current_rsi > self.parameters['rsi_overbought']:
                signal = "SELL"
        
        return {
            'signal': signal,
            'trend_strength': trend_strength,
            'trend_direction': 'UP' if trend_direction else 'DOWN',
            'rsi': current_rsi
        }

class VolatilityBreakoutPro(BaseStrategy):
    def __init__(self):
        super().__init__("Volatility Breakout Pro")
        
    def setup_parameters(self):
        self.parameters = {
            'bb_period': 20,
            'bb_std_dev': 2,
            'atr_period': 14,
            'volume_threshold': 1.5  # Volume should be 1.5x average
        }
        
    def get_required_indicators(self) -> List[str]:
        return [
            'BB_upper', 'BB_middle', 'BB_lower',
            'ATR',
            'Volume_SMA'
        ]
        
    def analyze(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        # Get indicator values
        bb_upper = indicators['volatility']['BB_upper']
        bb_lower = indicators['volatility']['BB_lower']
        atr = indicators['volatility']['ATR']
        volume_sma = indicators['volume']['Volume_SMA']
        
        # Get latest values
        current_price = df['close'].iloc[-1]
        current_bb_upper = bb_upper.iloc[-1]
        current_bb_lower = bb_lower.iloc[-1]
        current_atr = atr.iloc[-1]
        current_volume = df['volume'].iloc[-1]
        current_volume_sma = volume_sma.iloc[-1]
        
        # Check for breakout
        price_range = current_bb_upper - current_bb_lower
        volatility = current_atr / current_price
        
        # Generate signal
        signal = "NONE"
        if current_volume > current_volume_sma * self.parameters['volume_threshold']:
            if current_price > current_bb_upper:
                signal = "BUY"
            elif current_price < current_bb_lower:
                signal = "SELL"
        
        return {
            'signal': signal,
            'volatility': volatility,
            'price_range': price_range,
            'volume_ratio': current_volume / current_volume_sma
        }

class MeanReversionAI(BaseStrategy):
    def __init__(self):
        super().__init__("Mean Reversion AI")
        
    def setup_parameters(self):
        self.parameters = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'bb_period': 20,
            'bb_std_dev': 2
        }
        
    def get_required_indicators(self) -> List[str]:
        return [
            'RSI',
            'BB_upper', 'BB_middle', 'BB_lower'
        ]
        
    def analyze(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        # Get indicator values
        rsi = indicators['momentum']['RSI']
        bb_upper = indicators['volatility']['BB_upper']
        bb_middle = indicators['volatility']['BB_middle']
        bb_lower = indicators['volatility']['BB_lower']
        
        # Get latest values
        current_price = df['close'].iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_bb_upper = bb_upper.iloc[-1]
        current_bb_middle = bb_middle.iloc[-1]
        current_bb_lower = bb_lower.iloc[-1]
        
        # Check for mean reversion signals
        price_to_mean = (current_price - current_bb_middle) / current_bb_middle
        
        # Generate signal
        signal = "NONE"
        if current_rsi < self.parameters['rsi_oversold'] and current_price < current_bb_lower:
            signal = "BUY"
        elif current_rsi > self.parameters['rsi_overbought'] and current_price > current_bb_upper:
            signal = "SELL"
        
        return {
            'signal': signal,
            'rsi': current_rsi,
            'price_to_mean': price_to_mean,
            'bb_position': (current_price - current_bb_lower) / (current_bb_upper - current_bb_lower)
        }

class ScalpersEdgeAI(BaseStrategy):
    def __init__(self):
        super().__init__("Scalper's Edge AI")
        
    def setup_parameters(self):
        self.parameters = {
            'ema_fast': 8,
            'ema_slow': 21,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'volume_threshold': 1.2
        }
        
    def get_required_indicators(self) -> List[str]:
        return [
            'EMA_8', 'EMA_21',
            'RSI',
            'Volume_SMA'
        ]
        
    def analyze(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        # Get indicator values
        ema_fast = indicators['trend']['EMA_8']
        ema_slow = indicators['trend']['EMA_21']
        rsi = indicators['momentum']['RSI']
        volume_sma = indicators['volume']['Volume_SMA']
        
        # Get latest values
        current_price = df['close'].iloc[-1]
        current_ema_fast = ema_fast.iloc[-1]
        current_ema_slow = ema_slow.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_volume = df['volume'].iloc[-1]
        current_volume_sma = volume_sma.iloc[-1]
        
        # Check for scalping opportunities
        ema_cross = current_ema_fast > current_ema_slow
        volume_surge = current_volume > current_volume_sma * self.parameters['volume_threshold']
        
        # Generate signal
        signal = "NONE"
        if volume_surge:
            if ema_cross and current_rsi < self.parameters['rsi_oversold']:
                signal = "BUY"
            elif not ema_cross and current_rsi > self.parameters['rsi_overbought']:
                signal = "SELL"
        
        return {
            'signal': signal,
            'ema_cross': ema_cross,
            'volume_ratio': current_volume / current_volume_sma,
            'rsi': current_rsi
        }

# Strategy factory
def get_strategy(strategy_name: str) -> BaseStrategy:
    """
    Get strategy instance by name.
    
    Args:
        strategy_name: Name of the strategy
        
    Returns:
        Strategy instance
    """
    strategies = {
        "Dynamic Trend Rider": DynamicTrendRider,
        "Volatility Breakout Pro": VolatilityBreakoutPro,
        "Mean Reversion AI": MeanReversionAI,
        "Scalper's Edge AI": ScalpersEdgeAI
    }
    
    if strategy_name not in strategies:
        raise ValueError(f"Strategy '{strategy_name}' not found")
        
    return strategies[strategy_name]() 