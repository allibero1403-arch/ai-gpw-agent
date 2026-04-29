import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================
# 🎨 STYLIZACJA CSS: Tooltips + Wyrównanie tabel + Sidebar
# ============================================================
st.markdown("""
<style>
/* --- Tooltips --- */
.tooltip-wrap { position: relative; display: inline-flex; align-items: center; gap: 4px; cursor: pointer; }
.tooltip-icon { width: 16px; height: 16px; background: #3b82f6; color: white; border-radius: 50%; font-size: 10px; display: flex; align-items: center; justify-content: center; }
.tooltip-text {
    visibility: hidden; opacity: 0; width: 260px; background: #1e293b; color: #f8fafc;
    text-align: left; border-radius: 8px; padding: 8px 12px; position: absolute;
    z-index: 100; bottom: 110%; left: 50%; transform: translateX(-50%);
    font-size: 12px; line-height: 1.5; box-shadow: 0 6px 16px rgba(0,0,0,0.4);
    transition: all 0.25s ease; pointer-events: none;
}
.tooltip-wrap:hover .tooltip-text { visibility: visible; opacity: 1; bottom: 100%; }

/* --- Wyrównanie tabel (centrum dla wszystkich poza pierwszą kolumną) --- */
.stDataFrame table th:not(:first-child),
.stDataFrame table td:not(:first-child),
[data-testid="stTable"] table th:not(:first-child),
[data-testid="stTable"] table td:not(:first-child) { text-align: center !important; }
.stDataFrame table th:first-child,
.stDataFrame table td:first-child,
[data-testid="stTable"] table th:first-child,
[data-testid="stTable"] table td:first-child { text-align: left !important; }

/* --- Sidebar hint box --- */
.sidebar-hint {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
    border-radius: 10px; padding: 14px 16px; margin-top: 8px;
    border-left: 4px solid #3b82f6;
}
.sidebar-hint-title { color: #60a5fa; font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.sidebar-hint-item { color: #e2e8f0; font-size: 11px; padding: 3px 0; display: flex; gap: 6px; }
.sidebar-hint-item::before { content: "▸"; color: #3b82f6; }

/* --- Radio buttons poziome --- */
.stRadio [role="radiogroup"] { flex-direction: row !important; gap: 10px; }

/* --- Metric style --- */
[data-testid="stMetric"] { background: #1e293b; border-radius: 8px; padding: 10px; }

/* --- Tryb trader badge --- */
.trader-badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 12px; font-weight: 600;
}
.badge-daily { background: #059669; color: white; }
.badge-monthly { background: #7c3aed; color: white; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 📖 LEGENDA WSZYSTKICH WSKAŹNIKÓW
# ============================================================
INDICATOR_DESC = {
    "Ticker": "Symbol giełdowy spółki na GPW",
    "Price": "Aktualna cena rynkowa akcji (PLN)",
    "Target Price": "Średnia cena docelowa analityków (PLN)",
    "Upside %": "Potencjał wzrostu do ceny docelowej (%)",
    "Market Cap": "Kapitalizacja rynkowa spółki (PLN)",
    "Dividend Yield": "Roczna stopa dywidendy względem ceny (%)",
    "Revenue Est. Growth (2Y)": "Szacowany roczny wzrost przychodów (% rocznie, horyzont 2l)",
    "EPS Est. Growth (2Y)": "Szacowany roczny wzrost zysku na akcję (% rocznie, horyzont 2l)",
    "EPS Long-Term (5Y)": "Długoterminowy szacowany wzrost EPS (% rocznie, horyzont 5l)",
    "PS Ratio": "Cena / Przychody. Niższy → potencjalnie tańszy",
    "PE Ratio": "Cena / Zysk. <15 uznawane za atrakcyjne",
    "PEG Ratio": "PE / Wzrost zysków. <1 sugeruje niedowycenienie względem wzrostu",
    "Revenue (TTM)": "Przychody z ostatnich 12 miesięcy (PLN)",
    "Free Cash Flow (TTM)": "Gotówka po odliczeniu nakładów inwestycyjnych (PLN, 12m)",
    "Net Income (TTM)": "Zysk netto spółki (PLN, 12m)",
    "Debt/Assets (Q)": "Udział zadłużenia w aktywach (kwartalnie). <0.5 = bezpiecznie",
    "Quick Ratio (Q)": "Płynność szybka. >1 = zdolność do spłaty krótkich zobowiązań",
    "Analyst Rating": "Średnia ocena analityków (Strong Buy → Sell)",
    "Sentiment": "Nastroje rynkowe (-1 do +1)",
    "Signal": "Sygnał: 🟢 BUY / 🟡 HOLD / 🔴 SELL",
    "Signal Score": "Wynik kompozytowy 0-1: BUY≥0.6, HOLD 0.3-0.6, SELL≤0.3",
    "Ilość (ułamkowa)": "Ilość akcji w modelu (obsługuje ułamki)",
    "Faktyczny portfel": "Realna ilość akcji do wprowadzenia w brokerze (bez ułamków)"
}

def tooltip_header(col):
    """Zwraca nagłówek tabeli z hover-tooltip"""
    if col in INDICATOR_DESC:
        return f'<div class="tooltip-wrap">{col}<div class="tooltip-icon">i</div><div class="tooltip-text">{INDICATOR_DESC[col]}</div></div>'
    return col

def format_currency(val, curr="PLN"):
    """Formatuje liczbę z walutą i odstępami tysięcznymi"""
    if pd.isna(val): return "-"
    return f"{val:,.0f} {curr}"

# ============================================================
# 🔄 KONWERSJA HYBRYDOWA NAGŁÓWKÓW (HTML → tekst dla Table)
# ============================================================
def header_to_text(col):
    """Usuwa HTML z nagłówka dla native Table"""
    import re
    clean = re.sub(r'<[^>]+>', '', tooltip_header(col))
    return clean

# ============================================================
# 📊 GENERATOR DANYCH - OBA TRYBY
# ============================================================
@st.cache_data(ttl=3600)
def generate_mock_data(trader_mode="daily"):
    """Generuje pełny zestaw danych dla wybranego trybu tradera"""
    tickers = ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR",
               "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR",
               "PLW.WAR", "CCC.WAR", "CNT.WAR", "EUZ.WAR", "KRU.WAR"]
    data = []
    
    for t in tickers:
        price = np.round(np.random.uniform(20, 500), 2)
        target = price * np.round(np.random.uniform(0.80, 1.45), 2)
        
        # Różne zakresy dla trybów
        if trader_mode == "daily":
            upside_range = (-15, 35)
            pe_range = (5, 45)
            sentiment_range = (-0.5, 0.9)
            rev_growth = (-5, 30)
        else:  # monthly
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
    
    # === OBLICZENIE SIGNAL SCORE (zależne od trybu) ===
    if trader_mode == "daily":
        # Daily: krótkoterminowy - techniczne + momentum
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
        # Monthly: długoterminowy - wartość + dywidenda
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

if "real_portfolio" not in st.session_state:
    st.session_state.real_portfolio = {}

# ============================================================
# 🖥️ UI - STRONA GŁÓWNA
# ============================================================
st.set_page_config(
    page_title="🤖 AI Giełda Agent",
    layout="wide",
    page_icon="📈"
)

st.title("🤖 AI Giełda Agent")
st.markdown("*Paper Trading | GPW & IBKR | Rebalans | Sygnały AI*")

# ============================================================
# 📱 SIDEBAR - KONFIGURACJA
# ============================================================
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    
    # --- Tryb tradera ---
    st.markdown("**📊 Tryb tradera**")
    trader_mode = st.radio(
        "Wybierz horyzont czasowy",
        ["daily", "monthly"],
        index=0 if st.session_state.trader_mode == "daily" else 1,
        format_func=lambda x: "📈 Day Trade (intraday)" if x == "daily" else "📅 Swing/Monthly (długoterminowy)",
        help="Day Trade: krótkoterminowe momentum + techniczne\nMonthly: wartość + dywidenda + fundamenty"
    )
    st.session_state.trader_mode = trader_mode
    
    # Badge trybu
    badge_class = "badge-daily" if trader_mode == "daily" else "badge-monthly"
    st.markdown(f'<span class="trader-badge {badge_class}">Aktywny: {"Day Trade" if trader_mode == "daily" else "Swing/Monthly"}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # --- Waluta ---
    curr = st.selectbox("💱 Waluta raportowania", ["PLN", "USD"], index=0)
    st.session_state.currency = curr
    
    # --- Kapitał ---
    capital = st.number_input(
        "💰 Kapitał startowy (Paper)",
        min_value=1_000.0,
        value=st.session_state.paper_capital,
        step=5_000.0
    )
    st.session_state.paper_capital = capital
    
    st.divider()
    
    # --- Hint box (stylizowany) ---
    mode_hints = {
        "daily": "📊 Wskaźniki Day Trade: Momentum, Sentiment, Short-term Upside",
        "monthly": "📊 Wskaźniki Monthly: Wartość, Dywidenda, Długoterminowy Wzrost"
    }
    st.markdown(f"""
    <div class="sidebar-hint">
        <div class="sidebar-hint-title">📖 Legenda kluczowych wskaźników</div>
        <div class="sidebar-hint-item">PE < 15/20 → atrakcyjna wycena</div>
        <div class="sidebar-hint-item">DY > 3-4% → stabilna dywidenda</div>
        <div class="sidebar-hint-item">Quick > 1 → dobra płynność</div>
        <div class="sidebar-hint-item">Upside > 5-10% → potencjał wzrostu</div>
        <div class="sidebar-hint-item">Debt/Assets < 0.5 → niskie zadłużenie</div>
        <div class="sidebar-hint-item">Sentiment > 0.3 → pozytywne nastroje</div>
        <div class="sidebar-hint-item" style="margin-top:8px; color:#60a5fa;">{mode_hints[trader_mode]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.caption("🤖 AI Giełda Agent v2.0")

# ============================================================
# 📊 GENERUJ DANE DLA TRYBU
# ============================================================
df_all = generate_mock_data(st.session_state.trader_mode)

# Kolumny do wyświetlania (wspólne)
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
    st.subheader(f"📊 Dashboard — Tryb: {'Day Trade' if st.session_state.trader_mode == 'daily' else 'Swing/Monthly'}")
    
    # Metryki
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📈 Aktywa w portfelu", "20/30")
    col2.metric("🟢 Sygnały BUY", f"{len(df_all[df_all['Signal']=='🟢 BUY'])}")
    col3.metric("📊 Śr. Upside", f"{df_all['Upside %'].mean():.1f}%")
    col4.metric("🔄 Ostatni rebalans", datetime.now().strftime("%Y-%m-%d"))
    
    # Top Movers
    st.subheader("🔥 Top Movers (wg Upside %)")
    movers = df_all.sort_values("Upside %", ascending=False).head(5)
    
    # Nagłówki z tooltipami
    headers_html = " | ".join([tooltip_header(c) for c in COLS_DISPLAY])
    st.markdown(headers_html, unsafe_allow_html=True)
    
    # Tabela z formatowaniem
    st.dataframe(
        movers[COLS_DISPLAY].style.format({
            "Price": lambda x: f"{x:,.2f} {curr}",
            "Target Price": lambda x: f"{x:,.2f} {curr}",
            "Upside %": "{:.2f}%",
            "Market Cap": lambda x: format_currency(x, curr),
            "Revenue (TTM)": lambda x: format_currency(x, curr),
            "Free Cash Flow (TTM)": lambda x: format_currency(x, curr),
            "Net Income (TTM)": lambda x: format_currency(x, curr),
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
        st.success(f"Znaleziono {len(filt)} spółek spełniających kryteria")
        
        # Nagłówki z tooltipami
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
    st.subheader(f"🎯 Dzienna Lista Sygnałów — {('Day Trade' if st.session_state.trader_mode == 'daily' else 'Swing/Monthly')}")
    
    sig_filter = st.radio(
        "Filtr sygnałów",
        ["Wszystkie", "🟢 BUY", "🟡 HOLD", "🔴 SELL"],
        horizontal=True
    )
    df_sig = df_all[df_all["Signal"] == sig_filter] if sig_filter != "Wszystkie" else df_all
    
    # Nagłówki z tooltipami (JEDEN WIERZ ZA TABELĄ - info o hover)
    headers_html = " | ".join([tooltip_header(c) for c in COLS_DISPLAY])
    st.markdown(headers_html, unsafe_allow_html=True)
    
    st.dataframe(
        df_sig[COLS_DISPLAY].style.format({
            "Price": lambda x: f"{x:,.2f} {curr}",
            "Target Price": lambda x: f"{x:,.2f} {curr}",
            "Upside %": "{:.2f}%",
            "Market Cap": lambda x: format_currency(x, curr),
            "Revenue (TTM)": lambda x: format_currency(x, curr),
            "Free Cash Flow (TTM)": lambda x: format_currency(x, curr),
            "Net Income (TTM)": lambda x: format_currency(x, curr),
            "Signal Score": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Info o tooltipach
    st.caption("💡 Najedź na nagłówek kolumny, aby zobaczyć opis wskaźnika")

# ============================================================
# TAB 4: PAPER TRADING
# ============================================================
with tab4:
    st.subheader(f"💼 Panel Paper Trading — Tryb: {'Day Trade' if st.session_state.trader_mode == 'daily' else 'Swing/Monthly'}")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.metric("💰 Dostępny Kapitał", format_currency(st.session_state.paper_capital, curr))
        alloc_method = st.radio(
            "Metoda alokacji",
            ["Wg wartości (%)", "Wg ilości akcji (model)"]
        )
        tickers_list = st.multiselect(
            "Wybór walorów",
            df_all["Ticker"].tolist(),
            default=df_all["Ticker"].tolist()[:8]
        )
        
        # Pokaż zapisany portfel
        if not st.session_state.portfolio_alloc.empty:
            st.divider()
            st.markdown("**📁 Zapisany portfel:**")
            st.dataframe(
                st.session_state.portfolio_alloc[["Ticker", "Ilość (ułamkowa)", "Faktyczny portfel", "Wartość pozycji", "%"]].style.format({
                    "Ilość (ułamkowa)": "{:.4f}",
                    "Faktyczny portfel": "{:.4f}",
                    "Wartość pozycji": lambda x: f"{x:,.0f} {curr}",
                    "%": "{:.2f}%"
                }),
                use_container_width=True,
                hide_index=True
            )
    
    with col_right:
        st.markdown("### 📝 Konfiguracja pozycji")
        st.caption("Kolumna 'Faktyczny portfel' = realne wartości do wprowadzenia w brokerze")
        
        if tickers_list:
            alloc_data = []
            df_tickers = df_all[df_all["Ticker"].isin(tickers_list)]
            
            # Nagłówki tabeli z tooltipami
            table_headers = ["Ticker", "Cena", "Model %", "Ilość (ułamkowa)", "Faktyczny portfel", "Wartość model", "Wartość realna"]
            headers_html = " | ".join([tooltip_header(h) for h in table_headers])
            st.markdown(headers_html, unsafe_allow_html=True)
            
            # Przygotuj dane tabeli
            table_rows = []
            
            for idx, row in df_tickers.iterrows():
                ticker = row["Ticker"]
                
                if alloc_method == "Wg wartości (%)":
                    # Input procentowy
                    default_pct = 5.0
                    pct_key = f"pct_{ticker}"
                    pct = st.number_input(
                        f"% alokacji — {ticker}",
                        0.0, 100.0, default_pct, step=0.5,
                        key=pct_key
                    )
                    value_model = (pct / 100) * st.session_state.paper_capital
                    qty_model = value_model / row["Price"]
                else:
                    # Input ilości ułamkowej
                    default_qty = 10.0
                    qty_key = f"qty_{ticker}"
                    qty_model = st.number_input(
                        f"Ilość akcji (model) — {ticker}",
                        0.0, 10000.0, default_qty, step=0.5,
                        key=qty_key
                    )
                    value_model = qty_model * row["Price"]
                    pct = (value_model / st.session_state.paper_capital) * 100
                
                # FAKTYCZNY PORTFEL - input rzeczywisty (bez ułamków jeśli broker nie pozwala)
                real_qty_key = f"real_{ticker}"
                real_default = int(qty_model) if qty_model >= 1 else round(qty_model * 4) / 4  # kwarty akcji
                real_qty = st.number_input(
                    f"Faktyczny portfel — {ticker}",
                    0.0, 10000.0, real_default, step=0.25,
                    key=real_qty_key
                )
                
                value_real = real_qty * row["Price"]
                pct_real = (value_real / st.session_state.paper_capital) * 100
                
                # Różnica
                diff = real_qty - qty_model
                
                alloc_data.append({
                    "Ticker": ticker,
                    "Price": row["Price"],
                    "Model %": pct,
                    "Ilość (ułamkowa)": qty_model,
                    "Faktyczny portfel": real_qty,
                    "Wartość pozycji": value_model,
                    "Wartość realna": value_real,
                    "Różnica": diff,
                    "Upside %": row["Upside %"]
                })
            
            df_alloc = pd.DataFrame(alloc_data)
            
            # Sumy
            total_model = df_alloc["Wartość pozycji"].sum()
            total_real = df_alloc["Wartość realna"].sum()
            remaining_model = st.session_state.paper_capital - total_model
            remaining_real = st.session_state.paper_capital - total_real
            
            # Wyświetl tabelę z wyrównaniem
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
            
            # Metryki podsumowania
            cR1, cR2, cR3, cR4 = st.columns(4)
            cR1.metric("📊 Zaalokowano (model)", format_currency(total_model, curr))
            cR2.metric("💵 Gotówka (model)", format_currency(remaining_model, curr), 
                       delta=f"{(remaining_model/st.session_state.paper_capital)*100:.1f}%")
            cR3.metric("📊 Zaalokowano (real)", format_currency(total_real, curr))
            cR4.metric("⚠️ Nadpłynięcie", "TAK" if remaining_real < 0 else "NIE",
                       delta=f"{remaining_real:,.0f} {curr}")
            
            # Różnice
            st.markdown(f"**📐 Różnica między modelem a realnym portfelem:**")
            diff_col1, diff_col2 = st.columns(2)
            with diff_col1:
                st.metric("Różnica wartości", format_currency(total_real - total_model, curr),
                          delta=f"{(total_real - total_model)/st.session_state.paper_capital*100:.2f}%")
            with diff_col2:
                total_diff_qty = df_alloc["Różnica"].sum()
                st.metric("Różnica ilości akcji", f"{total_diff_qty:.2f} akcji")
            
            if st.button("💾 Zatwierdź portfel", type="primary"):
                st.session_state.portfolio_alloc = df_alloc.copy()
                st.session_state.portfolio_alloc["Data dodania"] = datetime.now().strftime("%Y-%m-%d")
                st.success("✅ Portfel zapisany! Śledź P&L w dashboardzie.")
            
            # Eksport CSV
            if not df_alloc.empty:
                csv = df_alloc.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Eksportuj do CSV",
                    csv,
                    f"portfolio_{st.session_state.trader_mode}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )

# ============================================================
# 📋 STOPKA
# ============================================================
st.markdown("---")
col_f1, col_f2 = st.columns([3, 1])
with col_f1:
    st.caption("🤖 AI Giełda Agent v2.0 | Dane testowe (symulacja) | Narzędzie analityczne, nie doradztwo inwestycyjne")
with col_f2:
    st.caption(f"Tryb: {'Day Trade' if st.session_state.trader_mode == 'daily' else 'Swing/Monthly'} | {datetime.now().strftime('%H:%M:%S')}")
