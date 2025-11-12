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
END_DATE = "2014-03-05"
INITIAL_CASH = 1_000_000

# Data streams
options_data = OptionsDataLoader(OPTIONS_DATA_PATH, "date", chunksize=10000)
ohlc_data = OhlcDataLoader(OHLC_DATA_PATH, "date")
multi_data_loader = MultiDataLoader(
    {"options": options_data, "ohlc": ohlc_data},
    end_date=END_DATE,
)

# Portfolio and strategy initialization
portfolio = Portfolio(INITIAL_CASH)
volatility_carry = VolatilityCarry(30, 1.1, 1.5, min_dte=10, max_dte=30)

# Store results
portfolio_value = []
dates = []

# Main simulation loop
for date, market_data in multi_data_loader.daily_multi_stream():
    ohlc_data = market_data["ohlc"]
    orders = volatility_carry.process_data(market_data, portfolio.get_options())
    portfolio.update_options(orders)
    portfolio.handle_expired_options(date)
    portfolio_value.append(portfolio.get_market_value())
    dates.append(date)

# Plot results
pct_returns = [(value / INITIAL_CASH - 1) for value in portfolio_value]

plt.plot(dates, pct_returns)
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
plt.ylabel("Portfolio Return (%)")
plt.xlabel("Date")
plt.show()
