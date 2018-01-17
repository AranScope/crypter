from backtesting import BackTester, RealtimeTester
from strategies import *
import yaml

tester_types = {
    'backtest': BackTester,
    'realtimetest': RealtimeTester
}

strategies = {
    'naive': NaiveStrategy,
    'devon': DevonStrategy,
    'peran': PeranStrategy,
    'trendema': TrendEmaStrategy,
    'strat1': Strat1,
    'trendstrat': TrendStrategy
}

config_uri = './configs/backtest.yml'

conf = yaml.load(open(config_uri, 'r'))

if conf['type'] in tester_types:
    if conf['strategy'] in strategies:
        Strategy = strategies[conf['strategy']]
        strat = Strategy()

        Tester = tester_types[conf['type']]
        tester = Tester(conf, strat)

        tester.run()
    else:
        print("Strategy type not implemented\nValid strategies are: {}".format(", ".join(strategies.keys())))
else:
    print("Tester type not implemented, Valid tester types are: {}".format(", ".join(tester_types.keys())))
