# Ticker comparison

Python script that pulls historical price data from Yahoo Finance and compares assets on return and risk metrics.

## Interactive dashboard

The repository now includes a Streamlit dashboard with interactive asset and lookback-period selection, performance and drawdown charts, risk/return analysis, a metrics table, CSV export and an optional USD-to-ZAR conversion view.

### Run locally

Install the dependencies:

```bash
pip install -r requirements.txt
```

Launch the dashboard:

```bash
streamlit run dashboard.py
```

Streamlit will open the dashboard in your browser. The app downloads adjusted price data from Yahoo Finance when it runs.

### Dashboard controls

- Select the assets to compare: S&P 500, Apple, Naspers and Nasdaq 100.
- Choose a lookback period from 1 to 10 years.
- Change the annual risk-free-rate assumption used in risk-adjusted metrics.
- View prices in local market currencies or convert USD assets to ZAR using USD/ZAR data.
- Download the displayed metrics as a CSV file.

## Original Python analysis

Run the original command-line analysis:

```bash
pip install pandas numpy yfinance
python compare_tickers.py
```

Edit the `tickers` list near the bottom of `compare_tickers.py` to compare other assets.

## Original results (3 years to Nov 2026)

| Ticker | CAGR | Volatility | Max drawdown | Sharpe | Worst day | Arith return |
|---|---|---|---|---|---|---|
| ^GSPC | 16.4% | 15.3% | -18.9% | 0.815 | -6.0% | 16.4% |
| AAPL | 22.7% | 27.0% | -33.4% | 0.694 | -9.2% | 24.2% |
| NPN.JO | -1.4% | 34.8% | -50.2% | -0.155 | -17.7% | 4.7% |
| ^NDX | 18.3% | 21.1% | -22.9% | 0.676 | -6.4% | 19.1% |

## What I found

- The S&P 500 achieved the highest Sharpe ratio in the original analysis, indicating the strongest return relative to risk under that calculation.
- Although Apple and the Nasdaq 100 generated higher returns, they also experienced greater volatility and larger drawdowns.
- NPN.JO recorded a positive average annual arithmetic return but a negative CAGR, illustrating how volatility can reduce compounded growth.

## Methodology and limitations

- The dashboard uses Yahoo Finance adjusted prices with automatic adjustment enabled.
- CAGR is based on the first and last available adjusted prices and elapsed calendar time.
- Annualised volatility uses daily-return standard deviation multiplied by the square root of 252.
- Dashboard Sharpe uses average daily excess returns over the selected daily risk-free rate, annualised by the square root of 252. This differs from the original script's CAGR-based Sharpe calculation, so the figures will not necessarily match.
- The dashboard's default annual risk-free rate is 7%, an editable assumption rather than a live sourced yield. The original command-line script defaults to 4%.
- ZAR conversion uses Yahoo Finance's USD/ZAR series; check exchange-rate coverage and date alignment before relying on converted comparisons.
- Naspers is quoted in ZAR while the US-listed assets are quoted in USD. Currency conversion helps align the comparison but does not remove differences in market hours, trading calendars or data coverage.
- Yahoo Finance is an unofficial data source. Verify data and assumptions before using the analysis in a professional setting.
- Historical performance is not a forecast and does not constitute investment advice.
