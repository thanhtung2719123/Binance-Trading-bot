import logging
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from trading_bot.core.binance_connector import BinanceConnector
from trading_bot.core.technical_analysis import TechnicalAnalysis
from trading_bot.ai.gemini_interface import GeminiInterface
from trading_bot.ui.cli import TradingBotCLI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        """Initialize the trading bot components."""
        self.binance = BinanceConnector()
        self.technical_analysis = TechnicalAnalysis()
        self.gemini = GeminiInterface()
        self.cli = TradingBotCLI()
        
        # Initialize CLI components
        self.cli.binance = self.binance
        self.cli.technical_analysis = self.technical_analysis
        self.cli.gemini = self.gemini
        
        self.scheduler = BackgroundScheduler()
        self.active_strategy = None
        self.monitored_pairs = []

    def initialize(self):
        """Initialize the bot and start the scheduler."""
        try:
            # Start the scheduler
            self.scheduler.start()
            
            # Schedule market data updates
            self.scheduler.add_job(
                self.update_market_data,
                trigger=IntervalTrigger(minutes=1),
                id='market_data_update',
                replace_existing=True
            )
            
            logger.info("Trading bot initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing trading bot: {str(e)}")
            raise

    def update_market_data(self):
        """Update market data and generate trade suggestions."""
        try:
            # Default timeframe for automatic updates
            interval = "1h"
            
            for symbol in self.monitored_pairs:
                # Get latest market data
                klines = self.binance.get_klines(symbol, interval=interval)
                if klines is None:
                    continue

                # Calculate technical indicators
                df = pd.DataFrame(klines)
                indicators = self.technical_analysis.calculate_indicators(df)
                
                # Get AI suggestions if strategy is active
                if self.active_strategy:
                    suggestion = self.gemini.get_trade_suggestion(
                        symbol=symbol,
                        timeframe=interval,
                        market_data=self.gemini.prepare_market_data(df, indicators),
                        strategy=self.active_strategy
                    )
                    if suggestion:
                        logger.info(f"Trade suggestion for {symbol}: {suggestion}")
                        self.cli.display_trade_suggestion(suggestion)
        except Exception as e:
            logger.error(f"Error updating market data: {str(e)}")

    def run(self):
        """Run the trading bot."""
        try:
            self.initialize()
            self.cli.run()
        except KeyboardInterrupt:
            logger.info("Trading bot stopped by user")
        except Exception as e:
            logger.error(f"Error running trading bot: {str(e)}")
        finally:
            self.scheduler.shutdown()

if __name__ == "__main__":
    bot = TradingBot()
    bot.run() 