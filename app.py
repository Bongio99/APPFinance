import streamlit as st
import pandas as pd
import requests

st.title("📊 Technical Stock Screener (Alpha Vantage API)")

# API Key da Streamlit Secrets (più sicuro) - fallback al valore hardcoded se vuoi testare in locale
api_key = st.secrets.get("alpha_vantage_api_key", "2QJ43KJ9AHL6I7WD")

# Input simbolo azionario
symbol = st.text_input("Inserisci il simbolo azionario (es. AAPL, MSFT)", "AAPL")

# Intervallo dati e indicatori tecnici da mostrare
interval = st.selectbox("Seleziona l'intervallo", ["daily", "weekly", "monthly"])

if st.button("Mostra dati e indicatori"):

    # Mappa funzione API Alpha Vantage in base all'intervallo scelto
    function_map = {
        "daily": "TIME_SERIES_DAILY_ADJUSTED",
        "weekly": "TIME_SERIES_WEEKLY_ADJUSTED",
        "monthly": "TIME_SERIES_MONTHLY_ADJUSTED"
    }
    function = function_map[interval]

    url = "https://www.alphavantage.co/query"
    params = {
        "function": function,
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "compact"
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Controlla se la risposta ha i dati
    time_series_key = None
    for key in data.keys():
        if "Time Series" in key:
            time_series_key = key
            break

    if time_series_key:
        df = pd.DataFrame.from_dict(data[time_series_key], orient="index", dtype=float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        st.subheader(f"📈 Dati {interval} per {symbol.upper()}")
        st.dataframe(df)

        # Grafico prezzo di chiusura adjusted
        st.line_chart(df["5. adjusted close"])

        # Calcolo indicatori tecnici base (es. SMA 10 e RSI 14)

        # SMA 10
        df['SMA_10'] = df["5. adjusted close"].rolling(window=10).mean()

        # RSI 14 (semplice calcolo)
        delta = df["5. adjusted close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['RSI_14'] = 100 - (100 / (1 + rs))

        st.subheader("Indicatori Tecnici")
        st.line_chart(df[['SMA_10', 'RSI_14']].dropna())

    else:
        st.error("❌ Errore: simbolo non trovato o limite API superato.")


