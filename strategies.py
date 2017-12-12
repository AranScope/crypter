"""
A set of trading strategies, each takes the current market environment: opens, highs etc. and
provides methods should_buy and should_sell to define which behaviours to execute for a given
environment.
"""

from indicators import *


class Strategy(object):
    def __init__(self):
        pass

    def should_buy(self, opens, highs, lows, closes, volume_froms, volume_tos):
        raise NotImplementedError()

    def should_sell(self, opens, highs, lows, closes, volume_froms, volume_tos):
        raise NotImplementedError()


class NaiveStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def should_buy(self, opens, highs, lows, closes, volume_froms, volume_tos):
        bollinger_high, bollinger_low = bollinger(np.array(closes), num_sd=1.5, period=20)
        return closes[-1] < bollinger_low[-1]

    def should_sell(self, opens, highs, lows, closes, volume_froms, volume_tos):
        bollinger_high, bollinger_low = bollinger(np.array(closes), num_sd=2.0, period=20)
        return closes[-1] > bollinger_high[-1]


class DevonStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def should_sell(self, opens, highs, lows, closes, volume_froms, volume_tos):
        rsi = relative_strength_index(np.array(closes), period=14)
        bollinger_high, bollinger_low = bollinger(np.array(closes), num_sd=2.0, period=20)
        sma = simple_moving_average(np.array(closes), 20)
        ema = exponential_moving_average(np.array(closes), 10)
        bull, bear = elder_ray(np.array(closes), np.array(highs), np.array(lows))

        indicator_truths = [
            rsi[-1] < 30,
            closes[-1] < bollinger_low[-1],
            closes[-1] < ema[-1],
            ema[-1] < sma[-1],
            ema[-1] < ema[-2],
            (bull[-1] > bull[-2]) and (bear[-1] > bear[-2]) and bear[-1] < 0 and bull[-1] < 0
        ]

        num_truths = sum([truth for truth in indicator_truths if truth])
        return num_truths > 2

    def should_buy(self, opens, highs, lows, closes, volume_froms, volume_tos):
        rsi = relative_strength_index(np.array(closes), period=14)
        ema = exponential_moving_average(np.array(closes), 10)
        bull, bear = elder_ray(np.array(closes), np.array(highs), np.array(lows))

        indicator_truths = [rsi[-1] > 70,
                            closes[-1] > ema[-1],
                            ema[-1] > ema[-2],
                            bull[-1] > 0 and bull[-1] < bull[-2],
                            (bear[-1] > bear[-2]) and bear[-1] < 0
                            ]

        num_truths = sum([truth for truth in indicator_truths if truth])
        return num_truths > 2


class AranStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def should_sell(self, opens, highs, lows, closes, volume_froms, volume_tos):
        rsi = relative_strength_index(np.array(closes), period=14)
        bollinger_high, bollinger_low = bollinger(np.array(closes), num_sd=2.0, period=20)
        sma = simple_moving_average(np.array(closes), 20)
        ema = exponential_moving_average(np.array(closes), 10)
        bull, bear = elder_ray(np.array(closes), np.array(highs), np.array(lows))

        indicators = {
            closes[-1] > bollinger_high[-1]: 0.5,
            ema[-1] < ema[-2]: 0.5
        }

        value = sum([v for k, v in indicators.items() if k])

        return value >= 1.0

    def should_buy(self, opens, highs, lows, closes, volume_froms, volume_tos):
        rsi = relative_strength_index(np.array(closes), period=14)
        ema = exponential_moving_average(np.array(closes), 10)
        bollinger_high, bollinger_low = bollinger(np.array(closes), num_sd=2.0, period=20)

        bull, bear = elder_ray(np.array(closes), np.array(highs), np.array(lows))

        indicators = {
            closes[-1] < bollinger_low[-1]: 0.5,
            ema[-1] > ema[-2]: 0.5
        }

        value = sum([v for k, v in indicators.items() if k])

        return value >= 1.0


class PeranStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def should_buy(self, opens, highs, lows, closes, volume_froms, volume_tos):
        # av = [(open + close) / 2 for open, close in zip(opens, closes)]
        av = lows #[(a + b) / 2 for a, b in zip(lows[::2], lows[1::2])]
        if av[-1] > av[-2] > av[-3] > av[-4]:
            return True
        return False

    def should_sell(self, opens, highs, lows, closes, volume_froms, volume_tos):
        av = [(open + close) / 2 for open, close in zip(opens, closes)]
        #av = highs #[(a + b) / 2 for a, b in zip(highs[::2], highs[1::2])]
        if av[-1] < av[-2] and av[-1] < av[-3]:
            return True
        return False


class TrendEmaStrategy(object):
    def __init__(self):
        pass

    def should_buy(self, opens, highs, lows, closes, volume_froms, volume_tos):
        ema_short = exponential_moving_average(np.array(closes), 5)
        ema_long = exponential_moving_average(np.array(closes), 20)

        return ema_short[-2] > ema_long[-1] and ema_short[-1] < ema_long[-1]

    def should_sell(self, opens, highs, lows, closes, volume_froms, volume_tos):
        ema_short = exponential_moving_average(np.array(closes), 5)
        ema_long = exponential_moving_average(np.array(closes), 20)

        return ema_short[-2] > ema_long[-1] and ema_short[-1] > ema_long[-1]
