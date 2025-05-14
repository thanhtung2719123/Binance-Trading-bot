from pydantic_settings import BaseSettings
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Trading Parameters
    DEFAULT_TIMEFRAMES: List[str] = ["1m", "5m", "15m", "1h", "4h", "1d"]
    DEFAULT_TRADING_PAIRS: List[str] = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"
    ]
    
    # Technical Analysis Parameters
    TA_INDICATORS: Dict[str, Dict] = {
        "SMA": {"periods": [20, 50, 200]},
        "EMA": {"periods": [12, 26, 50]},
        "RSI": {"period": 14},
        "MACD": {"fast": 12, "slow": 26, "signal": 9},
        "BB": {"period": 20, "std_dev": 2},
        "ATR": {"period": 14}
    }

    # Strategy Parameters
    DEFAULT_STRATEGY: str = "Dynamic Trend Rider"
    RISK_REWARD_RATIO: float = 2.0
    MAX_STOP_LOSS_PERCENTAGE: float = 2.0

    # AI Model Parameters
    GEMINI_MODEL_NAME: str = "gemini-1.5-flash"
    AI_CONFIDENCE_THRESHOLD: float = 0.7

    class Config:
        env_file = ".env"

settings = Settings() 