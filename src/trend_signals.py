def generate_trading_signals(short_term_ma, long_term_ma, rsi, macd, macd_signal, rsi_threshold=30, macd_threshold=0):
    """
    Generate trading signals based on technical indicators.

    Parameters:
    short_term_ma (list): Short-term moving average values.
    long_term_ma (list): Long-term moving average values.
    rsi (list): Relative Strength Index values.
    macd (list): Moving Average Convergence Divergence values.
    macd_signal (list): MACD signal line values.
    rsi_threshold (float): Threshold for the RSI indicator.
    macd_threshold (float): Threshold for the MACD indicator.

    Returns:
    list: A list of trading signals (e.g., 'BUY', 'SELL') and their positions.
    """
    try:
        signals = []
        for i in range(1, len(short_term_ma)):
            if short_term_ma[i] > long_term_ma[i] and short_term_ma[i-1] <= long_term_ma[i-1]:
                if rsi[i] < rsi_threshold and macd[i] > macd_signal[i]:
                    signals.append(('BUY', i))
            elif short_term_ma[i] < long_term_ma[i] and short_term_ma[i-1] >= long_term_ma[i-1]:
                if rsi[i] > 100 - rsi_threshold and macd[i] < macd_signal[i]:
                    signals.append(('SELL', i))
        return signals
    except Exception as e:
        print(f"Error generating trading signals: {e}")
        return []
