# src/core/engine.py

import pandas as pd
from portfolio import Portfolio
from core.data import OhlcDataLoader, OptionsDataLoader
from strategies.base import Strategy


class BacktestEngine:
    def __init__(self, portfolio: Portfolio, data_loaders: list, analytics=None):
        self.portfolio = portfolio
        self.data_loaders = data_loaders
        self.analytics = analytics
        pass

    def run(self, strategies: list[Strategy], start_date=None, end_date=None):
        pass
