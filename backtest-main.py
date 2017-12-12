from backtesting import BackTester
from indicators import *
from strategies import *

# strat = AranStrategy()
# strat = NaiveStrategy()
strat = DevonStrategy()

class Tester(BackTester):
    def __init__(self, currency_from, currency_to, currency_from_bal, currency_to_bal):
        super().__init__(currency_from, currency_to, currency_from_bal, currency_to_bal)

    def stop(self):
        if self.currency_to_balance > 0:
            self.buy(self.currency_to_balance)

        # if self.currency_from_balance > 0:
        #     self.sell(self.currency_from_balance)

        print("Final balance: {} {}, {} {}".format(self.currency_from_balance, self.currency_from,
                                                   self.currency_to_balance, self.currency_to))

        # print("Number of Trades: {}".format(self.num_trades))

        sma = simple_moving_average(np.array(self.closes), period=20)
        ema = exponential_moving_average(np.array(self.closes), smoothing_factor=0.095)

        tight_bollinger_high, tight_bollinger_low = bollinger(np.array(self.closes), num_sd=0.5, period=20)
        bollinger_high, bollinger_low = bollinger(np.array(self.closes), num_sd=2.0, period=20)

        rsis = relative_strength_index(np.array(self.closes))

        # obv = on_balance_volume(self.opens, self.closes, self.volume_tos)
        #
        # bull, bear = elder_ray(self.closes, self.highs, self.lows)
        # self.draw_bar_graph(
        #     ("bull", bull),
        #     ("bear", bear)
        # )

        self.draw_line_graph(
            ("sma", sma),
            ("ema", ema),
            ("close", self.closes),
            ("bol_high", bollinger_high),
            ("bol_low", bollinger_low)
            # ("RSI", rsis)
        )
        # )
        # self.draw_graph(
        #     ("close", self.closes),
        #     ("simple moving average", sma),
        #     ("exponential moving average", ema)
        # )

    def tick(self, time, open, high, low, close, volume_from, volume_to):

        if len(self.closes) > 20:
            #

            if strat.should_buy(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
                if self.currency_to_balance > 0:
                    self.buy(self.currency_to_balance)

            elif strat.should_sell(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
                if self.currency_from_balance > 0:
                    self.sell(self.currency_from_balance)

            # sma = simple_moving_average(np.array(self.closes), period=20)
            # ema = exponential_moving_average(np.array(self.closes), smoothing_factor=0.2)
            # tight_bollinger_high, tight_bollinger_low = bollinger(np.array(self.closes), num_sd=0.5, period=20)
            # bollinger_high, bollinger_low = bollinger(np.array(self.closes), num_sd=2, period=20)
            #
            # if self.should_sell(close, bollinger_low[-1]):
            #     if self.currency_from_balance > 0:
            #         self.sell(self.currency_from_balance / 10.0)
            #
            # elif self.should_buy(sma[-1], ema[-1], close, tight_bollinger_high[-1]):
            #     if self.currency_to_balance > 0:
            #         self.buy(self.currency_to_balance / 10.0)



# test = Tester("BTC", "OMG")
test = Tester("LTC", "USD", 1, 0)
test.run()
