import os
import json
import asyncio
import pandas as pd
import logging
import uuid

from datetime import datetime, timezone, timedelta
from alor.config import AlorConfiguration
from alor.api import AlorAPI

logger = logging.getLogger(__name__)


class AlorDownloader:
    def __init__(self):
        self.__config = AlorConfiguration()

    def prepare(self):

        percent_step = 100/len(self.__config.tickers)  # initial percentage
        percentage = 0.0  # complete percentage

        for ticker in self.__config.tickers:
            # Check ticker directory
            if not os.path.exists('alor/tickers/'+ticker+"/"):
                # Create ticker directory
                os.makedirs('alor/tickers/'+ticker+"/")
                logger.info(f"Created directory for {ticker}")

            # Check config file
            if not os.path.exists('alor/tickers/'+ticker+"/config.json"):
                # Create default config
                default = {
                    'indicators': [{'id': uuid.uuid4().hex, 'type': 'Super Trend', 'period': 10, 'multiplier': 3},
                                   {'id': uuid.uuid4().hex, 'type': 'Super Trend', 'period': 20, 'multiplier': 5}],
                }
                # Create config file
                with open('alor/tickers/'+ticker+"/config.json", 'w') as f:
                    json.dump(default, f)
                logger.info(f"Created config file for {ticker}")

            file_path = 'alor/tickers/'+ticker+"/quotes.csv"  # Path to quotes file
            api = AlorAPI()  # Initialize AlorAPI

            # **CREATE OR UPDATE QUOTES**

            # Check if quotes file exists
            if not os.path.exists(file_path):

                now = datetime.now(timezone.utc)  # Get current date and time
                one_month_ago = now - timedelta(days=31)  # Subtract approximately 1 month ago
                first_day_of_month = one_month_ago.replace(day=1, hour=0, minute=0, second=0, microsecond=0,
                                                           tzinfo=timezone(timedelta(hours=3)))  # Get first day of current month
                try:
                    quotes = asyncio.run(api.get_ticker_data(ticker, first_day_of_month))  # Get quotes for period
                except Exception as e:
                    logger.error(f"Error getting quotes for {ticker}: {e}")

                # Check if quotes is not empty
                if not quotes.empty:
                    quotes.to_csv(file_path, index=False)  # save quotes to file
                else:
                    logger.info(f"No data for {ticker} in the last month")

                logger.info(f"Created quotes file for {ticker}")

            # Update quotes
            else:
                quotes = pd.read_csv(file_path)  # Read file with quotes

                last_write_date = datetime.strptime(
                    quotes.iloc[-1]["DATE"], "%Y%m%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=3)))  # Get last write date
                try:
                    new_quotes = asyncio.run(api.get_ticker_data(ticker, last_write_date))  # Get new quotes for period
                except Exception as e:
                    logger.error(f"Error getting quotes for {ticker}: {e}")

                quotes = pd.concat([quotes.iloc[:-1], new_quotes])  # Combine quotes and new quotes into one DataFrame
                quotes.to_csv(file_path, index=False)  # save quotes to file

                logger.info(f"Updated quotes file for {ticker}")

            percentage += percent_step
            print(f"Downloaded {ticker} quotes, {percentage:.2f}% completed")
