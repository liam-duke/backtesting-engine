import pandas as pd
from pathlib import Path
from rich.console import Console

pd.set_option("display.max_rows", 1000)

console = Console()

from src.core.data import OptionsDataLoader, OhlcDataLoader, MultiDataLoader
from src.core.portfolio import Portfolio
from src.strategies.volatility_carry import VolatilityCarry

OPTIONS_DATA_PATH = Path("data/spx/spx_options_2013-01-01_2023-01-01.csv")
OHLC_DATA_PATH = Path("data/spx/spx_ohlcv_2013-01-01_2023-01-01.csv")

options_data = OptionsDataLoader(OPTIONS_DATA_PATH, "date", chunksize=10000)
ohlc_data = OhlcDataLoader(OHLC_DATA_PATH, "date")

volatility_carry = VolatilityCarry("VolCarry", 60, 1.20)

portfolio = Portfolio(1_000_000)

multi_data_loader = MultiDataLoader(
    {"options": options_data, "ohlc": ohlc_data},
    start_date="2013-06-28",
    end_date="2014-03-05",
)

for date, market_data in multi_data_loader.daily_multi_stream():
    orders = volatility_carry.process_data(market_data, portfolio.get_options())
    portfolio.read_orders(orders)
    if orders is not None:
        console.print(
            orders[
                [
                    "spot",
                    "action",
                    "quantity",
                    "date",
                    "exdate",
                    "cp_flag",
                    "strike_price",
                    "best_bid",
                    "best_offer",
                    "impl_volatility",
                    "delta",
                    "gamma",
                    "vega",
                    "theta",
                    "optionid",
                ]
            ]
        )
    print(portfolio.get_pnl())
