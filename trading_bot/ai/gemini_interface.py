import google.generativeai as genai
from typing import Dict, List, Optional, Union
import pandas as pd
import json
import logging
from ..config.settings import settings

logger = logging.getLogger(__name__)

class GeminiInterface:
    def __init__(self):
        self.model = None
        self.initialize_model()

    def initialize_model(self):
        """Initialize the Gemini model with API key."""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
            logger.info("Successfully initialized Gemini model")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise

    def prepare_market_data(self, df: pd.DataFrame, indicators: Dict) -> str:
        """
        Prepare market data and indicators for the AI model.
        
        Args:
            df: DataFrame with OHLCV data
            indicators: Dictionary containing technical indicators
            
        Returns:
            Formatted string containing market data and indicators
        """
        try:
            # Get the last few candles for context
            recent_data = df.tail(5).copy()
            
            # Convert timestamp to string
            recent_data['timestamp'] = recent_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert to dict and ensure all values are JSON serializable
            recent_data_dict = recent_data.to_dict('records')
            
            # Format the data
            market_context = {
                'recent_candles': recent_data_dict,
                'current_price': float(df['close'].iloc[-1]),
                'indicators': {
                    'trend': {k: float(v.iloc[-1]) if not pd.isna(v.iloc[-1]) else None for k, v in indicators['trend'].items()},
                    'momentum': {k: float(v.iloc[-1]) if not pd.isna(v.iloc[-1]) else None for k, v in indicators['momentum'].items()},
                    'volatility': {k: float(v.iloc[-1]) if not pd.isna(v.iloc[-1]) else None for k, v in indicators['volatility'].items()},
                    'volume': {k: float(v.iloc[-1]) if not pd.isna(v.iloc[-1]) else None for k, v in indicators['volume'].items()},
                    'patterns': {k: int(v.iloc[-1]) if not pd.isna(v.iloc[-1]) else 0 for k, v in indicators['patterns'].items()}
                }
            }
            
            return json.dumps(market_context, indent=2)
            
        except Exception as e:
            logger.error(f"Error preparing market data: {str(e)}")
            raise

    def get_trade_suggestion(
        self,
        symbol: str,
        timeframe: str,
        market_data: str,
        strategy: str
    ) -> Dict:
        """
        Get trade suggestion from the AI model.
        
        Args:
            symbol: Trading pair symbol
            timeframe: Trading timeframe
            market_data: Formatted market data string
            strategy: Selected trading strategy
            
        Returns:
            Dictionary containing trade suggestion
        """
        try:
            # Prepare the prompt with explicit JSON formatting instructions
            prompt = f"""
            You are a trading bot AI assistant. Analyze the following market data for {symbol} on {timeframe} timeframe using the {strategy} strategy.
            
            Market Data:
            {market_data}
            
            Provide your analysis in the following JSON format ONLY. Do not include any other text or explanation outside the JSON:
            {{
                "trading_pair": "{symbol}",
                "timeframe": "{timeframe}",
                "strategy": "{strategy}",
                "signal": "BUY/SELL/NONE",
                "entry_price": <current_price>,
                "stop_loss": <float>,
                "take_profit_levels": [<float>, <float>, <float>],
                "confidence_score": <float between 0 and 1>,
                "rationale": "<brief explanation of the analysis>"
            }}

            Important:
            1. Return ONLY the JSON object, no other text
            2. Ensure all numeric values are actual numbers, not strings
            3. Keep the rationale concise and focused on key technical factors
            4. Use the current price as the entry price
            5. Calculate stop loss and take profit levels based on the strategy
            """
            
            # Get response from the model
            response = self.model.generate_content(prompt)
            
            # Extract the response text and clean it
            response_text = response.text.strip()
            
            # Try to find JSON content if there's any surrounding text
            try:
                # First try direct JSON parsing
                suggestion = json.loads(response_text)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the text
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    suggestion = json.loads(json_match.group())
                else:
                    logger.error(f"Failed to extract JSON from response: {response_text}")
                    raise ValueError("Could not parse model response as JSON")
            
            # Validate the suggestion
            if not self.validate_suggestion(suggestion):
                raise ValueError("Invalid suggestion format")
                
            return suggestion
                
        except Exception as e:
            logger.error(f"Error getting trade suggestion: {str(e)}")
            raise

    def validate_suggestion(self, suggestion: Dict) -> bool:
        """
        Validate the trade suggestion from the AI model.
        
        Args:
            suggestion: Dictionary containing trade suggestion
            
        Returns:
            Boolean indicating if the suggestion is valid
        """
        try:
            required_fields = [
                'trading_pair', 'timeframe', 'strategy', 'signal',
                'entry_price', 'stop_loss', 'take_profit_levels',
                'confidence_score', 'rationale'
            ]
            
            # Check if all required fields are present
            if not all(field in suggestion for field in required_fields):
                return False
            
            # Validate signal
            if suggestion['signal'] not in ['BUY', 'SELL', 'NONE']:
                return False
            
            # Validate confidence score
            if not 0 <= suggestion['confidence_score'] <= 1:
                return False
            
            # Validate take profit levels
            if not isinstance(suggestion['take_profit_levels'], list) or len(suggestion['take_profit_levels']) != 3:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating suggestion: {str(e)}")
            return False 