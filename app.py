import streamlit as st
import yfinance as yf
import numpy as np
import datetime

# Seiteneinstellungen
st.set_page_config(page_title="Gold Scalping Pro", page_icon="💰", layout="centered")

# --- HIGH-END UI DESIGN (CSS) ---
st.markdown("""
    <style>
    /* Grundlayout Optimierung für Mobile (Kein Scrollen) */
    .block-container { 
        padding-top: 2rem !important; 
        padding-bottom: 0rem !important; 
        max-width: 500px !important; 
    }
    
    /* ANIMIERTER GOLD SCHRIFTZUG */
    .gold-title {
        font-size: 1.4rem !important;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: 1px;
        background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fcf6ba, #bf953f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: shine 3s linear infinite;
    }
    @keyframes shine {
        to { background-position: 200% center; }
    }
    .pro-red {
        color: #b91c1c; /* Mattes Rot */
        font-size: 1.4rem;
        font-weight: 900;
        text-shadow: none;
    }

    /* Sidebar Kontrast */
    [data-testid="stSidebar"] {
        background-color: #2d333f !important; /* Helleres Grau für Kontrast */
        border-left: 2px solid #3f444e !important;
        box-shadow: -5px 0px 15px rgba(0,0,0,0.5);
    }
    
    /* Live-Status Schrift */
    .status-online { font-size: 1rem !important; font-weight: bold; text-align: center; color: #00ff88; margin-bottom: 0.5rem; }
    
    /* Trade Boxen Design */
    .trade-container { display: flex; justify-content: space-between; gap: 4px; margin-bottom: 10px; }
    .trade-box {
        flex: 1;
        background-color: #1e222b;
        border: 1px solid #3f444e;
        border-radius: 6px;
        padding: 8px 2px;
        text-align: center;
    }
    .trade-label { font-size: 0.7rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; }
    .trade-value { font-size: 1.1rem; color: #fff; font-weight: 800; display: block; }

    /* Signal Zone */
    .signal-box { padding: 8px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 0.9rem; margin-bottom: 0.8rem; }
    .signal-buy { background-color: #052e16; border: 1px solid #00ff88; color: #00ff88; }
    .signal-sell { background-color: #2d0606; border: 1px solid #ff3333; color: #ff3333; }
    .signal-wait { background-color: #3b2a06; border: 1px solid #ffaa00; color: #ffaa00; }
    
    /* Lot Anzeige */
    .lot-box { background: #1e293b; border-left: 4px solid #38bdf8; padding: 10px; border-radius: 4px; margin-bottom: 10px; }

    /* AKTUALISIERUNGSKNOPF (HÖHER GESETZT) */
    div.stButton > button {
        position: fixed !important;
        right: 20px !important;
        bottom: 45px !important; /* Höher gesetzt für bessere Erreichbarkeit */
        z-index: 9999;
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        background-color: #38bdf8 !important;
        border: 2px solid #ccff00 !important;
        box-shadow: 0px 0px 15px rgba(204, 255, 0, 0.4) !important;
    }
    div.stButton > button::before { content: "↻" !important; font-size: 24px; color: white; }
    div.stButton > button p { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (RECHTS) ---
with st.sidebar:
    st.markdown("<h3 style='color: white; text-align: center;'>CONTROL</h3>", unsafe_allow_html=True)
    sl_val = st.slider("Stop Loss ($)", 3.0, 10.0, 3.0, 0.5)
    risk_val = st.number_input("Risiko (€)", 10, 1000, 50, 10)

# --- LOGIK ---
class GoldLogic:
    def get_data(self):
        try:
            data = yf.download(tickers="GC=F", period="2d", interval="15m", progress=False)
            current = float(data['Close'].iloc[-1])
            avg = float(data['Close'].rolling(20).mean().iloc[-1])
            return round(current, 2), round(avg, 2), True
        except: return 4505.50, 4500.00, False

db = GoldLogic()
price, sma, live = db.get_data()
now = datetime.datetime.now().strftime("%H:%M:%S")

# --- UI DARSTELLUNG ---
st.markdown(f'<div class="gold-title">GOLD SCALPING <span class="pro-red">PRO</span></div>', unsafe_allow_html=True)
st.markdown(f"<div class='status-online'>● Live-Daten • {now}</div>", unsafe_allow_html=True)

# Signal Berechnung
diff = price - sma
is_bullish = diff > 0
is_ready = abs(diff) <= 1.50

if is_ready:
    msg = "BUY SIGNAL AKTIV" if is_bullish else "SELL SIGNAL AKTIV"
    css = "signal-buy" if is_bullish else "signal-sell"
else:
    msg = f"WARTE... Trend {'Up' if is_bullish else 'Down'}"
    css = "signal-wait"

st.markdown(f"<div class='signal-box {css}'>{msg}</div>", unsafe_allow_html=True)

# Berechnung SL/TP
sl_price = price - sl_val if is_bullish else price + sl_val
tp_price = price + (sl_val * 3) if is_bullish else price - (sl_val * 3)
lots = round(risk_val / (sl_val * 100), 2)

# Trade Grid
st.markdown(f"""
<div class="trade-container">
    <div class="trade-box">
        <span class="trade-label">Einstieg</span>
        <span class="trade-value">{price}</span>
    </div>
    <div class="trade-box" style="border-color: #ef4444;">
        <span class="trade-label">Stop Loss</span>
        <span class="trade-value">{round(sl_price, 1)}</span>
    </div>
    <div class="trade-box" style="border-color: #10b981;">
        <span class="trade-label">Take Profit</span>
        <span class="trade-value">{round(tp_price, 1)}</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class='lot-box'>
    <span style='color: #38bdf8; font-size: 0.7rem; font-weight: bold;'>POSITION</span><br>
    <span style='font-size: 1.4rem; font-weight: bold; color: #fff;'>{lots} Lots</span>
</div>
""", unsafe_allow_html=True)

with st.expander("🔍 Rechner Info"):
    st.write(f"Risiko: {risk_val}€ | SL: {sl_val}$")

# Refresh Button
if st.button(" "):
    st.rerun()
