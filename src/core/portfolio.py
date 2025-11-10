# src/core/portfolio.py

import pandas as pd
from typing import Tuple


class Portfolio:
    def __init__(self, initial_cash: float):
        self.cash = initial_cash
        self.options = pd.DataFrame(
            columns=[
                "secid",
                "date",
                "symbol",
                "exdate",
                "cp_flag",
                "strike_price",
                "best_bid",
                "best_offer",
                "volume",
                "open_interest",
                "impl_volatility",
                "delta",
                "gamma",
                "vega",
                "theta",
                "optionid",
                "contract_size",
                "index_flag",
                "issuer",
                "exercise_style",
            ]
        )
        self.equities = pd.DataFrame(
            columns=["ticker", "quantity", "price_entered", "price_current"]
        )
        self.pnl = 0.0

    def get_optionids(self):
        """
        Returns series of optionids currently held in the portfolio. This is is passed
        into the strategy along with market data to update current positions and prevent
        duplicate orders.
        """
        return self.options["optionids"]

    def get_equities_positions(self):
        return self.equities

    def read_orders(self, orders: pd.DataFrame):
        for _, row in orders.iterrows():
            action = row["action"]
            match action:
                case "SELL":
                    pass
                case "BUY":
                    pass
                case "UPDATE":
                    pass

    def hedge_delta(self, option_ids: list[str]):
        pass
