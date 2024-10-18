from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Transaction, StockPrice, StockPrediction
import requests
from django.http import JsonResponse
from django.conf import settings
from .backtesting import run_backtest  # Import backtesting logic
import pickle
import numpy as np
import logging
from .backtest import run_backtest

# Initialize logger
logger = logging.getLogger(__name__)

def home(request):
    total_income = Transaction.objects.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Transaction.objects.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': total_income - total_expense
    }
    return render(request, 'home.html', context)

def transactions(request):
    all_transactions = Transaction.objects.all()
    context = {'transactions': all_transactions}
    return render(request, 'transactions.html', context)

def add_transaction(request):
    if request.method == 'POST':
        description = request.POST['description']
        amount = request.POST['amount']
        transaction_type = request.POST['transaction_type']
        transaction = Transaction(description=description, amount=amount, transaction_type=transaction_type)
        transaction.save()
        return redirect('transactions')
    return render(request, 'add_transaction.html')

def delete_transaction(request, id):
    transaction = Transaction.objects.get(id=id)
    transaction.delete()
    return redirect('transactions')

# Fetch Stock Data
def fetch_stock_data(request):
    symbol = request.GET.get('symbol', 'AAPL')
    api_key = settings.ALPHA_VANTAGE_API_KEY
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
    response = requests.get(url).json()

    if 'Time Series (Daily)' in response:
        time_series = response['Time Series (Daily)']
        for date, daily_data in time_series.items():
            StockPrice.objects.update_or_create(
                symbol=symbol,
                date=date,
                defaults={
                    'open_price': daily_data['1. open'],
                    'close_price': daily_data['4. close'],
                    'high_price': daily_data['2. high'],
                    'low_price': daily_data['3. low'],
                    'volume': daily_data['5. volume'],
                },
            )
        return JsonResponse({"message": "Stock data fetched and saved successfully!"})
    return JsonResponse({"error": "Failed to fetch stock data"}, status=400)

from django.http import JsonResponse
from .models import StockPrice
from .backtest import run_backtest  # Ensure this import points to your backtest function

from django.http import JsonResponse
from .models import StockPrice
import pandas as pd
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

# Prediction View
def predict_stock_prices(request):
    symbol = request.GET.get('symbol', 'AAPL')
    predictions = make_predictions(symbol)

    # Check if there is an error in predictions
    if "error" in predictions:
        return JsonResponse(predictions, status=400)  # Return a 400 status if there is an error

    return JsonResponse(predictions)

# Make Predictions
def make_predictions(symbol):
    model_path = f'models/{symbol}_model.pkl'
    try:
        with open(model_path, 'rb') as file:
            model = pickle.load(file)

        # Fetch recent stock data
        recent_data = StockPrice.objects.filter(symbol=symbol).order_by('-date')[:5]

        if len(recent_data) < 5:
            return {"error": "Not enough data to make a prediction."}

        # Prepare input data
        input_data = np.array([[stock.close_price for stock in recent_data]])

        # Make predictions
        predictions = model.predict(input_data)

        return {"predictions": predictions.tolist()}  # Convert to list for JSON serialization

    except FileNotFoundError:
        return {"error": f"Model file for {symbol} not found."}
    except Exception as e:
        return {"error": str(e)}

# Generate Report (with charts and PDFs)
def generate_report_view(request):
    symbol = request.GET.get('symbol', 'AAPL')
    stock_data = StockPrice.objects.filter(symbol=symbol).order_by('date')
    # Generate report with performance metrics and charts (not fully implemented here)
    report = generate_report(stock_data)  # Placeholder for report generation logic
    return JsonResponse(report)
def predict_view(request):
    # Assuming you expect certain parameters from the GET request
    parameter1 = request.GET.get('parameter1')
    parameter2 = request.GET.get('parameter2')

    # Check if the required parameters are provided
    if parameter1 is None or parameter2 is None:
        return JsonResponse({'error': 'Missing required parameters.'}, status=400)

    try:
        # Convert parameters to appropriate types if needed
        # For example:
        parameter1 = float(parameter1)
        parameter2 = float(parameter2)

        # Perform your prediction logic here
        # prediction_result = some_prediction_function(parameter1, parameter2)

        # Example response
        response_data = {
            'parameter1': parameter1,
            'parameter2': parameter2,
            # 'prediction': prediction_result
        }

        return JsonResponse(response_data)

    except ValueError:
        return JsonResponse({'error': 'Invalid parameter value.'}, status=400)

    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)