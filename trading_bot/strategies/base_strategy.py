from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
from ..config.settings import settings

class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.parameters = {}
        self.indicators = {}
        self.setup_parameters()

    @abstractmethod
    def setup_parameters(self):
        """Setup strategy-specific parameters."""
        pass

    @abstractmethod
    def analyze(self, df: pd.DataFrame, indicators: Dict) -> Dict:
        """
        Analyze market data and indicators to generate trading signals.
        
        Args:
            df: DataFrame with OHLCV data
            indicators: Dictionary containing technical indicators
            
        Returns:
            Dictionary containing analysis results
        """
        pass

    def validate_indicators(self, required_indicators: List[str]) -> bool:
        """
        Validate that all required indicators are present.
        
        Args:
            required_indicators: List of required indicator names
            
        Returns:
            Boolean indicating if all required indicators are present
        """
        return all(indicator in self.indicators for indicator in required_indicators)

    def calculate_risk_parameters(
        self,
        entry_price: float,
        atr: float,
        risk_reward_ratio: float = settings.RISK_REWARD_RATIO
    ) -> Dict[str, float]:
        """
        Calculate risk parameters based on ATR and risk-reward ratio.
        
        Args:
            entry_price: Entry price
            atr: Average True Range value
            risk_reward_ratio: Desired risk-reward ratio
            
        Returns:
            Dictionary containing stop loss and take profit levels
        """
        # Use ATR for stop loss distance
        stop_loss_distance = atr * 1.5
        
        # Calculate stop loss and take profit levels
        stop_loss = entry_price - stop_loss_distance
        take_profit = entry_price + (stop_loss_distance * risk_reward_ratio)
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward_ratio': risk_reward_ratio
        }

    def get_strategy_info(self) -> Dict:
        """
        Get strategy information and parameters.
        
        Returns:
            Dictionary containing strategy information
        """
        return {
            'name': self.name,
            'parameters': self.parameters,
            'required_indicators': self.get_required_indicators()
        }

    @abstractmethod
    def get_required_indicators(self) -> List[str]:
        """
        Get list of required indicators for the strategy.
        
        Returns:
            List of required indicator names
        """
        pass 