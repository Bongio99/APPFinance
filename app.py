import streamlit as st
import pandas as pd
import requests
from tqdm import tqdm

# Configurazione Streamlit
st.set_page_config(page_title="Technical Stock Screener - TAAPI.io", layout="wide")
st.title("📊 Technical Stock Screener (taapi.io API)")

# API Token
api_token = st.secrets["TAAPI_API_KEY"] if "TAAPI_API_KEY" in st.secrets else "<YOUR_API_TOKEN_HERE>"

# Funzione per ottenere simboli supportati
@st.cache_data
def fetch_symbols():
    url = 'https://api.taapi.io/exchange-symbols'
    params = {
        "secret": api_token,
        "type": "stocks"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch symbols from taapi.io API.")
        return []

# Otteniamo simboli disponibili
symbols = fetch_symbols()

if not symbols:
    st.stop()

# Sidebar per selezione simboli
symbol_options = [s['symbol'] for s in symbols]
selected_symbols = st.sidebar.multiselect("Select Symbols", symbol_options, default=symbol_options[:5])

# Selezione intervallo temporale
interval = st.sidebar.selectbox("Select Interval", ["1h", "4h", "1d"])

# Selezione indicatore
indicator = st.sidebar.selectbox("Select Technical Indicator", ["rsi", "macd", "ema"])

# Parametri RSI
if indicator == "rsi":
    rsi_lower = st.sidebar.slider("RSI Lower Threshold", 0, 50, 30)
    rsi_upper = st.sidebar.slider("RSI Upper Threshold", 50, 100, 70)

# Funzione per ottenere indicatori da taapi.io
def fetch_indicator(symbol, interval, indicator):
    url = f"https://api.taapi.io/{indicator}"
    params = {
        "secret": api_token,
        "exchange": "stocks",
        "symbol": symbol,
        "interval": interval
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Elaborazione dati
results = []

with st.spinner("Fetching indicator data..."):
    for symbol in tqdm(selected_symbols):
        data = fetch_indicator(symbol, interval, indicator)
        if data and 'value' in data:
            entry = {"Symbol": symbol, "Indicator Value": data['value']}
            if indicator == "rsi":
                if rsi_lower <= data['value'] <= rsi_upper:
                    results.append(entry)
            else:
                results.append(entry)

# Visualizzazione risultati
if results:
    st.subheader("📋 Filtered Results")
    st.dataframe(pd.DataFrame(results), use_container_width=True)
else:
    st.info("No stocks met the filter criteria.")

# Footer
st.markdown("---")
st.markdown("📄 **Technical Stock Screener using taapi.io API, Streamlit & Python**")

