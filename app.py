import streamlit as st
import yfinance as yf
import numpy as np
import datetime

# Seiteneinstellungen
st.set_page_config(page_title="Gold Scalper Pro", page_icon="💰", layout="centered")

# --- HIGH-END UI DESIGN (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 550px !important; }
    h1 { font-size: 1.6rem !important; text-align: center; color: #fff; margin-bottom: 0.5rem; }
    
    /* 1. Live-Schrift Größer & Dynamisch */
    .status-online { font-size: 1.2rem !important; font-weight: bold; text-align: center; color: #00ff88; margin-bottom: 1rem; text-shadow: 0 0 10px rgba(0,255,136,0.3); }
    .status-offline { font-size: 1.2rem !important; font-weight: bold; text-align: center; color: #ff3333; margin-bottom: 1rem; }
    
    /* 2. ERZWUNGENE HORIZONTALE ANORDNUNG (Einstieg, SL, TP) */
    .trade-container {
        display: flex;
        justify-content: space-between;
        gap: 5px;
        margin-bottom: 15px;
    }
    .trade-box {
        flex: 1;
        background-color: #1e222b;
        border: 1px solid #3f444e;
        border-radius: 8px;
        padding: 8px 5px;
        text-align: center;
    }
    .trade-label { font-size: 0.7rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; }
    .trade-value { font-size: 1.05rem; color: #fff; font-weight: bold; display: block; margin-top: 2px; }
    .delta-plus { color: #ff3333; font-size: 0.7rem; }
    .delta-minus { color: #00ff88; font-size: 0.7rem; }

    /* Signal Zone Styles */
    .signal-buy { background-color: #052e16; border: 2px solid #00ff88; color: #00ff88; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 1rem; }
    .signal-sell { background-color: #2d0606; border: 2px solid #ff3333; color: #ff3333; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 1rem; }
    
    .lot-box { background: linear-gradient(135deg, #1e293b, #0f172a); border-left: 5px solid #38bdf8; padding: 12px; border-radius: 4px; margin-bottom: 15px; }

    /* 3. KLEINERER STICKY BUTTON MIT AUFFÄLLIGER UMRANDUNG */
    div.stButton > button {
        position: fixed !important;
        right: 10px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 999999 !important;
        border-radius: 50% !important;
        width: 45px !important; /* Etwas kleiner */
        height: 45px !important; /* Etwas kleiner */
        background-color: #38bdf8 !important;
        color: white !important;
        border: 3px solid #ccff00 !important; /* Auffällige neongelbe Umrandung */
        box-shadow: 0px 0px 15px rgba(204, 255, 0, 0.6) !important; /* Leucht-Effekt */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div.stButton > button p { display: none !important; }
    div.stButton > button::before { content: "↻" !important; font-size: 20px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIK ---
class GoldLogic:
    def __init__(self):
        self.symbol = "GC=F"
    
    def get_data(self):
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period="1d", interval="1m")
            if data.empty: return None, False
            current = data['Close'].iloc[-1]
            return round(current, 2), True
        except: return 2350.50, False

db = GoldLogic()
current_price, is_live = db.get_data()
now = datetime.datetime.now().strftime("%H:%M:%S")

# UI
st.markdown("<h1>💰 GOLD SCALPER PRO</h1>", unsafe_allow_html=True)

if is_live:
    st.markdown(f"<div class='status-online'>● Live-Daten aktiv • {now}</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='status-offline'>○ Markt offline • {now}</div>", unsafe_allow_html=True)

# Eingabe
c_in1, c_in2 = st.columns(2)
with c_in1: sl_val = st.slider("Stop Loss ($)", 1.0, 10.0, 3.0, 0.5)
with c_in2: risk_val = st.number_input("Risiko (€)", 10, 1000, 50, 10)

# Berechnung (Beispielhaft Bullish)
is_bullish = True 
sl_price = current_price - sl_val
tp_price = current_price + (sl_val * 3)
lots = round(risk_val / (sl_val * 100), 2)

if is_bullish:
    st.markdown(f"<div class='signal-buy'>🚀 BUY ZONE AKTIV</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='signal-sell'>💥 SELL ZONE AKTIV</div>", unsafe_allow_html=True)

# --- HORIZONTALE TRADE-BOXEN (Fixiert für Mobile) ---
st.markdown(f"""
    <div class="trade-container">
        <div class="trade-box">
            <span class="trade-label">Einstieg</span>
            <span class="trade-value">{current_price}</span>
        </div>
        <div class="trade-box" style="border-color: #7f1d1d;">
            <span class="trade-label">Stop Loss</span>
            <span class="trade-value">{round(sl_price, 2)}</span>
            <span class="delta-plus">-{sl_val}$</span>
        </div>
        <div class="trade-box" style="border-color: #064e3b;">
            <span class="trade-label">Take Profit</span>
            <span class="trade-value">{round(tp_price, 2)}</span>
            <span class="delta-minus">+{sl_val*3}$</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class='lot-box'>
        <span style='color: #38bdf8; font-weight: bold; font-size: 0.8rem;'>POSITIONSGRÖSSE</span><br>
        <span style='font-size: 1.5rem; font-weight: bold; color: #fff;'>{lots} Lots</span>
    </div>
""", unsafe_allow_html=True)

# Schwebender Refresh Button
if st.button("Refresh"):
    st.rerun()
