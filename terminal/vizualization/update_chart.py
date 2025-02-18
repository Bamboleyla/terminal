import finplot as fplt
import pandas as pd
import asyncio

from alor.api import AlorAPI
from datetime import datetime, timezone, timedelta
from ..indicators.super_trend import Super_Trend

super_trend = Super_Trend()
api = AlorAPI()


def update_chart(ticker_config: dict, data: pd.DataFrame) -> None:
    start_time = datetime.now()  # start time

    last_write_date = datetime.strptime(
        data.iloc[-1]["DATE"], "%Y%m%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=3)))  # get last write date

    new_quotes = asyncio.run(api.get_ticker_data(ticker='SBER', start_date=last_write_date, tf=300))  # get new quotes

    terminal_data = pd.concat([data.iloc[-100:-1], new_quotes]).reset_index(drop=True)  # add new quotes to terminal data and reset index

    # calculate and update indicators
    for indicator in ticker_config['indicators']:
        if indicator['type'] == 'super_trend':
            indicator_data = pd.read_csv(f'terminal/data/SBER/indicators/{indicator["id"]}.csv').iloc[-100:]

            indicator_data = pd.concat([indicator_data.iloc[:-1], new_quotes]).reset_index(drop=True)
            indicator_data = indicator_data.astype({col: 'float64' for col in indicator_data.columns if col not in ['TICKER', 'DATE']})

            updated_indicator_data = super_trend.calculate_indicator(indicator_data, indicator, 99)

            terminal_data[f'{indicator["show"][0]["column"]}'] = updated_indicator_data['ST_UPPER']
            terminal_data[f'{indicator["show"][1]["column"]}'] = updated_indicator_data['ST_LOWER']

    terminal_data.set_index('DATE', inplace=True)
    terminal_data.index = pd.to_datetime(terminal_data.index).tz_localize('Etc/GMT-5')
    terminal_data.drop(columns=['TICKER'], inplace=True)
    terminal_data.to_csv('terminal/data/session_data.csv', index=True)

    for indicator in ticker_config['indicators']:
        if indicator['type'] == 'super_trend':
            for item in indicator['show']:
                fplt.plot(terminal_data[item['column']], color=item['color'], width=item['width'])

    fplt.candlestick_ochl(terminal_data[['OPEN', 'CLOSE', 'HIGH', 'LOW']].tail(100))
    fplt.refresh()

    last_row = terminal_data.iloc[-1]
    print(f'Update time: {datetime.now() - start_time}')
    print(f'DATE: {last_row.name}')
    for column in ['OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']:
        print(f'{column}: {last_row[column]}')
