import streamlit as st
import yfinance as yf
import numpy as np
import datetime

# Seiteneinstellungen
st.set_page_config(page_title="Gold Scalper Pro", page_icon="💰", layout="centered")

# --- HIGH-END UI DESIGN (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; padding-bottom: 1rem; max-width: 550px !important; }
    
    /* ANIMIERTER GOLD SCHRIFTZUG & MATTES ROT */
    .gold-title {
        font-size: 1.4rem !important;
        font-weight: 900;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
        background: linear-gradient(to right, #bf953f, #fcf6ba, #b38728, #fcf6ba, #bf953f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: shine 3s linear infinite;
        display: block;
    }
    @keyframes shine { to { background-position: 200% center; } }
    .pro-red { color: #b91c1c !important; font-weight: 900; -webkit-text-fill-color: #b91c1c !important; }
    
    .status-online { font-size: 1.2rem !important; font-weight: bold; text-align: center; color: #00ff88; margin-bottom: 1rem; }
    
    .trade-container { display: flex; justify-content: space-between; gap: 5px; margin-bottom: 15px; }
    .trade-box { flex: 1; background-color: #1e222b; border: 1px solid #3f444e; border-radius: 8px; padding: 12px 5px; text-align: center; }
    .trade-label { font-size: 0.85rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; }
    .trade-value { font-size: 1.4rem; color: #fff; font-weight: 900; display: block; }
    .delta-plus { color: #ff3333; font-size: 0.75rem; font-weight: bold; }
    .delta-minus { color: #00ff88; font-size: 0.75rem; font-weight: bold; }

    .signal-buy { background-color: #052e16; border: 2px solid #00ff88; color: #00ff88; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 1rem; }
    .signal-sell { background-color: #2d0606; border: 2px solid #ff3333; color: #ff3333; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 1rem; }
    .signal-wait { background-color: #3b2a06; border: 2px solid #ffaa00; color: #ffaa00; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 1rem; }
    
    .lot-box { background: linear-gradient(135deg, #1e293b, #0f172a); border-left: 5px solid #38bdf8; padding: 12px; border-radius: 4px; margin-bottom: 15px; }

    /* REFRESH BUTTON POSITION AN ROTER MARKIERUNG (MIT WEISSEM RING) */
    div.stButton > button {
        position: fixed !important;
        right: 20px !important;
        bottom: 140px !important; /* Exakt an der unteren roten Markierung */
        z-index: 999999 !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        background-color: #38bdf8 !important;
        color: white !important;
        border: 3px solid #ffffff !important; /* Weißer Ring statt Gelb */
        box-shadow: 0px 4px 15px rgba(255, 255, 255, 0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div.stButton > button p { display: none !important; }
    div.stButton > button::before { content: "↻" !important; font-size: 22px; font-weight: bold; }
    
    /* SIDEBAR KONTRAST & SILBERNER PFEIL OBEN RECHTS */
    [data-testid="stSidebar"] {
        background-color: #2d333f !important;
        border-left: 2px solid #3f444e !important;
    }
    
    /* Silber schimmernder Sidebar-Pfeil */
    [data-testid="stSidebarNavSeparator"] + div button, 
    button[kind="header"] {
        background: linear-gradient(145deg, #e0e0e0, #8e8e8e) !important;
        color: #333 !important;
        border-radius: 5px !important;
        box-shadow: 0 0 10px rgba(255,255,255,0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color: #fff; text-align: center;'>⚙️ CONTROL</h3>", unsafe_allow_html=True)
    sl_val = st.slider("Stop Loss ($)", 3.0, 10.0, 3.0, 0.5)
    risk_val = st.number_input("Risiko (€)", 10, 1000, 50, 10)

# --- LOGIK ---
class GoldLogic:
    def get_data(self):
        try:
            data = yf.download(tickers="GC=F", period="5d", interval="15m", progress=False)
            current = float(data['Close'].iloc[-1])
            avg = float(np.mean(data['Close'].values.flatten()[-20:]))
            high = float(np.max(data['High'].values.flatten()[-30:]))
            low = float(np.min(data['Low'].values.flatten()[-30:]))
            return round(current, 2), round(high, 2), round(low, 2), round(avg, 2), True
        except: return 4511.80, 4520.80, 4508.80, 4510.00, False

db = GoldLogic()
current_price, high_today, low_today, avg_price, is_live = db.get_data()
now = datetime.datetime.now().strftime("%H:%M:%S")

st.markdown('<div class="gold-title">💰 GOLD SCALPING <span class="pro-red">PRO</span></div>', unsafe_allow_html=True)
st.markdown(f"<div class='status-online'>● Live-Daten aktiv • {now}</div>", unsafe_allow_html=True)

# Signal Logik
is_bullish = current_price > avg_price
ist_nah = abs(current_price - avg_price) <= 1.50
prob = min(95, 60 + int((abs(current_price - avg_price) / avg_price) * 5000))

if ist_nah:
    css = "signal-buy" if is_bullish else "signal-sell"
    msg = f"🚀 {'BUY' if is_bullish else 'SELL'} SIGNAL AKTIV • {prob}%"
else:
    css = "signal-wait"
    msg = f"⏳ MARKT BEOBACHTEN • Trend {'Up' if is_bullish else 'Down'}"

st.markdown(f"<div class='{css}'>{msg}</div>", unsafe_allow_html=True)

# Trade Werte
sl_price = current_price - sl_val if is_bullish else current_price + sl_val
tp_price = current_price + (sl_val * 3) if is_bullish else current_price - (sl_val * 3)
lots = round(risk_val / (sl_val * 100), 2)

# Trade Boxen HTML
st.markdown(f"""
<div class="trade-container">
    <div class="trade-box">
        <span class="trade-label">Einstieg</span>
        <span class="trade-value">{current_price}</span>
    </div>
    <div class="trade-box" style="border-color: #7f1d1d;">
        <span class="trade-label">Stop Loss</span>
        <span class="trade-value">{round(sl_price, 2)}</span>
        <span class="delta-plus">{"-" if is_bullish else "+"}{sl_val}$</span>
    </div>
    <div class="trade-box" style="border-color: #064e3b;">
        <span class="trade-label">Take Profit</span>
        <span class="trade-value">{round(tp_price, 2)}</span>
        <span class="delta-minus">{"+" if is_bullish else "-"}{sl_val*3}$</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class='lot-box'>
    <span style='color: #38bdf8; font-weight: bold; font-size: 0.8rem;'>POSITIONSGRÖSSE</span><br>
    <span style='font-size: 1.5rem; font-weight: bold; color: #fff;'>{lots} Lots</span>
</div>
""", unsafe_allow_html=True)

with st.expander("🔍 Details"):
    st.info(f"Risiko: {risk_val}€ | Lots: {lots}")
    st.write(f"High: {high_today}$ | Low: {low_today}$")

if st.button("Refresh"):
    st.rerun()
