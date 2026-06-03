import streamlit as st
import yfinance as yf
import numpy as np
import datetime

# Seiteneinstellungen für die perfekte mobile Ansicht
st.set_page_config(page_title="Gold Scalper Pro", page_icon="💰", layout="centered")

# --- HIGH-END UI DESIGN (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 550px !important; }
    h1 { font-size: 1.8rem !important; margin-bottom: 0.2rem; text-align: center; color: #fff; }
    .update-text { text-align: center; color: #8a99ad; font-size: 0.8rem; margin-bottom: 1rem; }
    
    .signal-buy {
        background-color: #052e16; border: 2px solid #00ff88; color: #00ff88;
        padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.1rem;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.2); margin-bottom: 1rem;
    }
    .signal-sell {
        background-color: #2d0606; border: 2px solid #ff3333; color: #ff3333;
        padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.1rem;
        box-shadow: 0 0 15px rgba(255, 51, 51, 0.2); margin-bottom: 1rem;
    }
    
    div[data-testid="stMetricValue"] { font-size: 1.3rem !important; font-weight: bold !important; color: #fff !important; }
    
    div[data-testid="column"]:nth-of-type(1) div[data-testid="metric-container"] {
        background-color: #1e222b; border: 1px solid #3f444e; border-radius: 8px; padding: 10px;
    }
    div[data-testid="column"]:nth-of-type(2) div[data-testid="metric-container"] {
        background-color: #1a1515; border: 1px solid #7f1d1d; border-radius: 8px; padding: 10px;
    }
    div[data-testid="column"]:nth-of-type(3) div[data-testid="metric-container"] {
        background-color: #131a16; border: 1px solid #064e3b; border-radius: 8px; padding: 10px;
    }
    
    .lot-box {
        background: linear-gradient(135deg, #1e293b, #0f172a); border-left: 5px solid #38bdf8;
        padding: 12px; border-radius: 4px; margin-top: 10px; margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATENABRUF UND LOGIK ---
class GoldDashboardLogic:
    def __init__(self):
        self.symbol = "GC=F"
        self.data = None
        self.info = None

    def fetch_market_data(self):
        try:
            self.data = yf.download(tickers=self.symbol, period="3d", interval="15m", progress=False)
            ticker = yf.Ticker(self.symbol)
            self.info = ticker.fast_info
            if self.data is None or len(self.data) < 5: return False
            return True
        except: return False

    def process(self, sl_dist, euro_risk, live_aktiv):
        if live_aktiv and self.data is not None and len(self.data) >= 5:
            try:
                close_prices = self.data['Close'].values.flatten()
                current_price = float(close_prices[-1])
                avg_price = float(np.mean(close_prices[-20:]))
                high_today = float(self.info.get('day_high', current_price))
                low_today = float(self.info.get('day_low', current_price))
                
                is_bullish = current_price > avg_price
                
                # VARIABLE PROBABILITY BERECHNUNG (Abstand zum SMA bestimmt die Stärke)
                abstand_prozent = abs(current_price - avg_price) / avg_price
                basis_chance = 60 if is_bullish else 40
                zusatz_chance = min(35, int(abstand_prozent * 5000)) # Dynamischer Bonus je nach Trendstärke
                
                prob = min(95, basis_chance + zusatz_chance) if is_bullish else max(5, basis_chance - zusatz_chance)
                
            except: 
                current_price, high_today, low_today, is_bullish, prob = 2350.0, 2360.0, 2340.0, True, 75
        else: 
            # Demo/Wochenend-Modus
            current_price, high_today, low_today, is_bullish, prob = 2350.0, 2365.0, 2340.0, True, 75
        
        if is_bullish:
            sl, tp = current_price - sl_dist, current_price + (sl_dist * 3.0)
        else:
            sl, tp = current_price + sl_dist, current_price - (sl_dist * 3.0)
            
        lot_size = euro_risk / (sl_dist * 100.0)
        return {
            "current": round(current_price, 2), "sl": round(sl, 2), "tp": round(tp, 2),
            "is_bullish": is_bullish, "high": round(high_today, 2), "prob": prob,
            "low": round(low_today, 2), "lot": round(lot_size, 2)
        }

db = GoldDashboardLogic()
live_verfuegbar = db.fetch_market_data()

# Header
now = datetime.datetime.now().strftime("%H:%M:%S")
st.markdown("<h1>💰 GOLD SCALPER PRO</h1>", unsafe_allow_html=True)

if live_verfuegbar:
    st.markdown(f"<div class='update-text'>🔄 Live-Daten aktiv • Update: {now}</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='update-text' style='color:#ff9900;'>⚠️ Demo-Modus (Märkte geschlossen) • Zeit: {now}</div>", unsafe_allow_html=True)

# Inputs
col_input1, col_input2 = st.columns(2)
with col_input1:
    sl_input = st.slider("Stop Loss ($)", 3.0, 10.0, 3.0, 0.5)
with col_input2:
    risk_input = st.number_input("Gewünschtes Risiko (€)", 10, 2000, 50, 10)
    
res = db.process(sl_input, risk_input, live_verfuegbar)

# DYNAMISCHES SIGNAL (Mit variabler Prozent-Chance)
if res["is_bullish"]:
    st.markdown(f"<div class='signal-buy'>🚀 BUY ZONE • TREND-STÄRKE {res['prob']}%</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='signal-sell'>💥 SELL ZONE • TREND-STÄRKE {100 - res['prob']}%</div>", unsafe_allow_html=True)
    
# Preis-Metriken
c1, c2, c3 = st.columns(3)
with c1: st.metric("EINSTIEG", res["current"])
with c2: st.metric("STOP LOSS", res["sl"], delta=f"{'+' if not res['is_bullish'] else '-'}{sl_input}$", delta_color="inverse")
with c3: st.metric("TAKE PROFIT", res["tp"], delta=f"{'-' if not res['is_bullish'] else '+'}{sl_input*3.0}$")
    
# Lot-Box Hauptanzeige
st.markdown(f"""
    <div class='lot-box'>
        <span style='color: #38bdf8; font-weight: bold;'>📋 MT5 POSITIONSGRÖSSE</span><br>
        <span style='font-size: 1.4rem; font-weight: bold; color: #fff;'>{res['lot']} Lots</span>
    </div>
""", unsafe_allow_html=True)

# --- DAS AUSKLAPPBARE FENSTER FÜR DETAILS (EXPANDER) ---
with st.expander("🔍 Details & Lot-Rechner einblenden"):
    st.info(f"Um bei einem Verlust exakt **{risk_input} €** zu riskieren, musst du im MetaTrader 5 eine Positionsgröße von **{res['lot']} Lots** eingeben.")
    st.markdown("---")
    st.write("**Tagesstatistiken (Heute):**")
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1: st.metric(label="Höchstkurs (High)", value=f"{res['high']} $")
    with col_stat2: st.metric(label="Tiefstkurs (Low)", value=f"{res['low']} $")

st.markdown("---")
if st.button("🔄 Dashboard live aktualisieren", use_container_width=True):
    st.rerun()
