import os
import json
import asyncio
import pandas as pd

from datetime import datetime, timezone, timedelta
from alor.config import AlorConfiguration
from alor.api import AlorAPI


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
            file_path = 'alor/tickers/'+ticker+"/quotes.csv"  # Path to quotes file

            if not os.path.exists(file_path):

                now = datetime.now(timezone.utc)  # Get current date and time
                one_month_ago = now - timedelta(days=31)  # Subtract approximately 1 month ago
                first_day_of_month = one_month_ago.replace(day=1, hour=0, minute=0, second=0, microsecond=0,
                                                           tzinfo=timezone(timedelta(hours=3)))  # Get first day of current month
                api = AlorAPI()
                quotes = asyncio.run(api.get_ticker_data(ticker, first_day_of_month))

                if not quotes.empty:
                    quotes.to_csv(file_path, index=False)  # save quotes to file
                else:
                    print(f"No data for {ticker} in the last month")
