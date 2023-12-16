def generate_trading_signals(short_term_ma, long_term_ma, rsi, macd, macd_signal, rsi_threshold=30, macd_threshold=0):
    signals = []
    for i in range(1, len(short_term_ma)):
        if short_term_ma[i] > long_term_ma[i] and short_term_ma[i-1] <= long_term_ma[i-1]:
            if rsi[i] < rsi_threshold and macd[i] > macd_signal[i]:
                signals.append(('BUY', i))
        elif short_term_ma[i] < long_term_ma[i] and short_term_ma[i-1] >= long_term_ma[i-1]:
            if rsi[i] > 100 - rsi_threshold and macd[i] < macd_signal[i]:
                signals.append(('SELL', i))
    return signals