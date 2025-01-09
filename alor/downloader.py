import logging
import os
import json
import pandas as pd

from alor.config import AlorConfiguration


class AlorDownloader:
    def __init__(self):
        self.__config = AlorConfiguration()

    def prepare(self):

        for ticker in self.__config.tickers:
            # Check ticker directory
            if not os.path.exists('alor/tickers/'+ticker+"/"):
                # Create ticker directory
                os.makedirs('alor/tickers/'+ticker+"/")

            # Check config file
            if not os.path.exists('alor/tickers/'+ticker+"/config.json"):
                # Create default config
                default = {
                    'var_take': 1.5, 'period': [10, 20], 'multiplier': [3, 5]
                }
                # Create config file
                with open('alor/tickers/'+ticker+"/config.json", 'w') as f:
                    json.dump(default, f)

            # Check quotes file
            if not os.path.exists('alor/tickers/'+ticker+"/quotes.csv"):
                # Create quotes file
                df = pd.DataFrame(columns=['TICKER', 'DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME'])
                df.to_csv('alor/tickers/'+ticker+"/quotes.csv", index=False)
