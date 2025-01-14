import os
import pandas as pd
import finplot as fplt


class Terminal:
    def __init__(self):
        pass

    def prepare(self):
        file_path = 'terminal/data/sber.csv'
        if not os.path.exists(file_path):
            with open('alor/tickers/SBER/quotes.csv', 'r') as source:
                with open(file_path, 'w') as dest:
                    dest.write(source.read())

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
