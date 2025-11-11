# src/core/portfolio.py

import pandas as pd
from typing import Tuple


class Portfolio:
    def __init__(self, initial_cash: float):
        self.cash = initial_cash
        self.options = pd.DataFrame(
            columns=[
                "action",
                "quantity",
                "spot",
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

    def get_options(self):
        return self.options

    def get_equities_positions(self):
        return self.equities

    def get_pnl(self):
        return self.pnl

    def get_delta_exposure(self):
        return self.options["delta"].sum() * 100

    def read_orders(self, orders: pd.DataFrame | None):
        if orders is None:
            return

        for _, order_row in orders.iterrows():
            action = order_row["action"]
            match action:
                case "SELL":
                    # Calculate premium
                    mid_price = (order_row["best_bid"] + order_row["best_offer"]) / 2
                    self.pnl += 100 * mid_price

                    # Add position to portfolio
                    self.options = pd.concat(
                        [self.options, order_row.to_frame().T], ignore_index=True
                    )

                case "BUY":
                    # Implement this later

                    pass
                case "UPDATE":
                    optionid = order_row["optionid"]
                    mask = self.options["optionid"] == optionid

                    # Update columns past the first
                    cols_to_update = self.options.columns[1:]
                    self.options.loc[mask, cols_to_update] = order_row[
                        cols_to_update
                    ].values

                    # Get the updated row
                    option_row = self.options.loc[mask].iloc[0]

                    # Check for expiry
                    date = option_row["date"].tz_localize(None)
                    exdate = pd.to_datetime(option_row["exdate"]).tz_localize(None)

                    if date == exdate:
                        # Calculate intrinsic value
                        if option_row["cp_flag"] == "C":
                            intrinsic_value = (
                                max(option_row["spot"] - option_row["strike_price"], 0)
                                * 100
                            )
                        else:
                            intrinsic_value = (
                                max(option_row["strike_price"] - option_row["spot"], 0)
                                * 100
                            )

                        # Update PnL
                        if option_row["action"] == "BUY":
                            self.pnl += intrinsic_value
                        elif option_row["action"] == "SELL":
                            self.pnl -= intrinsic_value

                        # Remove expired row
                        self.options = self.options[~mask].reset_index(drop=True)

    def hedge_delta(self, option_ids: list[str]):
        net_delta_exposure = self.get_delta_exposure()
