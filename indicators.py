import numpy as np
import time


def rolling_window(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def simple_moving_average(values, period):
    """
    Compute a moving average over a list.

    The first N values where N < period will have moving averages with period N.

    :param values: List of values
    :param period: The period over which to compute the simple moving average
    :return: The simple moving average of the data
    """

    if len(values) >= period:
        padding = np.full((period - 1,), np.nan)
        mean = np.mean(rolling_window(values, period), 1)
        return np.concatenate([padding, mean])

    raise RuntimeError("Can not compute SMA of dataset smaller than period")


def exponential_moving_average(values, smoothing_factor):
    """
    Compute an exponential moving average over a list.

    The first value will be unchanged from the source data as we have no historical data.

    :param values: List of values
    :param smoothing_factor: The degree of weighting decrease for previous observations
    :return: The exponential moving average of the data
    """

    ema = [values[0]]

    for i in range(1, len(values)):
        ema.append(smoothing_factor * values[i] + (1 - smoothing_factor) * ema[i - 1])
    return ema


def bollinger(prices, num_sd=2.0, period=20):
    """
    Compute the Bollinger bands for a list of prices.

    :param prices: List of prices
    :param stdev_multiplier: Constant factor for standard deviation of Bollinger bands, proportional to volatility
    :param period: The period over which to compute the underlying moving average and standard deviation
    :return: Tuple of (top band, bottom band) lists, representing the upper and lower Bollinger bands
    """

    sma = simple_moving_average(prices, period=period)
    msd = moving_standard_deviation(prices, period=period)

    stdevs = np.multiply(msd, num_sd)

    upper, lower = np.add(sma, stdevs), np.subtract(sma, stdevs)
    assert (len(upper) == len(prices))

    return upper, lower


def moving_standard_deviation(data, period):
    """
    Compute the moving standard deviation over a list.

    The first N values where N < period will have standard deviations with period N.

    :param data: List of values
    :param period: The period over which to compute the moving standard deviation
    :return: The moving standard deviation of the data
    """

    padding = np.full((period - 1,), np.nan)
    std = np.std(rolling_window(data, period), 1)
    return np.concatenate([padding, std])


def on_balance_volume(opens, closes, volumes):
    if not opens or not closes or not volumes:
        raise RuntimeError("Can not compute on_balance_volume of empty datasets")

    obv = 0
    obvs = []

    for open, close, volume in zip(opens, closes, volumes):
        if close - open > 0:
            obv += volume
        elif close != open:
            obv -= volume

        obvs.append(obv)

    return obvs


def relative_strength_index(values, period=14):
    rsis = []
    windows = rolling_window(values, period)

    for window in windows:
        gains = []
        losses = []

        for i in range(len(window) - 1):
            diff = window[i + 1] - window[i]
            if diff > 0:
                gains.append(diff)
            elif diff < 0:
                losses.append(-diff)
            else:
                pass

        if not gains:
            gains.append(1)

        if not losses:
            losses.append(1)

        rs = (sum(gains) / len(gains)) / (sum(losses) / len(losses))

        # (sum(gains) / max(1, len(gains))) / (max(1, (sum(losses) / max(1, len(losses)))))

        rsi = 100 - 100 / (1 + rs)
        rsis.append(rsi)

    # TODO: This is FIX
    padding = np.full((period - 1,), 0)

    result = np.concatenate([padding, np.array(rsis)])
    assert (len(result) == len(values))

    return result


def elder_ray(closes, highs, lows, period=13.0):
    ema = exponential_moving_average(closes, smoothing_factor=2.0 / (period + 1.0))
    bull = [high - avg for high, avg in zip(highs, ema)]
    bear = [low - avg for low, avg in zip(lows, ema)]

    return bull, bear


if __name__ == "__main__":
    print("Profiling")

    times = []

    for i in range(10000):
        start = time.time()
        simple_moving_average(np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), 5)
        end = time.time()
        times.append(end - start)

    avg_time = sum(times) / len(times)

    print("Average time: {}".format(avg_time))
    print("Cumulative time: {}".format(sum(times)))
