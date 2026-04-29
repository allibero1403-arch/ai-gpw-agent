import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================
# 🎨 STYLIZACJA CSS - Poprawiony kontrast i tooltips
# ============================================================
st.markdown("""
<style>
/* === Metric boxes - biały tekst na ciemnym tle === */
[data-testid="stMetric"] {
    background: #1e293b !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    border: 1px solid #334155 !important;
}
[data-testid="stMetric"] label,
[data-testid="stMetric"] [data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] {
    color: #86efac !important;
}

/* === Tooltips - lepszy kontrast i styl === */
.tooltip-wrap {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    cursor: help;
    font-size: 13px;
    font-weight: 600;
    color: #e2e8f0;
    padding: 4px 8px;
    background: rgba(59, 130, 246, 0.15);
    border-radius: 6px;
    margin: 2px;
}
.tooltip-icon {
    width: 18px;
    height: 18px;
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    color: white;
    border-radius: 50%;
    font-size: 11px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}
.tooltip-text {
    visibility: hidden;
    opacity: 0;
    width: 280px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f1f5f9;
    text-align: left;
    border-radius: 10px;
    padding: 12px 14px;
    position: absolute;
    z-index: 1000;
    bottom: 120%;
    left: 50%;
    transform: translateX(-50%);
    font-size: 12px;
    line-height: 1.6;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(59,130,246,0.3);
    transition: all 0.2s ease;
    pointer-events: none;
    border: 1px solid rgba(59,130,246,0.2);
}
.tooltip-text::before {
    content: "ℹ️ Opis";
    display: block;
    font-size: 11px;
    font-weight: 700;
    color: #60a5fa;
    margin-bottom: 6px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.tooltip-wrap:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
    bottom: 100%;
}

/* === Wyrównanie tabel === */
.stDataFrame table th:not(:first-child),
.stDataFrame table td:not(:first-child),
[data-testid="stTable"] table th:not(:first-child),
[data-testid="stTable"] table td:not(:first-child) {
    text-align: center !important;
}
.stDataFrame table th:first-child,
.stDataFrame table td:first-child,
[data-testid="stTable"] table th:first-child,
[data-testid="stTable"] table td:first-child {
    text-align: left !important;
}

/* === Sidebar hint box === */
.sidebar-hint {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 10px;
    border: 1px solid #334155;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.sidebar-hint-title {
    color: #60a5fa;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.sidebar-hint-item {
    color: #cbd5e1;
    font-size: 11px;
    padding: 4px 0;
    display: flex;
    gap: 8px;
}
.sidebar-hint-item::before {
    content: "▸";
    color: #3b82f6;
    font-weight: bold;
}
.sidebar-hint-item strong {
    color: #fbbf24;
}

/* === Badge trybu === */
.trader-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
.badge-daily {
    background: linear-gradient(135deg, #059669, #047857);
    color: white;
}
.badge-monthly {
    background: linear-gradient(135deg, #7c3aed, #6d28d9);
    color: white;
}

/* === Inputs === */
.stNumberInput > div > div > input {
    background: #1e293b !important;
    color: #f1f5f9 !important;
    border-color: #475569 !important;
}

/* === Radio horizontal === */
.stRadio [role="radiogroup"] {
    flex-direction: row !important;
    gap: 12px;
}

/* === Headers === */
h1, h2, h3 {
    color: #f1f5f9 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 📖 LEGENDA WSZYSTKICH WSKAŹNIKÓW
# ============================================================
INDICATOR_DESC = {
    "Ticker": "Symbol giełdowy spółki na GPW",
    "Price": "Aktualna cena rynkowa akcji (PLN)",
    "Target Price": "Średnia cena docelowa analityków (PLN)",
    "Upside %": "Potencjał wzrostu (%) = (Cena docelowa - Cena) / Cena × 100",
    "Market Cap": "Kapitalizacja rynkowa spółki (PLN)",
    "Dividend Yield": "Roczna stopa dywidendy (%) = Dywidenda na akcję / Cena × 100",
    "Revenue Est. Growth (2Y)": "Szacowany roczny wzrost przychodów (% rocznie)",
    "EPS Est. Growth (2Y)": "Szacowany roczny wzrost zysku na akcję (% rocznie)",
    "EPS Long-Term (5Y)": "Długoterminowy wzrost EPS (% rocznie, horyzont 5 lat)",
    "PS Ratio": "Cena / Przychody na akcję. Niższy → tańsza spółka",
    "PE Ratio": "Cena / Zysk. <15 atrakcyjne, >25 drogo",
    "PEG Ratio": "PE / Wzrost. <1 niedowartościowana, >2 przewartościowana",
    "Revenue (TTM)": "Przychody ostatnie 12 miesięcy (PLN)",
    "Free Cash Flow (TTM)": "Gotówka po CAPEX (PLN, 12m)",
    "Net Income (TTM)": "Zysk netto (PLN, 12m)",
    "Debt/Assets (Q)": "Zadłużenie/Aktywa. <0.5 bezpieczne, >0.6 ryzyko",
    "Quick Ratio (Q)": "Płynność szybka = (Obr.tot.-Zapasy)/Zob.krótk. >1 OK",
    "Analyst Rating": "Ocena analityków: Strong Buy → Sell",
    "Sentiment": "Nastroje rynkowe: -1 (negatywne) do +1 (pozytywne)",
    "Signal": "Sygnał: 🟢 BUY / 🟡 HOLD / 🔴 SELL",
    "Signal Score": "Wynik kompozytowy: BUY≥0.6, HOLD 0.3-0.6, SELL≤0.3",
    "%": "Procent alokacji kapitału w portfelu",
    "Ilość (ułamkowa)": "Ilość akcji w modelu (możliwe ułamki)",
    "Faktyczny portfel": "Realna ilość do wprowadzenia w brokerze"
}

def tooltip_header(col):
    """Nagłówek z tooltipem - lepszy styl"""
    if col in INDICATOR_DESC:
        return f'<div class="tooltip-wrap">{col}<div class="tooltip-icon">i</div><div class="tooltip-text">{INDICATOR_DESC[col]}</div></div>'
    return f'<div style="color:#cbd5e1;font-size:13px;font-weight:600;padding:4px 8px;">{col}</div>'

def format_currency(val, curr="PLN"):
    """Formatowanie walutowe"""
    if pd.isna(val): return "-"
    return f"{val:,.0f} {curr}"

# ============================================================
# 📊 GENERATOR DANYCH
# ============================================================
@st.cache_data(ttl=3600)
def generate_mock_data(trader_mode="daily"):
    tickers = ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR",
               "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR",
               "PLW.WAR", "CCC.WAR", "CNT.WAR", "EUZ.WAR", "KRU.WAR"]
    data = []
    
    for t in tickers:
        price = np.round(np.random.uniform(20, 500), 2)
        target = price * np.round(np.random.uniform(0.80, 1.45), 2)
        
        if trader_mode == "daily":
            upside_range = (-15, 35)
            pe_range = (5, 45)
            sentiment_range = (-0.5, 0.9)
            rev_growth = (-5, 30)
        else:
            upside_range = (0, 50)
            pe_range = (8, 35)
            sentiment_range = (-0.2, 0.7)
            rev_growth = (-2, 25)
        
        data.append({
            "Ticker": t,
            "Price": price,
            "Target Price": target,
            "Upside %": np.round((target/price - 1)*100, 2),
            "Market Cap": np.random.randint(1e9, 50e9),
            "Dividend Yield": np.round(np.random.uniform(0, 14), 2),
            "Revenue Est. Growth (2Y)": np.round(np.random.uniform(*rev_growth), 2),
            "EPS Est. Growth (2Y)": np.round(np.random.uniform(-5, 30), 2),
            "EPS Long-Term (5Y)": np.round(np.random.uniform(0, 20), 2),
            "PS Ratio": np.round(np.random.uniform(0.5, 8.0), 2),
            "PE Ratio": np.round(np.random.uniform(*pe_range), 2),
            "PEG Ratio": np.round(np.random.uniform(0.4, 3.5), 2),
            "Revenue (TTM)": np.random.randint(300e6, 30e9),
            "Free Cash Flow (TTM)": np.random.randint(-300e6, 5e9),
            "Net Income (TTM)": np.random.randint(-150e6, 4e9),
            "Debt/Assets (Q)": np.round(np.random.uniform(0.10, 0.80), 2),
            "Quick Ratio (Q)": np.round(np.random.uniform(0.3, 4.0), 2),
            "Analyst Rating": np.random.choice(["Strong Buy", "Buy", "Hold", "Sell"], p=[0.15, 0.35, 0.40, 0.10]),
            "Sentiment": np.round(np.random.uniform(*sentiment_range), 2)
        })
    
    df = pd.DataFrame(data)
    
    if trader_mode == "daily":
        df["Signal Score"] = (
            (df["PE Ratio"] < 20) * 0.15 +
            (df["PEG Ratio"] < 1.0) * 0.15 +
            (df["Upside %"] > 5) * 0.20 +
            (df["Quick Ratio (Q)"] > 1.2) * 0.15 +
            (df["Sentiment"] > 0.3) * 0.20 +
            (df["Revenue Est. Growth (2Y)"] > 10) * 0.15
        )
        df["Trading Horizon"] = "Day Trade"
    else:
        df["Signal Score"] = (
            (df["PE Ratio"] < 15) * 0.20 +
            (df["Dividend Yield"] > 4) * 0.20 +
            (df["Quick Ratio (Q)"] > 1) * 0.15 +
            (df["Debt/Assets (Q)"] < 0.4) * 0.15 +
            (df["EPS Long-Term (5Y)"] > 8) * 0.15 +
            (df["Market Cap"] > 10e9) * 0.15
        )
        df["Trading Horizon"] = "Swing/Monthly"
    
    df["Signal"] = df["Signal Score"].apply(
        lambda x: "🟢 BUY" if x >= 0.60 else ("🔴 SELL" if x <= 0.30 else "🟡 HOLD")
    )
    df["Signal Score"] = df["Signal Score"].round(2)
    
    return df

# ============================================================
# 💾 STAN APLIKACJI
# ============================================================
if "trader_mode" not in st.session_state:
    st.session_state.trader_mode = "daily"
if "paper_capital" not in st.session_state:
    st.session_state.paper_capital = 100_000.0
if "portfolio_alloc" not in st.session_state:
    st.session_state.portfolio_alloc = pd.DataFrame()
if "currency" not in st.session_state:
    st.session_state.currency = "PLN"
if "show_tooltips" not in st.session_state:
    st.session_state.show_tooltips = True

# ============================================================
# 🖥️ UI
# ============================================================
st.set_page_config(
    page_title="🤖 AI Giełda Agent",
    layout="wide",
    page_icon="📈"
)

st.title("🤖 AI Giełda Agent")
st.markdown("*Paper Trading | GPW & IBKR | Rebalans | Sygnały AI*")

# ============================================================
# 📱 SIDEBAR
# ============================================================
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    
    st.markdown("**📊 Tryb tradera**")
    trader_mode = st.radio(
        "Wybierz horyzont czasowy",
        ["daily", "monthly"],
        index=0 if st.session_state.trader_mode == "daily" else 1,
        format_func=lambda x: "📈 Day Trade" if x == "daily" else "📅 Swing/Monthly"
    )
    st.session_state.trader_mode = trader_mode
    
    badge_class = "badge-daily" if trader_mode == "daily" else "badge-monthly"
    st.markdown(f'<span class="trader-badge {badge_class}">{"✅ Day Trade" if trader_mode == "daily" else "✅ Swing/Monthly"}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    curr = st.selectbox("💱 Waluta", ["PLN", "USD"], index=0)
    st.session_state.currency = curr
    
    capital = st.number_input(
        "💰 Kapitał startowy",
        min_value=1_000.0,
        value=st.session_state.paper_capital,
        step=5_000.0
    )
    st.session_state.paper_capital = capital
    
    # Opcja pokazywania tooltipów
    show_tt = st.toggle("📖 Pokaż opisy wskaźników", value=st.session_state.show_tooltips)
    st.session_state.show_tooltips = show_tt
    
    st.divider()
    
    mode_hints = {
        "daily": "Day Trade: Momentum + Sentiment + Short-term Upside",
        "monthly": "Monthly: Wartość + Dywidenda + Długoterminowy Wzrost"
    }
    st.markdown(f"""
    <div class="sidebar-hint">
        <div class="sidebar-hint-title">📖 Legenda wskaźników</div>
        <div class="sidebar-hint-item"><strong>PE &lt; 15/20</strong> → atrakcyjna wycena</div>
        <div class="sidebar-hint-item"><strong>DY &gt; 3-4%</strong> → stabilna dywidenda</div>
        <div class="sidebar-hint-item"><strong>Quick &gt; 1</strong> → dobra płynność</div>
        <div class="sidebar-hint-item"><strong>Upside &gt; 5-10%</strong> → potencjał wzrostu</div>
        <div class="sidebar-hint-item"><strong>Debt/Assets &lt; 0.5</strong> → niskie zadłużenie</div>
        <div class="sidebar-hint-item"><strong>Sentiment &gt; 0.3</strong> → pozytywne nastroje</div>
        <div class="sidebar-hint-item" style="margin-top:8px;color:#60a5fa;font-size:10px;">▶ {mode_hints[trader_mode]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.caption("🤖 AI Giełda Agent v2.1")

# ============================================================
# 📊 GENERUJ DANE
# ============================================================
df_all = generate_mock_data(st.session_state.trader_mode)

COLS_DISPLAY = [
    "Ticker", "Price", "Target Price", "Upside %", "Market Cap", "Dividend Yield",
    "PE Ratio", "PEG Ratio", "Quick Ratio (Q)", "Debt/Assets (Q)", "Signal", "Signal Score"
]

# ============================================================
# 📊 ZAKŁADKI
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "🔍 Skaner",
    "📈 Sygnały",
    "💼 Paper Trading"
])

# ============================================================
# TAB 1: DASHBOARD
# ============================================================
with tab1:
    mode_label = 'Day Trade' if st.session_state.trader_mode == 'daily' else 'Swing/Monthly'
    st.subheader(f"📊 Dashboard — {mode_label}")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📈 Aktywa w portfelu", "20/30")
    col2.metric("🟢 Sygnały BUY", f"{len(df_all[df_all['Signal']=='🟢 BUY'])}")
    col3.metric("📊 Śr. Upside", f"{df_all['Upside %'].mean():.1f}%")
    col4.metric("🔄 Ostatni rebalans", datetime.now().strftime("%Y-%m-%d"))
    
    st.subheader("🔥 Top Movers")
    movers = df_all.sort_values("Upside %", ascending=False).head(5)
    
    if st.session_state.show_tooltips:
        headers_html = " | ".join([tooltip_header(c) for c in COLS_DISPLAY])
        st.markdown(headers_html, unsafe_allow_html=True)
    
    st.dataframe(
        movers[COLS_DISPLAY].style.format({
            "Price": lambda x: f"{x:,.2f} {curr}",
            "Target Price": lambda x: f"{x:,.2f} {curr}",
            "Upside %": "{:.2f}%",
            "Market Cap": lambda x: format_currency(x, curr),
            "Signal Score": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# TAB 2: SKANER
# ============================================================
with tab2:
    st.subheader("🔍 Zaawansowany Skaner")
    
    colA, colB, colC = st.columns(3)
    with colA:
        pe_max = st.number_input("Max P/E", 5, 50, 25 if st.session_state.trader_mode == "daily" else 18)
        dy_min = st.number_input("Min Dywidenda %", 0.0, 20.0, 0.0 if st.session_state.trader_mode == "daily" else 2.0)
    with colB:
        upside_min = st.number_input("Min Upside %", -20.0, 60.0, 0.0 if st.session_state.trader_mode == "daily" else 5.0)
        quick_min = st.number_input("Min Quick Ratio", 0.3, 5.0, 0.8 if st.session_state.trader_mode == "daily" else 1.0)
    with colC:
        debt_max = st.number_input("Max Debt/Assets", 0.1, 1.0, 0.6 if st.session_state.trader_mode == "daily" else 0.4)
        cap_min = st.number_input("Min Market Cap (mld)", 0.1, 100.0, 1.0)
    
    if st.button("🔎 Szukaj", type="primary"):
        filt = df_all[
            (df_all["PE Ratio"] <= pe_max) &
            (df_all["Dividend Yield"] >= dy_min) &
            (df_all["Upside %"] >= upside_min) &
            (df_all["Quick Ratio (Q)"] >= quick_min) &
            (df_all["Debt/Assets (Q)"] <= debt_max) &
            (df_all["Market Cap"] >= cap_min * 1e9)
        ]
        st.success(f"Znaleziono {len(filt)} spółek")
        
        if st.session_state.show_tooltips:
            headers_html = " | ".join([tooltip_header(c) for c in COLS_DISPLAY])
            st.markdown(headers_html, unsafe_allow_html=True)
        
        st.dataframe(
            filt[COLS_DISPLAY].style.format({
                "Price": lambda x: f"{x:,.2f} {curr}",
                "Target Price": lambda x: f"{x:,.2f} {curr}",
                "Upside %": "{:.2f}%",
                "Market Cap": lambda x: format_currency(x, curr),
                "Signal Score": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# TAB 3: SYGNAŁY
# ============================================================
with tab3:
    mode_label = 'Day Trade' if st.session_state.trader_mode == 'daily' else 'Swing/Monthly'
    st.subheader(f"🎯 Lista Sygnałów — {mode_label}")
    
    sig_filter = st.radio("Filtr sygnałów", ["Wszystkie", "🟢 BUY", "🟡 HOLD", "🔴 SELL"], horizontal=True)
    df_sig = df_all[df_all["Signal"] == sig_filter] if sig_filter != "Wszystkie" else df_all
    
    if st.session_state.show_tooltips:
        headers_html = " | ".join([tooltip_header(c) for c in COLS_DISPLAY])
        st.markdown(headers_html, unsafe_allow_html=True)
    
    st.dataframe(
        df_sig[COLS_DISPLAY].style.format({
            "Price": lambda x: f"{x:,.2f} {curr}",
            "Target Price": lambda x: f"{x:,.2f} {curr}",
            "Upside %": "{:.2f}%",
            "Market Cap": lambda x: format_currency(x, curr),
            "Signal Score": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.caption("💡 Najedź na nagłówek kolumny z ikoną (i), aby zobaczyć opis wskaźnika")

# ============================================================
# TAB 4: PAPER TRADING
# ============================================================
with tab4:
    mode_label = 'Day Trade' if st.session_state.trader_mode == 'daily' else 'Swing/Monthly'
    st.subheader(f"💼 Paper Trading — {mode_label}")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.metric("💰 Kapitał", f"{st.session_state.paper_capital:,.0f} {curr}")
        alloc_method = st.radio("Metoda alokacji", ["Wg wartości (%)", "Wg ilości akcji (model)"])
        tickers_list = st.multiselect("Wybór walorów", df_all["Ticker"].tolist(), default=df_all["Ticker"].tolist()[:8])
        
        if not st.session_state.portfolio_alloc.empty and len(st.session_state.portfolio_alloc) > 0:
            st.divider()
            st.markdown("**📁 Zapisany portfel:**")
            saved_cols = ["Ticker", "Ilość (ułamkowa)", "Faktyczny portfel", "Wartość pozycji"]
            available_cols = [c for c in saved_cols if c in st.session_state.portfolio_alloc.columns]
            if available_cols:
                st.dataframe(
                    st.session_state.portfolio_alloc[available_cols].style.format({
                        "Ilość (ułamkowa)": "{:.4f}",
                        "Faktyczny portfel": "{:.2f}",
                        "Wartość pozycji": lambda x: f"{x:,.0f} {curr}"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    
    with col_right:
        st.markdown("### 📝 Konfiguracja pozycji")
        
        if st.session_state.show_tooltips:
            table_headers = ["Ticker", "Cena", "% Model", "Ilość (ułamkowa)", "Faktyczny portfel", "Wartość"]
            headers_html = " | ".join([tooltip_header(h) for h in table_headers])
            st.markdown(headers_html, unsafe_allow_html=True)
        
        if tickers_list:
            alloc_data = []
            df_tickers = df_all[df_all["Ticker"].isin(tickers_list)]
            
            for idx, row in df_tickers.iterrows():
                ticker = row["Ticker"]
                
                if alloc_method == "Wg wartości (%)":
                    pct = st.number_input(f"% — {ticker}", 0.0, 100.0, 5.0, step=0.5, key=f"pct_{ticker}")
                    value_model = (pct / 100) * st.session_state.paper_capital
                    qty_model = value_model / row["Price"]
                else:
                    qty_model = st.number_input(f"Ilość — {ticker}", 0.0, 10000.0, 10.0, step=0.5, key=f"qty_{ticker}")
                    value_model = qty_model * row["Price"]
                    pct = (value_model / st.session_state.paper_capital) * 100
                
                real_default = max(1, int(qty_model)) if qty_model >= 1 else round(qty_model * 4) / 4
                real_qty = st.number_input(f"Real — {ticker}", 0.0, 10000.0, real_default, step=1.0, key=f"real_{ticker}")
                
                value_real = real_qty * row["Price"]
                
                alloc_data.append({
                    "Ticker": ticker,
                    "Price": row["Price"],
                    "Model %": pct,
                    "Ilość (ułamkowa)": qty_model,
                    "Faktyczny portfel": real_qty,
                    "Wartość pozycji": value_model,
                    "Wartość realna": value_real,
                    "Różnica": real_qty - qty_model
                })
            
            df_alloc = pd.DataFrame(alloc_data)
            
            total_model = df_alloc["Wartość pozycji"].sum()
            total_real = df_alloc["Wartość realna"].sum()
            remaining_model = st.session_state.paper_capital - total_model
            remaining_real = st.session_state.paper_capital - total_real
            
            display_cols = ["Ticker", "Price", "Model %", "Ilość (ułamkowa)", "Faktyczny portfel", "Wartość pozycji"]
            st.dataframe(
                df_alloc[display_cols].style.format({
                    "Price": lambda x: f"{x:,.2f} {curr}",
                    "Model %": "{:.1f}%",
                    "Ilość (ułamkowa)": "{:.4f}",
                    "Faktyczny portfel": "{:.2f}",
                    "Wartość pozycji": lambda x: f"{x:,.0f} {curr}"
                }),
                use_container_width=True,
                hide_index=True
            )
            
            st.divider()
            
            cR1, cR2, cR3, cR4 = st.columns(4)
            cR1.metric("📊 Zaalokowano (model)", f"{total_model:,.0f} {curr}")
            cR2.metric("💵 Gotówka (model)", f"{remaining_model:,.0f} {curr}")
            cR3.metric("📊 Zaalokowano (real)", f"{total_real:,.0f} {curr}")
            cR4.metric("⚠️ Nadpłynięcie", "TAK" if remaining_real < 0 else "NIE")
            
            if st.button("💾 Zatwierdź portfel", type="primary"):
                st.session_state.portfolio_alloc = df_alloc.copy()
                st.session_state.portfolio_alloc["Data dodania"] = datetime.now().strftime("%Y-%m-%d")
                st.success("✅ Portfel zapisany!")
            
            if not df_alloc.empty:
                csv = df_alloc.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Eksportuj CSV", csv, f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

# ============================================================
# 📋 STOPKA
# ============================================================
st.markdown("---")
mode_label = 'Day Trade' if st.session_state.trader_mode == 'daily' else 'Swing/Monthly'
st.caption(f"🤖 AI Giełda Agent v2.1 | {mode_label} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
