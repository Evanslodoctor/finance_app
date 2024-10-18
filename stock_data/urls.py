from django.contrib import admin
from django.urls import path
from . import views

app_name = 'stock_data'  # Replace with your actual app name

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls, name='admin'),

    # Home page
    path('', views.home, name='home'),

    # Transactions
    path('transactions/', views.transactions, name='transactions'),  # List all transactions
    path('transactions/add/', views.add_transaction, name='add_transaction'),  # Add a new transaction
    path('transactions/delete/<int:id>/', views.delete_transaction, name='delete_transaction'),  # Delete a transaction

    # Stock Data
    path('fetch_stock_data/', views.fetch_stock_data, name='fetch_stock_data'),  # Fetch stock data from API

    # Backtesting
    path('backtest/', views.run_backtest_view, name='run_backtest'),  # Run backtesting logic

    # Prediction
    path('predict/', views.predict_stock_prices, name='predict_view'),  # Predict future stock prices

    # Reports
    path('report/', views.generate_report_view, name='generate_report'),  # Generate a report
]
