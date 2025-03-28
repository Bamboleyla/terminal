import os
import json
import pandas as pd
import logging
import uuid

from myLib import Brokers
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)
brokers = Brokers()


class AlorDownloader:

    def prepare(self):

        percent_step = 100 / len(["SBER"])  # initial percentage
        percentage = 0.0  # complete percentage

        for ticker in ["SBER"]:
            # Check ticker directory
            if not os.path.exists("alor/tickers/" + ticker + "/"):
                # Create ticker directory
                os.makedirs("alor/tickers/" + ticker + "/")
                logger.info(f"Created directory for {ticker}")

            # Check config file
            if not os.path.exists("alor/tickers/" + ticker + "/config.json"):
                id1 = uuid.uuid4().hex[:6]
                id2 = uuid.uuid4().hex[:6]
                # Create default config
                default = {
                    "indicators": [
                        {
                            "id": id1,
                            "type": "super_trend",
                            "period": 10,
                            "multiplier": 3,
                            "show": [
                                {
                                    "column": f"ST_UPPER_{id1}",
                                    "legend": "ST_UP 3 10",
                                    "color": "#ed6464",
                                    "width": 2,
                                },
                                {
                                    "column": f"ST_LOWER_{id1}",
                                    "legend": "ST_LOW 3 10",
                                    "color": "#7dbe62",
                                    "width": 2,
                                },
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex[:6],
                            "type": "super_trend",
                            "period": 20,
                            "multiplier": 5,
                            "show": [
                                {
                                    "column": f"ST_UPPER_{id2}",
                                    "legend": "ST_UP 5 20",
                                    "color": "#d91717",
                                    "width": 3,
                                },
                                {
                                    "column": f"ST_LOWER_{id2}",
                                    "legend": "ST_LOW 5 20",
                                    "color": "#578544",
                                    "width": 3,
                                },
                            ],
                        },
                    ],
                }
                # Create config file
                with open("alor/tickers/" + ticker + "/config.json", "w") as f:
                    json.dump(default, f)
                logger.info(f"Created config file for {ticker}")

            file_path = "alor/tickers/" + ticker + "/quotes.csv"  # Path to quotes file

            # **CREATE OR UPDATE QUOTES**

            # Check if quotes file exists
            if not os.path.exists(file_path):

                now = datetime.now(timezone.utc)  # Get current date and time
                one_month_ago = now - timedelta(
                    days=31
                )  # Subtract approximately 1 month ago
                first_day_of_month = one_month_ago.replace(
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                    tzinfo=timezone(timedelta(hours=3)),
                )  # Get first day of current month
                try:
                    quotes = brokers.alor.downloader.get_quotes(
                        ticker=ticker, start_date=first_day_of_month, tf=300
                    )
                    # Get quotes for period
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
                    quotes.iloc[-1]["DATE"], "%Y%m%d %H:%M:%S"
                ).replace(
                    tzinfo=timezone(timedelta(hours=3))
                )  # Get last write date
                if (
                    quotes.iloc[0]["TICKER"] != "SBER"
                    and (datetime.now(timezone.utc) - last_write_date).days < 7
                ):
                    percentage += percent_step
                    print(
                        f"Loading {ticker} quotes was skipped, {percentage:.2f}% completed"
                    )
                    continue  # Skip if last write date is less than 7 days ago
                try:
                    new_quotes = brokers.alor.downloader.get_quotes(
                        ticker=ticker, start_date=last_write_date, tf=300
                    )  # Get new quotes for period
                    quotes = pd.concat(
                        [quotes.iloc[:-1], new_quotes]
                    )  # Combine quotes and new quotes into one DataFrame
                    quotes.to_csv(file_path, index=False)  # save quotes to file
                except Exception as e:
                    logger.error(f"Error getting quotes for {ticker}: {e}")

                logger.info(f"Updated quotes file for {ticker}")

            percentage += percent_step
            print(f"Downloaded {ticker} quotes, {percentage:.2f}% completed")
