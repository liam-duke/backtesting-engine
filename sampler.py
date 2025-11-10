import pandas as pd

df = pd.read_csv("data/spx/spx_options_2013-01-01_2023-01-01.csv", chunksize=1000000)

for chunk in df:
    chunk.to_csv("data/spx/samples/spx_options_samples_~1y")
    break
