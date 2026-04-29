import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 🎨 STYLIZACJA CSS - Jasny motyw + Tooltipy + Czytelny layout
st.markdown("""
<style>
/* Główny motyw - jasny pastelowy */
.stApp {
    background: #f8fafc;
}

/* Tabele - czytelne nagłówki */
[data-testid="stDataFrame"] table th,
[data-testid="stTable"] table th {
    background: #e2e8f0 !important;
    color: #1e3a5f !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #3b82f6 !important;
    padding: 12px 8px !important;
}

[data-testid="stDataFrame"] table td,
[data-testid="stTable"] table td {
    background: #ffffff !important;
    color: #1e293b !important;
    border-bottom: 1px solid #e2e8f0 !important;
    padding: 10px 8px !important;
}

/* Wyrównanie tabeli */
[data-testid="stDataFrame"] table th:not(:first-child), 
[data-testid="stDataFrame"] table td:not(:first-child),
[data-testid="stTable"] th:not(:first-child),
[data-testid="stTable"] td:not(:first-child) { 
    text-align: center !important; 
}
[data-testid="stDataFrame"] table th:first-child, 
[data-testid="stDataFrame"] table td:first-child,
[data-testid="stTable"] th:first-child,
[data-testid="stTable"] td:first-child { 
    text-align: left !important; 
}

/* Paper Trading - czytelny layout z inputami w linii */
.pt-container {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
    margin: 10px 0;
}
.pt-header {
    background: #f1f5f9;
    padding: 14px 12px;
    font-weight: 600;
    color: #1e3a5f;
    border-bottom: 2px solid #3b82f6;
    display: flex;
    align-items: center;
}
.pt-row {
    display: flex;
    align-items: center;
    padding: 12px 12px;
    border-bottom: 1px solid #e2e8f0;
    gap: 12px;
    background: #ffffff;
}
.pt-row:hover {
    background: #f8fafc;
}
.pt-row:last-child {
    border-bottom: none;
}
.pt-col {
    flex: 1;
    text-align: center;
}
.pt-col:first-child {
    text-align: left;
    flex: 1.5;
    font-weight: 600;
    color: #1e3a5f;
}
.pt-label {
    font-size: 10px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.pt-value {
    font-size: 14px;
    color: #1e293b;
    font-weight: 500;
}
.pt-value.highlight {
    color: #3b82f6;
    font-weight: 600;
}
.pt-input-container {
    width: 100%;
}
.pt-input-container label {
    display: none !important;
}
.pt-input-container input {
    width: 100%;
    text-align: center;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 4px;
    font-size: 13px;
    background: #f8fafc;
}
.pt-input-container input:focus {
    border-color: #3b82f6;
    outline: none;
    background: #ffffff;
}

/* Metric boxes - pastelowe */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 13px !important;
}
[data-testid="stMetricValue"] {
    color: #1e3a5f !important;
    font-size: 24px !important;
}
[data-testid="stMetricDelta"] {
    color: #10b981 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f1f5f9 !important;
}

/* Buttons */
.stButton > button {
    background: #3b82f6 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    background: #2563eb !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9;
    border-radius: 8px 8px 0 0;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: #e2e8f0;
    color: #64748b;
    border-radius: 6px 6px 0 0;
    padding: 10px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #3b82f6 !important;
    font-weight: 600;
}

/* Exchange selector badges */
.exchange-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 4px 2px;
}
.exchange-wig20 { background: #dbeafe; color: #1e40af; }
.exchange-wig40 { background: #dcfce7; color: #166534; }
.exchange-wig80 { background: #fef3c7; color: #92400e; }
.exchange-ibkr { background: #e0e7ff; color: #4338ca; }

/* Tooltip info box */
.tooltip-info {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 10px 0;
    font-size: 12px;
    color: #1e40af;
}

/* Section headers */
.section-header {
    color: #1e3a5f;
    font-size: 18px;
    font-weight: 600;
    margin: 20px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# 📖 LEGENDA WSKAŹNIKÓW - używamy help parametru Streamlit
INDICATOR_HELP = {
    "Ticker": "Symbol giełdowy spółki",
    "Price": "Aktualna cena rynkowa akcji",
    "Target Price": "Średnia cena docelowa analityków",
    "Upside %": "Potencjał wzrostu (%) = (Target - Price) / Price × 100",
    "Market Cap": "Kapitalizacja rynkowa spółki",
    "Dividend Yield": "Stopa dywidendy (%) = Dywidenda / Cena × 100",
    "PE Ratio": "Cena/Zysk. <15 = tanio, >25 = drogo",
    "PEG Ratio": "PE/Wzrost. <1 = niedowyceniony",
    "Quick Ratio (Q)": "Płynność szybka. >1 = zdolność do spłaty zobowiązań",
    "Debt/Assets (Q)": "Zadłużenie/Aktywa. <0.5 = bezpieczny poziom",
    "Signal Score": "Wynik AI (0-1). BUY≥0.6, HOLD 0.3-0.6, SELL≤0.3",
    "Signal": "Sygnał: 🟢BUY HOLD 🔴SELL",
    "Cena": "Cena pojedynczej akcji",
    "% Model": "Procent alokacji wg modelu AI",
    "Ilość (ułamkowa)": "Sugerowana ilość akcji z modelu",
    "Faktyczny portfel": "Realna ilość do wprowadzenia u brokera",
    "Wartość Realna": "Rzeczywista wartość pozycji"
}

def format_currency(val, curr="PLN"):
    if pd.isna(val): 
        return "-"
    return f"{val:,.0f} {curr}"

# 📊 DANE DLA RÓŻNYCH INDEKSÓW
INDEX_TICKERS = {
    "WIG20": ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR"],
    "WIG40": ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR", "PLW.WAR", "CCC.WAR", "CNT.WAR", "EUZ.WAR", "KRU.WAR"],
    "WIG80": ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR", "PLW.WAR", "CCC.WAR", "CNT.WAR", "EUZ.WAR", "KRU.WAR", "ATA.WAR", "BDS.WAR", "BHW.WAR", "BIO.WAR", "BLO.WAR"],
    "IBKR": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "JNJ"]
}

@st.cache_data(ttl=3600)
def generate_mock_data(tickers, trade_mode="daily"):
    data = []
    for t in tickers:
        if t in INDEX_TICKERS["IBKR"]:
            price = np.round(np.random.uniform(100, 500), 2)
        else:
            price = np.round(np.random.uniform(40, 350), 2)
        target = price * np.round(np.random.uniform(0.85, 1.35), 2)
        
        if trade_mode == "daily":
            sentiment = np.round(np.random.uniform(-0.4, 0.9), 2)
        else:
            sentiment = np.round(np.random.uniform(-0.2, 0.6), 2)
            
        data.append({
            "Ticker": t, 
            "Price": price, 
            "Target Price": target, 
            "Upside %": np.round((target/price - 1)*100, 2),
            "Market Cap": np.random.randint(2e9, 40e9),
            "Dividend Yield": np.round(np.random.uniform(0, 12), 2),
            "PE Ratio": np.round(np.random.uniform(6, 30), 2),
            "PEG Ratio": np.round(np.random.uniform(0.6, 2.8), 2),
            "Quick Ratio (Q)": np.round(np.random.uniform(0.4, 3.2), 2),
            "Debt/Assets (Q)": np.round(np.random.uniform(0.15, 0.75), 2),
            "Sentiment": sentiment
        })
    
    df = pd.DataFrame(data)
    
    if trade_mode == "daily":
        df["Signal Score"] = (
            (df["PE Ratio"] < 18) * 0.15 + 
            (df["PEG Ratio"] < 1.0) * 0.2 + 
            (df["Dividend Yield"] > 2) * 0.1 +
            (df["Quick Ratio (Q)"] > 0.8) * 0.15 + 
            (df["Upside %"] > 8) * 0.25 + 
            (df["Sentiment"] > 0.4) * 0.15
        )
    else:
        df["Signal Score"] = (
            (df["PE Ratio"] < 15) * 0.2 + 
            (df["PEG Ratio"] < 1.2) * 0.15 + 
            (df["Dividend Yield"] > 3) * 0.2 +
            (df["Quick Ratio (Q)"] > 1) * 0.15 + 
            (df["Upside %"] > 10) * 0.2 + 
            (df["Debt/Assets (Q)"] < 0.5) * 0.1
        )
    
    df["Signal"] = df["Signal Score"].apply(lambda x: "🟢 BUY" if x >= 0.6 else ("🔴 SELL" if x <= 0.3 else "🟡 HOLD"))
    return df

# 💾 STAN APLIKACJI
if "paper_capital" not in st.session_state: 
    st.session_state.paper_capital = 100000.0
if "portfolio_alloc" not in st.session_state: 
    st.session_state.portfolio_alloc = pd.DataFrame()
if "currency" not in st.session_state: 
    st.session_state.currency = "PLN"
if "trade_mode" not in st.session_state:
    st.session_state.trade_mode = "daily"
if "exchange" not in st.session_state:
    st.session_state.exchange = "WIG20"

# 🖥️ UI
st.set_page_config(page_title="🤖 AI Giełda Agent", layout="wide", page_icon="📈")

# Header
st.markdown("<h1 style='color: #1e3a5f; font-size: 28px; margin-bottom: 8px;'>🤖 AI Giełda Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 20px;'>Paper Trading | GPW & IBKR | Rebalans | Sygnały BUY/HOLD/SELL</p>", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("<h3 style='color: #1e3a5f; margin-bottom: 16px;'>⚙️ Konfiguracja</h3>", unsafe_allow_html=True)
    
    # ✅ WYBÓR GIEŁDY
    st.markdown("<p style='color: #64748b; font-size: 12px; font-weight: 600; margin-bottom: 8px;'>📍 Giełda / Indeks</p>", unsafe_allow_html=True)
    exchange = st.selectbox(
        "Wybierz indeks",
        ["WIG20", "WIG40", "WIG80", "IBKR"],
        index=["WIG20", "WIG40", "WIG80", "IBKR"].index(st.session_state.exchange) if st.session_state.exchange in ["WIG20", "WIG40", "WIG80", "IBKR"] else 0,
        label_visibility="collapsed"
    )
    st.session_state.exchange = exchange
    
    # Badge giełdy
    badge_class = f"exchange-{exchange.lower()}"
    st.markdown(f'<span class="exchange-badge {badge_class}">📊 {exchange}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # Tryb tradingu
    st.markdown("<p style='color: #64748b; font-size: 12px; font-weight: 600; margin-bottom: 8px;'>🎯 Strategia</p>", unsafe_allow_html=True)
    trade_mode = st.radio(
        "Tryb",
        ["Daily Trade", "Monthly Trade"],
        index=0 if st.session_state.trade_mode == "daily" else 1,
        label_visibility="collapsed"
    )
    st.session_state.trade_mode = "daily" if trade_mode == "Daily Trade" else "monthly"
    
    badge_text = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    badge_color = "#ef4444" if st.session_state.trade_mode == "daily" else "#10b981"
    st.markdown(f'<span style="background: {badge_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; display: inline-block; margin-top: 8px;">🔴 {badge_text}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # Waluta
    curr = st.selectbox("💱 Waluta", ["PLN", "USD"], index=0)
    st.session_state.currency = curr
    
    # Kapitał
    capital = st.number_input("💰 Kapitał startowy", min_value=1000.0, value=100000.0, step=5000.0)
    st.session_state.paper_capital = capital
    
    st.divider()
    
    # Info
    mode_hint = "Szybkie momentum, sentyment" if st.session_state.trade_mode == "daily" else "Wartość, dywidendy"
    st.markdown(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-top: 10px;">
        <p style="color: #3b82f6; font-weight: 600; margin-bottom: 8px; font-size: 12px;">📖 Strategia: {badge_text}</p>
        <p style="color: #64748b; font-size: 11px; margin: 4px 0;">{mode_hint}</p>
        <p style="color: #64748b; font-size: 11px; margin: 4px 0;">PE&lt;15 | DY&gt;3% | Quick&gt;1</p>
    </div>
    """, unsafe_allow_html=True)

# Generuj dane dla wybranego indeksu
tickers = INDEX_TICKERS[st.session_state.exchange]
df_all = generate_mock_data(tickers, st.session_state.trade_mode)

# Kolumny z help dla tooltipów
cols_with_help = [
    ("Ticker", INDICATOR_HELP["Ticker"]),
    ("Price", INDICATOR_HELP["Price"]),
    ("Target Price", INDICATOR_HELP["Target Price"]),
    ("Upside %", INDICATOR_HELP["Upside %"]),
    ("Market Cap", INDICATOR_HELP["Market Cap"]),
    ("Dividend Yield", INDICATOR_HELP["Dividend Yield"]),
    ("PE Ratio", INDICATOR_HELP["PE Ratio"]),
    ("PEG Ratio", INDICATOR_HELP["PEG Ratio"]),
    ("Quick Ratio (Q)", INDICATOR_HELP["Quick Ratio (Q)"]),
    ("Debt/Assets (Q)", INDICATOR_HELP["Debt/Assets (Q)"]),
    ("Signal", INDICATOR_HELP["Signal"]),
    ("Signal Score", INDICATOR_HELP["Signal Score"])
]

cols_display = [col[0] for col in cols_with_help]

# 📊 ZAKŁADKI
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Skaner", "📈 Sygnały", "💼 Paper Trading"])

# TAB 1: DASHBOARD
with tab1:
    mode_label = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    st.markdown(f"<h3 class='section-header'>📊 Dashboard — {mode_label} | {st.session_state.exchange}</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📈 Aktywa w portfelu", "20/30")
    c2.metric("🟢 Sygnały BUY", f"{len(df_all[df_all['Signal']=='🟢 BUY'])}")
    c3.metric("📊 Śr. Upside", f"{df_all['Upside %'].mean():.1f}%")
    c4.metric("🔄 Ostatni rebalans", datetime.now().strftime("%Y-%m-%d"))
    
    st.markdown("<h4 style='color: #1e3a5f; margin-top: 24px;'>🔥 Top Movers</h4>", unsafe_allow_html=True)
    movers = df_all.sort_values("Upside %", ascending=False).head(5)
    
    st.dataframe(movers[cols_display].style.format({
        "Price": f"{{:,.2f}} {st.session_state.currency}", 
        "Target Price": f"{{:,.2f}} {st.session_state.currency}", 
        "Upside %": "{:.2f}%",
        "Market Cap": lambda x: format_currency(x, st.session_state.currency), 
        "Signal Score": "{:.2f}"
    }), use_container_width=True, hide_index=True)
    
    # ✅ Tooltip info box
    st.markdown("""
    <div class="tooltip-info">
        💡 <b>Wskazówka:</b> Najedź kursorem na nagłówek kolumny w tabeli, aby zobaczyć opis wskaźnika
    </div>
    """, unsafe_allow_html=True)

# TAB 2: SKANER
with tab2:
    st.markdown("<h3 class='section-header'>🔍 Zaawansowany Skaner</h3>", unsafe_allow_html=True)
    colA, colB, colC = st.columns(3)
    with colA:
        pe_max = st.number_input("Max P/E", 5, 50, 25)
        dy_min = st.number_input("Min Dywidenda %", 0.0, 15.0, 2.0)
    with colB:
        upside_min = st.number_input("Min Upside %", -10.0, 50.0, 5.0)
        quick_min = st.number_input("Min Quick Ratio", 0.5, 5.0, 1.0)
    with colC:
        debt_max = st.number_input("Max Debt/Assets", 0.1, 1.0, 0.5)
        cap_min = st.number_input("Min Market Cap (mld)", 0.1, 50.0, 1.0)
    
    if st.button("🔎 Szukaj", type="primary"):
        filt = df_all[
            (df_all["PE Ratio"] <= pe_max) & 
            (df_all["Dividend Yield"] >= dy_min) &
            (df_all["Upside %"] >= upside_min) & 
            (df_all["Quick Ratio (Q)"] >= quick_min) &
            (df_all["Debt/Assets (Q)"] <= debt_max) & 
            (df_all["Market Cap"] >= cap_min*1e9)
        ]
        st.success(f"Znaleziono {len(filt)} spółek")
        
        st.dataframe(filt[cols_display].style.format({
            "Price": f"{{:,.2f}} {st.session_state.currency}", 
            "Target Price": f"{{:,.2f}} {st.session_state.currency}", 
            "Upside %": "{:.2f}%",
            "Market Cap": lambda x: format_currency(x, st.session_state.currency), 
            "Signal Score": "{:.2f}"
        }), use_container_width=True, hide_index=True)

# TAB 3: SYGNAŁY
with tab3:
    mode_label = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    st.markdown(f"<h3 class='section-header'>🎯 Lista Sygnałów — {mode_label}</h3>", unsafe_allow_html=True)
    
    sig_filter = st.radio("Filtr sygnałów", ["Wszystkie", "🟢 BUY", "🟡 HOLD", "🔴 SELL"], horizontal=True)
    df_sig = df_all[df_all["Signal"] == sig_filter] if sig_filter != "Wszystkie" else df_all
    
    st.dataframe(df_sig[cols_display].style.format({
        "Price": f"{{:,.2f}} {st.session_state.currency}", 
        "Target Price": f"{{:,.2f}} {st.session_state.currency}", 
        "Upside %": "{:.2f}%",
        "Market Cap": lambda x: format_currency(x, st.session_state.currency), 
        "Signal Score": "{:.2f}"
    }), use_container_width=True, hide_index=True)

# TAB 4: PAPER TRADING - CZYTELNY LAYOUT Z INPUTAMI
with tab4:
    mode_label = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    st.markdown(f"<h3 class='section-header'>💼 Panel Paper Trading — {mode_label} | {st.session_state.exchange}</h3>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("<p style='color: #64748b; font-size: 12px;'>💰 Dostępny Kapitał</p>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: #1e3a5f; margin: 8px 0;'>{format_currency(st.session_state.paper_capital, st.session_state.currency)}</h2>", unsafe_allow_html=True)
        
        alloc_method = st.radio("Metoda alokacji", ["Wg wartości (%)", "Wg ilości akcji"])
        tickers_list = st.multiselect("Wybór walorów", df_all["Ticker"].tolist(), default=df_all["Ticker"].tolist()[:5])
        
    with col_right:
        st.markdown("<p style='color: #64748b; font-size: 12px;'>📝 Konfiguracja pozycji</p>", unsafe_allow_html=True)
        st.caption("💡 Ułamkowe części akcji dozwolone (2 miejsca po przecinku)")
        
        if tickers_list:
            alloc_data = []
            df_tickers = df_all[df_all["Ticker"].isin(tickers_list)]
            
            # ✅ NAGŁÓWEK TABELI
            st.markdown("""
            <div class="pt-header">
                <div class="pt-col" style="text-align:left; flex:1.5;">Ticker</div>
                <div class="pt-col">Cena</div>
                <div class="pt-col">Model %</div>
                <div class="pt-col">Model (szt)</div>
                <div class="pt-col">Faktyczny (szt)</div>
                <div class="pt-col">Wartość</div>
            </div>
            """, unsafe_allow_html=True)
            
            for idx, row in df_tickers.iterrows():
                # Obliczenia
                if alloc_method == "Wg wartości (%)":
                    pct = st.number_input("Model %", 0.0, 100.0, 5.0, step=1.0, key=f"pct_{idx}_{row['Ticker']}", label_visibility="collapsed")
                    model_value = (pct/100) * st.session_state.paper_capital
                    model_qty = model_value / row["Price"]
                else:
                    model_qty = st.number_input("Model szt.", 0.0, 10000.0, 10.0, step=0.5, key=f"qty_{idx}_{row['Ticker']}", label_visibility="collapsed")
                    model_value = model_qty * row["Price"]
                    pct = (model_value / st.session_state.paper_capital) * 100
                
                # Faktyczny portfel - step=0.01 dla ułamków
                real_qty = st.number_input(
                    "Faktyczny", 
                    0.0, 
                    10000.0, 
                    float(round(model_qty, 2)),
                    step=0.01,
                    key=f"real_{idx}_{row['Ticker']}",
                    label_visibility="collapsed"
                )
                real_value = real_qty * row["Price"]
                
                # ✅ SPÓJNY WIERZ Z INPUTAMI W LINII
                st.markdown(f"""
                <div class="pt-row">
                    <div class="pt-col" style="text-align:left; flex:1.5;">{row['Ticker']}</div>
                    <div class="pt-col">
                        <span class="pt-value">{row['Price']:,.2f}</span>
                        <div class="pt-label">{st.session_state.currency}</div>
                    </div>
                    <div class="pt-col">
                        <span class="pt-value">{pct:.1f}%</span>
                    </div>
                    <div class="pt-col">
                        <span class="pt-value">{model_qty:.2f}</span>
                        <div class="pt-label">szt</div>
                    </div>
                    <div class="pt-col">
                        <span class="pt-value highlight">{real_qty:.2f}</span>
                        <div class="pt-label">szt</div>
                    </div>
                    <div class="pt-col">
                        <span class="pt-value">{real_value:,.0f}</span>
                        <div class="pt-label">{st.session_state.currency}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                alloc_data.append({
                    "Ticker": row["Ticker"], 
                    "Cena": row["Price"],
                    "% Model": pct, 
                    "Ilość (ułamkowa)": model_qty, 
                    "Faktyczny portfel": real_qty, 
                    "Wartość Realna": real_value
                })
            
            df_alloc = pd.DataFrame(alloc_data)
            total_real_alloc = df_alloc["Wartość Realna"].sum()
            remaining = st.session_state.paper_capital - total_real_alloc
            
            st.divider()
            
            # Podsumowanie
            cR1, cR2, cR3, cR4 = st.columns(4)
            cR1.metric("📊 Zaalokowano", format_currency(total_real_alloc, st.session_state.currency))
            cR2.metric("💵 Gotówka", format_currency(remaining, st.session_state.currency), 
                       delta=f"{(remaining/st.session_state.paper_capital)*100:.1f}%")
            cR3.metric("📊 Pozycji", f"{len(df_alloc)}")
            cR4.metric("⚠️ Nadpłynięcie", "TAK" if remaining < 0 else "NIE", 
                       delta=f"{remaining:,.0f} {st.session_state.currency}")
            
            if st.button("💾 Zatwierdź portfel", type="primary"):
                st.session_state.portfolio_alloc = df_alloc.copy()
                st.session_state.portfolio_alloc["Data dodania"] = datetime.now().strftime("%Y-%m-%d")
                st.success("✅ Portfel zapisany!")
            
            if not df_alloc.empty:
                csv = df_alloc.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Eksportuj CSV",
                    csv,
                    f"portfolio_{st.session_state.exchange}_{st.session_state.trade_mode}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )

# Stopka
st.markdown("---")
st.caption("🤖 AI Giełda Agent | Dane testowe (symulacja) | To narzędzie analityczne, nie doradztwo inwestycyjne")
