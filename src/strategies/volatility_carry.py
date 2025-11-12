# src/strategies/volatility_carry.py

import pandas as pd
import numpy as np
from collections import deque
from .base import Strategy


class VolatilityCarry(Strategy):
    def __init__(
        self,
        rv_window: int,
        min_straddle_premium: float,
        max_straddle_premium: float,
        min_dte: int = 7,
        max_dte: int = 30,
    ):
        self.rv_window = rv_window
        self.min_straddle_premium = min_straddle_premium
        self.max_straddle_premium = max_straddle_premium
        self.min_dte = min_dte
        self.max_dte = max_dte

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
        orders = []
        ohlc_data = market_data["ohlc"]
        close = round(ohlc_data["close"], 3)
        self.price_window.append(close)

        # Check for rolling volatility availability
        if len(self.price_window) < self.rv_window:
            return None
        rv = self.compute_rv()

        options_data = market_data.get("options")
        if options_data is None:
            return None

        # Get ATM strike filters plus room for options held in portoflio (so they can be updated)
        if options_positions.empty:
            min_strike = close * 0.999
            max_strike = close * 1.001
        else:
            min_strike = min(close * 0.999, options_positions["strike_price"].min())
            max_strike = max(close * 1.001, options_positions["strike_price"].max())

        # Filter for options within strike and desired DTE range
        mask = (
            (options_data["strike_price"] >= min_strike * 1000)
            & (options_data["strike_price"] <= max_strike * 1000)
            & ((options_data["exdate"] - options_data["date"]).dt.days <= self.max_dte)
        )
        options_data = options_data[mask]

        # Define ATM option bounds
        lower_straddle_strike = close * 0.999
        upper_straddle_strike = close * 1.001

        # Filter option orders
        strike_price = options_data["strike_price"] / 1000

        held_mask = options_data["optionid"].isin(options_positions["optionid"])
        atm_mask = strike_price.between(lower_straddle_strike, upper_straddle_strike)
        vol_mask = (
            options_data["impl_volatility"] >= rv * self.min_straddle_premium
        ) & (options_data["impl_volatility"] <= rv * self.max_straddle_premium)

        update_rows = options_data[held_mask]
        sell_rows = options_data[~held_mask & atm_mask & vol_mask]

        # Create order rows
        orders = []
        for _, option_row in update_rows.iterrows():
            orders.append(self.create_order("UPDATE", 1, close, option_row))
        for _, option_row in sell_rows.iterrows():
            orders.append(self.create_order("SELL", 1, close, option_row))

        return pd.DataFrame(orders) if orders else None
