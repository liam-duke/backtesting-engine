import pandas as pd

a = pd.Series(
    {
        "action": "SELL",
        "Unnamed: 0": 484605,
        "secid": 108105,
        "date": "2013-08-16 00:00:00",
        "symbol": "SPX 130921C1655000",
        "exdate": "2013-09-21",
        "cp_flag": "C",
        "strike_price": 1655000,
        "best_bid": 26.0,
        "best_offer": 27.2,
        "volume": 14818,
        "open_interest": 4076,
        "impl_volatility": 0.130907,
        "delta": 0.505794,
        "gamma": 0.005938,
        "vega": 204.3529,
        "theta": -133.4169,
        "optionid": 100959462,
        "contract_size": 100,
        "index_flag": 1,
        "issuer": "CBOE S&P 500 INDEX",
        "exercise_style": "E",
    }
)

b = pd.Series(
    {
        "action": "UPDATE",
        "Unnamed: 0": 484605,
        "secid": 108105,
        "date": "2013-09-16 00:00:00",
        "symbol": "SPX 130921C1655000",
        "exdate": "2013-09-21",
        "cp_flag": "C",
        "strike_price": 1655000,
        "best_bid": 26.0,
        "best_offer": 27.2,
        "volume": 14818,
        "open_interest": 4076,
        "impl_volatility": 0.130907,
        "delta": 0.6,
        "gamma": 0.002,
        "vega": 204.3529,
        "theta": -133.4169,
        "optionid": 100959462,
        "contract_size": 100,
        "index_flag": 1,
        "issuer": "CBOE S&P 500 INDEX",
        "exercise_style": "E",
    }
)

a.iloc[1:] = b.iloc[1:].values

print(a)
