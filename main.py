import pandas as pd
from pathlib import Path
from rich.console import Console
import matplotlib.pyplot as plt

pd.set_option("display.max_rows", 1000)

console = Console()

from src.core.data import OptionsDataLoader, OhlcDataLoader, MultiDataLoader
from src.core.portfolio import Portfolio
from src.strategies.volatility_carry import VolatilityCarry

OPTIONS_DATA_PATH = Path("data/spx_options_samples_~1y.csv")
OHLC_DATA_PATH = Path("data/^SPX_history_2013-01-01_2015-01-1.csv")

END_DATE = "2014-03-05"

options_data = OptionsDataLoader(OPTIONS_DATA_PATH, "date", chunksize=10000)
ohlc_data = OhlcDataLoader(OHLC_DATA_PATH, "date")

volatility_carry = VolatilityCarry("VolCarry", 30, 1.2, 1.3)

portfolio = Portfolio(1_000_000)

multi_data_loader = MultiDataLoader(
    {"options": options_data, "ohlc": ohlc_data},
    end_date=END_DATE,
)

END_DATE = pd.to_datetime(END_DATE)
START_DATE = pd.to_datetime("2013-01-01")
total_days = (END_DATE - START_DATE).days

pnl = []
dates = []
day = 0

for date, market_data in multi_data_loader.daily_multi_stream():
    ohlc_data = market_data["ohlc"]
    print(f"{(date - START_DATE).days / total_days * 100:.1f}%")
    orders = volatility_carry.process_data(market_data, portfolio.get_options())
    portfolio.read_orders(orders)
    portfolio.handle_expired(date)
    pnl.append(portfolio.get_pnl())
    dates.append(date)

plt.plot(dates, pnl)
plt.show()
