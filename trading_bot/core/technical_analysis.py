import pandas as pd
import numpy as np
import sys
import os

# Add TA-Lib to Python path
ta_lib_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ta-lib-python-master')
sys.path.append(ta_lib_path)

import talib
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator, IchimokuIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice, OnBalanceVolumeIndicator
from typing import Dict, List, Optional, Union
import logging
from ..config.settings import settings

logger = logging.getLogger(__name__)

class TechnicalAnalysis:
    def __init__(self):
        """Initialize the technical analysis engine."""
        self.indicators = {}

    def calculate_indicators(self, df: pd.DataFrame) -> dict:
        """
        Calculate technical indicators for the given DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame with OHLCV data
            
        Returns:
            dict: Dictionary containing calculated indicators organized by category
        """
        try:
            # Ensure required columns exist
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"DataFrame must contain columns: {required_columns}")

            # Initialize indicators dictionary with categories
            indicators = {
                'trend': {},
                'momentum': {},
                'volatility': {},
                'volume': {},
                'patterns': {}
            }
            
            # Trend Indicators
            # SMA
            sma_20 = SMAIndicator(close=df['close'], window=20)
            sma_50 = SMAIndicator(close=df['close'], window=50)
            sma_200 = SMAIndicator(close=df['close'], window=200)
            indicators['trend']['sma_20'] = sma_20.sma_indicator()
            indicators['trend']['sma_50'] = sma_50.sma_indicator()
            indicators['trend']['sma_200'] = sma_200.sma_indicator()
            
            # EMA
            ema_12 = EMAIndicator(close=df['close'], window=12)
            ema_26 = EMAIndicator(close=df['close'], window=26)
            ema_50 = EMAIndicator(close=df['close'], window=50)
            indicators['trend']['ema_12'] = ema_12.ema_indicator()
            indicators['trend']['ema_26'] = ema_26.ema_indicator()
            indicators['trend']['ema_50'] = ema_50.ema_indicator()
            
            # ADX
            adx = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
            indicators['trend']['adx'] = adx.adx()
            indicators['trend']['di_plus'] = adx.adx_pos()
            indicators['trend']['di_minus'] = adx.adx_neg()
            
            # Momentum Indicators
            # RSI
            rsi = RSIIndicator(close=df['close'], window=14)
            indicators['momentum']['rsi'] = rsi.rsi()
            
            # MACD
            macd = MACD(close=df['close'])
            indicators['momentum']['macd'] = macd.macd()
            indicators['momentum']['macd_signal'] = macd.macd_signal()
            indicators['momentum']['macd_diff'] = macd.macd_diff()
            
            # Stochastic
            stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
            indicators['momentum']['stoch_k'] = stoch.stoch()
            indicators['momentum']['stoch_d'] = stoch.stoch_signal()
            
            # Williams %R
            willr = WilliamsRIndicator(high=df['high'], low=df['low'], close=df['close'])
            indicators['momentum']['willr'] = willr.williams_r()
            
            # Volatility Indicators
            # Bollinger Bands
            bb = BollingerBands(close=df['close'], window=20, window_dev=2)
            indicators['volatility']['bb_upper'] = bb.bollinger_hband()
            indicators['volatility']['bb_middle'] = bb.bollinger_mavg()
            indicators['volatility']['bb_lower'] = bb.bollinger_lband()
            
            # ATR
            atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
            indicators['volatility']['atr'] = atr.average_true_range()
            
            # Volume Indicators
            # VWAP
            vwap = VolumeWeightedAveragePrice(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                volume=df['volume']
            )
            indicators['volume']['vwap'] = vwap.volume_weighted_average_price()
            
            # OBV
            obv = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume'])
            indicators['volume']['obv'] = obv.on_balance_volume()
            
            # Initialize patterns with zeros (placeholder for now)
            indicators['patterns'] = {
                'doji': pd.Series(0, index=df.index),
                'hammer': pd.Series(0, index=df.index),
                'engulfing': pd.Series(0, index=df.index)
            }
            
            return indicators
            
        except Exception as e:
            raise Exception(f"Error calculating indicators: {str(e)}")

    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Calculate all technical indicators for the given DataFrame.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary containing all calculated indicators
        """
        try:
            # Calculate indicators
            self.indicators = {
                'trend': self._calculate_trend_indicators(df),
                'momentum': self._calculate_momentum_indicators(df),
                'volatility': self._calculate_volatility_indicators(df),
                'volume': self._calculate_volume_indicators(df),
                'patterns': self._detect_candlestick_patterns(df)
            }
            
            return self.indicators
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
            raise

    def _calculate_trend_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate trend indicators."""
        indicators = {}
        
        # Moving Averages
        for period in settings.TA_INDICATORS['SMA']['periods']:
            indicators[f'SMA_{period}'] = talib.SMA(df['close'], timeperiod=period)
            indicators[f'EMA_{period}'] = talib.EMA(df['close'], timeperiod=period)
        
        # Ichimoku Cloud
        high_9 = df['high'].rolling(window=9).max()
        low_9 = df['low'].rolling(window=9).min()
        indicators['tenkan_sen'] = (high_9 + low_9) / 2
        
        high_26 = df['high'].rolling(window=26).max()
        low_26 = df['low'].rolling(window=26).min()
        indicators['kijun_sen'] = (high_26 + low_26) / 2
        
        indicators['senkou_span_a'] = ((indicators['tenkan_sen'] + indicators['kijun_sen']) / 2).shift(26)
        
        high_52 = df['high'].rolling(window=52).max()
        low_52 = df['low'].rolling(window=52).min()
        indicators['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)
        
        # ADX
        indicators['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
        indicators['DI_plus'] = talib.PLUS_DI(df['high'], df['low'], df['close'], timeperiod=14)
        indicators['DI_minus'] = talib.MINUS_DI(df['high'], df['low'], df['close'], timeperiod=14)
        
        return indicators

    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate momentum indicators."""
        indicators = {}
        
        # RSI
        indicators['RSI'] = talib.RSI(df['close'], timeperiod=settings.TA_INDICATORS['RSI']['period'])
        
        # Stochastic
        indicators['slowk'], indicators['slowd'] = talib.STOCH(
            df['high'], df['low'], df['close'],
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0
        )
        
        # MACD
        macd, macd_signal, macd_hist = talib.MACD(
            df['close'],
            fastperiod=settings.TA_INDICATORS['MACD']['fast'],
            slowperiod=settings.TA_INDICATORS['MACD']['slow'],
            signalperiod=settings.TA_INDICATORS['MACD']['signal']
        )
        indicators['MACD'] = macd
        indicators['MACD_signal'] = macd_signal
        indicators['MACD_hist'] = macd_hist
        
        # CCI
        indicators['CCI'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)
        
        # Williams %R
        indicators['WILLR'] = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=14)
        
        return indicators

    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate volatility indicators."""
        indicators = {}
        
        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(
            df['close'],
            timeperiod=settings.TA_INDICATORS['BB']['period'],
            nbdevup=settings.TA_INDICATORS['BB']['std_dev'],
            nbdevdn=settings.TA_INDICATORS['BB']['std_dev']
        )
        indicators['BB_upper'] = upper
        indicators['BB_middle'] = middle
        indicators['BB_lower'] = lower
        
        # ATR
        indicators['ATR'] = talib.ATR(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=settings.TA_INDICATORS['ATR']['period']
        )
        
        # Keltner Channels
        atr = indicators['ATR']
        indicators['KC_upper'] = middle + (2 * atr)
        indicators['KC_lower'] = middle - (2 * atr)
        
        return indicators

    def _calculate_volume_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate volume indicators."""
        indicators = {}
        
        # On-Balance Volume (OBV)
        indicators['OBV'] = talib.OBV(df['close'], df['volume'])
        
        # Volume SMA
        indicators['Volume_SMA'] = talib.SMA(df['volume'], timeperiod=20)
        
        return indicators

    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Detect candlestick patterns."""
        patterns = {}
        
        # Single candlestick patterns
        patterns['DOJI'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
        patterns['HAMMER'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])
        patterns['HANGING_MAN'] = talib.CDLHANGINGMAN(df['open'], df['high'], df['low'], df['close'])
        
        # Multiple candlestick patterns
        patterns['ENGULFING'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
        patterns['MORNING_STAR'] = talib.CDLMORNINGSTAR(df['open'], df['high'], df['low'], df['close'])
        patterns['EVENING_STAR'] = talib.CDLEVENINGSTAR(df['open'], df['high'], df['low'], df['close'])
        patterns['THREE_WHITE_SOLDIERS'] = talib.CDL3WHITESOLDIERS(df['open'], df['high'], df['low'], df['close'])
        patterns['THREE_BLACK_CROWS'] = talib.CDL3BLACKCROWS(df['open'], df['high'], df['low'], df['close'])
        
        return patterns

    def get_support_resistance_levels(self, df: pd.DataFrame, window: int = 20) -> Dict[str, List[float]]:
        """
        Identify potential support and resistance levels using local minima and maxima.
        
        Args:
            df: DataFrame with OHLCV data
            window: Window size for identifying local extrema
            
        Returns:
            Dictionary containing support and resistance levels
        """
        try:
            # Find local minima and maxima
            df['min'] = df['low'].rolling(window=window, center=True).min()
            df['max'] = df['high'].rolling(window=window, center=True).max()
            
            # Identify support levels (local minima)
            support_levels = df[df['low'] == df['min']]['low'].unique().tolist()
            
            # Identify resistance levels (local maxima)
            resistance_levels = df[df['high'] == df['max']]['high'].unique().tolist()
            
            return {
                'support': sorted(support_levels),
                'resistance': sorted(resistance_levels)
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance levels: {str(e)}")
            raise 