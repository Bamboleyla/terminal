import pandas as pd
import os
from myLib.indicators import price_chanel, super_trend


def prepare_date(broker, strategy) -> pd.DataFrame:
    # 1. Get tickers list from config
    share = strategy.get_config()["share"]
    data = pd.DataFrame()

    # 2. Process each ticker in the list

    ticker_dir = os.path.join("t_terminal\data", share["tiker"])
    now = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    # 2.1. If ticker's data directory doesn't exist
    if not os.path.exists(ticker_dir):
        os.makedirs(ticker_dir)
        print(f"Created directory for ticker: {ticker_dir}")

        # 2.2. Set time range for initial data load (start of current week)
        from_date = (
            (
                pd.Timestamp.now(tz="UTC")
                - pd.Timedelta(days=pd.Timestamp.now(tz="UTC").weekday())
            )
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        # 2.3. Load data into ticker's directory
        data = broker.get_candles(
            instrumentId=share["figi"], start_date=from_date, end_date=now
        )
    # 2.1 If ticker's data directory exists
    else:
        # 2.2. Read data from ticker's directory
        data = pd.read_csv(os.path.join(ticker_dir, "data.csv"))
        # 2.3. Select only necessary columns for further processing
        data = data[["DATE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]]
        # 2.4. Set time range for new data load (last date in file)
        last_date = (
            pd.to_datetime(data["DATE"].iloc[-1]) - pd.Timedelta(hours=3)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        # 2.5. Load new data into ticker's directory
        new_candles = broker.get_candles(
            instrument_id=share["figi"], start_date=last_date, end_date=now
        )
        data = pd.concat([data.iloc[:-1], new_candles])

    # 3. Add indicators to data
    for indicator in strategy.get_config()["indicators"]:
        if indicator["type"] == "price_chanel":
            data = price_chanel(df=data, period=indicator["period"])
        elif indicator["type"] == "super_trend":
            data = super_trend(
                df=data,
                config=[
                    {
                        "period": indicator["period"],
                        "multiplier": indicator["multiplier"],
                    }
                ],
            )
        else:
            raise ValueError("Indicator type is not supported")
    data.to_csv(os.path.join(ticker_dir, "data.csv"), index=False)
    return data
