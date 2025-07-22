import finplot as fplt
import pandas as pd
from .methods.prepare import prepare_date
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

        pc_period, st_period, st_multiplier = self.strategy.get_indicators_params()

        # Calculate indicators
        df = price_chanel(df, pc_period)
        df = super_trend(df, [{"period": st_period, "multiplier": st_multiplier}])

        self.strategy.run(df)
