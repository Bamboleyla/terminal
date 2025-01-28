import finplot as fplt
import pandas as pd

from datetime import datetime, timezone, timedelta
from ..indicators.super_trend import Super_Trend


def update_chart(ticker_config):
    data = pd.read_csv('terminal/data/SBER/sber.csv')
    super_trend = Super_Trend()
    last_write_date = datetime.strptime(
        data.iloc[-1]["DATE"], "%Y%m%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=3)))
    # result = asyncio.run(self.__api.get_ticker_data(ticker='SBER', start_date=last_write_date, tf=10))
    # result.to_csv('terminal/data/ticks.csv', index=False)
    ticks = pd.read_csv('terminal/data/ticks.csv')
    future_date = last_write_date + timedelta(minutes=5)
    ticks['DATE'] = pd.to_datetime(ticks['DATE'], format='%Y%m%d %H:%M:%S').dt.tz_localize('Europe/Moscow').dt.tz_convert('Etc/GMT-3')

    five_min_ticks = ticks[(ticks['DATE'] >= last_write_date.strftime('%Y%m%d %H:%M:%S')) & (ticks['DATE'] < future_date.strftime('%Y%m%d %H:%M:%S'))]

    new_candle = pd.DataFrame({
        "TICKER": ["SBER"],
        "DATE": [future_date.strftime('%Y%m%d %H:%M:%S')],
        "OPEN": [five_min_ticks.iloc[0]["OPEN"]],
        "HIGH": [five_min_ticks["HIGH"].max()],
        "LOW": [five_min_ticks["LOW"].min()],
        "CLOSE": [five_min_ticks.iloc[-1]["CLOSE"]],
        "VOLUME": [five_min_ticks["VOLUME"].sum()],
    }, columns=data.columns)
    print(new_candle)
    terminal_data = pd.concat([data, new_candle], ignore_index=True)

    is_there_new_data = ticks['DATE'].max() > future_date

    for indicator in ticker_config['indicators']:
        if indicator['type'] == 'super_trend':
            indicator_data = pd.read_csv(f'terminal/data/SBER/indicators/{indicator["id"]}.csv')
            start_index = len(indicator_data)-1
            indicator_data = pd.concat([indicator_data.iloc[:-1], terminal_data.iloc[start_index:]])
            indicator_data = indicator_data.astype({col: 'float64' for col in indicator_data.columns if col not in ['TICKER', 'DATE']})
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

    terminal_data.set_index('DATE', inplace=True)
    terminal_data.index = pd.to_datetime(terminal_data.index).tz_localize('Etc/GMT-5')
    terminal_data = terminal_data .tail(100)

    fplt.candlestick_ochl(terminal_data[['OPEN', 'CLOSE', 'HIGH', 'LOW']])
    fplt.refresh()
