import pandas as pd
import talib


class Super_Trend:

    def add_indicator(self, quotes: pd.DataFrame, indicator: dict) -> pd.DataFrame:
        # Set names for indicator properties
        period = indicator['period']
        multiplier = indicator['multiplier']
        name_indicator = indicator['id']
        name_ATR = f'ATR_{indicator["period"]}'

        # Create a multi-level index for columns
        if not isinstance(quotes.columns, pd.MultiIndex):
            quotes.columns = pd.MultiIndex.from_product([quotes.columns, ['']])

        # Calculating ATR
        atr_values = talib.ATR(quotes['HIGH'].values, quotes['LOW'].values, quotes['CLOSE'].values,
                               timeperiod=period)

        # Assign ATR values ​​to the new column
        quotes.loc[:, (name_indicator, name_ATR)] = atr_values.round(2)

        # Calculate upper and lower SuperTrend lines using the multiplier
        quotes.loc[:, (name_indicator, 'UPPER_LINE')] = (quotes['HIGH'] + (multiplier * quotes[name_indicator][name_ATR])).round(2)
        quotes.loc[:, (name_indicator, 'LOWER_LINE')] = (quotes['LOW'] - (multiplier * quotes[name_indicator][name_ATR])).round(2)

        # Initialize columns for the SuperTrend values
        quotes.loc[:, (name_indicator, 'ST UPPER_LINE')] = pd.Series(dtype=float)
        quotes.loc[:, (name_indicator, 'ST LOWER_LINE')] = pd.Series(dtype=float)

        trend = 'lower'

        for index, row in quotes.iterrows():
            upper_line = row[name_indicator]['UPPER_LINE']
            lower_line = row[name_indicator]['LOWER_LINE']
            # Check if the upper and lower SuperTrend lines are None
            if pd.isnull(upper_line) or pd.isnull(lower_line):
                continue

            prev_st_upper = quotes.loc[index - 1, (name_indicator, 'ST UPPER_LINE')]
            prev_st_lower = quotes.loc[index - 1, (name_indicator, 'ST LOWER_LINE')]

            upper = round(upper_line, 2) if pd.isnull(prev_st_upper
                                                      ) else round(min(prev_st_upper, upper_line), 2)
            lower = round(lower_line, 2) if pd.isnull(prev_st_lower
                                                      ) else round(max(prev_st_lower, lower_line), 2)
            close = float(row['CLOSE'])
            open = float(row['OPEN'])

            if trend == 'lower':
                if open >= lower:
                    if close >= lower:
                        quotes.loc[index, (name_indicator, 'ST LOWER_LINE')] = lower
                    elif close < lower:
                        quotes.loc[index, (name_indicator, 'ST UPPER_LINE')] = round(row[name_indicator]['UPPER_LINE'], 2)
                        trend = 'upper'
                    else:
                        raise ValueError("error:001 Something went wrong")
                elif open < lower:
                    quotes.loc[index, (name_indicator, 'ST UPPER_LINE')] = round(row[name_indicator]['UPPER_LINE'], 2)
                    trend = 'upper'
                else:
                    raise ValueError("error:002 Something went wrong")
            elif trend == 'upper':
                if open <= upper:
                    if close <= upper:
                        quotes.loc[index, (name_indicator, 'ST UPPER_LINE')] = upper
                    elif close > upper:
                        quotes.loc[index, (name_indicator, 'ST LOWER_LINE')] = round(row[name_indicator]['LOWER_LINE'], 2)
                        trend = 'lower'
                    else:
                        raise ValueError("error:003 Something went wrong")
                elif open > upper:
                    quotes.loc[index, (name_indicator, 'ST LOWER_LINE')] = round(row[name_indicator]['LOWER_LINE'], 2)
                    trend = 'lower'
                else:
                    raise ValueError("error:004 Something went wrong")
            else:
                raise ValueError("error:005 Unexpected value")

        return quotes
