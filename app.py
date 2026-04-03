"""
Stackly - Live Indian Stock Market Dashboard
Tech: Streamlit, yfinance, Pandas, Plotly
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh

# --- Page config ---
st.set_page_config(
    page_title="Stackly | Indian Stock Dashboard",
    page_icon="📈",
    layout="wide",
)

# --- Custom CSS ---
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px 20px;
    }
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
        font-size: 0.85rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f0f6fc !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    .anomaly-alert {
        background-color: #2d1b1b;
        border: 1px solid #f85149;
        border-radius: 8px;
        padding: 12px 18px;
        margin: 10px 0;
        color: #f85149;
        font-weight: 600;
    }
    .normal-status {
        background-color: #1b2d1b;
        border: 1px solid #3fb950;
        border-radius: 8px;
        padding: 12px 18px;
        margin: 10px 0;
        color: #3fb950;
        font-weight: 600;
    }
    .company-header {
        font-size: 2rem;
        font-weight: 800;
        color: #f0f6fc;
        margin-bottom: 0;
    }
    .company-sector {
        color: #8b949e;
        font-size: 0.95rem;
    }
    .footer-text {
        color: #484f58;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 30px;
        padding: 15px;
        border-top: 1px solid #21262d;
    }
</style>
""", unsafe_allow_html=True)

# --- Stock list (.NS = NSE tickers) ---
STOCKS = {
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ITC": "ITC.NS",
    "Wipro": "WIPRO.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Asian Paints": "ASIANPAINT.NS",
}

# --- Time range options (label -> days) ---
TIME_RANGES = {
    "7 Days": 7,
    "1 Month": 30,
    "3 Months": 90,
    "1 Year": 365,
}


# --- Data fetching (cached for 30 min) ---

@st.cache_data(ttl=1800, show_spinner=False)
def get_stock_info(ticker_symbol):
    """Fetch stock info (price, 52-week range, volume, etc.)."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        return ticker.info
    except Exception:
        return {}


@st.cache_data(ttl=1800, show_spinner=False)
def get_stock_history(ticker_symbol, days):
    """Fetch historical OHLCV data for the given number of days."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        start_date = datetime.now(ZoneInfo("Asia/Kolkata")) - timedelta(days=days + 10)
        data = ticker.history(start=start_date, end=datetime.now(ZoneInfo("Asia/Kolkata")))
        return data
    except Exception:
        return pd.DataFrame()


# --- Chart builders ---

def create_candlestick_chart(data, stock_name):
    """Build an interactive candlestick chart with dark theme."""
    fig = go.Figure(data=[
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            increasing_line_color="#3fb950",
            decreasing_line_color="#f85149",
            increasing_fillcolor="#238636",
            decreasing_fillcolor="#da3633",
            name="Price",
        )
    ])
    fig.update_layout(
        title=dict(text=f"{stock_name} — Candlestick Chart", font=dict(color="#f0f6fc", size=16)),
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="#8b949e"),
        xaxis=dict(gridcolor="#21262d", rangeslider=dict(visible=False)),
        yaxis=dict(gridcolor="#21262d", title="Price (₹)"),
        height=450,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def create_line_chart(data, stock_name, show_sma_20, show_sma_50):
    """Build a line chart with optional 20/50-day SMA overlays."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="Close Price",
        line=dict(color="#58a6ff", width=2),
    ))

    # 20-day Simple Moving Average
    if show_sma_20 and len(data) >= 20:
        sma_20 = data["Close"].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=data.index, y=sma_20, mode="lines", name="20-Day SMA",
            line=dict(color="#f0883e", width=1.5, dash="dash"),
        ))

    # 50-day Simple Moving Average
    if show_sma_50 and len(data) >= 50:
        sma_50 = data["Close"].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=data.index, y=sma_50, mode="lines", name="50-Day SMA",
            line=dict(color="#bc8cff", width=1.5, dash="dot"),
        ))

    fig.update_layout(
        title=dict(text=f"{stock_name} — Price Trend", font=dict(color="#f0f6fc", size=16)),
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="#8b949e"),
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d", title="Price (₹)"),
        legend=dict(bgcolor="rgba(22,27,34,0.8)", bordercolor="#30363d", font=dict(color="#e0e0e0")),
        height=400,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# --- Sidebar ---

with st.sidebar:
    st.markdown("### 📊 Stackly Dashboard")
    st.markdown("*Live Indian Stock Market Dashboard*")

    st.caption(
        "Real-time Indian stock market tracker powered by Yahoo Finance (NSE). "
        "Tracks 8 major stocks with live prices, trend analysis, and volatility "
        "alerts. Data refreshes every 30 minutes."
    )
    st.markdown("---")

    selected_stock_name = st.selectbox(
        "Select Stock",
        options=list(STOCKS.keys()),
        index=0,
    )
    ticker_symbol = STOCKS[selected_stock_name]

    st.markdown("---")

    selected_range = st.radio(
        "Price History Range",
        options=list(TIME_RANGES.keys()),
        index=1,
    )
    days = TIME_RANGES[selected_range]

    st.markdown("---")

    st.markdown("**Moving Averages**")
    show_sma_20 = st.checkbox("20-Day SMA", value=True)
    show_sma_50 = st.checkbox("50-Day SMA", value=True)

    st.markdown("---")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(f"**Last Updated**  \n{datetime.now(ZoneInfo("Asia/Kolkata")).strftime('%d %b %Y, %I:%M %p')}")


# --- Main content ---

st.markdown(f"<div class='company-header'>{selected_stock_name}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='company-sector'>NSE: {ticker_symbol.replace('.NS', '')} &nbsp;•&nbsp; Indian Stock Market</div>", unsafe_allow_html=True)
st.markdown("")

with st.spinner("Fetching market data..."):
    info = get_stock_info(ticker_symbol)
    hist_candle = get_stock_history(ticker_symbol, 90)
    hist_line = get_stock_history(ticker_symbol, days)

if not info or hist_candle.empty:
    st.error("⚠️ Could not fetch data. The market may be closed or the ticker may be invalid. Please try refreshing.")
    st.stop()

# --- Extract key metrics ---
current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose", 0)
high_52_week = info.get("fiftyTwoWeekHigh", 0)
low_52_week = info.get("fiftyTwoWeekLow", 0)
volume = info.get("volume") or info.get("regularMarketVolume", 0)
sector = info.get("sector", "N/A")

# Daily price change
if previous_close and previous_close > 0:
    day_change = current_price - previous_close
    day_change_pct = (day_change / previous_close) * 100
else:
    day_change = 0
    day_change_pct = 0

# --- Metric cards ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label="Current Price", value=f"₹{current_price:,.2f}")

with col2:
    st.metric(label="Day Change", value=f"{day_change_pct:+.2f}%", delta=f"₹{day_change:+.2f}")

with col3:
    st.metric(label="52-Week High", value=f"₹{high_52_week:,.2f}")

with col4:
    st.metric(label="52-Week Low", value=f"₹{low_52_week:,.2f}")

with col5:
    st.metric(label="Volume", value=f"{volume:,.0f}")

# --- Volatility alert (flags moves > 3%) ---
st.markdown("")

if abs(day_change_pct) > 3:
    direction = "UP" if day_change_pct > 0 else "DOWN"
    st.markdown(
        f"<div class='anomaly-alert'>⚠️ VOLATILITY ALERT: {selected_stock_name} "
        f"moved {direction} {abs(day_change_pct):.2f}% today — exceeds 3% threshold</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"<div class='normal-status'>✅ Normal trading range — "
        f"daily change: {day_change_pct:+.2f}%</div>",
        unsafe_allow_html=True,
    )

# --- Charts (candlestick + line side by side) ---
st.markdown("")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if not hist_candle.empty:
        candlestick_fig = create_candlestick_chart(hist_candle, selected_stock_name)
        st.plotly_chart(candlestick_fig, use_container_width=True)

with chart_col2:
    if not hist_line.empty:
        line_fig = create_line_chart(hist_line, selected_stock_name, show_sma_20, show_sma_50)
        st.plotly_chart(line_fig, use_container_width=True)

# --- Raw data table ---
with st.expander("📋 View Raw Data (Recent Trading Days)"):
    if not hist_line.empty:
        display_data = hist_line.tail(20).copy()
        display_data = display_data[["Open", "High", "Low", "Close", "Volume"]]
        display_data.index = display_data.index.strftime("%d %b %Y")
        display_data = display_data.sort_index(ascending=False)
        for col in ["Open", "High", "Low", "Close"]:
            display_data[col] = display_data[col].round(2)
        st.dataframe(display_data, use_container_width=True)

# --- Footer ---
st.markdown(
    "<div class='footer-text'>"
    "Stackly — Live Indian Stock Market Dashboard &nbsp;|&nbsp; "
    "Data: Yahoo Finance (NSE) &nbsp;|&nbsp; "
    f"Dashboard loaded: {datetime.now(ZoneInfo("Asia/Kolkata")).strftime('%d %b %Y, %I:%M:%S %p')}"
    "</div>",
    unsafe_allow_html=True,
)

# --- Auto-refresh every 30 minutes (non-blocking browser timer) ---
st_autorefresh(interval=1800 * 1000, key="market_data_refresh")
