import pandas as pd
from pathlib import Path
from rich.console import Console

pd.set_option("display.max_rows", 1000)

console = Console()

from src.core.data import OptionsDataLoader, OhlcDataLoader, MultiDataLoader
from src.strategies.volatility_carry import VolatilityCarry

OPTIONS_DATA_PATH = Path("data/spx/samples/spx_options_samples_~1y.csv")
OHLC_DATA_PATH = Path("data/spx/spx_ohlcv_2013-01-01_2023-01-01.csv")

options_data = OptionsDataLoader(OPTIONS_DATA_PATH, "date", chunksize=10000)
ohlc_data = OhlcDataLoader(OHLC_DATA_PATH, "date")

options_positions = pd.Series(dtype=float, name="optionid")
volcarry = VolatilityCarry("VolCarry", 30, 1.50)

daily_data = MultiDataLoader(
    {"options": options_data, "ohlc": ohlc_data}, end_date="2014-03-05"
)

count = 1

# for data in daily_data.daily_multi_stream():
#     result = volcarry.process_data(data[1], options_positions)
#     if result is not None and not result.empty:
#         print(result.columns)
#         break

for data in options_data.daily_stream():
    result = data[1]
    if result is not None and not result.empty:
        print(result.columns)
        break
