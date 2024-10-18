import pandas as pd

def load_data(file_path):
    """Load historical stock data from a CSV file."""
    data = pd.read_csv(file_path, parse_dates=True, index_col='Date')
    return data

def simple_moving_average_strategy(data, short_window=40, long_window=100):
    """Implement a simple moving average crossover strategy."""
    signals = pd.DataFrame(index=data.index)
    signals['Price'] = data['Close']

    # Create short and long moving averages
    signals['Short_MA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
    signals['Long_MA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()

    # Create signals
    signals['Signal'] = 0
    signals['Signal'][short_window:] = \
        np.where(signals['Short_MA'][short_window:] > signals['Long_MA'][short_window:], 1, 0)
    signals['Position'] = signals['Signal'].diff()

    return signals

def backtest_strategy(signals, data):
    """Backtest the strategy and calculate returns."""
    initial_capital = 10000  # Starting capital
    shares = 0  # Initial shares
    portfolio = pd.DataFrame(index=signals.index)
    
    for index, signal in signals.iterrows():
        if signal['Position'] == 1:  # Buy signal
            shares = initial_capital // signal['Price']
            initial_capital -= shares * signal['Price']
        elif signal['Position'] == -1:  # Sell signal
            initial_capital += shares * signal['Price']
            shares = 0
            
        # Calculate portfolio value
        portfolio.loc[index, 'Holdings'] = shares * signal['Price'] + initial_capital

    return portfolio

def run_backtest(file_path):
    """Run the backtest and display the results."""
    data = load_data(file_path)
    signals = simple_moving_average_strategy(data)
    portfolio = backtest_strategy(signals, data)

    # Display final portfolio value
    final_value = portfolio['Holdings'].iloc[-1]
    print(f'Final Portfolio Value: ${final_value:.2f}')
    
    return signals, portfolio

# Example usage:
if __name__ == "__main__":
    file_path = 'path_to_your_stock_data.csv'  # Replace with your CSV file path
    signals, portfolio = run_backtest(file_path)
