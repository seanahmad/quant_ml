import pandas as _pd
from typing import Union as _Union
import quant_ml.indicator.features as _i

_PANDAS = _Union[_pd.DataFrame, _pd.Series]


def ta_future_pct_of_mean(df: _pd.Series, forecast_period=1, period=14):
    assert isinstance(df, _pd.Series)

    future = df.shift(-forecast_period)
    mean = df.rolling(period).mean()

    return (future / mean) - 1


def ta_future_sma_cross(df: _pd.Series, forecast_period=14, fast_period=12, slow_period=26):
    assert isinstance(df, _pd.Series)
    fast = _i.ta_sma(df, fast_period)
    slow = _i.ta_sma(df, slow_period)
    cross = _i.ta_cross_over(None, fast, slow) | _i.ta_cross_under(None, fast, slow)
    return cross.shift(-forecast_period)


def ta_future_macd_cross(df: _pd.Series, forecast_period=14, fast_period=12, slow_period=26, signal_period=9):
    assert isinstance(df, _pd.Series)

    # calculate all macd crossings
    macd = _i.ta_macd(df, fast_period=fast_period, slow_period=slow_period, signal_period=signal_period)
    zero = macd["histogram"] * 0
    cross = _i.ta_cross_over(macd["histogram"], zero) | _i.ta_cross_under(macd["histogram"], zero)
    return cross.shift(-forecast_period)