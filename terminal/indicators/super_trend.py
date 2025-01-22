import pandas as pd
import talib


class Super_Trend:

    def calculate_indicator(self, quotes: pd.DataFrame, indicator: dict, start_index: int = None) -> pd.DataFrame:
        # Extracting parameters from the indicator dictionary
        period = indicator['period']
        multiplier = indicator['multiplier']

        # Creating a copy of the DataFrame without the VOLUME column
        data = quotes[quotes.columns.drop('VOLUME')].copy()

        # Calculating ATR (Average True Range)
        data['ATR'] = talib.ATR(quotes['HIGH'].values, quotes['LOW'].values, quotes['CLOSE'].values,
                                timeperiod=period).round(2)

        # Calculate the upper and lower SuperTrend lines
        data['UPPER_LINE'] = (data['HIGH'] + (multiplier * data['ATR'])).round(2)
        data['LOWER_LINE'] = (data['LOW'] - (multiplier * data['ATR'])).round(2)

        # Initializing columns for SuperTrend indicator values
        data['ST_UPPER'] = pd.Series(dtype=float)
        data['ST_LOWER'] = pd.Series(dtype=float)

        trend = 'lower'
        # Calculating SuperTrend
        for index, row in data.iterrows():
            if start_index is not None and index < start_index:
                if index == 0:
                    trend = 'lower' if not pd.isna(data.loc[start_index, 'ST_LOWER']) else 'upper'
                continue
            # Check if the upper and lower SuperTrend lines are None
            if pd.isnull(row['UPPER_LINE']) or pd.isnull(row['LOWER_LINE']):
                continue

            upper = round(row['UPPER_LINE'], 2) if pd.isnull(data.loc[index - 1, 'ST_UPPER']
                                                             ) else round(min(data.loc[index - 1, 'ST_UPPER'], row['UPPER_LINE']), 2)
            lower = round(row['LOWER_LINE'], 2) if pd.isnull(data.loc[index - 1, 'ST_LOWER']
                                                             ) else round(max(data.loc[index - 1, 'ST_LOWER'], row['LOWER_LINE']), 2)
            close = row['CLOSE']
            open = row['OPEN']

            if trend == 'lower':
                if open >= lower:
                    if close >= lower:
                        data.loc[index, 'ST_LOWER'] = lower
                    elif close < lower:
                        data.loc[index, 'ST_UPPER'] = row['UPPER_LINE']
                        trend = 'upper'
                    else:
                        raise ValueError("error:001 Something went wrong")
                elif open < lower:
                    data.loc[index, 'ST_UPPER'] = row['UPPER_LINE']
                    trend = 'upper'
                else:
                    raise ValueError("error:002 Something went wrong")
            elif trend == 'upper':
                if open <= upper:
                    if close <= upper:
                        data.loc[index, 'ST_UPPER'] = upper
                    elif close > upper:
                        data.loc[index, 'ST_LOWER'] = row['LOWER_LINE']
                        trend = 'lower'
                    else:
                        raise ValueError("error:003 Something went wrong")
                elif open > upper:
                    data.loc[index, 'ST_LOWER'] = row['LOWER_LINE']
                    trend = 'lower'
                else:
                    raise ValueError("error:004 Something went wrong")
            else:
                raise ValueError("error:005 Unexpected value")

        return data
