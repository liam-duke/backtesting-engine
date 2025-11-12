# src/core/portfolio.py

import pandas as pd


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

    def update_to_market(self):
        pass
        ### IMPLEMENT VECTORIZED UPDATE OF PORTFOLIO OPTIONS LATER IF ITS THAT MUCH FASTER ###

        # # Calculate pnl for expired options if present
        # expiry_mask = self.options["date"] == pd.to_datetime(self.options["exdate"])

        # if expiry_mask.any():
        #     expired_options = self.options[expiry_mask]
        #     expired_calls = expired_options[expired_options["cp_flag"] == "C"]
        #     expired_puts = expired_options[expired_options["cp_flag"] == "P"]

        #     if not expired_calls.empty:
        #         intrinsic_calls = (
        #             np.maximum(expired_calls["spot"] - expired_calls["strike_price"], 0)
        #             * 100
        #         )
        #         self.pnl += (
        #             (intrinsic_calls * (expired_calls["action"] == "BUY"))
        #             - (intrinsic_calls * (expired_calls["action"] == "SELL"))
        #         ).sum()

        #     if not expired_puts.empty:
        #         intrinsic_puts = (
        #             np.maximum(expired_puts["strike_price"] - expired_puts["spot"], 0)
        #             * 100
        #         )
        #         self.pnl += (
        #             (intrinsic_puts * (expired_puts["action"] == "BUY"))
        #             - (intrinsic_puts * (expired_puts["action"] == "SELL"))
        #         ).sum()

        #     # Remove expired options
        #     self.options = self.options[~expiry_mask].reset_index(drop=True)

    def get_options(self):
        return self.options

    def get_equities_positions(self):
        return self.equities

    def get_pnl(self):
        return self.pnl

    def get_delta_exposure(self):
        return self.options["delta"].sum() * 100

    def handle_expired(self, current_date: pd.Timestamp):
        expired_idx = self.options.index[self.options["exdate"] <= current_date]

        for idx in expired_idx:
            expired_row = self.options.loc[idx]

            # Calculate intrinsic value
            if expired_row["cp_flag"] == "C":
                intrinsic_value = (
                    max(expired_row["spot"] - expired_row["strike_price"], 0) * 100
                )
            else:
                intrinsic_value = (
                    max(expired_row["strike_price"] - expired_row["spot"], 0) * 100
                )

            # Update PnL
            if expired_row["action"] == "BUY":
                self.pnl += intrinsic_value
            elif expired_row["action"] == "SELL":
                self.pnl -= intrinsic_value

        # Remove expired rows
        self.options.drop(expired_idx, inplace=True)

    def read_orders(self, orders: pd.DataFrame | None):
        if orders is None:
            return

        # Separate orders by action
        sell_orders = orders[orders["action"] == "SELL"]
        update_orders = orders[orders["action"] == "UPDATE"]

        sell_mid_prices = (sell_orders["best_bid"] + sell_orders["best_offer"]) / 2
        self.pnl += (100 * sell_mid_prices).sum()

        self.options = pd.concat([self.options, sell_orders], ignore_index=True)

        if not update_orders.empty:
            self.options = self.options.set_index("optionid", drop=False)
            update_orders = update_orders.set_index("optionid", drop=False)

            cols_to_update = self.options.columns.difference(["action", "exdate"])

            self.options.loc[update_orders.index, cols_to_update] = update_orders[
                cols_to_update
            ]
            self.options = self.options.reset_index(drop=True)

    def hedge_delta(self, spot: float):
        ### IMPLEMENT LATER ###
        pass
