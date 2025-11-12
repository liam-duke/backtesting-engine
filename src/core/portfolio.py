# src/core/portfolio.py

import pandas as pd
import numpy as np
from src.core.constants import OPTION_COLUMNS, EQUITY_COLUMNS


class Portfolio:
    def __init__(self, initial_cash: float):
        self.options = pd.DataFrame(columns=OPTION_COLUMNS)
        self.equities = pd.DataFrame(columns=EQUITY_COLUMNS)
        self.market_value = initial_cash

    def get_options(self):
        return self.options

    def get_equities(self):
        return self.equities

    def get_market_value(self):
        return self.market_value

    def get_delta_exposure(self):
        return self.options["delta"].sum() * 100

    def update_equities(self, orders: pd.DataFrame):
        if self.equities is None:
            return

        # Update equity positions to market

    def update_options(self, orders: pd.DataFrame | None):
        if orders is None:
            return

        # Separate orders by action
        buy_orders = orders[orders["action"] == "BUY"]
        sell_orders = orders[orders["action"] == "SELL"]
        update_orders = orders[orders["action"] == "UPDATE"]

        # Calculate and process net premium / allocation
        buy_mid_prices = -(buy_orders["best_bid"] + buy_orders["best_offer"]) / 2
        sell_mid_prices = (sell_orders["best_bid"] + sell_orders["best_offer"]) / 2
        self.market_value += 100 * (sell_mid_prices.sum() + buy_mid_prices.sum())

        # Add positions to portfolio
        self.options = pd.concat([self.options, sell_orders], ignore_index=True)

        # Update held options to market data
        if not update_orders.empty:
            self.options = self.options.set_index("optionid", drop=False)
            update_orders = update_orders.set_index("optionid", drop=False)

            cols_to_update = self.options.columns.difference(["action", "exdate"])

            self.options.loc[update_orders.index, cols_to_update] = update_orders[
                cols_to_update
            ]

    def handle_expired_options(self, current_date: pd.Timestamp):
        if self.options.empty:
            return

        expired_mask = self.options["exdate"] <= current_date
        expired_options = self.options.loc[expired_mask]

        if not expired_options.empty:
            # Calculate intrinsic vlaues
            call_intrinsic = (
                expired_options["spot"] - expired_options["strike_price"]
            ).clip(lower=0)
            put_intrinsic = (
                expired_options["strike_price"] - expired_options["spot"]
            ).clip(lower=0)

            # Separate by long and short positions
            intrinsic_values = (
                np.where(
                    expired_options["cp_flag"] == "C", call_intrinsic, put_intrinsic
                )
                * 100
            )
            sign = np.where(expired_options["action"] == "BUY", 1, -1)

            # Adjust market value
            pnl_adjustments = intrinsic_values * sign
            self.market_value += pnl_adjustments.sum()

            # Drop expired options
            self.options = self.options.loc[~expired_mask]
            self.options = self.options.reset_index(drop=True)

    def hedge_delta(self, spot: float):
        ### IMPLEMENT LATER ###
        pass
