from backtesting import BackTester
from indicators import *
from strategies import *

# strat = AranStrategy()
#strat = NaiveStrategy()
# strat = DevonStrategy()
strat = PeranStrategy()



# strat = TrendEmaStrategy()

class Tester(BackTester):
    def __init__(self, config_uri):
        super().__init__(config_uri)

    def stop(self):

        # if self.currency_to_balance > 0:
        #     print("Transferring back to {}".format(self.currency_from))
        #     self.buy(self.currency_to_balance)

        if self.sell_on_finish is not None:
            if self.sell_on_finish == self.currency_from:
                print("SELLING TO ETH")
                if self.currency_to_balance > 0:
                    print("Transferring remaining {} to {}".format(self.currency_to, self.currency_from))
                    self.buy(self.currency_to_balance)

            else:
                if self.currency_from_balance > 0:
                    print("Transferring remaining {} to {}".format(self.currency_from, self.currency_to))
                    self.sell(self.currency_from_balance)



        print("Final balance: {} {}, {} {}".format(self.currency_from_balance, self.currency_from,
                                                   self.currency_to_balance, self.currency_to))

        sma = simple_moving_average(np.array(self.closes), period=20)
        ema = exponential_moving_average(np.array(self.closes), 10)
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
