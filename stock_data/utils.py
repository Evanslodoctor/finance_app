import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
import numpy as np
from django.http import JsonResponse
from django.db import models

# Django model for stock prices
class StockPrice(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.IntegerField()

# Fetch financial data from Alpha Vantage
def fetch_stock_data(symbol):
    ALPHA_VANTAGE_API_KEY = '7UOMQH79EKM7ETBP'  # Replace with your actual API key
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if "Error Message" in data:
        raise ValueError("Invalid symbol or request limit reached.")

    time_series = data.get("Time Series (Daily)", {})
    for date_str, prices in time_series.items():
        StockPrice.objects.update_or_create(
            symbol=symbol,
            date=date_str,
            defaults={
                'open_price': float(prices['1. open']),
                'high_price': float(prices['2. high']),
                'low_price': float(prices['3. low']),
                'close_price': float(prices['4. close']),
                'volume': int(prices['5. volume']),
            }
        )

# Data Preparation
def prepare_data(symbol):
    # Fetch data from the database
    data = StockPrice.objects.filter(symbol=symbol).values()
    df = pd.DataFrame(data)

    # Convert date column to datetime and set it as index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Feature Engineering: Example of moving averages
    df['short_ma'] = df['close_price'].rolling(window=50).mean()
    df['long_ma'] = df['close_price'].rolling(window=200).mean()

    # Drop rows with NaN values
    df.dropna(inplace=True)

    # Define features and labels
    X = df[['open_price', 'high_price', 'low_price', 'close_price', 'volume', 'short_ma', 'long_ma']]
    y = df['close_price'].shift(-1).dropna()  # Predicting next day's close price

    # Align X and y
    X = X[:-1]  # Drop the last row of X to match y
    return train_test_split(X, y, test_size=0.2, random_state=42)

# Model Training
def train_model_view(request):
    symbol = request.GET.get('symbol', 'AAPL')  # Default to AAPL if not provided
    try:
        train_model(symbol)
        return JsonResponse({'message': f'Model for {symbol} trained successfully.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Load a pre-trained ML model
def load_model(symbol):
    return joblib.load(f'models/{symbol}_stock_price_model.pkl')

# Predict future stock prices
def predict_stock_prices(request, symbol):
    try:
        model = load_model(symbol)
    except FileNotFoundError:
        return JsonResponse({'error': 'Model not found.'}, status=404)

    # Fetch the last 30 days of historical data
    recent_data = StockPrice.objects.filter(symbol=symbol).order_by('-date')[:30]
    if len(recent_data) < 30:
        return JsonResponse({'error': 'Not enough data to predict.'}, status=400)

    # Prepare input data for prediction
    recent_data_df = pd.DataFrame(list(recent_data))
    recent_data_df['date'] = pd.to_datetime(recent_data_df['date'])
    recent_data_df.set_index('date', inplace=True)

    # Calculate moving averages
    recent_data_df['short_ma'] = recent_data_df['close_price'].rolling(window=50).mean()
    recent_data_df['long_ma'] = recent_data_df['close_price'].rolling(window=200).mean()

    # Use the latest available values for prediction
    input_data = pd.DataFrame({
        'open_price': [recent_data_df['open_price'].iloc[-1]],
        'high_price': [recent_data_df['high_price'].iloc[-1]],
        'low_price': [recent_data_df['low_price'].iloc[-1]],
        'close_price': [recent_data_df['close_price'].iloc[-1]],
        'volume': [recent_data_df['volume'].iloc[-1]],
        'short_ma': [recent_data_df['short_ma'].iloc[-1]],  # Last value of short MA
        'long_ma': [recent_data_df['long_ma'].iloc[-1]],    # Last value of long MA
    })

    predictions = model.predict(input_data)

    return JsonResponse({'predictions': predictions.tolist()})

# Calculate moving averages for backtesting
def calculate_moving_averages(data, window):
    return data.rolling(window=window).mean()

# Backtesting logic
def backtest(symbol, initial_investment, short_ma=50, long_ma=200):
    stock_data = StockPrice.objects.filter(symbol=symbol).order_by('date')
    stock_data_df = pd.DataFrame(list(stock_data))

    # Calculate moving averages
    stock_data_df['short_ma'] = calculate_moving_averages(stock_data_df['close_price'], short_ma)
    stock_data_df['long_ma'] = calculate_moving_averages(stock_data_df['close_price'], long_ma)

    investment = initial_investment
    stock_owned = 0

    for index, row in stock_data_df.iterrows():
        if row['short_ma'] > row['long_ma'] and stock_owned == 0:
            stock_owned = investment / row['close_price']
            investment = 0
        elif row['short_ma'] < row['long_ma'] and stock_owned > 0:
            investment = stock_owned * row['close_price']
            stock_owned = 0

    final_value = investment + (stock_owned * stock_data_df['close_price'].iloc[-1] if stock_owned > 0 else 0)
    return final_value

# Backtesting view
def run_backtest_view(request):
    symbol = request.GET.get('symbol', 'AAPL')  # Default to 'AAPL' if no symbol is provided
    initial_investment_str = request.GET.get('initial_investment')

    # Check if initial_investment is provided and convert it to float
    if initial_investment_str is None:
        return JsonResponse({'error': 'Initial investment parameter is required.'}, status=400)

    try:
        initial_investment = float(initial_investment_str)
    except ValueError:
        return JsonResponse({'error': 'Invalid initial investment value.'}, status=400)

    stock_data = StockPrice.objects.filter(symbol=symbol).order_by('date')

    if stock_data.exists():
        try:
            logger.info(f"Running backtest for symbol: {symbol} with initial investment: {initial_investment}")

            # Call run_backtest with the correct number of arguments
            total_return, trades = run_backtest(symbol, initial_investment)  
            
            # Prepare the response data
            backtest_results = {
                'total_return': total_return,
                'trades': trades
            }
            return JsonResponse(backtest_results)
        except ValueError as e:
            logger.error(f"ValueError: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
    else:
        return JsonResponse({'error': f'No stock data found for symbol: {symbol}'}, status=404)

