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
    
    /* Live-Schrift Größer & Dynamisch */
    .status-online { font-size: 1.2rem !important; font-weight: bold; text-align: center; color: #00ff88; margin-bottom: 1rem; text-shadow: 0 0 10px rgba(0,255,136,0.3); }
    .status-offline { font-size: 1.2rem !important; font-weight: bold; text-align: center; color: #ff3333; margin-bottom: 1rem; }
    
    /* ERZWUNGENE HORIZONTALE ANORDNUNG (Einstieg, SL, TP) */
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
        padding: 12px 5px;
        text-align: center;
    }
    .trade-label { font-size: 0.85rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
    .trade-value { font-size: 1.4rem; color: #fff; font-weight: 900; display: block; margin-top: 5px; margin-bottom: 3px; }
    .delta-plus { color: #ff3333; font-size: 0.75rem; font-weight: bold; }
    .delta-minus { color: #00ff88; font-size: 0.75rem; font-weight: bold; }

    /* Signal Zone Styles */
    .signal-buy { background-color: #052e16; border: 2px solid #00ff88; color: #00ff88; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 1rem; }
    .signal-sell { background-color: #2d0606; border: 2px solid #ff3333; color: #ff3333; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 1rem; }
    .signal-wait { background-color: #3b2a06; border: 2px solid #ffaa00; color: #ffaa00; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 1rem; }
    
    .lot-box { background: linear-gradient(135deg, #1e293b, #0f172a); border-left: 5px solid #38bdf8; padding: 12px; border-radius: 4px; margin-bottom: 15px; }

    /* REFRESH BUTTON POSITION (NOCH TIEFER GESETZT) */
    div.stButton > button {
        position: fixed !important;
        right: 25px !important;
        bottom: 90px !important; /* Tiefer gesetzt */
        z-index: 999999 !important;
        border-radius: 50% !important;
        width: 54px !important;
        height: 54px !important;
        background-color: #38bdf8 !important;
        color: white !important;
        border: 3px solid #ffffff !important;
        box-shadow: 0px 4px 15px rgba(255, 255, 255, 0.4) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div.stButton > button p { display: none !important; }
    div.stButton > button::before { content: "↻" !important; font-size: 24px; font-weight: bold; }
    
    /* SIDEBAR PFEIL OBEN RECHTS & SILBER SCHIMMERND */
    [data-testid="stSidebarCollapsedControl"] {
        left: auto !important;
        right: 15px !important;
        top: 15px !important;
        background: linear-gradient(145deg, #ffffff, #a1a1a1) !important; /* Silberner Schimmer */
        border: 1px solid #ffffff !important;
        border-radius: 8px !important;
        padding: 4px !important;
        box-shadow: 0px 0px 12px rgba(255, 255, 255, 0.4) !important;
    }
    
    /* SIDEBAR RECHTS AUSRICHTEN */
    section[data-testid="stSidebar"] {
        left: auto !important;
        right: 0 !important;
        background-color: #2d333f !important;
        border-left: 2px solid #3f444e !important;
    }
    
    .stApp { flex-direction: row-reverse !important; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (RECHTS) ---
with st.sidebar:
    st.markdown("<h3 style='color: #fff; text-align: center;'>⚙️ Einstellungen</h3>", unsafe_allow_html=True)
    st.markdown("---")
    sl_val = st.slider("Stop Loss ($)", 3.0, 10.0, 3.0, 0.5)
    risk_val = st.number_input("Risiko (€)", 10, 1000, 50, 10)

# --- DATENABRUF UND LOGIK ---
class GoldLogic:
    def __init__(self):
        self.symbol = "GC=F"
    
    def get_data(self):
        try:
            data = yf.download(tickers=self.symbol, period="5d", interval="15m", progress=False)
            if data.empty or len(data) < 20: 
                return 4500.0, 4510.0, 4490.0, 4495.0, False
                
            close_prices = data['Close'].values.flatten()
            high_prices = data['High'].values.flatten()
            low_prices = data['Low'].values.flatten()
            
            current_price = float(close_prices[-1])
            avg_price = float(np.mean(close_prices[-20:]))
            
            high_today = float(np.max(high_prices[-30:]))
            low_today = float(np.min(low_prices[-30:]))
            
            if high_today == low_today:
                high_today += 2.5
                low_today -= 2.5
            
            return round(current_price, 2), round(high_today, 2), round(low_today, 2), round(avg_price, 2), True
        except: 
            return 4502.20, 4520.00, 4495.00, 4500.00, False

db = GoldLogic()
current_price, high_today, low_today, avg_price, is_live = db.get_data()
now = datetime.datetime.now().strftime("%H:%M:%S")

# UI Header
st.markdown('<div class="gold-title">💰 GOLD SCALPING <span class="pro-red">PRO</span></div>', unsafe_allow_html=True)

if is_live:
    st.markdown(f"<div class='status-online'>● Live-Daten aktiv • {now}</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='status-offline'>○ Markt offline (Demo-Modus) • {now}</div>", unsafe_allow_html=True)

# --- INTELLIGENTE SIGNAL-PRÜFUNG ---
is_bullish = current_price > avg_price
abstand_absolut = abs(current_price - avg_price)
ist_nah_am_durchschnitt = abstand_absolut <= 1.50

abstand_prozent = abstand_absolut / avg_price
basis_chance = 60 if is_bullish else 40
zusatz_chance = min(35, int(abstand_prozent * 5000))
prob = min(95, basis_chance + zusatz_chance)

if is_bullish:
    sl_price = current_price - sl_val
    tp_price = current_price + (sl_val * 3)
    prefix_sl = "-"
    prefix_tp = "+"
else:
    sl_price = current_price + sl_val
    tp_price = current_price - (sl_val * 3)
    prefix_sl = "+"
    prefix_tp = "-"

# SIGNAL ANZEIGEN
if ist_nah_am_durchschnitt:
    if is_bullish:
        st.markdown(f"<div class='signal-buy'>🚀 BUY SIGNAL AKTIV • STÄRKE {prob}%</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='signal-sell'>💥 SELL SIGNAL AKTIV • STÄRKE {prob}%</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='signal-wait'>⏳ MARKT BEOBACHTEN • Trend ist {'Up' if is_bullish else 'Down'} (Warte auf Rücksetzer)</div>", unsafe_allow_html=True)

lots = round(risk_val / (sl_val * 100), 2)

# HORIZONTALE TRADE-BOXEN
trade_html = f"""
<div class="trade-container">
    <div class="trade-box">
        <span class="trade-label">Einstieg</span>
        <span class="trade-value">{current_price}</span>
    </div>
    <div class="trade-box" style="border-color: #7f1d1d;">
        <span class="trade-label">Stop Loss</span>
        <span class="trade-value">{round(sl_price, 2)}</span>
        <span class="delta-plus">{prefix_sl}{sl_val}$</span>
    </div>
    <div class="trade-box" style="border-color: #064e3b;">
        <span class="trade-label">Take Profit</span>
        <span class="trade-value">{round(tp_price, 2)}</span>
        <span class="delta-minus">{prefix_tp}{sl_val*3}$</span>
    </div>
</div>
"""
st.markdown(trade_html, unsafe_allow_html=True)

# Lot Anzeige
st.markdown(f"""
<div class='lot-box'>
    <span style='color: #38bdf8; font-weight: bold; font-size: 0.8rem;'>POSITIONSGRÖSSE</span><br>
    <span style='font-size: 1.5rem; font-weight: bold; color: #fff;'>{lots} Lots</span>
</div>
""", unsafe_allow_html=True)

# --- EXPANDER MIT VOLLSTÄNDIGEN DETAILS ---
with st.expander("🔍 Details & Lot-Rechner einblenden"):
    st.info(f"Um bei einem Verlust exakt **{risk_val} €** zu riskieren, musst du im MetaTrader 5 eine Positionsgröße von **{lots} Lots** eingeben.")
    st.markdown("---")
    st.write("**Trading-Logik & Bedingungen:**")
    st.markdown(f"""
    - **Trendrichtung:** Kurs befindet sich aktuell *{'über' if is_bullish else 'unter'}* dem gleitenden Durchschnitt (SMA-20).
    - **Einstiegs-Bedingung:** Ein Signal wird erst aktiv, wenn der Live-Kurs maximal **1.50 $** an den SMA heranreicht (Schutz vor Einstiegen in überteuerte Märkte).
    - **Einstiegspreis:** Nutzt bei Signal-Aktivierung den aktuellen Sekunden-Kurs bei Klick auf Refresh.
    """)
    st.markdown("---")
    st.write("**Tagesstatistiken (Rollierend):**")
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1: st.metric(label="Höchstkurs (High)", value=f"{high_today} $")
    with col_stat2: st.metric(label="Tiefstkurs (Low)", value=f"{low_today} $")

# Schwebender Refresh Button
if st.button("Refresh"):
    st.rerun()
