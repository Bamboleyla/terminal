import os
import pandas as pd
import finplot as fplt
import logging
import json

from terminal.indicators.super_trend import Super_Trend

logger = logging.getLogger(__name__)

super_trend = Super_Trend()


class Terminal:
    def __init__(self):
        pass

    def prepare(self):
        # **CREATE OR UPDATE DATA**
        # Check ticker directory
        if not os.path.exists('terminal/data/'):
            # Create ticker directory
            os.makedirs('terminal/data/')
            logger.info(f"Created directory for terminal data")

        file_path = 'terminal/data/sber.csv'  # Path to data file
        # Check if data file exists
        if not os.path.exists(file_path):
            quotes = pd.read_csv('alor/tickers/SBER/quotes.csv')
            with open('alor/tickers/SBER/config.json') as json_file:
                config = json.load(json_file)
                for indicator in config['indicators']:
                    if indicator['type'] == 'Super Trend':
                        quotes = super_trend.add_indicator(quotes, indicator)

            quotes.to_csv(file_path)
            logger.info(f"Created data file for terminal")
        else:
            pass

    def show(self):
        data = pd.read_csv('terminal/data/sber.csv')

        fplt.foreground = '#FFFFFF'
        fplt.background = '#000000'
        fplt.cross_hair_color = '#FFFFFF'

        data.set_index('DATE', inplace=True)
        data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')

        fplt.candlestick_ochl(data[['OPEN', 'CLOSE', 'HIGH', 'LOW']].tail(100))
        fplt.add_legend("SBER")
        fplt.show()
