import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Ticker Comparison Dashboard", page_icon="📈", layout="wide")

TICKERS = {"S&P 500": "^GSPC", "Apple": "AAPL", "Naspers": "NPN.JO", "Nasdaq 100": "^NDX"}
TRADING_DAYS = 252


@st.cache_data(ttl=900, show_spinner=False)
def load_prices(tickers, period):
    raw = yf.download(list(tickers.values()), period=period, auto_adjust=True,
                      progress=False, group_by="ticker", threads=True)
    prices = {}
    for label, ticker in tickers.items():
        try:
            series = raw[ticker]["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw["Close"]
            series = pd.to_numeric(series, errors="coerce").dropna()
            if not series.empty:
                prices[label] = series.rename(label)
        except (KeyError, TypeError):
            continue
    return pd.concat(prices.values(), axis=1).sort_index().dropna(how="all") if prices else pd.DataFrame()


def calculate_metrics(prices, annual_rf):
    rows = []
    daily_rf = (1 + annual_rf) ** (1 / TRADING_DAYS) - 1
    for asset in prices.columns:
        close = prices[asset].dropna()
        returns = close.pct_change().dropna()
        if len(close) < 2 or len(returns) < 2:
            continue
        years = (close.index[-1] - close.index[0]).days / 365.25
        if years <= 0:
            continue
        cagr = (close.iloc[-1] / close.iloc[0]) ** (1 / years) - 1
        daily_std = returns.std(ddof=1)
        volatility = daily_std * np.sqrt(TRADING_DAYS)
        excess = returns - daily_rf
        sharpe = excess.mean() / daily_std * np.sqrt(TRADING_DAYS) if daily_std > 0 else np.nan
        downside = np.minimum(returns - daily_rf, 0)
        downside_dev = np.sqrt(np.mean(downside ** 2)) * np.sqrt(TRADING_DAYS)
        sortino = (cagr - annual_rf) / downside_dev if downside_dev > 0 else np.nan
        drawdown = close / close.cummax() - 1
        rows.append({
            "Asset": asset, "Start": close.index[0].date(), "End": close.index[-1].date(),
            "Total return": close.iloc[-1] / close.iloc[0] - 1, "CAGR": cagr,
            "Volatility": volatility, "Max drawdown": drawdown.min(),
            "Sharpe": sharpe, "Sortino": sortino, "Worst day": returns.min(),
        })
    return pd.DataFrame(rows).set_index("Asset") if rows else pd.DataFrame()


st.title("Ticker Comparison Dashboard")
st.caption("Historical market performance | Yahoo Finance data | Educational analysis, not investment advice")

with st.sidebar:
    st.header("Dashboard controls")
    period = st.selectbox("Lookback period", ["1y", "2y", "3y", "5y", "10y"], index=2)
    selected = st.multiselect("Assets", list(TICKERS), default=list(TICKERS))
    annual_rf = st.number_input("Annual risk-free rate (%)", -5.0, 30.0, 7.0, 0.25) / 100
    currency_mode = st.selectbox("Currency view", ["Local market currency", "Convert all to ZAR"])
    refresh = st.button("Refresh market data", use_container_width=True)

if not selected:
    st.info("Select at least one asset in the sidebar.")
    st.stop()

if refresh:
    st.cache_data.clear()

with st.spinner("Downloading adjusted price history..."):
    prices = load_prices({label: TICKERS[label] for label in selected}, period)

if prices.empty:
    st.error("No usable price data was returned. Check the ticker symbols or try again later.")
    st.stop()

currency_note = "Returns are shown in each instrument's quoted market currency."
if currency_mode == "Convert all to ZAR":
    fx = yf.download("USDZAR=X", period=period, auto_adjust=True, progress=False)
    fx_close = fx["Close"].squeeze() if isinstance(fx.columns, pd.MultiIndex) else fx["Close"]
    fx_close = pd.to_numeric(fx_close, errors="coerce").dropna().rename("USD/ZAR")
    prices = prices.join(fx_close, how="left")
    for asset in prices.columns.drop("USD/ZAR"):
        if asset != "Naspers":
            prices[asset] = prices[asset] * prices["USD/ZAR"]
    prices = prices.drop(columns=["USD/ZAR"])
    currency_note = "USD assets are converted to ZAR using daily USD/ZAR rates; Naspers is already quoted in ZAR."
st.caption(currency_note)

metrics = calculate_metrics(prices, annual_rf)
if metrics.empty:
    st.error("There is not enough valid price history to calculate metrics.")
    st.stop()

best_cagr = metrics["CAGR"].idxmax()
best_sharpe = metrics["Sharpe"].idxmax() if metrics["Sharpe"].notna().any() else "N/A"
lowest_vol = metrics["Volatility"].idxmin()

c1, c2, c3 = st.columns(3)
c1.metric("Highest CAGR", best_cagr, f"{metrics.loc[best_cagr, 'CAGR']:.1%}")
c2.metric("Highest Sharpe", best_sharpe, f"{metrics.loc[best_sharpe, 'Sharpe']:.2f}" if best_sharpe != "N/A" else "N/A")
c3.metric("Lowest volatility", lowest_vol, f"{metrics.loc[lowest_vol, 'Volatility']:.1%}")

st.subheader("Indexed performance")
indexed = prices.copy()
for asset in indexed.columns:
    series = indexed[asset].dropna()
    if not series.empty:
        indexed[asset] = series / series.iloc[0] * 100
fig = px.line(indexed, x=indexed.index, y=indexed.columns,
              labels={"value": "Growth of 100", "variable": "Asset", "x": "Date"})
fig.update_layout(legend_title_text="", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)
st.caption("Each asset is rebased to 100 at its first available observation. Start dates may differ.")

left, right = st.columns(2)
with left:
    st.subheader("Risk vs. return")
    chart = px.scatter(metrics.reset_index(), x="Volatility", y="CAGR", color="Asset",
                       text="Asset", labels={"Volatility": "Annualised volatility", "CAGR": "CAGR"})
    chart.update_traces(textposition="top center")
    st.plotly_chart(chart, use_container_width=True)
with right:
    st.subheader("Drawdown over time")
    drawdowns = prices / prices.cummax() - 1
    chart = px.line(drawdowns, x=drawdowns.index, y=drawdowns.columns,
                    labels={"value": "Drawdown", "variable": "Asset", "x": "Date"})
    chart.update_yaxes(tickformat=".0%")
    chart.update_layout(legend_title_text="", hovermode="x unified")
    st.plotly_chart(chart, use_container_width=True)

st.subheader("Performance and risk metrics")
display = metrics.copy()
for col in ["Total return", "CAGR", "Volatility", "Max drawdown", "Worst day"]:
    display[col] = display[col].map(lambda x: f"{x:.2%}" if pd.notna(x) else "—")
for col in ["Sharpe", "Sortino"]:
    display[col] = display[col].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
st.dataframe(display, use_container_width=True)
st.download_button("Download metrics CSV", metrics.reset_index().to_csv(index=False).encode("utf-8"),
                   "ticker_comparison_metrics.csv", "text/csv")

st.subheader("Key interpretation")
st.markdown(f"""
- **Return leader:** {best_cagr} has the highest CAGR in this selected period.
- **Risk-adjusted leader:** {best_sharpe} has the highest Sharpe ratio under the selected risk-free-rate assumption.
- **Lowest volatility:** {lowest_vol} had the lowest annualised daily-return variability.
- **Drawdown matters:** maximum drawdown highlights the largest peak-to-trough decline.
""")

with st.expander("Methodology and limitations"):
    st.markdown("""
- Adjusted prices are downloaded from Yahoo Finance with auto-adjustment enabled.
- CAGR uses the first and last available adjusted prices and elapsed calendar time.
- Annualised volatility is daily-return standard deviation multiplied by the square root of 252.
- Sharpe uses average daily excess returns over the assumed daily risk-free rate, annualised by the square root of 252.
- Sortino uses downside deviation relative to the daily risk-free rate.
- The risk-free rate is an editable assumption, not a live sourced yield.
- ZAR conversion uses Yahoo Finance's USD/ZAR series; verify FX coverage and dates before relying on converted results.
- Different market hours, currencies, missing observations and start dates can affect comparisons.
- Historical performance is not a forecast or a recommendation to buy or sell.
""")
st.caption("For learning and portfolio analysis only. Verify data and assumptions independently.")
