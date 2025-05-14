from binance.client import Client
from binance.exceptions import BinanceAPIException
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging
from ..config.settings import settings

logger = logging.getLogger(__name__)

class BinanceConnector:
    def __init__(self):
        self.client = None
        self.initialize_client()

    def initialize_client(self):
        """Initialize the Binance client with API credentials."""
        try:
            self.client = Client(
                settings.BINANCE_API_KEY,
                settings.BINANCE_API_SECRET
            )
            logger.info("Successfully connected to Binance API")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {str(e)}")
            raise

    def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 500,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch kline/candlestick data for a given symbol and interval.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (e.g., '1m', '5m', '1h')
            limit: Number of klines to fetch
            start_time: Start time for historical data
            end_time: End time for historical data
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            klines = self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                startTime=int(start_time.timestamp() * 1000) if start_time else None,
                endTime=int(end_time.timestamp() * 1000) if end_time else None
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Convert string values to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
                
            return df
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error while fetching klines: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching klines: {str(e)}")
            raise

    def get_ticker_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error fetching ticker price: {str(e)}")
            raise

    def get_account_balance(self) -> Dict:
        """Get account balance information."""
        try:
            account = self.client.futures_account()
            return {
                'total_balance': float(account['totalWalletBalance']),
                'unrealized_pnl': float(account['totalUnrealizedProfit']),
                'available_balance': float(account['availableBalance'])
            }
        except Exception as e:
            logger.error(f"Error fetching account balance: {str(e)}")
            raise

    def get_position_info(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get position information for all or specific symbol."""
        try:
            positions = self.client.futures_position_information(symbol=symbol) if symbol else self.client.futures_position_information()
            return positions
        except Exception as e:
            logger.error(f"Error fetching position information: {str(e)}")
            raise

    def get_exchange_info(self) -> Dict:
        """Get exchange information including trading rules."""
        try:
            return self.client.futures_exchange_info()
        except Exception as e:
            logger.error(f"Error fetching exchange info: {str(e)}")
            raise 