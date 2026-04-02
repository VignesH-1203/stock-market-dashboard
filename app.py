"""
Indian Stock Market Dashboard
Stackly - Live Indian Stock Market Dashboard
Author: Vignesh | Stackly | For: Dan Rodney & stakeholders
Tech: Streamlit + yfinance + Plotly
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# ============================================================
# PAGE CONFIGURATION
# Sets the browser tab title, icon, and layout to wide mode
# ============================================================
st.set_page_config(
    page_title="Stackly | Indian Stock Dashboard",
    page_icon="📈",
    layout="wide",
)

# ============================================================
# CUSTOM CSS - DARK PROFESSIONAL THEME
# This block injects custom CSS into the Streamlit app to
# override default styles and create a sleek dark theme.
# ============================================================
st.markdown("""
<style>
    /* --- Metric cards: the boxes that show price, volume etc. --- */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px 20px;
    }

    /* Metric label text (e.g. "Current Price") */
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
        font-size: 0.85rem !important;
    }

    /* Metric value text (e.g. "₹2,450.00") */
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f0f6fc !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }

    /* --- Anomaly alert box --- */
    .anomaly-alert {
        background-color: #2d1b1b;
        border: 1px solid #f85149;
        border-radius: 8px;
        padding: 12px 18px;
        margin: 10px 0;
        color: #f85149;
        font-weight: 600;
    }

    /* --- Normal status box --- */
    .normal-status {
        background-color: #1b2d1b;
        border: 1px solid #3fb950;
        border-radius: 8px;
        padding: 12px 18px;
        margin: 10px 0;
        color: #3fb950;
        font-weight: 600;
    }

    /* --- Company header styling --- */
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

    /* --- Footer --- */
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

# ============================================================
# STOCK LIST
# Dictionary mapping display names to Yahoo Finance ticker
# symbols. The .NS suffix tells yfinance to fetch from NSE.
# ============================================================
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

# ============================================================
# TIME RANGE OPTIONS
# Maps user-friendly labels to the number of calendar days
# we need to fetch from Yahoo Finance.
# ============================================================
TIME_RANGES = {
    "7 Days": 7,
    "1 Month": 30,
    "3 Months": 90,
    "1 Year": 365,
}


# ============================================================
# DATA FETCHING FUNCTIONS
# These functions call the Yahoo Finance API via yfinance
# to get stock data. We use Streamlit's @st.cache_data
# decorator so that repeated calls with the same arguments
# return cached results instead of hitting the API again.
# The ttl (time-to-live) means the cache expires after
# 1800 seconds (30 minutes), keeping data reasonably fresh.
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def get_stock_info(ticker_symbol):
    """
    Fetch general info about a stock (name, sector, 52-week
    high/low, etc.) from Yahoo Finance.

    Args:
        ticker_symbol: e.g. "RELIANCE.NS"

    Returns:
        dict with stock info, or empty dict on failure
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        return ticker.info
    except Exception:
        return {}


@st.cache_data(ttl=1800, show_spinner=False)
def get_stock_history(ticker_symbol, days):
    """
    Fetch historical price data for a stock.

    Args:
        ticker_symbol: e.g. "RELIANCE.NS"
        days: how many calendar days of history to fetch

    Returns:
        pandas DataFrame with columns: Open, High, Low, Close, Volume
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        # We add 10 extra days to ensure we have enough trading days
        # (markets are closed on weekends/holidays)
        start_date = datetime.now() - timedelta(days=days + 10)
        data = ticker.history(start=start_date, end=datetime.now())
        return data
    except Exception:
        return pd.DataFrame()


# ============================================================
# CHART BUILDING FUNCTIONS
# These use Plotly to create interactive charts that the user
# can zoom, pan, and hover over for details.
# ============================================================

def create_candlestick_chart(data, stock_name):
    """
    Build a candlestick chart — the standard chart type for
    stock trading. Each "candle" shows 4 prices for one day:
      - Open (where the body starts)
      - Close (where the body ends)
      - High (top of the wick/shadow)
      - Low (bottom of the wick/shadow)

    Green candle = price went UP that day (close > open)
    Red candle   = price went DOWN that day (close < open)

    Args:
        data: DataFrame with Open, High, Low, Close columns
        stock_name: display name for the chart title

    Returns:
        plotly Figure object
    """
    fig = go.Figure(data=[
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            increasing_line_color="#3fb950",   # Green for up days
            decreasing_line_color="#f85149",   # Red for down days
            increasing_fillcolor="#238636",
            decreasing_fillcolor="#da3633",
            name="Price",
        )
    ])

    # Apply dark theme styling to the chart
    fig.update_layout(
        title=dict(text=f"{stock_name} — Candlestick Chart", font=dict(color="#f0f6fc", size=16)),
        plot_bgcolor="#0d1117",       # Chart area background
        paper_bgcolor="#0d1117",      # Surrounding area background
        font=dict(color="#8b949e"),
        xaxis=dict(
            gridcolor="#21262d",
            rangeslider=dict(visible=False),  # Hide the mini chart below
        ),
        yaxis=dict(
            gridcolor="#21262d",
            title="Price (₹)",
        ),
        height=450,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def create_line_chart(data, stock_name, show_sma_20, show_sma_50):
    """
    Build a line chart showing closing prices over time, with
    optional moving average overlays.

    Moving Averages (SMA = Simple Moving Average):
      - 20-day SMA: average of the last 20 closing prices.
        Shows short-term trend direction.
      - 50-day SMA: average of the last 50 closing prices.
        Shows medium-term trend direction.

    When the 20-day crosses ABOVE the 50-day, it's often seen
    as a bullish (buy) signal. The reverse is bearish (sell).

    Args:
        data: DataFrame with Close column
        stock_name: display name for the chart title
        show_sma_20: bool — whether to draw the 20-day SMA line
        show_sma_50: bool — whether to draw the 50-day SMA line

    Returns:
        plotly Figure object
    """
    fig = go.Figure()

    # Main price line
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="Close Price",
        line=dict(color="#58a6ff", width=2),  # Blue line
    ))

    # 20-day Simple Moving Average (short-term trend)
    if show_sma_20 and len(data) >= 20:
        # .rolling(20).mean() calculates the average of each
        # sliding window of 20 consecutive closing prices
        sma_20 = data["Close"].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=sma_20,
            mode="lines",
            name="20-Day SMA",
            line=dict(color="#f0883e", width=1.5, dash="dash"),  # Orange dashed
        ))

    # 50-day Simple Moving Average (medium-term trend)
    if show_sma_50 and len(data) >= 50:
        sma_50 = data["Close"].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=sma_50,
            mode="lines",
            name="50-Day SMA",
            line=dict(color="#bc8cff", width=1.5, dash="dot"),  # Purple dotted
        ))

    # Dark theme styling
    fig.update_layout(
        title=dict(text=f"{stock_name} — Price Trend", font=dict(color="#f0f6fc", size=16)),
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font=dict(color="#8b949e"),
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d", title="Price (₹)"),
        legend=dict(
            bgcolor="rgba(22,27,34,0.8)",
            bordercolor="#30363d",
            font=dict(color="#e0e0e0"),
        ),
        height=400,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


# ============================================================
# SIDEBAR - User Controls
# The sidebar contains all interactive controls: stock picker,
# time range, moving average toggles, and a refresh button.
# ============================================================

with st.sidebar:
    # Company branding
    st.markdown("### 📊 Stackly Dashboard")
    st.markdown("*Live Indian Stock Market Dashboard*")

    # About section — brief description for anyone visiting the dashboard
    st.caption(
        "Real-time Indian stock market tracker powered by Yahoo Finance (NSE). "
        "Tracks 8 major stocks with live prices, trend analysis, and volatility "
        "alerts. Data refreshes every 30 minutes."
    )
    st.markdown("---")

    # Stock selector dropdown
    # The user picks a friendly name; we look up the ticker symbol
    selected_stock_name = st.selectbox(
        "Select Stock",
        options=list(STOCKS.keys()),   # ["Reliance Industries", "TCS", ...]
        index=0,                        # Default to first stock
    )
    ticker_symbol = STOCKS[selected_stock_name]

    st.markdown("---")

    # Time range radio buttons for the line chart
    selected_range = st.radio(
        "Price History Range",
        options=list(TIME_RANGES.keys()),
        index=1,  # Default to "1 Month"
    )
    days = TIME_RANGES[selected_range]

    st.markdown("---")

    # Moving average toggles (checkboxes)
    st.markdown("**Moving Averages**")
    show_sma_20 = st.checkbox("20-Day SMA", value=True)
    show_sma_50 = st.checkbox("50-Day SMA", value=True)

    st.markdown("---")

    # Manual refresh button — clears the cache so fresh data is fetched
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Show when data was last fetched
    st.markdown(f"**Last Updated**  \n{datetime.now().strftime('%d %b %Y, %I:%M %p')}")


# ============================================================
# MAIN CONTENT AREA
# ============================================================

# --- Page Title ---
st.markdown(f"<div class='company-header'>{selected_stock_name}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='company-sector'>NSE: {ticker_symbol.replace('.NS', '')} &nbsp;•&nbsp; Indian Stock Market</div>", unsafe_allow_html=True)
st.markdown("")  # Spacer

# --- Fetch Data ---
# Show a spinner while we wait for the API response
with st.spinner("Fetching market data..."):
    info = get_stock_info(ticker_symbol)
    # For candlestick chart we always fetch 90 days
    hist_candle = get_stock_history(ticker_symbol, 90)
    # For the line chart we fetch the user-selected range
    hist_line = get_stock_history(ticker_symbol, days)

# --- Handle errors ---
# If yfinance returned no data, show a warning and stop
if not info or hist_candle.empty:
    st.error("⚠️ Could not fetch data. The market may be closed or the ticker may be invalid. Please try refreshing.")
    st.stop()  # Halts the rest of the script

# ============================================================
# EXTRACT KEY METRICS FROM STOCK INFO
# The `info` dict from yfinance contains many fields. We pull
# out only the ones we need. The .get() method provides a
# fallback value if the field is missing.
# ============================================================
current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose", 0)
high_52_week = info.get("fiftyTwoWeekHigh", 0)
low_52_week = info.get("fiftyTwoWeekLow", 0)
volume = info.get("volume") or info.get("regularMarketVolume", 0)
sector = info.get("sector", "N/A")

# Calculate daily change (how much the price moved today)
if previous_close and previous_close > 0:
    day_change = current_price - previous_close          # Absolute change in ₹
    day_change_pct = (day_change / previous_close) * 100  # Percentage change
else:
    day_change = 0
    day_change_pct = 0

# ============================================================
# METRIC CARDS ROW
# Display 5 key metrics in a horizontal row using st.columns.
# st.metric() automatically colors the delta green (positive)
# or red (negative).
# ============================================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Current Price",
        value=f"₹{current_price:,.2f}",    # Format with commas and 2 decimals
        delta=None,                          # No delta arrow for this card
    )

with col2:
    st.metric(
        label="Day Change",
        value=f"{day_change_pct:+.2f}%",     # +/- sign always shown
        delta=f"₹{day_change:+.2f}",         # Shows the ₹ change with arrow
    )

with col3:
    st.metric(
        label="52-Week High",
        value=f"₹{high_52_week:,.2f}",
    )

with col4:
    st.metric(
        label="52-Week Low",
        value=f"₹{low_52_week:,.2f}",
    )

with col5:
    # Format volume with commas for readability (e.g. 12,345,678)
    st.metric(
        label="Volume",
        value=f"{volume:,.0f}",
    )

# ============================================================
# VOLATILITY / ANOMALY ALERT
# If the stock price moved more than 3% in a single day,
# that's unusual — we flag it as an anomaly for attention.
# ============================================================
st.markdown("")  # Spacer

if abs(day_change_pct) > 3:
    # Big move detected — show red alert
    direction = "UP" if day_change_pct > 0 else "DOWN"
    st.markdown(
        f"<div class='anomaly-alert'>⚠️ VOLATILITY ALERT: {selected_stock_name} "
        f"moved {direction} {abs(day_change_pct):.2f}% today — exceeds 3% threshold</div>",
        unsafe_allow_html=True,
    )
else:
    # Normal trading day — show green status
    st.markdown(
        f"<div class='normal-status'>✅ Normal trading range — "
        f"daily change: {day_change_pct:+.2f}%</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# CHARTS SECTION
# Two charts side by side: candlestick (left) and line (right)
# ============================================================
st.markdown("")  # Spacer

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if not hist_candle.empty:
        candlestick_fig = create_candlestick_chart(hist_candle, selected_stock_name)
        st.plotly_chart(candlestick_fig, use_container_width=True)

with chart_col2:
    if not hist_line.empty:
        line_fig = create_line_chart(hist_line, selected_stock_name, show_sma_20, show_sma_50)
        st.plotly_chart(line_fig, use_container_width=True)

# ============================================================
# RAW DATA TABLE (expandable)
# Users can expand this section to see the actual numbers
# behind the chart. We show only the last 20 trading days
# and format prices to 2 decimal places.
# ============================================================
with st.expander("📋 View Raw Data (Recent Trading Days)"):
    if not hist_line.empty:
        # Take last 20 rows, reverse so newest is first
        display_data = hist_line.tail(20).copy()
        display_data = display_data[["Open", "High", "Low", "Close", "Volume"]]
        display_data.index = display_data.index.strftime("%d %b %Y")  # Format dates nicely
        display_data = display_data.sort_index(ascending=False)

        # Round prices to 2 decimal places for clean display
        for col in ["Open", "High", "Low", "Close"]:
            display_data[col] = display_data[col].round(2)

        st.dataframe(display_data, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    "<div class='footer-text'>"
    "Stackly — Live Indian Stock Market Dashboard &nbsp;|&nbsp; "
    "Data: Yahoo Finance (NSE) &nbsp;|&nbsp; "
    f"Dashboard loaded: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}"
    "</div>",
    unsafe_allow_html=True,
)

# ============================================================
# AUTO-REFRESH (lightweight, non-blocking)
# st_autorefresh triggers a page rerun every 1,800,000 ms
# (30 minutes). Unlike time.sleep(), this does NOT freeze the
# app — it uses a tiny JS timer in the browser. When the timer
# fires, Streamlit reruns the script and the expired cache
# (@st.cache_data ttl=1800) fetches fresh data automatically.
# ============================================================
st_autorefresh(interval=1800 * 1000, key="market_data_refresh")
