import pandas as pd
import numpy as np
from pathlib import Path
from rich.console import Console
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from src.core.data import OptionsDataLoader, OhlcDataLoader, MultiDataLoader
from src.core.portfolio import Portfolio
from src.strategies.volatility_carry import VolatilityCarry

# Print formatting
pd.set_option("display.max_rows", 1000)
console = Console()

# Constants
OPTIONS_DATA_PATH = Path("data/spx/spx_options_2013-01-01_2023-01-01.csv")
OHLC_DATA_PATH = Path("data/spx/spx_ohlcv_2013-01-01_2023-01-01.csv")
START_DATE = "2013-01-01"
END_DATE = "2023-01-01"
INITIAL_CASH = 1_000_000

# Data streams
options_data = OptionsDataLoader(OPTIONS_DATA_PATH, "date", chunksize=10000)
ohlc_data = OhlcDataLoader(OHLC_DATA_PATH, "date")
multi_data_loader = MultiDataLoader(
    {"options": options_data, "ohlc": ohlc_data},
    end_date=END_DATE,
)

# Portfolio and strategy initialization
options_portfolio = Portfolio(INITIAL_CASH)
volatility_carry = VolatilityCarry(
    rv_window=30,
    min_straddle_premium=1.2,
    max_straddle_premium=1.8,
    min_dte=23,
    max_dte=30,
    max_positions=16,
)

# Store results
prev_spot = 0.0
options_portfolio_value = []
dates = []

# Main simulation loop
for date, market_data in multi_data_loader.daily_multi_stream():
    ohlc_data = market_data["ohlc"]
    close = ohlc_data["close"]
    orders = volatility_carry.process_data(market_data, options_portfolio.get_options())
    options_portfolio.update_options(orders)
    options_portfolio.handle_expired_options(date)
    # if prev_spot != 0:
    # options_portfolio.update_delta_pnl(close, close - prev_spot, 0.01, 0.05, 0.02)
    options_portfolio_value.append(options_portfolio.get_market_value())
    dates.append(date)
    prev_spot = close

# Calculate percent returns
options_pct_returns = [(value / INITIAL_CASH - 1) for value in options_portfolio_value]

# Calculate sharpe ratio
options_returns = np.diff(options_portfolio_value) / options_portfolio_value[:-1]
sharpe_ratio = np.mean(options_returns) / np.std(options_returns) * np.sqrt(252)
print(f"Annualized Sharpe Ratio: {sharpe_ratio:.2f}")

plt.figure(figsize=(12, 6))
plt.plot(dates, options_pct_returns)

plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

plt.xlabel("Date")
plt.ylabel("Portfolio Return (%)")
plt.title("SPX Volatility Carry (23-30 DTE)")
plt.tight_layout()
plt.show()
