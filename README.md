# Ticker comparison

Python script that pulls 3 years of price data (yfinance) and compares
tickers on CAGR, volatility, max drawdown, Sharpe ratio and worst day.

## Run it

```
pip install pandas numpy yfinance
python compare_tickers.py
```

Edit the `tickers` list near the bottom of the script to compare other assets.

## Results (3 years to Nov 2026)

| Ticker | CAGR | Volatility | Max drawdown | Sharpe | Worst day | Arith return |
|---|---|---|---|---|---|---|
| ^GSPC | 16.4% | 15.3% | -18.9% | 0.815 | -6.0% | 16.4% |
| AAPL | 22.7% | 27.0% | -33.4% | 0.694 | -9.2% | 24.2% |
| NPN.JO | -1.4% | 34.8% | -50.2% | -0.155 | -17.7% | 4.7% |
| ^NDX | 18.3% | 21.1% | -22.9% | 0.676 | -6.4% | 19.1% |

## What I found

- The S&P 500 achieved the highest Sharpe ratio, indicating the strongest return relative to risk. Although Apple and the Nasdaq 100 generated higher returns, they also experienced greater risk and therefore did not outperform the index on a risk-adjusted basis.



Higher volatility was generally associated with larger drawdowns. As volatility increased from approximately 15% to 35%, maximum drawdowns worsened from around -19% to -50%.



NPN.JO recorded a positive average annual return of 4.7%, but its CAGR was negative at -1.4%. This highlights the impact of volatility drag, where price fluctuations reduce compounded returns, particularly for more volatile investments.

## Limitations

- NPN.JO is priced in rand and the others in dollars, so the comparison
  mixes currencies.
- The 4% risk-free rate is an assumption, not a market rate.
- One 3-year window says nothing about future performance.
- yfinance is unofficial data: fine for learning, not for client work.