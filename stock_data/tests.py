from django.test import TestCase
from .models import StockPrice
from .utils import fetch_stock_data, backtest

class StockDataTestCase(TestCase):
    def test_fetch_stock_data(self):
        fetch_stock_data('AAPL')
        stock_data = StockPrice.objects.filter(symbol='AAPL')
        self.assertTrue(stock_data.exists())

    def test_backtesting(self):
        stock_data = StockPrice.objects.filter(symbol='AAPL')
        initial_investment = 1000
        result = backtest(stock_data, initial_investment)
        self.assertIsInstance(result, float)
