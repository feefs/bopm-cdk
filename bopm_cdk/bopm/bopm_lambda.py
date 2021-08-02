import bs4
import json
import numpy as np
import pandas as pd
import scipy
import yfinance as yf


def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'response': "Hello world!",
            'method': event['httpMethod']
        })
    }
