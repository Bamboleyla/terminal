import pandas as pd
import asyncio

from datetime import datetime, timezone, timedelta
from alor.api import AlorAPI
from ..indicators.super_trend import Super_Trend

super_trend = Super_Trend()
api = AlorAPI()


def update_chart(ticker_config: dict, data: pd.DataFrame, live_objects) -> None:
    start_time = datetime.now()

    # Get date of last candle in data
    last_write_date = datetime.strptime(
        data.iloc[-1]["DATE"], "%Y%m%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=3)))

    # Request new data
    new_quotes = asyncio.run(api.get_ticker_data(ticker='SBER', start_date=last_write_date, tf=300))

    # We combine old and new data
    terminal_data = pd.concat([data.iloc[-100:-1], new_quotes]).reset_index(drop=True)

    # Update indicators
    for indicator in ticker_config['indicators']:
        if indicator['type'] == 'super_trend':
            # Load indicator data
            indicator_data = pd.read_csv(f'terminal/data/SBER/indicators/{indicator["id"]}.csv').iloc[-100:]
            indicator_data = pd.concat([indicator_data.iloc[:-1], new_quotes]).reset_index(drop=True)
            indicator_data = indicator_data.astype({col: 'float64' for col in indicator_data.columns if col not in ['TICKER', 'DATE']})

            # Calculate indicator
            updated_indicator_data = super_trend.calculate_indicator(indicator_data, indicator, 99)

            # Update data for display
            terminal_data[f'{indicator["show"][0]["column"]}'] = updated_indicator_data['ST_UPPER']
            terminal_data[f'{indicator["show"][1]["column"]}'] = updated_indicator_data['ST_LOWER']

    # Prepare data for visualization
    terminal_data.set_index('DATE', inplace=True)
    terminal_data.index = pd.to_datetime(terminal_data.index).tz_localize('Etc/GMT-5')
    terminal_data.drop(columns=['TICKER'], inplace=True)
    terminal_data.to_csv('terminal/data/session_data.csv', index=True)

    # Update candles
    live_objects[0].candlestick_ochl(terminal_data[['OPEN', 'CLOSE', 'HIGH', 'LOW']])

    # Update indicators
    indicator_index = 1  # Index for tracking live indicator objects
    for indicator in ticker_config['indicators']:
        if indicator['type'] == 'super_trend':
            for item in indicator['show']:
                live_objects[indicator_index].plot(
                    terminal_data[item['column']],
                    legend=item['legend'],
                    color=item['color'],
                    width=item['width']
                )
                indicator_index += 1

    # Display information about last candle
    last_row = terminal_data.iloc[-1]
    print(f'Update time: {datetime.now() - start_time}')
    print(f'DATE: {last_row.name}')
    for column in ['OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']:
        print(f'{column}: {last_row[column]}')
