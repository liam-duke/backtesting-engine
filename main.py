import pandas as pd
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
END_DATE = "2015-01-01"
INITIAL_CASH = 1_000_000

# Data streams
options_data = OptionsDataLoader(OPTIONS_DATA_PATH, "date", chunksize=10000)
ohlc_data = OhlcDataLoader(OHLC_DATA_PATH, "date")
multi_data_loader = MultiDataLoader(
    {"options": options_data, "ohlc": ohlc_data},
    end_date=END_DATE,
)

# Portfolio and strategy initialization
options_portfolio = Portfolio(INITIAL_CASH / 2)
volatility_carry = VolatilityCarry(
    rv_window=14,
    min_straddle_premium=1.2,
    max_straddle_premium=1.8,
    min_dte=7,
    max_dte=14,
    max_positions=36,
)

# Store results
prev_spot = 0.0
options_portfolio_value = []
equity_portfolio_value = [INITIAL_CASH / 2]
pure_portfolio_value = [INITIAL_CASH]
dates = []

# Main simulation loop
for date, market_data in multi_data_loader.daily_multi_stream():
    ohlc_data = market_data["ohlc"]
    close = ohlc_data["close"]
    orders = volatility_carry.process_data(market_data, options_portfolio.get_options())
    options_portfolio.update_options(orders)
    options_portfolio.handle_expired_options(date)
    if prev_spot != 0:
        equity_portfolio_value.append((close / prev_spot) * equity_portfolio_value[-1])
        pure_portfolio_value.append((close / prev_spot) * pure_portfolio_value[-1])
        options_portfolio.update_delta_pnl(close, close - prev_spot, 0.01, 0.02, 0.01)
    options_portfolio_value.append(options_portfolio.get_market_value())
    dates.append(date)
    prev_spot = close

mixed_portfolio_value = [
    x + y for x, y in zip(equity_portfolio_value, options_portfolio_value)
]

# Calculate percent returns
pure_pct_returns = [(value / INITIAL_CASH - 1) for value in pure_portfolio_value]
mixed_pct_returns = [(value / INITIAL_CASH - 1) for value in mixed_portfolio_value]

# Basic analytics
pure_sharpe = []

plt.figure(figsize=(12, 6))
plt.plot(dates, pure_pct_returns, label="SPX Pure Equity")
plt.plot(dates, mixed_pct_returns, label="SPX Mixed Equity & Volatility Carry")

plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

plt.xlabel("Date")
plt.ylabel("Portfolio Return (%)")
plt.title("SPX Pure Equity vs SPX Mixed Equty and Volatility Carry (7-14 DTE)")
plt.legend()
plt.tight_layout()
plt.show()
