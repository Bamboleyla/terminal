import pandas as pd
import finplot as fplt

from .update_chart import update_chart


def show_chart(ticker_config):
    data = pd.read_csv('terminal/data/SBER/sber.csv')

    fplt.foreground = '#FFFFFF'
    fplt.background = '#000000'
    fplt.cross_hair_color = '#FFFFFF'

    data.set_index('DATE', inplace=True)
    data.index = pd.to_datetime(data.index).tz_localize('Etc/GMT-5')
    data = data.tail(100)

    for indicator in ticker_config['indicators']:
        if indicator['type'] == 'super_trend':
            for item in indicator['show']:
                fplt.plot(data[item['column']], legend=item['legend'], color=item['color'], width=item['width'])

    fplt.candlestick_ochl(data[['OPEN', 'CLOSE', 'HIGH', 'LOW']])
    fplt.add_legend("Ticker-SBER")
    fplt.timer_callback(lambda: update_chart(ticker_config), 10)  # start update timer
    fplt.show()
