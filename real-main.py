# import gdax
#
# key = "d69b13f3760cc3c768d81041658431e8"
# secret = "oBzHR9em71+wbyfRCbOPDNlIrBbiReGf+i7tt2CFoxn4gN4Racr30N1KO0s75PGg2YaAxtimHQIfnznJvvw+3Q=="
# passcode = "gjwjmt51ydm"
#
# auth_client = gdax.AuthenticatedClient(key, secret, passcode)
#
# eth_account = "b1935030-d8b0-45ac-a3b5-def29d311f46"
#
# # sell 0.001 ethereum at 0.02782 BTC
# # print(auth_client.sell(price='0.02781', size='0.001', product_id='ETH-BTC'))
# print(auth_client.buy(price='0.02764', size='0.00002772', product_id='ETH-BTC'))
#
# # print(auth_client.get_accounts())

from backtesting import GDAXTester
from indicators import *
from strategies import *

strat = DevonStrategy()


class Tester(GDAXTester):
    def __init__(self, config_uri):
        super().__init__(config_uri)

    def tick(self, time, open, high, low, close, volume_from, volume_to):

        if len(self.closes) > 20:

            if strat.should_buy(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
                if self.currency_to_balance > 0:
                    self.buy(self.currency_to_balance)

            elif strat.should_sell(self.opens, self.highs, self.lows, self.closes, self.volume_froms, self.volume_tos):
                if self.currency_from_balance > 0:
                    self.sell(self.currency_from_balance)

if __name__ == "__main__":
    test = Tester("LTC", "BTC", 0.00878773, 0.00103903)
    # 0.00012783
    test.run()
