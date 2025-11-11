# src/strategies/volatility_carry.py

import pandas as pd
import numpy as np
from collections import deque
from .base import Strategy


class VolatilityCarry(Strategy):
    def __init__(self, name: str, rv_window: int, min_straddle_premium: float):
        super().__init__(name)
        self.rv_window = rv_window
        self.min_straddle_premium = min_straddle_premium
        self.price_window = deque(maxlen=rv_window)
        self.rolling_rv = -1

    def compute_rv(self):
        prices = np.array(self.price_window)
        log_returns = np.diff(np.log(prices))
        rv = np.std(log_returns) * np.sqrt(252)
        return rv

    def process_data(
        self,
        market_data: dict[str, pd.DataFrame | pd.Series],
        options_positions: pd.DataFrame,
    ):
        order_rows = []

        ohlc_data = market_data["ohlc"]
        close = round(ohlc_data["close"], 3)

        self.price_window.append(close)

        # Check for RV availability
        if len(self.price_window) < self.rv_window:
            return None
        rv = self.compute_rv()
        print(len(self.price_window))

        if options_positions.empty:
            min_strike = close * 0.95
            max_strike = close * 1.05
        else:
            min_strike = 0.95 * options_positions["strike_price"].min()
            max_strike = 1.05 * options_positions["strike_price"].max()

        options_data = market_data.get("options")
        if options_data is None:
            return None
        options_data = options_data[
            (options_data["strike_price"] >= min_strike * 1000)
            & (options_data["strike_price"] <= max_strike * 1000)
        ]

        lower_straddle_strike = close * 0.999
        upper_straddle_strike = close * 1.001

        # Main processing loop
        for _, option_row in options_data.iterrows():
            strike_price = option_row["strike_price"] / 1000

            # Update held position
            if option_row["optionid"] in options_positions["optionid"].values:
                update_order = self.create_order("UPDATE", 1, close, option_row)
                order_rows.append(update_order)

            # Check ATM options
            elif lower_straddle_strike <= strike_price <= upper_straddle_strike:
                if option_row["impl_volatility"] >= rv * self.min_straddle_premium:
                    sell_order = self.create_order("SELL", 1, close, option_row)
                    order_rows.append(sell_order)

        return pd.DataFrame(order_rows) if order_rows else None
