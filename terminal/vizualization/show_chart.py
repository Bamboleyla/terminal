import pandas as pd
import finplot as fplt

from .update_chart import update_chart


def show_chart(ticker_config):
    data = pd.read_csv('terminal/data/SBER/sber.csv')

    fplt.foreground = '#FFFFFF'
    fplt.background = '#000000'
    fplt.cross_hair_color = '#FFFFFF'

    plot_data = data.copy()
    plot_data.set_index('DATE', inplace=True)
    plot_data.index = pd.to_datetime(plot_data.index).tz_localize('Etc/GMT-5')
    plot_data = plot_data.tail(100)

    for indicator in ticker_config['indicators']:
        if indicator['type'] == 'super_trend':
            for item in indicator['show']:
                fplt.plot(plot_data[item['column']], legend=item['legend'], color=item['color'], width=item['width'])

    fplt.candlestick_ochl(plot_data[['OPEN', 'CLOSE', 'HIGH', 'LOW']])
    fplt.add_legend("SBER")
    fplt.timer_callback(lambda: update_chart(ticker_config, data), 10)  # start update timer
    fplt.show()
