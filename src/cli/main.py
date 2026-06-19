"""
Command-line interface for StockStats.
"""
import argparse
import datetime
import cmd2
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from polygon_source import get_polygon_stock_data
from stockstats import StockDataFrame

console = Console()

class StockStatsCLI(cmd2.Cmd):
    """A comprehensive CLI client for StockStats using cmd2 and rich."""
    
    prompt = 'stockstats> '
    intro = "Welcome to the StockStats CLI! Type 'help' to see available commands."
    
    def __init__(self):
        super().__init__()
        self.stock_df = None
        self.ticker = None

    fetch_parser = cmd2.Cmd2ArgumentParser(description='Fetch stock data from Polygon API')
    fetch_parser.add_argument('ticker', type=str, help='Ticker symbol (e.g., AAPL)')
    fetch_parser.add_argument('--multiplier', type=int, default=1, help='Timespan multiplier')
    fetch_parser.add_argument('--timespan', type=str, default='day', help='Timespan (e.g., day, minute)')
    fetch_parser.add_argument('--from-date', type=str, help='Start date (YYYY-MM-DD), default is 1 year ago')
    fetch_parser.add_argument('--to-date', type=str, help='End date (YYYY-MM-DD), default is today')

    @cmd2.with_argparser(fetch_parser)
    def do_fetch(self, args):
        """Fetch stock data from Polygon API and load it into the session."""
        ticker = args.ticker.upper()
        
        # Set default dates if not provided (default: last 1 year)
        today = datetime.date.today()
        to_date = args.to_date if args.to_date else today.strftime("%Y-%m-%d")
        
        if args.from_date:
            from_date = args.from_date
        else:
            # Default to 1 year ago
            one_year_ago = today.replace(year=today.year - 1) if today.month != 2 or today.day != 29 else today.replace(year=today.year - 1, day=28)
            from_date = one_year_ago.strftime("%Y-%m-%d")
            
        console.print(f"[cyan]Fetching data for {ticker} from {from_date} to {to_date}...[/cyan]")
        try:
            self.stock_df = get_polygon_stock_data(
                ticker=ticker,
                multiplier=args.multiplier,
                timespan=args.timespan,
                from_date=from_date,
                to_date=to_date
            )
            self.ticker = ticker
            console.print(f"[green]Successfully loaded {len(self.stock_df)} records for {self.ticker}.[/green]")
        except Exception as e:
            console.print(f"[red]Error fetching data: {e}[/red]")

    def do_show(self, args):
        """Show the currently loaded stock data."""
        if self.stock_df is None:
            console.print("[yellow]No data loaded. Use 'fetch' command first.[/yellow]")
            return
            
        table = Table(title=f"{self.ticker} Stock Data (Head)")
        table.add_column("Date", justify="left", style="cyan")
        table.add_column("Open", justify="right", style="magenta")
        table.add_column("High", justify="right", style="magenta")
        table.add_column("Low", justify="right", style="magenta")
        table.add_column("Close", justify="right", style="magenta")
        table.add_column("Volume", justify="right", style="green")

        # Just show top 10
        head_df = self.stock_df.head(10)
        for index, row in head_df.iterrows():
            table.add_row(
                str(index),
                f"{row['open']:.2f}",
                f"{row['high']:.2f}",
                f"{row['low']:.2f}",
                f"{row['close']:.2f}",
                f"{row['volume']:.0f}"
            )
        
        console.print(table)

    indicator_parser = cmd2.Cmd2ArgumentParser(description='Calculate and display a stock indicator')
    indicator_parser.add_argument('indicator', type=str, help='Indicator name (e.g., close_10_sma, rsi_14, macd)')
    indicator_parser.add_argument('--tail', type=int, default=10, help='Number of rows to show')

    @cmd2.with_argparser(indicator_parser)
    def do_calc(self, args):
        """Calculate and display a specific indicator."""
        if self.stock_df is None:
            console.print("[yellow]No data loaded. Use 'fetch' command first.[/yellow]")
            return
            
        console.print(f"[cyan]Calculating {args.indicator}...[/cyan]")
        try:
            # Accessing the column triggers the calculation in StockDataFrame
            series = self.stock_df[args.indicator]
            
            table = Table(title=f"{self.ticker} - {args.indicator} (Last {args.tail} records)")
            table.add_column("Date", justify="left", style="cyan")
            table.add_column("Value", justify="right", style="yellow")
            
            tail_series = series.tail(args.tail)
            for index, value in tail_series.items():
                table.add_row(str(index), f"{value:.4f}")
                
            console.print(table)
        except Exception as e:
            console.print(f"[red]Error calculating indicator: {e}[/red]")

    def do_list(self, args):
        """List all available indicators and their default windows."""
        from stockstats import _dft_windows
        
        table = Table(title="Available Indicators in StockStats")
        table.add_column("Indicator", justify="left", style="cyan", no_wrap=True)
        table.add_column("Default Window(s)", justify="left", style="magenta")
        
        # Sort alphabetically for display
        for indicator, windows in sorted(_dft_windows.items()):
            # Format windows nicely
            if isinstance(windows, tuple):
                win_str = ", ".join(map(str, windows))
            else:
                win_str = str(windows)
                
            table.add_row(indicator, win_str)
            
        console.print(table)
        console.print("\n[yellow]Tip: Most indicators support custom windows (e.g. 'rsi_20' instead of 'rsi')[/yellow]")
        console.print("[yellow]     And custom columns (e.g. 'high_10_sma' instead of 'close_10_sma')[/yellow]")

    def do_status(self, args):
        """Show current CLI status."""
        if self.stock_df is None:
            status = "No data loaded."
        else:
            status = f"Loaded {len(self.stock_df)} records for {self.ticker}."
            
        panel = Panel(
            Text(status, justify="center"),
            title="Session Status",
            border_style="blue"
        )
        console.print(panel)


def main():
    app = StockStatsCLI()
    app.cmdloop()

if __name__ == '__main__':
    main()
