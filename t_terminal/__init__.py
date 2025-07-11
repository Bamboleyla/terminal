import finplot as fplt
import pandas as pd
from .methods.prepare import prepare_date
from datetime import datetime
from myLib.indicators import price_chanel, super_trend


__all__ = ["T_Terminal"]


class T_Terminal:

    def __init__(self, strategy, broker) -> None:
        self.strategy = strategy
        self.broker = broker
        self.data = pd.DataFrame()

    def prepare(self):
        self.data = prepare_date(broker=self.broker, strategy=self.strategy)

    def run(self) -> pd.DataFrame:
        """Builds an interactive candlestick chart with 5-second data updates."""
        # Set graph colors
        fplt.foreground = "#FFFFFF"
        fplt.background = "#000000"
        fplt.cross_hair_color = "#FFFFFF"

        # Load and prepare data
        df = self.data.tail(200)
        df["DATE"] = pd.to_datetime(df["DATE"]) - pd.Timedelta(hours=5)
        df = df.set_index("DATE")

        # Create plot
        ax = fplt.create_plot("SBER Chart")

        # Create Live objects for candles and indicators
        live_objects = fplt.live(6)  # 1 for candles + 5 for indicators

        # Initialize candles
        live_objects[0].candlestick_ochl(df[["OPEN", "CLOSE", "HIGH", "LOW"]])

        # Initialize indicators
        live_objects[1].plot(
            df["PC_20_HIGH"], color="#1f77b4", width=1.5, legend="PC High"
        )
        live_objects[2].plot(
            df["PC_20_LOW"], color="#1f77b4", width=1.5, legend="PC Low"
        )
        live_objects[3].plot(
            df["PC_20_MID"], color="#ffffff", width=1.5, legend="PC Mid"
        )
        live_objects[4].plot(
            df["ST_UPPER_30_7"], color="#d62728", width=3, legend="ST Upper"
        )
        live_objects[5].plot(
            df["ST_LOWER_30_7"], color="#2ca02c", width=3, legend="ST Lower"
        )

        # Add legend
        fplt.add_legend("SBER", ax=ax)

        # Start timer for data updates
        fplt.timer_callback(lambda: self.update_plot(live_objects), 10.0)

        # Display plot
        fplt.show()

    def update_plot(self, live_objects):
        """Updates data on the plot."""
        try:
            # Load and prepare new data
            df = self.load_and_prepare_data()
            # Update candles
            live_objects[0].candlestick_ochl(
                df[["OPEN", "CLOSE", "HIGH", "LOW"]],
                xaxis_autorange=True,
                xaxis_autorange_relayout=True,
            )

            # Update indicators
            live_objects[1].plot(df["PC_20_HIGH"], color="#1f77b4", width=1.5)
            live_objects[2].plot(df["PC_20_LOW"], color="#1f77b4", width=1.5)
            live_objects[3].plot(df["PC_20_MID"], color="#ffffff", width=1.5)
            live_objects[4].plot(df["ST_UPPER_30_7"], color="#d62728", width=3)
            live_objects[5].plot(df["ST_LOWER_30_7"], color="#2ca02c", width=3)

            print(f"Data updated: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Error updating data: {e}")

    def load_and_prepare_data(self):
        """Loads data from file and calculates indicators."""
        # Load data
        now = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        last_date = (
            pd.to_datetime(self.data["DATE"].iloc[-1]) - pd.Timedelta(hours=3)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

        new_candles = self.broker.get_candles(
            instrument_id="BBG004730N88",
            start_date=last_date,
            end_date=now,
            is_complete=False,
        )
        print(new_candles.iloc[-1])
        df = pd.concat([self.data.iloc[:-1], new_candles])

        # Process date
        df["DATE"] = pd.to_datetime(df["DATE"]) - pd.Timedelta(hours=5)
        df = df.set_index("DATE")

        # Select last 100 candles
        df = df.tail(200)

        # Calculate indicators
        df = price_chanel(df, 20)
        df = super_trend(df, [{"period": 30, "multiplier": 7}])

        return df
