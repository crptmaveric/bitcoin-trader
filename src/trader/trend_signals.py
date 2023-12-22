from trader.market_indicators import calculate_moving_average, calculate_RSI, calculate_MACD


def generate_signals(data, short_term_window, long_term_window, rsi_threshold, macd_threshold):
    """
    Generate buy and sell signals based on moving average crossovers and confirmations from RSI and MACD.
    """
    # Calculate indicators
    data['short_term_ma'] = calculate_moving_average(data, short_term_window)
    data['long_term_ma'] = calculate_moving_average(data, long_term_window)
    data['rsi'] = calculate_RSI(data)
    data['macd'], data['macd_signal'] = calculate_MACD(data)

    # Initialize columns for signals
    data['buy_signal'] = False
    data['sell_signal'] = False

    # Loop through the data to find crossovers and confirm with RSI and MACD
    for i in range(1, len(data)):
        if data['short_term_ma'][i] > data['long_term_ma'][i] and data['short_term_ma'][i - 1] <= data['long_term_ma'][i - 1]:
            if data['rsi'][i] > rsi_threshold and data['macd'][i] > macd_threshold:
                data.at[i, 'buy_signal'] = True
        elif data['short_term_ma'][i] < data['long_term_ma'][i] and data['short_term_ma'][i - 1] >= data['long_term_ma'][i - 1]:
            if data['rsi'][i] < 100 - rsi_threshold and data['macd'][i] < macd_threshold:
                data.at[i, 'sell_signal'] = True

    return data

# Example usage
# data = pd.DataFrame({'price': [/* historical prices */]})
# signals = generate_signals(data, 50, 200, 70, 0)  # Example parameters

