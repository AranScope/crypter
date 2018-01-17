import requests

class Market(object):
    def __init__(self, public_key=None, secret_key=None):

        self.public_key = public_key
        self.secret_key = secret_key

    def request(self, url):
        try:
            response = requests.get(url)
        except ConnectionError as e:
            print("error: {}".format(e))
            return None
        except:
            print("error occured in requesting url: {}".format(url))
            return None

        if response.status_code != 200:
            print("error: {}".format(response.json()))
            return None

        return response.json()

    # def histo_quarter_hour(self, fsym, tsym, exchange="bittrex", limit=1440):
    #     url = "https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&e={}&aggregate=15&limit={}".format(
    #         fsym, tsym, exchange, limit)
    #
    #     result = self.request(url)
    #
    #     if result['Response'] == 'Error':
    #         return None
    #
    #     return result


    def histo_minute(self, fsym, tsym, exchange="bittrex", limit=1440):
        url = "https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&e={}&limit={}".format(fsym, tsym,
                                                                                                        exchange, limit)
        result = self.request(url)

        if result['Response'] == 'Error':
            return None

        return result

    def histo_n_minute(self, fsym, tsym, n, exchange="bittrex", limit=1440):
        url = "https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&e={}&limit={}&aggregate={}".format(fsym, tsym,
                                                                                                        exchange, limit, n)
        result = self.request(url)

        if result['Response'] == 'Error':
            print(result)
            return None

        return result

    def latest_price(self, fsym, tsym, exchange="bittrex"):
        url = "https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&e={}&limit=1".format(fsym, tsym,
                                                                                                       exchange)
        return self.request(url)

    def histo_hour(self, fsym, tsym, exchange="bittrex", limit=672):
        url = "https://min-api.cryptocompare.com/data/histohour?fsym={}&tsym={}&e={}&limit={}".format(fsym, tsym,
                                                                                                      exchange, limit)
        result = self.request(url)

        if result['Response'] == 'Error':
            return None

        return result

    def get_markets(self):
        url = "https://bittrex.com/api/v2.0/pub/markets/GetMarkets?_=1500913483670"
        return self.request(url)

    def get_ticker(self, market):
        url = "https://bittrex.com/api/v1.1/public/getticker?market={}".format(market)
        return self.request(url)
