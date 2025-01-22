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
        # Check directory for terminal data
        if not os.path.exists('terminal/data/'):
            # Create directory for terminal data
            os.makedirs('terminal/data/')
            logger.info(f"Created directory for terminal data")

        if not os.path.exists('terminal/data/SBER'):
            # Create ticker directory
            os.makedirs('terminal/data/SBER')
            logger.info(f"Created directory for SBER data")

        if not os.path.exists('terminal/data/SBER/indicators'):
            # Create directory for indicators
            os.makedirs('terminal/data/SBER/indicators')
            logger.info(f"Created directory for SBER indicators")

        file_path = 'terminal/data/sber.csv'  # Path to data file
        quotes = pd.read_csv('alor/tickers/SBER/quotes.csv')

        with open('alor/tickers/SBER/config.json') as json_file:
            config = json.load(json_file)
            # Check if data file exists
            if not os.path.exists(file_path):
                terminal_data = quotes.copy()  # Copy quotes to terminal data
                for indicator in config['indicators']:
                    if indicator['type'] == 'super_trend':
                        indicator_data = super_trend.calculate_indicator(quotes, indicator)
                        indicator_data.to_csv(f'terminal/data/SBER/indicators/{indicator["id"]}.csv', index=False)

                        terminal_data[f'{indicator["show"][0]["column"]}'] = indicator_data['ST_UPPER']
                        terminal_data[f'{indicator["show"][1]["column"]}'] = indicator_data['ST_LOWER']

                logger.info(f"Data file for terminal was created")
            else:
                terminal_data = pd.read_csv(file_path)
                terminal_data = pd.concat([terminal_data.iloc[:-1], quotes.iloc[(len(terminal_data)-1):]])

                for indicator in config['indicators']:
                    if indicator['type'] == 'super_trend':
                        indicator_data = pd.read_csv(f'terminal/data/SBER/indicators/{indicator["id"]}.csv')
                        start_index = len(indicator_data)-1
                        indicator_data = pd.concat([indicator_data.iloc[:-1], quotes.iloc[start_index:]])

                        updated_indicator_data = super_trend.calculate_indicator(indicator_data, indicator, start_index)
                        updated_indicator_data = pd.concat([indicator_data.iloc[:start_index], updated_indicator_data.iloc[start_index:]])
                        updated_indicator_data = updated_indicator_data[updated_indicator_data.columns.drop('VOLUME')]
                        updated_indicator_data.to_csv(f'terminal/data/SBER/indicators/{indicator["id"]}.csv', index=False)

                        terminal_data[f'{indicator["show"][0]["column"]}'] = updated_indicator_data['ST_UPPER']
                        terminal_data[f'{indicator["show"][1]["column"]}'] = updated_indicator_data['ST_LOWER']

                logger.info(f"Data file for terminal was updated")

            terminal_data.to_csv(file_path, index=False)  # Save data to file

    def show(self):
        data = pd.read_csv('terminal/data/sber.csv')

        fplt.foreground = '#FFFFFF'
        fplt.background = '#000000'
        fplt.cross_hair_color = '#FFFFFF'

        data.set_index('DATE', inplace=True)
        data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')
        data = data.tail(100)

        with open('alor/tickers/SBER/config.json') as json_file:
            config = json.load(json_file)
            for indicator in config['indicators']:
                if indicator['type'] == 'super_trend':
                    for item in indicator['show']:
                        fplt.plot(data[item['column']], legend=item['legend'], color=item['color'], width=item['width'])

        fplt.candlestick_ochl(data[['OPEN', 'CLOSE', 'HIGH', 'LOW']])
        fplt.add_legend("Ticker-SBER")
        fplt.show()
