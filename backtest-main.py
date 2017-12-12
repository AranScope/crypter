from backtesting import BackTester
from indicators import *
from strategies import *
from graphics import plot_stock_graph

# strat = AranStrategy()
strat = NaiveStrategy()
# strat = DevonStrategy()
# strat = PeranStrategy()
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

    def tick(self, time, open, high, low, close, volume_from, volume_to):

        if strat.should_sell(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
            if self.currency_from_balance > 0:
                self.sell(self.currency_from_balance)
        elif strat.should_buy(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
            if self.currency_to_balance > 0:
                self.buy(self.currency_to_balance)


test = Tester('./configs/backtest.yml')
test.run()
