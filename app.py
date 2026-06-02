import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

# Seiteneinstellungen für das Handy optimieren
st.set_page_config(page_title="Gold Scalping Tool", page_icon="💰", layout="centered")

st.title("💰 Gold Scalping Analyzer")
st.write("Lokale Echtzeitanalyse für XAU-USD (Gold)")

# Logik-Klasse für die Berechnung
class GoldScalpingLogic:
    def __init__(self, symbol="GC=F"):
        self.symbol = symbol
        self.data = None

    def fetch_data(self):
        try:
            # Holt die neuesten 15-Minuten-Daten der letzten 5 Tage
            self.data = yf.download(tickers=self.symbol, period="5d", interval="15m", progress=False)
            return True
        except:
            return False

    def calculate_metrics(self, crv_ratio):
        if self.data is None or len(self.data) < 20:
            return 50, 0, 0, 0
        
        # Daten glätten
        close_prices = self.data['Close'].values.flatten()
        current_price = float(close_prices[-1])
        avg_price = float(np.mean(close_prices[-20:]))
        
        # Wahrscheinlichkeits-Heuristik
        if current_price > avg_price:
            prob = 72
        else:
            prob = 42
            
        # SL und TP berechnen (0.5% Risiko vom aktuellen Kurs)
        sl_dist = current_price * 0.005
        sl = current_price - sl_dist
        tp = current_price + (sl_dist * crv_ratio)
        
        return prob, round(current_price, 2), round(sl, 2), round(tp, 2)

logic = GoldScalpingLogic()

# Button zum manuellen Aktualisieren
if st.button("🔄 Daten aktualisieren"):
    st.rerun()

if logic.fetch_data():
    # Slider für das Chance-Risiko-Verhältnis (CRV)
    crv = st.slider("Chance-Risiko-Verhältnis (CRV)", min_value=2, max_value=4, value=2, step=1)
    
    # Metriken berechnen
    prob, entry, sl, tp = logic.calculate_metrics(crv)
    
    st.markdown("---")
    
    # Farbige Anzeige der Wahrscheinlichkeit
    if prob > 60:
        st.success(f"### Erfolgswahrscheinlichkeit: {prob}% (Starkes Signal)")
    else:
        st.warning(f"### Erfolgswahrscheinlichkeit: {prob}% (Neutral/Schwach)")
        
    # Preis-Boxen anzeigen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Einstieg (USD)", value=f"{entry}")
    with col2:
        st.metric(label="Stop Loss", value=f"{sl}")
    with col3:
        st.metric(label="Take Profit", value=f"{tp}")
        
    st.markdown("---")
    
    # Fake MT5 Sektion (wie im Kivy Prototyp)
    with st.expander("🔐 MetaTrader 5 Verbindung (Optional)"):
        server = st.text_input("MT5 Server")
        login = st.text_input("Kontonummer / Login")
        password = st.text_input("Passwort", type="password")
        if st.button("Login & Trade"):
            st.info("MT5-Schnittstelle im Prototyp inaktiv. Daten werden nur lokal berechnet.")
else:
    st.error("Fehler beim Laden der Live-Marktdaten von Yahoo Finance. Bitte lade die Seite neu.")
