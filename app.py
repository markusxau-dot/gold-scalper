import streamlit as st
import yfinance as yf
import numpy as np

# Seiteneinstellungen für maximale Kompaktheit
st.set_page_config(page_title="Gold Scalper", page_icon="💰", layout="centered")

# CSS für Schatten, fette Slider, definierte Kanten und extreme Kompaktheit
st.markdown("""
    <style>
    /* Abstände global verringern */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    h1 { font-size: 1.8rem !important; margin-bottom: 0.5rem; }
    
    /* Boxen mit Schatten und definierten Kanten */
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: bold;
    }
    div[data-testid="metric-container"] {
        background-color: #1e222b;
        padding: 8px 12px;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border: 1px solid #2d3139;
    }
    
    /* Fetterer, definierter Slider */
    .stSlider [data-baseweb="slider"] {
        height: 12px;
    }
    .stSlider [data-testid="stTickBar"] {
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 Gold Scalper Pro")

# Logik-Klasse mit deinen neuen starren Grenzwerten (max 3$ SL / 9$ TP)
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

    def calculate_metrics(self, crv_ratio, risk_amount):
        if self.data is None or len(self.data) < 20:
            return 50, 0, 0, 0
        
        close_prices = self.data['Close'].values.flatten()
        current_price = float(close_prices[-1])
        avg_price = float(np.mean(close_prices[-20:]))
        
        # Signal-Logik
        prob = 75 if current_price > avg_price else 45
            
        # NEU: Strukturierte Punkte-Begrenzung basierend auf deinem Wunsch
        # Bei CRV 3 -> SL = 3, TP = 9. Bei CRV 2 -> SL = 3, TP = 6.
        sl_points = float(risk_amount)
        tp_points = sl_points * float(crv_ratio)
        
        sl = current_price - sl_points
        tp = current_price + tp_points
        
        return prob, round(current_price, 2), round(sl, 2), round(tp, 2)

logic = GoldScalpingLogic()

if logic.fetch_data():
    # Zwei Slider nebeneinander für maximale Platzersparnis
    col_sl1, col_sl2 = st.columns(2)
    with col_sl1:
        crv = st.slider("CRV Verhältnis", min_value=2, max_value=4, value=3, step=1)
    with col_sl2:
        # Hier ist dein Limit: Maximal 3 Dollar Stop Loss
        risk_dist = st.slider("Max SL Abstand ($)", min_value=1.0, max_value=3.0, value=3.0, step=0.5)
    
    prob, entry, sl, tp = logic.calculate_metrics(crv, risk_dist)
    
    # Kompakter Signal-Kasten
    if prob > 60:
        st.success(f"**Signal: STARK ({prob}%)**")
    else:
        st.warning(f"**Signal: NEUTRAL ({prob}%)**")
        
    # Extrem kompakte Preis-Kacheln NEBENEINANDER (Handy-optimiert)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="EINSTIEG", value=f"{entry}")
    with c2:
        st.metric(label="STOP LOSS", value=f"{sl}", delta=f"-{risk_dist}$", delta_color="inverse")
    with col_sl2 if not c3 else c3: # Fix für Spaltenbündelung
        st.metric(label="TAKE PROFIT", value=f"{tp}", delta=f"+{risk_dist*crv}$")
        
    # Winziger Refresh-Button ganz unten, um Platz zu sparen
    st.button("🔄 Kurse aktualisieren", use_container_width=True)
    
    # MetaTrader Bereich extrem flach halten
    with st.expander("🔐 MT5 Verbindung"):
        st.text_input("Server", key="srv")
        st.text_input("Login", key="log")
        st.text_input("Passwort", type="password", key="pwd")
else:
    st.error("Marktdaten temporär nicht erreichbar.")
