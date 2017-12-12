from market import Market
import time
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.finance as finance
from indicators import *
import os
import yaml

plt.style.use("aran")
# plt.style.use("ggplot")

class Tester(object):
    def __init__(self, config_uri):

        with open(config_uri, 'r') as f:
            conf = yaml.load(f)
            self.currency_from = conf['currency_from']['symbol']
            self.currency_to = conf['currency_to']['symbol']
            self.currency_from_balance = conf['currency_from']['balance']
            self.currency_to_balance = conf['currency_to']['balance']
            self.transaction_fee = conf['transaction_fee']
            self.tick_start_delay = conf['tick_start_delay']
            self.number_of_ticks = conf['number_of_ticks']

        self.step_number = 0

        self.times = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volume_froms = []
        self.volume_tos = []

        self.buys = []
        self.sells = []

    def current_time(self):
        raise NotImplementedError()

    def current_price(self):
        raise NotImplementedError()

    def buy(self, amount):
        """
        Buy 'amount' worth of currency_to

        E.g. For the ETH-BTC pair
             We want to buy 'amount' BTC worth of ETH

        :param amount: Amount of currency_from to spend on currency_to
        """

        price = self.current_price()

        conversion_rate = price['close']

        if amount <= self.currency_to_balance:
            self.currency_to_balance -= amount
            self.currency_from_balance += amount * (1/conversion_rate) * (1 - self.transaction_fee)

            print("Time: {}, BUY ORDER: Purchased {} {} for {} {}".format(self.current_time(), amount / conversion_rate, self.currency_from, amount,
                                                                self.currency_to))
            self.buys.append((self.step_number, price))
        else:
            print("Time: {}, BUY ORDER: Do not have enough {} to make this order".format(self.current_time(), self.currency_to))

    def sell(self, amount):
        """
        Sell 'amount' worth of currency_to

        E.g. For the ETH-BTC pair
             We want to sell 'amount' ETH to BTC

        :param amount: Amount of currency_to to spend on currency_from
        """

        price = self.current_price()

        conversion_rate = price['close']

        if amount <= self.currency_from_balance:

            self.currency_from_balance -= amount
            self.currency_to_balance += amount * conversion_rate * (1 - self.transaction_fee)

            self.sells.append((self.step_number, price))

            print("Time: {}, SELL ORDER: Purchased {} {} for {} {}".format(self.current_time(), amount * conversion_rate, self.currency_to, amount,
                                                                 self.currency_from))
        else:
            print("Time: {}, SELL ORDER: Do not have enough {} to make this order".format(self.current_time(), self.currency_from))

    def tick(self, time, open, high, low, close, volume_from, volume_to):
        raise NotImplementedError()

    def stop(self):
        pass

    def run(self):
        price = self.current_price()

        while price is not None:
            self.times.append(price["time"])
            self.opens.append(price["open"])
            self.highs.append(price["high"])
            self.lows.append(price["low"])
            self.closes.append(price["close"])
            self.volume_froms.append(price["volumefrom"])
            self.volume_tos.append(price["volumeto"])

            if self.step_number >= self.tick_start_delay:
                self.tick(price["time"], price["open"], price["high"], price["low"], price["close"], price["volumefrom"],
                          price["volumeto"])

            # print("Current balance: {} {}, {} {}".format(self.currency_from_balance, self.currency_from,
            #                                              self.currency_to_balance, self.currency_to))

            self.step_number += 1
            price = self.current_price()

        self.step_number -= 1
        self.stop()


class BackTester(Tester):
    def __init__(self, config_uri):
        super().__init__(config_uri)

        bt = Market() # Pass keys in

        self.prices = bt.histo_minute(self.currency_from, self.currency_to, n=(300), exchange="gdax")
        # self.prices = bt.histo_hour(currency_from, currency_to, exchange="bittrex")
        if self.prices is None:
            print("Failed to retrieve histogram data")
            exit(-1)

    def current_time(self):
        return self.step_number

    def current_price(self):
        if self.step_number < len(self.prices['Data']) - 1:
            return self.prices['Data'][self.step_number]
        else:
            return None

    def draw_line_graph(self, *args):

        ax = plt.subplot(311)
        legend = []

        finance.candlestick2_ochl(ax, self.opens, self.closes, self.highs, self.lows, width=1,
                                  colorup='g', colordown='r',
                                  alpha=0.25)

        for series_name, series_values in args:
            plt.plot(np.arange(len(series_values)), series_values, label=series_name)

        legend.append("buys")
        ax.scatter([x[0] for x in self.buys], [x[1]["close"] for x in self.buys], c='#00ff00', label='buys', marker='^', zorder=10, linewidths=2)

        legend.append("sells")
        ax.scatter([x[0] for x in self.sells], [x[1]["close"] for x in self.sells], c='#ee0000', label='sells', marker='v', zorder=10, linewidths=2)

        plt.ylabel('price')

        plt.legend(loc='upper left')

        plt.subplot(312)

        bull, bear = elder_ray(self.closes, self.highs, self.lows)
        legend2 = []
        legend2.append("bull")
        plt.bar(np.arange(len(bull)), bull)
        plt.bar(np.arange(len(bear)), bear)
        legend2.append("bear")
        plt.ylabel("bull/bear")

        plt.subplot(313)
        rsi = relative_strength_index(np.array(self.closes), period=14)

        plt.bar(np.arange(len(rsi)), rsi, label="RSI")
        plt.ylabel("rsi")
        plt.legend(loc="upper left")
        plt.show()


    def draw_bar_graph(self, *args):
        x = np.arange(len(self.closes))

        legend = []

        for series_name, series_values in args:
            legend.append(series_name)
            plt.bar(x, list(series_values))

        plt.ylabel('Price')

        plt.legend(legend, loc='upper left')

        plt.show()


import gdax


class RealtimeTester(Tester):
    def __init__(self, config_uri):

        super().__init__(config_uri)
        self.market = Market()

        for price in self.market.histo_minute(self.currency_from, self.currency_to, n=self.number_of_ticks)['Data']:
            self.times.append(price["time"])
            self.opens.append(price["open"])
            self.highs.append(price["high"])
            self.lows.append(price["low"])
            self.closes.append(price["close"])
            self.volume_froms.append(price["volumefrom"])
            self.volume_tos.append(price["volumeto"])


    def current_price(self):
        response = self.market.latest_price(self.currency_from, self.currency_to)

        if response is not None:
            return response['Data'][0]
        else:
            print("COULD NOT FETCH LATEST DATA")
            exit(-1)



class GDAXTester(Tester):
    def __init__(self, config_uri):

        super().__init__(config_uri)
        self.market = Market()

        key = os.environ.get('GDAX_PUBLIC')
        secret = os.environ.get('GDAX_SECRET')
        passcode = os.environ.get('GDAX_PASSCODE')

        if None in [key, secret, passcode]:
            print("Check your GDAX environment variables")
            exit(-1)

        self.auth_client = gdax.AuthenticatedClient(key, secret, passcode)

        for price in self.market.histo_minute(self.currency_from, self.currency_to, n=self.number_of_ticks)['Data']:
            self.times.append(price["time"])
            self.opens.append(price["open"])
            self.highs.append(price["high"])
            self.lows.append(price["low"])
            self.closes.append(price["close"])
            self.volume_froms.append(price["volumefrom"])
            self.volume_tos.append(price["volumeto"])


    def current_price(self):
        response = self.market.latest_price(self.currency_from, self.currency_to)

        if response is not None:
            return response['Data'][0]
        else:
            print("COULD NOT FETCH LATEST DATA")
            exit(-1)

    def buy(self, amount):
        """

        Buy 'amount' worth of currency_to

        E.g. For the ETH-BTC pair
             We want to buy 'amount' BTC worth of ETH

        :param amount: Amount of currency_from to spend on currency_to
        """

        price = self.current_price()

        conversion_rate = price['close']

        if amount <= self.currency_to_balance:
            self.currency_to_balance -= amount
            self.currency_from_balance += (amount * (1 - self.transaction_fee)) / conversion_rate

            # MAKE THE ACTUAL PURCHASE

            print(self.auth_client.buy(price='{0:.6f}'.format(conversion_rate), size='{0:.6f}'.format(amount/conversion_rate), product_id='ETH-BTC'))

            # print(auth_client.get_accounts())

            print("BUY ORDER: Purchased {} {} for {} {}".format(amount / conversion_rate, self.currency_from, amount,
                                                                self.currency_to))
            self.buys.append((self.step_number - 1, price))
        else:
            print("BUY ORDER: Do not have enough {} to make this order".format(self.currency_to))

    def sell(self, amount):
        """
        Sell 'amount' worth of currency_to

        E.g. For the ETH-BTC pair
             We want to sell 'amount' ETH to BTC

        :param amount: Amount of currency_to to spend on currency_from
        """

        price = self.current_price()

        conversion_rate = price['close']

        if amount <= self.currency_from_balance:

            self.currency_from_balance -= amount
            self.currency_to_balance += amount * conversion_rate * (1 - self.transaction_fee)

            # MAKE THE ACTUAL SELL
            # sell 0.001 ethereum at 0.02782 BTC

            print(self.auth_client.sell(price='{0:.6f}'.format(conversion_rate), size='{0:.6f}'.format(amount), product_id='ETH-BTC'))
            # sell 0.05002773 ETH at 0.02760 BTC per ETC
            #
            # 0.00137712

            self.sells.append((self.step_number, price))

            print("SELL ORDER: Purchased {} {} for {} {}".format(amount*conversion_rate, self.currency_to, amount,
                                                                 self.currency_from))
        else:
            print("SELL ORDER: Do not have enough {} to make this order".format(self.currency_from))