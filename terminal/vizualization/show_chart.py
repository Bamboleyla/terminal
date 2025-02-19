import finplot as fplt
import pandas as pd

from .update_chart import update_chart


def show_chart(ticker_config):
    # Download historical data
    data = pd.read_csv('terminal/data/SBER/sber.csv')

    # Set up the colors of the graphics
    fplt.foreground = '#FFFFFF'
    fplt.background = '#000000'
    fplt.cross_hair_color = '#FFFFFF'

    # Prepare data for display
    plot_data = data.copy()
    plot_data.set_index('DATE', inplace=True)
    plot_data.index = pd.to_datetime(plot_data.index).tz_localize('Etc/GMT-5')
    plot_data = plot_data.tail(100)

    # We create a chart
    ax = fplt.create_plot('SBER Chart')

    # Create LIVE objects for candles and indicators
    # Number of Live objects: 1 (candles) + number of indicators lines
    num_indicators = sum(len(indicator['show']) for indicator in ticker_config['indicators'])
    live_objects = fplt.live(1 + num_indicators)  # The first object is candles, the rest are indicators' lines

    # Initialize candles
    candle_live = live_objects[0]
    candle_live.candlestick_ochl(plot_data[['OPEN', 'CLOSE', 'HIGH', 'LOW']])

    # Initialize the indicators
    indicator_live_objects = live_objects[1:]  # remaining objects for indicators
    indicator_index = 0  # Index for tracking the current Live object

    for indicator in ticker_config['indicators']:
        if indicator['type'] == 'super_trend':
            for item in indicator['show']:
                # Assign a Live object for each indicator line
                indicator_live_objects[indicator_index].plot(
                    plot_data[item['column']],
                    legend=item['legend'],
                    color=item['color'],
                    width=item['width']
                )
                indicator_index += 1  # move on to the next Live object

    # Add the legend
    fplt.add_legend("SBER", ax=ax)

    # Launch a timer for updating chart every 10 seconds
    fplt.timer_callback(lambda: update_chart(ticker_config, data, live_objects), 10)

    # We display chart
    fplt.show()
