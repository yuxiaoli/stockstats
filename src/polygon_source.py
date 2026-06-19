import os
import pandas as pd
from dotenv import load_dotenv
from polygon import RESTClient

from stockstats import wrap, StockDataFrame

# Load environment variables from .env file
load_dotenv()

def get_polygon_stock_data(
    ticker: str, 
    multiplier: int = 1, 
    timespan: str = "day", 
    from_date: str = "2023-01-01", 
    to_date: str = "2023-01-31"
) -> StockDataFrame:
    """
    Fetch historical stock data from Polygon API and wrap it in a StockDataFrame.
    
    :param ticker: The ticker symbol (e.g., 'AAPL')
    :param multiplier: The size of the timespan multiplier
    :param timespan: The size of the time window (e.g., 'day', 'minute')
    :param from_date: The start date of the data (YYYY-MM-DD)
    :param to_date: The end date of the data (YYYY-MM-DD)
    :return: A StockDataFrame containing the fetched data
    """
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in environment variables. Please set it in the .env file.")
        
    client = RESTClient(api_key)
    
    # Fetch aggregate bars from Polygon
    aggs = client.get_aggs(ticker, multiplier, timespan, from_date, to_date)
    
    data = []
    for a in aggs:
        data.append({
            'timestamp': a.timestamp,
            'open': a.open,
            'high': a.high,
            'low': a.low,
            'close': a.close,
            'volume': a.volume,
            'vwap': a.vwap,
            'transactions': a.transactions
        })
        
    df = pd.DataFrame(data)
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
    return wrap(df)

if __name__ == "__main__":
    # Example usage
    try:
        stock_df = get_polygon_stock_data("AAPL", 1, "day", "2023-01-01", "2023-01-10")
        print("Data loaded from Polygon API successfully:")
        print(stock_df.head())
        print("\nCalculating SMA 2:")
        print(stock_df['close_2_sma'])
    except Exception as e:
        print(f"Error fetching data: {e}")