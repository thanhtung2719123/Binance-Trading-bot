import sys
import os
from rich.console import Console
from rich.panel import Panel

def main():
    console = Console()
    console.print(Panel.fit(
        "[bold green]Trading Bot Test Run[/bold green]\n"
        "If you can see this message, the executable is working correctly!",
        title="Trading Bot",
        border_style="green"
    ))
    
    # Print Python path and working directory for debugging
    console.print("\n[bold]Debug Information:[/bold]")
    console.print(f"Python Path: {sys.path}")
    console.print(f"Working Directory: {os.getcwd()}")
    
    # Wait for user input before closing
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 