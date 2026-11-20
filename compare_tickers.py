import yfinance as yf
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)


def stats(ticker, period="3y", rf=0.04):
    close = yf.download(ticker, period=period, progress=False)["Close"].squeeze()
    r = close.pct_change().dropna()
    years = (close.index[-1] - close.index[0]).days / 365.25
    cagr = (close.iloc[-1] / close.iloc[0]) ** (1 / years) - 1
    vol = r.std() * 252 ** 0.5
    return {
        "CAGR": cagr,
        "Volatility": vol,
        "Max drawdown": (close / close.cummax() - 1).min(),
        "Sharpe": (cagr - rf) / vol,
        "Worst day": r.min(),
        "Arith return": r.mean() * 252,
    }


tickers = ["^GSPC", "AAPL", "NPN.JO", "^NDX"]
table = pd.DataFrame({t: stats(t) for t in tickers}).T
print(table.round(3))