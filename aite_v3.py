# AITE v3.0 - Real-Time BTCUSDT Validator Engine (Bybit Spot + News Integration)
# --------------------------------------------------
# Author: ChatGPT (for Ali / AITE Project)
# Description: This bot fetches real-time BTCUSDT data, intraday high/low, validates SL/TP,
# and scrapes financial news to support precision trade validation. Expanding as Option C.

import requests
import time
from datetime import datetime, timezone
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st

BYBIT_API_URL = "https://api.bybit.com"
SYMBOL = "BTCUSDT"

# ========== [1] Fetch Real-Time Ticker Info ==========
def get_realtime_price():
    url = f"{BYBIT_API_URL}/v2/public/tickers?symbol={SYMBOL}"
    response = requests.get(url)
    data = response.json()
    ticker = data['result'][0]
    return {
        'price': float(ticker['last_price']),
        'high': float(ticker['high_price_24h']),
        'low': float(ticker['low_price_24h']),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

# ========== [2] Validate SL and TP ==========
def validate_trade(entry, sl, tp):
    market = get_realtime_price()
    is_tp_valid = tp <= market['high']
    is_sl_valid = sl >= market['low']
    return {
        'entry': entry,
        'SL': sl,
        'TP': tp,
        'valid_SL': is_sl_valid,
        'valid_TP': is_tp_valid,
        'live_price': market['price'],
        'high': market['high'],
        'low': market['low'],
        'timestamp_utc': market['timestamp']
    }

# ========== [3] Fetch Live News (Sample RSS - FXStreet) ==========
def get_fxstreet_news():
    try:
        rss_url = "https://www.fxstreet.com/rss/news"
        response = requests.get(rss_url)
        if response.status_code != 200:
            return ["News fetch failed."]
        soup = BeautifulSoup(response.text, 'xml')
        headlines = soup.find_all('title')[1:6]
        return [headline.text for headline in headlines]
    except Exception as e:
        return [f"Error fetching news: {str(e)}"]

# ========== [4] Streamlit UI ==========
st.set_page_config(page_title="AITE v3.0 Realtime Engine", layout="wide")
st.title("📈 AITE v3.0: BTCUSDT Real-Time Validator")

entry_price = st.number_input("Entry Price", min_value=10000.0, max_value=100000.0, value=67000.0, step=10.0)
stop_loss = st.number_input("Stop Loss", min_value=10000.0, max_value=100000.0, value=66000.0, step=10.0)
take_profit = st.number_input("Take Profit", min_value=10000.0, max_value=100000.0, value=69000.0, step=10.0)

if st.button("🚦 Validate Trade"):
    result = validate_trade(entry_price, stop_loss, take_profit)
    st.subheader("✅ Trade Validation Result:")
    st.dataframe(pd.DataFrame([result]))

    st.subheader("📰 Live FXStreet Headlines:")
    news_list = get_fxstreet_news()
    for news in news_list:
        st.write(f"- {news}")
