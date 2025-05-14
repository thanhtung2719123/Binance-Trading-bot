import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint
from typing import Optional, List
import logging
import pandas as pd

logger = logging.getLogger(__name__)
console = Console()

class TradingBotCLI:
    def __init__(self):
        """Initialize the CLI interface."""
        self.console = Console()
        self.monitored_pairs = []
        self.active_strategy = None
        self.binance = None
        self.technical_analysis = None
        self.gemini = None

    def display_welcome(self):
        """Display welcome message and menu."""
        self.console.print(Panel.fit(
            "[bold blue]VTT Trading Bot[/bold blue]\n"
            "[italic]Your AI-Powered Trading Assistant[/italic]",
            title="Welcome",
            border_style="blue"
        ))

    def display_menu(self) -> str:
        """Display main menu and get user choice."""
        menu_text = """
        [bold]Main Menu:[/bold]
        1. Manage Trading Strategies
        2. View Trade Suggestions
        3. Manage Monitored Pairs
        4. Exit
        """
        self.console.print(Panel(menu_text, title="Menu", border_style="green"))
        return Prompt.ask("Select an option", choices=["1", "2", "3", "4"])

    def configure_api_keys(self):
        """Configure Binance and Gemini API keys."""
        self.console.print("\n[bold]Configure API Keys[/bold]")
        
        # Binance API Key
        binance_key = Prompt.ask("Enter your Binance API Key")
        binance_secret = Prompt.ask("Enter your Binance API Secret", password=True)
        
        # Gemini API Key
        gemini_key = Prompt.ask("Enter your Gemini API Key")
        
        # Save to .env file
        with open(".env", "w") as f:
            f.write(f"BINANCE_API_KEY={binance_key}\n")
            f.write(f"BINANCE_API_SECRET={binance_secret}\n")
            f.write(f"GEMINI_API_KEY={gemini_key}\n")
        
        self.console.print("[green]API keys saved successfully![/green]")

    def manage_strategies(self):
        """Manage trading strategies."""
        self.console.print("\n[bold]Manage Trading Strategies[/bold]")
        
        # List available strategies
        strategies = [
            "Dynamic Trend Rider",
            "Volatility Breakout Pro",
            "Mean Reversion AI",
            "Scalper's Edge AI"
        ]
        
        table = Table(title="Available Strategies")
        table.add_column("ID", style="cyan")
        table.add_column("Strategy Name", style="green")
        
        for idx, strategy in enumerate(strategies, 1):
            table.add_row(str(idx), strategy)
        
        self.console.print(table)
        
        # Select strategy
        choice = Prompt.ask(
            "Select a strategy to activate",
            choices=[str(i) for i in range(1, len(strategies) + 1)]
        )
        
        self.active_strategy = strategies[int(choice) - 1]
        self.console.print(f"[green]Activated strategy: {self.active_strategy}[/green]")

    def manage_pairs(self):
        """Manage monitored trading pairs."""
        self.console.print("\n[bold]Manage Monitored Pairs[/bold]")
        
        while True:
            self.console.print("\n1. List monitored pairs")
            self.console.print("2. Add pair")
            self.console.print("3. Remove pair")
            self.console.print("4. Back to main menu")
            
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                self._list_pairs()
            elif choice == "2":
                self._add_pair()
            elif choice == "3":
                self._remove_pair()
            else:
                break

    def _list_pairs(self):
        """List all monitored trading pairs."""
        if not self.monitored_pairs:
            self.console.print("[yellow]No pairs are currently being monitored.[/yellow]")
            return
        
        table = Table(title="Monitored Trading Pairs")
        table.add_column("Pair", style="cyan")
        
        for pair in self.monitored_pairs:
            table.add_row(pair)
        
        self.console.print(table)

    def _add_pair(self):
        """Add a new trading pair to monitor."""
        pair = Prompt.ask("Enter trading pair (e.g., BTCUSDT)").upper()
        if pair not in self.monitored_pairs:
            self.monitored_pairs.append(pair)
            self.console.print(f"[green]Added {pair} to monitored pairs[/green]")
        else:
            self.console.print(f"[yellow]{pair} is already being monitored[/yellow]")

    def _remove_pair(self):
        """Remove a trading pair from monitoring."""
        if not self.monitored_pairs:
            self.console.print("[yellow]No pairs to remove[/yellow]")
            return
        
        pair = Prompt.ask(
            "Enter pair to remove",
            choices=self.monitored_pairs
        )
        
        self.monitored_pairs.remove(pair)
        self.console.print(f"[green]Removed {pair} from monitored pairs[/green]")

    def display_trade_suggestion(self, suggestion: dict):
        """Display trade suggestion in a formatted table."""
        table = Table(title="Trade Suggestion")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in suggestion.items():
            table.add_row(key, str(value))
        
        self.console.print(table)

    def view_trade_suggestions(self):
        """View trade suggestions for monitored pairs."""
        if not self.active_strategy:
            self.console.print("[yellow]Please select a strategy first[/yellow]")
            return
            
        if not self.monitored_pairs:
            self.console.print("[yellow]Please add trading pairs to monitor[/yellow]")
            return
            
        self.console.print("\n[bold]Generating Trade Suggestions...[/bold]")
        
        # Select timeframe
        timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
        timeframe_table = Table(title="Available Timeframes")
        timeframe_table.add_column("ID", style="cyan")
        timeframe_table.add_column("Timeframe", style="green")
        
        for idx, tf in enumerate(timeframes, 1):
            timeframe_table.add_row(str(idx), tf)
        
        self.console.print(timeframe_table)
        choice = Prompt.ask(
            "Select a timeframe",
            choices=[str(i) for i in range(1, len(timeframes) + 1)]
        )
        selected_timeframe = timeframes[int(choice) - 1]
        
        for pair in self.monitored_pairs:
            try:
                # Get latest market data
                klines = self.binance.get_klines(pair, interval=selected_timeframe)
                if klines is None:
                    continue

                # Calculate technical indicators
                df = pd.DataFrame(klines)
                indicators = self.technical_analysis.calculate_indicators(df)
                
                # Get AI suggestions
                suggestion = self.gemini.get_trade_suggestion(
                    symbol=pair,
                    timeframe=selected_timeframe,
                    market_data=self.gemini.prepare_market_data(df, indicators),
                    strategy=self.active_strategy
                )
                
                if suggestion:
                    self.display_trade_suggestion(suggestion)
                    
            except Exception as e:
                self.console.print(f"[red]Error getting suggestions for {pair}: {str(e)}[/red]")

    def run(self):
        """Run the CLI interface."""
        try:
            self.display_welcome()
            
            while True:
                choice = self.display_menu()
                
                if choice == "1":
                    self.manage_strategies()
                elif choice == "2":
                    self.view_trade_suggestions()
                elif choice == "3":
                    self.manage_pairs()
                else:
                    if Confirm.ask("Are you sure you want to exit?"):
                        break
            
            self.console.print("[green]Thank you for using the Trading Bot![/green]")
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Trading bot stopped by user[/yellow]")
        except Exception as e:
            logger.error(f"Error in CLI: {str(e)}")
            self.console.print(f"[red]Error: {str(e)}[/red]") 