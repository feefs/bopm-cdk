import json

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from scipy.interpolate import interp1d

TREE_DEPTH = 50

def handler(event, context):
    body = json.loads(event['body'])

    time_in_years = body['days'] / 365
    stock = yf.Ticker(body['ticker'])
    price = stock.history(period='1d')['Close'][0]
    risk_free_interest_rate = risk_free_rate(time_in_years)
    history = stock.history(period='1y')
    percent_changes = (history['Open'] / history['Close'] - 1)
    proportional_volatility = percent_changes.std() * np.sqrt(time_in_years * 253)

    american, european, delta_t = bopm(
        time_in_years,
        TREE_DEPTH,
        price,
        body['strike'],
        risk_free_interest_rate,
        proportional_volatility,
        body['type']
    )

    american_coords, european_coords = generate_coordinates(american, delta_t), generate_coordinates(european, delta_t)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'response': 'Success!',
            'method': event['httpMethod'],
            'american_points': american_coords.tolist(),
            'european_points': european_coords.tolist(),
        })
    }


def bopm(t, n, s, k, r, v, option_type):
    """
    t = time to expiration (years)
    n = height of binomial tree
    s = stock price
    k = strike price
    r = risk-free interest rate (annual)
    v = stock volatility
    """
    delta_t = t / n

    up = np.exp(v * np.sqrt(delta_t))
    down = 1 / up
    p = (np.exp(r * delta_t) - down) / (up - down)

    american, european = np.zeros((n + 1, n + 1)), np.zeros((n + 1, n + 1))

    # up^(j) * down^(N - j) * S = up^(j) * (1/up)^(N - j) * S = up^(2j - N) * S
    expiration_intrinsic_values = (up ** ((2 * np.arange(0, n + 1)) - n)) * s
    expiration_values = np.maximum(
        (expiration_intrinsic_values - k) if option_type == 'C' else (k - expiration_intrinsic_values),
        0
    )
    american[n, :], european[n, :] = expiration_values, expiration_values

    binomial_value_constant = np.exp(-r * delta_t)
    for i in reversed(range(0, n, 1)):
        american_option_up, american_option_down = american[i + 1, 1:i + 2], american[i + 1, 0:i + 1]
        european_option_up, european_option_down = european[i + 1, 1:i + 2], european[i + 1, 0:i + 1]

        american_binomial_values = ((p * american_option_up) + ((1 - p) * american_option_down)) * binomial_value_constant
        european_binomial_values = ((p * european_option_up) + ((1 - p) * european_option_down)) * binomial_value_constant

        intrinsic_values = (up ** ((2 * np.arange(0, i + 1)) - i)) * s

        american[i, 0:i + 1] = np.maximum(
            (intrinsic_values - k) if option_type == 'C' else (k - intrinsic_values),
            american_binomial_values
        )
        european[i, 0:i + 1] = european_binomial_values

    return american, european, delta_t


def generate_coordinates(arr, delta_t):
    n = len(arr)
    result = np.empty((int((n * (n + 1)) / 2), 3))

    curr_time_delta, starting_offset, curr_row = 0, 0, 0
    for i, row in enumerate(arr, start=1):
        time_deltas = np.full(i, curr_time_delta)
        indices = np.arange(starting_offset, starting_offset + (2 * i), 2)
        values = row[:i]

        result[curr_row:curr_row + i, :] = np.stack((time_deltas, indices, values), axis=1)
        curr_time_delta, starting_offset, curr_row = curr_time_delta + delta_t, starting_offset - 1, curr_row + i

    return result


# source: https://github.com/mcdallas/wallstreet
def risk_free_rate(t):
    try:
        r = requests.get(
            'http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield'
        )
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table', attrs={'class' : 't-chart'})
        rows = table.find_all('tr')
        lastrow = len(rows) - 1
        cells = rows[lastrow].find_all('td')

        years = np.array([0, 1, 3, 6, 12, 24, 36, 60, 84, 120, 240, 360]) / 12
        rates = np.array([0] + [float(cells[n].get_text()) for n in range(1, 12)]) / 100

        return float(interp1d(years, rates)(t))
    except Exception as e:
        print(e)
        return 0.02
