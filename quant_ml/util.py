from collections import OrderedDict

import numpy as np
from numba import guvectorize, float32, int32, float64, int64
from pandas.core.base import PandasObject


def one_hot(index, len):
    arr = np.zeros(len)

    if np.issubdtype(np.uint32, np.integer):
        arr[index] = 1.0
    elif index.values >= 0:
        arr[index] = 1.0
    else:
        arr += np.NAN

    return arr


def unique(items):
    return list(OrderedDict.fromkeys(items))


def arange_open(start, stop, step, round=None):
    arr = np.arange(start, stop + step / 10, step)

    if len(arr) > 0:
        arr[0] = -float('inf')
        arr[-1] = float('inf')

    return arr if round is None else arr.round(round)


def pandas_data(df, col):
    if isinstance(col, PandasObject):
        return col
    else:
        return df[col]


@guvectorize([(float32[:], int32, float32[:]),
              (float64[:], int64, float64[:])], '(n),()->(n)')
def wilders_smoothing(arr: np.ndarray, period: int, res: np.ndarray):
    assert period > 0
    alpha = (period - 1) / period
    beta = 1 / period

    res[0:period] = np.nan
    res[period - 1] = arr[0:period].mean()
    for i in range(period, len(arr)):
        res[i] = alpha * res[i-1] + arr[i] * beta


class LazyInit(object):

    def __init__(self, supplier):
        self.supplier = supplier
        self.value = None

    def __call__(self, *args, **kwargs):
        if self.value is not None:
            return self.value
        else:
            self.value = self.supplier()
            return self.value

    def __getstate__(self):
        return self.supplier

    def __setstate__(self, state):
        self.supplier = state
        self.value = None
