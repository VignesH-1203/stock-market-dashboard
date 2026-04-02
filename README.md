# Stackly — Indian Stock Market Dashboard

Live Indian stock market dashboard tracking 8 major NSE stocks.

## Stocks Tracked (NSE)
Reliance Industries, TCS, Infosys, HDFC Bank, ITC, Wipro, Bharti Airtel, Asian Paints

## Features
- Stock selector dropdown with 8 major NSE stocks
- Live price display with daily % change (color-coded)
- Metric cards: Current Price, Day Change %, 52-Week High/Low, Volume
- Interactive candlestick chart (Plotly)
- Line chart with 7-day / 1-month / 3-month / 1-year toggle
- 20-day and 50-day SMA overlays
- Volatility alert when daily change exceeds 3%
- Auto-refresh every 30 minutes
- Dark professional theme

## Setup
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tech Stack
Python, Streamlit, yfinance, Pandas, Plotly
