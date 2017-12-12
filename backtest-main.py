from backtesting import BackTester
from indicators import *
from strategies import *

# strat = AranStrategy()
# strat = NaiveStrategy()
# strat = DevonStrategy()
strat = PeranStrategy()


class Tester(BackTester):
    def __init__(self, config_uri):
        super().__init__(config_uri)

    def stop(self):
        if self.currency_to_balance > 0:
            print("Transferring back to {}".format(self.currency_from))
            self.buy(self.currency_to_balance)

        print("Final balance: {} {}, {} {}".format(self.currency_from_balance, self.currency_from,
                                                   self.currency_to_balance, self.currency_to))

        sma = simple_moving_average(np.array(self.closes), period=1)
        ema = exponential_moving_average(np.array(self.closes), smoothing_factor=0.095)
        bollinger_high, bollinger_low = bollinger(np.array(self.closes), num_sd=2.0, period=20)

        self.draw_line_graph(
            ("sma", sma),
            #("ema", ema),
            #("close", self.closes),
            #("bol upper", bollinger_high),
            #("bol lower", bollinger_low)
            # ("RSI", rsis)
        )

    def tick(self, time, open, high, low, close, volume_from, volume_to):

        if strat.should_sell(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
            if self.currency_from_balance > 0:
                self.sell(self.currency_from_balance)
        elif strat.should_buy(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
            if self.currency_to_balance > 0:
                self.buy(self.currency_to_balance)


test = Tester('./configs/backtest.yml')
test.run()
