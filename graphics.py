import matplotlib.finance as finance
from matplotlib import pyplot as plt
import numpy as np
from indicators import *

#plt.style.use("aran")


def plot_stock_graph(opens, closes, highs, lows, buys, sells):
    ax = plt.subplot(311)
    legend = []

    finance.candlestick2_ochl(ax, opens, closes, highs, lows, width=1,
                              colorup='g', colordown='r',
                              alpha=0.25)

    sma = simple_moving_average(np.array(closes), period=20)
    ema = exponential_moving_average(np.array(closes), 10)
    bollinger_high, bollinger_low = bollinger(np.array(closes), num_sd=1.7, period=20)

    series = [("sma", sma),
              ("ema", ema),
              ("close", closes),
              ("bol upper", bollinger_high),
              ("bol lower", bollinger_low)]

    for series_name, series_values in series:
        plt.plot(np.arange(len(series_values)), series_values, label=series_name)
    legend.append("buys")
    ax.scatter([x[0] for x in buys], [x[1]["close"] for x in buys], c='#00ff00', label='buys', marker='^',
               zorder=10, linewidths=2)

    legend.append("sells")
    ax.scatter([x[0] for x in sells], [x[1]["close"] for x in sells], c='#ee0000', label='sells',
               marker='v', zorder=10, linewidths=2)

    plt.ylabel('price')

    plt.legend(loc='upper left')

    plt.subplot(312)

    bull, bear = elder_ray(closes, highs, lows, period = 100)
    legend2 = []
    legend2.append("bull")
    plt.bar(np.arange(len(bull)), bull, alpha=0.8)
    plt.bar(np.arange(len(bear)), bear, alpha=0.8)
    legend2.append("bear")
    plt.ylabel("bull/bear")

    plt.subplot(313)
    rsi = relative_strength_index(np.array(closes), period=14)

    plt.plot(np.arange(len(rsi)), rsi, label="RSI")
    plt.ylabel("rsi")
    plt.legend(loc="upper left")
    plt.show()
