import requests

from logger import Logger

logger = Logger()


def get_fear_and_greed_index():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    data = response.json()
    index_value = int(data['data'][0]['value'])

    logger.info(f"Fear index: {index_value}")

    return index_value


def adaptive_average_cost(fear_greed_index, monthly_limit, frequency):
    base_amount = monthly_limit / frequency

    if fear_greed_index > 65:
        # Při vysoké hodnotě FGI neinvestujeme
        return 0
    elif fear_greed_index > 50:
        # Neutrální trh, standardní investice
        investment_amount = base_amount
    elif fear_greed_index > 30:
        # Opatrný trh, mírně zvýšená investice
        investment_amount = base_amount * 1.25
    elif fear_greed_index > 20:
        # Trh ve strachu, výrazně zvýšená investice
        investment_amount = base_amount * 1.5
    else:
        # Velký strach na trhu, maximální zvýšení investice
        investment_amount = base_amount * 2

    return round(investment_amount, 1)


def adaptive_cost_average_with_market_timing(fear_greed_index, btc_price_change, monthly_budget, investment_frequency):
    # Base weekly investment amount
    base_investment = monthly_budget / investment_frequency

    # Adjust investment based on Fear and Greed Index
    if fear_greed_index < 30:
        # Market fear - increase investment
        index_adjustment = 1.5
    elif fear_greed_index > 65:
        # Market greed - decrease investment
        index_adjustment = 0.5
    else:
        # Neutral market condition
        index_adjustment = 1.0

    # Adjust investment based on Bitcoin price trend
    if btc_price_change < -4:
        # Significant price drop - increase investment
        price_adjustment = 1.5
    elif btc_price_change > 4:
        # Price rise - decrease or skip investment
        price_adjustment = 0.5
    else:
        # Price stable
        price_adjustment = 1.0

    # Calculate final investment amount
    investment_amount = base_investment * index_adjustment * price_adjustment

    return round(investment_amount, 1)


def adaptive_average_cost_with_technical_analysis(row):
    monthly_limit = 100
    frequency = 4
    base_amount = monthly_limit / frequency
    investment_multiplier = 1
    moving_average_trend = 'bullish' if row['Price'] > row['30d_MA'] else 'bearish'

    if moving_average_trend == 'bullish':
        investment_multiplier = 1.1
    elif moving_average_trend == 'bearish':
        investment_multiplier = 0.9

    if row['value'] > 65:
        return 0
    elif row['value'] > 50:
        investment_amount = base_amount * investment_multiplier
    elif row['value'] > 30:
        investment_amount = base_amount * 1.25 * investment_multiplier
    elif row['value'] > 20:
        investment_amount = base_amount * 1.5 * investment_multiplier
    else:
        investment_amount = base_amount * 2 * investment_multiplier

    return round(investment_amount, 1)


def adaptive_cost_average_with_market_timing_and_dynamic_coefficients(row):
    monthly_budget = 100
    investment_frequency = 4
    base_investment = monthly_budget / investment_frequency
    index_adjustment = 1.5 if row['value'] < 30 else (0.5 if row['value'] > 65 else 1.0)
    price_adjustment = 1.5 if row['BTC_Price_Change'] < -4 else (0.5 if row['BTC_Price_Change'] > 4 else 1.0)

    investment_amount = base_investment * index_adjustment * price_adjustment

    return round(investment_amount, 1)
