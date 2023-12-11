import requests


def get_fear_and_greed_index():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    data = response.json()
    return int(data['data'][0]['value'])


def calculate_investment_amount(index_value, monthly_limit, frequency):
    base_amount = monthly_limit / frequency

    if index_value > 55:
        # Při vysoké hodnotě FGI neinvestujeme
        return 0
    elif index_value > 45:
        # Neutrální trh, standardní investice
        investment_amount = base_amount
    elif index_value > 30:
        # Opatrný trh, mírně zvýšená investice
        investment_amount = base_amount * 1.25
    elif index_value > 20:
        # Trh ve strachu, výrazně zvýšená investice
        investment_amount = base_amount * 1.5
    else:
        # Velký strach na trhu, maximální zvýšení investice
        investment_amount = base_amount * 2

    return round(investment_amount, 1)
