from django.http import JsonResponse
from .models import StockPrice
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def run_backtest(symbol, initial_investment, short_ma_days=50, long_ma_days=200):
    # Fetch the stock data for the given symbol
    data = StockPrice.objects.filter(symbol=symbol).order_by('date')

    # Check if there's any data for the given symbol
    if not data.exists():
        raise ValueError(f"No stock data found for symbol: {symbol}")

    # Create a DataFrame from the query results
    df = pd.DataFrame(list(data.values()))

    # Ensure that we have enough data to calculate moving averages
    if len(df) < long_ma_days:
        raise ValueError(f"Not enough data to calculate moving averages for symbol: {symbol}")

    # Calculate the moving averages
    df['short_mavg'] = df['close_price'].rolling(window=short_ma_days).mean()
    df['long_mavg'] = df['close_price'].rolling(window=long_ma_days).mean()

    # Initialize variables for backtesting
    investment = initial_investment
    position = 0
    trades = []

    # Iterate over the DataFrame to check for buy/sell signals
    for index, row in df.iterrows():
        # Buy signal
        if row['short_mavg'] > row['long_mavg'] and position == 0:  
            position = investment / row['close_price']  # Buy the stock
            trades.append((row['date'], 'BUY', row['close_price']))
            investment = 0  # Investment is now in the stock

        # Sell signal
        elif row['short_mavg'] < row['long_mavg'] and position > 0:  
            investment = position * row['close_price']  # Sell the stock
            trades.append((row['date'], 'SELL', row['close_price']))
            position = 0  # No stock held

    # If there's still stock held at the end, convert it back to cash
    if position > 0:
        investment = position * df['close_price'].iloc[-1]  # Sell at the last close price
        trades.append((df['date'].iloc[-1], 'SELL', df['close_price'].iloc[-1]))  # Final sell action

    # Calculate the total return percentage
    total_return = (investment - initial_investment) / initial_investment * 100 if investment > 0 else -100

    return total_return, trades

