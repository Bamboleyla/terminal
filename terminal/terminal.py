import os
import pandas as pd
import finplot as fplt
import logging
import json
import asyncio

from datetime import datetime, timezone, timedelta
from terminal.indicators.super_trend import Super_Trend
from alor.api import AlorAPI

logger = logging.getLogger(__name__)

super_trend = Super_Trend()


class Terminal:
    def __init__(self):
        self.__api = AlorAPI()

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

        file_path = 'terminal/data/SBER/sber.csv'  # Path to data file
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

    def __update(self):
        data = pd.read_csv('terminal/data/SBER/sber.csv')
        last_write_date = datetime.strptime(
            data.iloc[-1]["DATE"], "%Y%m%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=3)))
        # result = asyncio.run(self.__api.get_ticker_data(ticker='SBER', start_date=last_write_date, tf=10))
        # result.to_csv('terminal/data/ticks.csv', index=False)
        ticks = pd.read_csv('terminal/data/ticks.csv')
        future_date = last_write_date + timedelta(minutes=5)
        ticks['DATE'] = pd.to_datetime(ticks['DATE'], format='%Y%m%d %H:%M:%S').dt.tz_localize('Europe/Moscow').dt.tz_convert('Etc/GMT-3')

        five_min_ticks = ticks[(ticks['DATE'] >= last_write_date.strftime('%Y%m%d %H:%M:%S')) & (ticks['DATE'] < future_date.strftime('%Y%m%d %H:%M:%S'))]

        new_candles = pd.DataFrame(columns=data.columns)
        new_candles.loc[0, "TICKER"] = "SBER"
        new_candles.loc[0, "DATE"] = future_date.strftime('%Y%m%d %H:%M:%S')
        new_candles.loc[0, "OPEN"] = five_min_ticks.iloc[0]["OPEN"]
        new_candles.loc[0, "HIGH"] = five_min_ticks["HIGH"].max()
        new_candles.loc[0, "LOW"] = five_min_ticks["LOW"].min()
        new_candles.loc[0, "CLOSE"] = five_min_ticks.iloc[-1]["CLOSE"]
        new_candles.loc[0, "VOLUME"] = five_min_ticks["VOLUME"].sum()
        print(new_candles)

        with open('alor/tickers/SBER/config.json') as json_file:
            config = json.load(json_file)

            terminal_data = pd.concat([data, new_candles], ).reset_index(drop=True)

            is_there_new_data = ticks['DATE'].max() > future_date

            for indicator in config['indicators']:
                if indicator['type'] == 'super_trend':
                    indicator_data = pd.read_csv(f'terminal/data/SBER/indicators/{indicator["id"]}.csv')
                    start_index = len(indicator_data)-1
                    indicator_data = pd.concat([indicator_data.iloc[:-1], terminal_data.iloc[start_index:]])

                    updated_indicator_data = super_trend.calculate_indicator(indicator_data, indicator, start_index)
                    updated_indicator_data = pd.concat([indicator_data.iloc[:start_index], updated_indicator_data.iloc[start_index:]])
                    updated_indicator_data = updated_indicator_data[updated_indicator_data.columns.drop('VOLUME')]
                    if is_there_new_data:
                        updated_indicator_data.to_csv(f'terminal/data/SBER/indicators/{indicator["id"]}.csv', index=False)

                    terminal_data[f'{indicator["show"][0]["column"]}'] = updated_indicator_data['ST_UPPER']
                    terminal_data[f'{indicator["show"][1]["column"]}'] = updated_indicator_data['ST_LOWER']

                if is_there_new_data:
                    # terminal_data.to_csv('terminal/data/SBER/sber.csv' , index=False)  # Save data to file
                    print('Done')

            # terminal_data.set_index('date', inplace=True)
            # terminal_data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')
            # terminal_data = data.tail(100)

            # fplt.candlestick_ochl(data[['open', 'close', 'high', 'low']].tail(100))
            # fplt.refresh()

    def show(self):
        data = pd.read_csv('terminal/data/SBER/sber.csv')

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
        fplt.timer_callback(self.__update, 10)  # start update timer
        fplt.show()
