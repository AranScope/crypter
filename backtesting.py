import os

import gdax

from graphics import plot_stock_graph
from market import Market


class Tester(object):
    def __init__(self, config):

        self.config = config
        self.currency_from = config['currency_from']['symbol']
        self.currency_to = config['currency_to']['symbol']
        self.currency_from_balance = config['currency_from']['balance']
        self.currency_to_balance = config['currency_to']['balance']
        self.transaction_fee = config['transaction_fee']
        self.tick_start_delay = config['tick_start_delay']
        self.tick_duration = config['tick_duration']
        self.num_ticks = config['num_ticks']
        self.exchange = config['exchange']
        self.strategy = config['strategy']

        if 'sell_on_finish' in config:
            if config['sell_on_finish'] == "default":
                if self.currency_from_balance > self.currency_to_balance:
                    self.sell_on_finish=self.currency_from
                else:
                    self.sell_on_finish=self.currency_to
            else:
                self.sell_on_finish = config['sell_on_finish']
        else:
            self.sell_on_finish = None

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
            self.currency_from_balance += amount * (1 / conversion_rate) * (1 - self.transaction_fee)

            print(
                "\nBUY ORDER:\n\tPurchased: {} {}\n\tFor: {} {}\n\tExchange rate: {}\n\tAt time: {}\n".format(
                    amount / conversion_rate,
                    self.currency_from,
                    amount,
                    self.currency_to,
                    conversion_rate,
                    self.current_time()))


            # TODO: We've sold some of currency_from to currency_to, probably get better wording
            self.sells.append((self.step_number, price))
        else:
            print("Time: {}, BUY ORDER: Do not have enough {} to make this order".format(self.current_time(),
                                                                                         self.currency_to))

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

            # SEE ABOVE TODO
            self.buys.append((self.step_number, price))

            print(
                "\nSELL ORDER:\n\tPurchased: {} {}\n\tFor: {} {}\n\tExchange rate: {}\n\tAt time: {}\n".format(
                    amount * conversion_rate,
                    self.currency_to,
                    amount,
                    self.currency_from,
                    conversion_rate,
                    self.current_time()))

        else:
            print("Time: {}, SELL ORDER: Do not have enough {} to make this order".format(self.current_time(),
                                                                                          self.currency_from))

    def tick(self, time, open, high, low, close, volume_from, volume_to):
        raise NotImplementedError()

    def stop(self):
        pass

    def write_output(self):
        if not os.path.exists('./output'):
            os.mkdir('./output')

        base_file_name = os.path.join('./output', self.strategy)
        num_existing_files = len([fname for fname in os.listdir('./output') if self.strategy in fname])
        print(num_existing_files)

        out_file_name = "{}-{}.csv".format(base_file_name, num_existing_files)

        with open(out_file_name, 'w') as f:

            f.write('strategy, buys, sells, total trades, start {0}, start {1}, end {0}, end {1}\n'.format(self.currency_from, self.currency_to))
            f.write('{}, {}, {}, {}, {}, {}, {}, {}'.format(
                self.strategy,
                len(self.buys),
                len(self.sells),
                len(self.buys) + len(self.sells),
                self.config['currency_from']['balance'],
                self.config['currency_to']['balance'],
                self.currency_from_balance,
                self.currency_to_balance
            ))

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
                self.tick(price["time"], price["open"], price["high"], price["low"], price["close"],
                          price["volumefrom"],
                          price["volumeto"])

            self.step_number += 1
            price = self.current_price()

        self.step_number -= 1
        self.stop()
        self.write_output()


class BackTester(Tester):
    def __init__(self, config_uri, strategy):
        super().__init__(config_uri)

        self.strat = strategy

        bt = Market()  # Pass keys in

        if self.tick_duration % 60 == 0:
            self.prices = bt.histo_hour(self.currency_from, self.currency_to, exchange=self.exchange, limit=self.num_ticks)
        else:
            self.prices = bt.histo_n_minute(self.currency_from, self.currency_to, self.tick_duration,
                                        limit=self.num_ticks, exchange=self.exchange)

        # self.prices = bt.histo_hour(currency_from, currency_to, exchange="bittrex")

        if self.prices is None:
            print("Failed to retrieve histogram data")
            exit(-1)

        print(self.prices)

    def current_time(self):
        return self.step_number

    def current_price(self):
        if self.step_number < len(self.prices['Data']) - 1:
            return self.prices['Data'][self.step_number]
        else:
            return None

    def tick(self, time, open, high, low, close, volume_from, volume_to):

        if self.strat.should_sell(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
            if self.currency_from_balance > 0:
                self.sell(self.currency_from_balance)
        elif self.strat.should_buy(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
            if self.currency_to_balance > 0:
                self.buy(self.currency_to_balance)

    def stop(self):

        if self.sell_on_finish is not None:
            if self.sell_on_finish == self.currency_from:
                if self.currency_to_balance > 0:
                    print("Transferring remaining {} to {}".format(self.currency_to, self.currency_from))
                    self.buy(self.currency_to_balance)
            else:
                if self.currency_from_balance > 0:
                    print("Transferring remaining {} to {}".format(self.currency_from, self.currency_to))
                    self.sell(self.currency_from_balance)

        print("Final balance: {} {}, {} {}".format(self.currency_from_balance, self.currency_from,
                                                   self.currency_to_balance, self.currency_to))

        plot_stock_graph(self.opens, self.closes, self.highs, self.lows, self.buys, self.sells)


class RealtimeTester(Tester):
    def __init__(self, config_uri):
        super().__init__(config_uri)
        self.market = Market()

        for price in self.market.histo_minute(self.currency_from, self.currency_to, limit=self.num_ticks)['Data']:
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

        for price in self.market.histo_minute(self.currency_from, self.currency_to, limit=self.num_ticks)['Data']:
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

            print(self.auth_client.buy(price='{0:.6f}'.format(conversion_rate),
                                       size='{0:.6f}'.format(amount / conversion_rate), product_id='ETH-BTC'))

            print("BUY ORDER: Purchased {} {} for {} {}".format(amount / conversion_rate, self.currency_from, amount,
                                                                self.currency_to))

            # TODO: We've sold some of currency_from to currency_to, probably get better wording
            self.sells.append((self.step_number - 1, price))
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

            print(self.auth_client.sell(price='{0:.6f}'.format(conversion_rate), size='{0:.6f}'.format(amount),
                                        product_id='ETH-BTC'))
            # sell 0.05002773 ETH at 0.02760 BTC per ETC
            #
            # 0.00137712

            # TODO: See previous TODO.
            self.buys.append((self.step_number, price))

            print("SELL ORDER: Purchased {} {} for {} {}".format(amount * conversion_rate, self.currency_to, amount,
                                                                 self.currency_from))
        else:
            print("SELL ORDER: Do not have enough {} to make this order".format(self.currency_from))
