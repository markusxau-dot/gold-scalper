import streamlit as st
import yfinance as yf
import numpy as np

# Seiteneinstellungen für maximale Kompaktheit
st.set_page_config(page_title="Gold Scalper", page_icon="💰", layout="centered")

# CSS für Schatten, fette Slider und definierte Kanten auf dem Handy
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    h1 { font-size: 1.8rem !important; margin-bottom: 0.5rem; }
    
    /* Boxen mit Schatten und definierten Kanten */
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: bold;
    }
    div[data-testid="metric-container"] {
        background-color: #1e222b;
        padding: 10px 14px;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border: 1px solid #2d3139;
    }
    
    /* Fetterer, definierter Schieberegler */
    .stSlider [data-baseweb="slider"] {
        height: 14px;
    }
    .stSlider [data-testid="stTickBar"] {
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 Gold Scalper Pro")

class GoldScalpingLogic:
    def __init__(self, symbol="GC=F"):
        self.symbol = symbol
        self.data = None

    def fetch_data(self):
        try:
            self.data = yf.download(tickers=self.symbol, period="3d", interval="15m", progress=False)
            return True
        except:
            return False

    def calculate_metrics(self, sl_dist):
        if self.data is None or len(self.data) < 20:
            return 50, 0, 0, 0
        
        close_prices = self.data['Close'].values.flatten()
        current_price = float(close_prices[-1])
        avg_price = float(np.mean(close_prices[-20:]))
        
        # Signal-Logik (Kaufsignal wenn Kurs über dem Durchschnitt)
        prob = 75 if current_price > avg_price else 45
            
        # Berechnung basierend auf deinem neuen Wunsch:
        # SL wird direkt übergeben, TP ist starr das Dreifache (CRV 1:3)
        sl_points = float(sl_dist)
        tp_points = sl_points * 3.0
        
        sl = current_price - sl_points
        tp = current_price + tp_points
        
        return prob, round(current_price, 2), round(sl, 2), round(tp, 2)

logic = GoldScalpingLogic()

if logic.fetch_data():
    # Neuer, fetter Schieberegler genau nach deinen Vorgaben (3$ bis 10$ in 0.5$ Schritten)
    sl_input = st.slider("Stop Loss Abstand ($)", min_value=3.0, max_value=10.0, value=3.0, step=0.5)
    
    # Berechne Werte mit festem CRV von 1:3
    prob, entry, sl, tp = logic.calculate_metrics(sl_input)
    
    # Berechne den automatischen TP-Abstand für die Anzeige
    tp_dist = sl_input * 3.0
    
    # Kompakter Signal-Kasten
    if prob > 60:
        st.success(f"**Signal: STARK ({prob}%)**")
    else:
        st.warning(f"**Signal: NEUTRAL ({prob}%)**")
        
    # Preis-Kacheln nebeneinander für perfekten Handy-Überblick
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="EINSTIEG", value=f"{entry}")
    with c2:
        st.metric(label="STOP LOSS", value=f"{sl}", delta=f"-{sl_input}$", delta_color="inverse")
    with c3:
        st.metric(label="TAKE PROFIT", value=f"{tp}", delta=f"+{tp_dist}$")
        
    # Großer Refresh-Button direkt darunter
    st.button("🔄 Kurse aktualisieren", use_container_width=True)
    
    # Flacher MetaTrader Bereich
    with st.expander("🔐 MT5 Verbindung"):
        st.text_input("Server", key="srv")
        st.text_input("Login", key="log")
        st.text_input("Passwort", type="password", key="pwd")
else:
    st.error("Marktdaten temporär nicht erreichbar. Bitte aktualisieren.")
