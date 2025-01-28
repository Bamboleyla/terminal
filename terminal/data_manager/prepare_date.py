import os
import logging
import pandas as pd

from ..indicators.super_trend import Super_Trend

logger = logging.getLogger(__name__)
super_trend = Super_Trend()


def prepare_date(quotes, ticker_config):
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

    # Check if data file exists
    if not os.path.exists(file_path):
        terminal_data = quotes.copy()  # Copy quotes to terminal data
        for indicator in ticker_config['indicators']:
            if indicator['type'] == 'super_trend':
                indicator_data = super_trend.calculate_indicator(quotes, indicator)
                indicator_data.to_csv(f'terminal/data/SBER/indicators/{indicator["id"]}.csv', index=False)

                terminal_data[f'{indicator["show"][0]["column"]}'] = indicator_data['ST_UPPER']
                terminal_data[f'{indicator["show"][1]["column"]}'] = indicator_data['ST_LOWER']

        logger.info(f"Data file for terminal was created")
    else:
        terminal_data = pd.read_csv(file_path)
        terminal_data = pd.concat([terminal_data.iloc[:-1], quotes.iloc[(len(terminal_data)-1):]])

        for indicator in ticker_config['indicators']:
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
