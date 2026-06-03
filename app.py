import streamlit as st
import yfinance as yf
import numpy as np
import datetime
from fpdf import FPDF

# Seiteneinstellungen für die perfekte mobile Ansicht
st.set_page_config(page_title="Gold Scalper Pro", page_icon="💰", layout="centered")

# --- HIGH-END UI DESIGN (CSS) ---
st.markdown("""
    <style>
    /* Hintergrund und Abstände */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 550px !important; }
    h1 { font-size: 1.8rem !important; margin-bottom: 0.2rem; text-align: center; color: #fff; }
    .update-text { text-align: center; color: #8a99ad; font-size: 0.8rem; margin-bottom: 1rem; }
    
    /* Fetterer, definierter Schieberegler */
    .stSlider [data-baseweb="slider"] { height: 14px; background-color: #2d3139; }
    .stSlider [data-testid="stTickBar"] { font-weight: bold; }
    
    /* Neon Signal-Pillen */
    .signal-buy {
        background-color: #052e16; border: 2px solid #00ff88; color: #00ff88;
        padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.1rem;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.2); margin-bottom: 1rem;
    }
    .signal-wait {
        background-color: #2d0606; border: 2px solid #ff3333; color: #ff3333;
        padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.1rem;
        box-shadow: 0 0 15px rgba(255, 51, 51, 0.2); margin-bottom: 1rem;
    }
    
    /* Preis-Kacheln mit Schatten und farbigen Akzenten */
    div[data-testid="stMetricValue"] { font-size: 1.3rem !important; font-weight: bold !important; color: #fff !important; }
    
    /* Einstieg (Neutral) */
    div[data-testid="column"]:nth-of-type(1) div[data-testid="metric-container"] {
        background-color: #1e222b; border: 1px solid #3f444e; border-radius: 8px; padding: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    /* Stop Loss (Roter Glüheffekt) */
    div[data-testid="column"]:nth-of-type(2) div[data-testid="metric-container"] {
        background-color: #1a1515; border: 1px solid #7f1d1d; border-radius: 8px; padding: 10px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
    }
    /* Take Profit (Grüner Glüheffekt) */
    div[data-testid="column"]:nth-of-type(3) div[data-testid="metric-container"] {
        background-color: #131a16; border: 1px solid #064e3b; border-radius: 8px; padding: 10px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
    }
    
    /* Infobox für Lot-Größe */
    .lot-box {
        background: linear-gradient(135deg, #1e293b, #0f172a); border-left: 5px solid #38bdf8;
        padding: 12px; border-radius: 4px; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- PDF GENERATOR FÜR DEN DOWNLOAD-BUTTON ---
def generate_handbook_pdf(sl_val):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Handbuch: Gold Scalper Pro Logik", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "1. Zeitfenster & Datenhistorie", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, "Das Tool nutzt 15-Minuten-Kerzen (15m Interval) und analysiert den Durchschnitt der letzten 20 Perioden. Das entspricht einem festen historischen Blickfeld von exakt 5 Stunden.")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "2. Trend- und Signalbestimmung", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, "Kurs > 5-Stunden-Schnitt: BULLISCH (Käufermarkt) -> Signal-Stärke 75%\nKurs < 5-Stunden-Schnitt: BÄRISCH (Verkäufermarkt) -> Signal-Stärke 45%")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "3. Starres CRV 1:3 Verhältnis", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, f"Das Gewinnverhältnis ist starr auf 1:3 gekoppelt.\nGewähltes Risiko (SL): {sl_val} $\nAutomatisches Ziel (TP): {sl_val * 3.0} $")
    return pdf.output()

# --- DATENABRUF UND LOGIK ---
class GoldDashboardLogic:
    def __init__(self):
        self.symbol = "GC=F"
        self.data = None
        self.info = None

    def fetch_market_data(self):
        try:
            # Holt die Daten für Berechnungen und Tagesstatistiken
            self.data = yf.download(tickers=self.symbol, period="3d", interval="15m", progress=False)
            ticker = yf.Ticker(self.symbol)
            self.info = ticker.fast_info
            return True
        except:
            return False

    def process(self, sl_dist, euro_risk):
        if self.data is None or len(self.data) < 20:
            return {}
        
        close_prices = self.data['Close'].values.flatten()
        current_price = float(close_prices[-1])
        avg_price = float(np.mean(close_prices[-20:]))
        
        # Tages-Statistiken (Hoch/Tief) extrahieren
        high_today = float(self.info.get('day_high', current_price))
        low_today = float(self.info.get('day_low', current_price))
        
        # Signal-Entscheidung
        is_bullish = current_price > avg_price
        prob = 75 if is_bullish else 45
        
        # Preis-Level berechnen
        sl = current_price - sl_dist
        tp = current_price + (sl_dist * 3.0)
        
        # RECHNUNG POSITIONSSIZE (1 Lot Gold = 100 Unzen. 1$ Bewegung = 100$ Kontowert pro Lot)
        # Formel: Lot = Risiko_Euro / (SL_Abstand_Dollar * 100)
        lot_size = euro_risk / (sl_dist * 100.0)
        
        return {
            "current": round(current_price, 2), "sl": round(sl, 2), "tp": round(tp, 2),
            "prob": prob, "is_bullish": is_bullish, "high": round(high_today, 2),
            "low": round(low_today, 2), "lot": round(lot_size, 2)
        }

db = GoldDashboardLogic()

if db.fetch_market_data():
    # Header mit automatischem Zeitstempel
    now = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown("<h1>💰 GOLD SCALPER PRO</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='update-text'>🔄 Live-Märkte aktiv • Letztes Update: {now}</div>", unsafe_allow_html=True)
    
    # --- BLOCK 1: DIE TRADING STEUERUNG ---
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        sl_input = st.slider("Stop Loss ($)", min_value=3.0, max_value=10.0, value=3.0, step=0.5)
    with col_input2:
        risk_input = st.number_input("Gewünschtes Risiko (€)", min_value=10, max_value=2000, value=50, step=10)
        
    # Berechnungen durchführen
    res = db.process(sl_input, risk_input)
    
    # --- BLOCK 2: DYNAMISCHE NEON SIGNAL-ANZEIGE ---
    if res["is_bullish"]:
        st.markdown(f"<div class='signal-buy'>🚀 BUY ZONE • ERFOLGSCHANCE {res['prob']}%</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='signal-wait'>🛑 WAIT / NO TRADE • ERFOLGSCHANCE {res['prob']}%</div>", unsafe_allow_html=True)
        
    # --- BLOCK 3: PREIS-KACHELN NEBENEINANDER (HANDY GRID) ---
    c1, c2, c3 = st.columns(3)
    with c1: st.metric(label="EINSTIEG", value=f"{res['current']}")
    with c2: st.metric(label="STOP LOSS", value=f"{res['sl']}", delta=f"-{sl_input}$", delta_color="inverse")
    with c3: st.metric(label="TAKE PROFIT", value=f"{res['tp']}", delta=f"+{sl_input*3.0}$")
        
    # --- BLOCK 4: POSITIONSGRÖSSEN-RECHNER FÜR MT5 ---
    st.markdown(f"""
        <div class='lot-box'>
            <span style='color: #38bdf8; font-weight: bold; font-size: 0.9rem;'>📋 MT5 POSITIONSGRÖSSE</span><br>
            <span style='font-size: 1.4rem; font-weight: bold; color: #fff;'>{res['lot']} Lots</span>
            <p style='margin: 4px 0 0 0; font-size: 0.75rem; color: #94a3b8;'>
                Tippe diesen Lot-Wert im MetaTrader 5 ein, um bei einem Verlust exakt <b>{risk_input} €</b> zu riskieren.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- BLOCK 5: ZUSÄTZLICHE TAGES-STATISTIKEN ---
    with st.expander("📊 Zusätzliche Marktstatistiken (Heute)"):
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1: st.metric(label="Tages-Höchstkurs", value=f"{res['high']} $")
        with col_stat2: st.metric(label="Tages-Tiefstkurs", value=f"{res['low']} $")
        st.button("🔄 Manuell aktualisieren", use_container_width=True)
        
    # --- BLOCK 6: INTEGRATION DES DOWNLOAD-CENTERS ---
    st.markdown("---")
    pdf_bytes = generate_handbook_pdf(sl_input)
    st.download_button(
        label="📥 Handbuch für deinen Freund (PDF)",
        data=bytes(pdf_bytes),
        file_name="Gold_Scalper_Handbuch.pdf",
        mime="application/pdf",
        use_container_width=True
    )
else:
    st.error("Yahoo Finance Server antwortet nicht. Bitte lade das Dashboard neu.")
