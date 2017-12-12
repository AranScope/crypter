from backtesting import RealtimeTester
from indicators import *
from strategies import *

strat = DevonStrategy()


class Tester(RealtimeTester):
    def __init__(self, currency_from, currency_to, currency_from_bal, currency_to_bal):
        super().__init__(currency_from, currency_to, currency_from_bal, currency_to_bal)

    def tick(self, time, open, high, low, close, volume_from, volume_to):

        if len(self.closes) > 20:

            if strat.should_buy(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
                if self.currency_to_balance > 0:
                    self.buy(self.currency_to_balance)

            elif strat.should_sell(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
                if self.currency_from_balance > 0:
                    self.sell(self.currency_from_balance)

if __name__ == "__main__":
    test = Tester("ETH", "BTC", 10, 0)
    test.run()
