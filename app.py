import streamlit as st
import yfinance as yf
import numpy as np
import datetime

# Seiteneinstellungen
st.set_page_config(page_title="Gold Scalper Pro", page_icon="💰", layout="centered")

# --- HIGH-END UI DESIGN (CSS) ---
st.markdown("""
    <style>
    /* Sicherer Abstand nach oben (50px), damit auf Mobilgeräten nichts verschwindet */
    .block-container { padding-top: 50px !important; padding-bottom: 0.5rem !important; max-width: 550px !important; }
    
    /* ANIMIERTER GOLD SCHRIFTZUG & MATTES ROT */
    .gold-title {
        font-size: 1.4rem !important;
        font-weight: 900;
        text-align: center;
        margin-top: 0px !important;
        margin-bottom: 0.2rem !important;
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
    
    /* Live-Schrift */
    .status-online { font-size: 1.2rem !important; font-weight: bold; text-align: center; color: #00ff88; margin-bottom: 0.6rem !important; text-shadow: 0 0 10px rgba(0,255,136,0.3); }
    .status-offline { font-size: 1.2rem !important; font-weight: bold; text-align: center; color: #ff3333; margin-bottom: 0.6rem !important; }
    
    /* ERZWUNGENE HORIZONTALE ANORDNUNG (Einstieg, SL, TP) */
    .trade-container {
        display: flex;
        justify-content: space-between;
        gap: 5px;
        margin-top: 0px !important;
        margin-bottom: 10px !important;
    }
    .trade-box {
        flex: 1;
        background-color: #1e222b;
        border: 1px solid #3f444e;
        border-radius: 8px;
        padding: 9px 4px !important;
        text-align: center;
    }
    .trade-label { font-size: 0.8rem !important; color: #94a3b8; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
    .trade-value { font-size: 1.35rem !important; color: #fff; font-weight: 900; display: block; margin-top: 3px !important; margin-bottom: 1px !important; }
    .delta-plus { color: #ff3333; font-size: 0.72rem !important; font-weight: bold; }
    .delta-minus { color: #00ff88; font-size: 0.72rem !important; font-weight: bold; }

    /* Signal Zone Styles */
    .signal-buy { background-color: #052e16; border: 2px solid #00ff88; color: #00ff88; padding: 8px !important; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 0.25rem !important; }
    .signal-sell { background-color: #2d0606; border: 2px solid #ff3333; color: #ff3333; padding: 8px !important; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 0.25rem !important; }
    .signal-wait { background-color: #3b2a06; border: 2px solid #ffaa00; color: #ffaa00; padding: 8px !important; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 0.25rem !important; }
    
    /* Positionsgrößen-Box */
    .lot-box { background: linear-gradient(135deg, #1e293b, #0f172a); border-left: 5px solid #38bdf8; padding: 9px !important; border-radius: 4px; margin-bottom: 10px !important; }

    /* REFRESH BUTTON POSITION */
    div.stButton > button {
        position: fixed !important;
        right: 0px !important;
        bottom: 80px !important;
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
    
    /* ORIGINAL SIDEBARS VERSTECKT */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }

    /* --- ERZWUNGENE ZENTRIERUNG FÜR DEN EINSTELLUNGS-BUTTON --- */
    div[data-testid="stExpander"] {
        display: block !important;
        margin: 0 auto !important;
        text-align: center !important;
        width: 100% !important;
    }
    div[data-testid="stExpander"] > details {
        display: inline-block !important;
        margin: 0 auto !important;
        text-align: left !important;
    }

    /* Der eigentliche Header-Button (Einstellungen) */
    div[data-testid="stExpander"] details summary {
        display: flex !important;
        justify-content: center !important; 
        align-items: center !important;
        gap: 8px !important;
        background-color: #1e222b !important;
        border: 1px solid #3f444e !important;
        border-radius: 8px !important;
        padding: 5px 14px !important;
        width: fit-content !important;
        margin: 0 auto !important;
        height: auto !important;
    }
    div[data-testid="stExpander"] details summary svg { fill: #94a3b8 !important; color: #94a3b8 !important; }
    div[data-testid="stExpander"] details summary p { margin: 0 !important; font-weight: bold !important; color: #fff !important; font-size: 0.9rem !important; }

    /* Das aufgeklappte Einstellungsfenster */
    div[data-testid="stExpander"] details div[data-testid="stExpanderDetails"] {
        background-color: #1e222b !important;
        border: 1px solid #3f444e !important;
        border-radius: 8px !important;
        padding: 12px !important;
        width: 280px !important;
        margin: 4px auto 0 auto !important;
    }
    </style>
""", unsafe_allow_html=True)

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

# --- SIGNAL ANZEIGEN ---
is_bullish = current_price > avg_price
abstand_absolut = abs(current_price - avg_price)
ist_nah_am_durchschnitt = abstand_absolut <= 1.50

abstand_prozent = abstand_absolut / avg_price
basis_chance = 60 if is_bullish else 40
zusatz_chance = min(35, int(abstand_prozent * 5000))
prob = min(95, basis_chance + zusatz_chance)

if ist_nah_am_durchschnitt:
    if is_bullish:
        st.markdown(f"<div class='signal-buy'>🚀 BUY SIGNAL AKTIV • STÄRKE {prob}%</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='signal-sell'>💥 SELL SIGNAL AKTIV • STÄRKE {prob}%</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='signal-wait'>⏳ MARKT BEOBACHTEN • Trend ist {'Up' if is_bullish else 'Down'} (Warte auf Rücksetzer)</div>", unsafe_allow_html=True)


# --- REIN MITTIG ZENTRIERTER BUTTON "EINSTELLUNGEN" MIT NEUEM CRV-SLIDER ---
with st.expander("Einstellungen", expanded=False):
    sl_val = st.slider("Stop Loss ($)", 3.0, 10.0, 3.0, 0.5)
    crv_val = st.slider("Chance-Risiko-Verhältnis (1:X)", 1.0, 5.0, 3.0, 0.5) # Neuer CRV Slider
    risk_val = st.number_input("Risiko ($)", 10, 1000, 50, 10)


# --- BERECHNUNGEN (DYNAMISCH BASIEREND AUF CRV) ---
tp_abstand = sl_val * crv_val  # Berechnet den TP-Abstand anhand des gewählten Sliders

if is_bullish:
    sl_price = current_price - sl_val
    tp_price = current_price + tp_abstand
    prefix_sl = "-"
    prefix_tp = "+"
else:
    sl_price = current_price + sl_val
    tp_price = current_price - tp_abstand
    prefix_sl = "+"
    prefix_tp = "-"

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
        <span class="delta-minus">{prefix_tp}{round(tp_abstand, 2)}$</span>
    </div>
</div>
"""
st.markdown(trade_html, unsafe_allow_html=True)

# Lot Anzeige
st.markdown(f"""
<div class='lot-box'>
    <span style='color: #38bdf8; font-weight: bold; font-size: 0.75rem;'>POSITIONSGRÖSSE</span><br>
    <span style='font-size: 1.4rem; font-weight: bold; color: #fff;'>{lots} Lots</span>
</div>
""", unsafe_allow_html=True)

# --- EXPANDER MIT DETAILS (STATISTIK JETZT OBEN) ---
with st.expander("🔍 Details & Lot-Rechner einblenden"):
    # 1. 24h-Statistiken ganz oben
    st.write("**Tagesstatistiken (Rollierende letzte 24 Std.):**")
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1: st.metric(label="Höchstkurs (High)", value=f"{high_today} $")
    with col_stat2: st.metric(label="Tiefstkurs (Low)", value=f"{low_today} $")
    
    st.markdown("---")
    
    # 2. Lot-Berechnung Info
    st.info(f"Um bei einem Verlust exakt **{risk_val} $** zu riskieren, musst du im MetaTrader 5 eine Positionsgröße von **{lots} Lots** eingeben.")
    
    st.markdown("---")
    
    # 3. Trading-Logik & Bedingungen (Dynamisches CRV eingebaut)
    st.write("**Trading-Logik & Bedingungen:**")
    st.markdown(f"""
    - **Trendbestimmung (SMA-20):** Der Kurs befindet sich aktuell *{'über (Bullish)' if is_bullish else 'unter (Bearish)'}* dem gleitenden Durchschnitt der letzten 20 Kerzen. Es werden nur Trades in Trendrichtung vorgeschlagen.
    - **Einstiegs-Trigger:** Ein Signal schaltet erst auf aktiv (BUY/SELL), wenn der Abstand zwischen dem Live-Kurs und dem SMA-20 maximal **1.50 $** beträgt (Rücksetzer-Strategie).
    - **Risiko-Management (CRV 1:{crv_val}):** Der Take Profit ist fest auf das **{crv_val}-Fache** des gewählten Stop Loss eingestellt, um ein mathematisch positives Gewinnverhältnis zu sichern.
    - **Lot-Formel:** Berechnung basiert auf dem eingestellten Dollar-Risiko geteilt durch den Stop-Loss-Abstand (Multiplikator 100 pro Punkt im Gold-Future).
    """)

# Schwebender Refresh Button
if st.button("Refresh"):
    st.rerun()
