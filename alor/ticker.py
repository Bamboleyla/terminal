import logging
import json
import pandas as pd

logger = logging.getLogger(__name__)


class Ticker:

    def __init__(self, ticker):
        self.config = json.load(open('alor/tickers/' + ticker + '/config.json'))
        self.quotes = pd.read_csv('alor/tickers/' + ticker + '/quotes.csv')
