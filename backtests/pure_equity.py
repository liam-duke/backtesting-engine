import pandas as pd
from pathlib import Path
from rich.console import Console
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from src.core.data import OhlcDataLoader

# Print formatting
pd.set_option("display.max_rows", 1000)
console = Console()

# Constants
OPTIONS_DATA_PATH = Path("data/spx/spx_options_2013-01-01_2023-01-01.csv")
OHLC_DATA_PATH = Path("data/spx/spx_ohlcv_2013-01-01_2023-01-01.csv")
START_DATE = "2013-01-01"
END_DATE = "2015-01-01"
INITIAL_CASH = 1_000_000

# Data streams
ohlc_data = OhlcDataLoader(OHLC_DATA_PATH, "date")

prev_spot = 0.0
pure_portfolio_value = [INITIAL_CASH]
dates = []

# Main simulation loop
for date, ohlc_data in ohlc_data.daily_stream():
    close = ohlc_data["close"]
    if prev_spot != 0:
        pure_portfolio_value.append((close / prev_spot) * pure_portfolio_value[-1])
    dates.append(date)
    prev_spot = close

# Calculate percent returns
pure_pct_returns = [(value / INITIAL_CASH - 1) for value in pure_portfolio_value]

# Basic analytics
pure_sharpe = []

plt.figure(figsize=(12, 6))
plt.plot(dates, pure_portfolio_value, label="SPX Pure Equity")

plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

plt.xlabel("Date")
plt.ylabel("Portfolio Return (%)")
plt.title("SPX Pure Equity Return")
plt.legend()
plt.tight_layout()
plt.show()
