import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 🎨 STYLIZACJA CSS
st.markdown("""
<style>
/* Tooltipy */
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

/* Wyrównanie tabel - środek dla kolumn poza pierwszą */
.stDataFrame table th:not(:first-child), .stDataFrame table td:not(:first-child) { text-align: center !important; }
.stDataFrame table th:first-child, .stDataFrame table td:first-child { text-align: left !important; }

/* Metric boxes */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #1e3a5f !important; font-size: 24px !important; }
[data-testid="stMetricDelta"] { color: #10b981 !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: #f1f5f9 !important; }

/* Buttons */
.stButton > button {
    background: #3b82f6 !important; color: white !important;
    border: none !important; border-radius: 6px !important;
    padding: 10px 20px !important; font-weight: 500 !important;
}
.stButton > button:hover { background: #2563eb !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #f1f5f9; border-radius: 8px 8px 0 0; gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: #e2e8f0; color: #64748b;
    border-radius: 6px 6px 0 0; padding: 10px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important; color: #3b82f6 !important; font-weight: 600;
}

/* Exchange badges */
.exchange-badge {
    display: inline-block; padding: 6px 14px; border-radius: 20px;
    font-size: 12px; font-weight: 600; margin: 4px 2px;
}
.exchange-wig20 { background: #dbeafe; color: #1e40af; }
.exchange-wig40 { background: #dcfce7; color: #166534; }
.exchange-wig80 { background: #fef3c7; color: #92400e; }
.exchange-ibkr { background: #e0e7ff; color: #4338ca; }

/* Tooltip legend */
.tooltip-legend {
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 8px; padding: 12px 16px; margin: 16px 0;
}
.tooltip-legend-title { color: #1e40af; font-weight: 600; font-size: 13px; margin-bottom: 10px; }
.tooltip-item {
    display: inline-block; background: #ffffff; border: 1px solid #dbeafe;
    border-radius: 6px; padding: 6px 10px; margin: 4px;
    font-size: 11px; color: #1e3a5f; cursor: help;
}
.tooltip-item:hover { background: #dbeafe; border-color: #3b82f6; }

/* Section headers */
.section-header {
    color: #1e3a5f; font-size: 18px; font-weight: 600;
    margin: 20px 0 12px 0; padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
}

/* Summary box */
.summary-box {
    background: #f1f5f9; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 16px; margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# 📖 LEGENDA WSKAŹNIKÓW
INDICATOR_DESC = {
    "Ticker": "Symbol giełdowy spółki",
    "Price": "Aktualna cena rynkowa akcji",
    "Target Price": "Średnia cena docelowa analityków",
    "Upside %": "Potencjał wzrostu do ceny docelowej (%)",
    "Market Cap": "Kapitalizacja rynkowa spółki",
    "Dividend Yield": "Roczna stopa dywidendy względem ceny (%)",
    "PE Ratio": "Cena / Zysk. <15 często uznawane za atrakcyjne",
    "PEG Ratio": "PE / Wzrost zysków. <1 sugeruje niedowycenienie",
    "Quick Ratio (Q)": "Płynność szybka. >1 = zdolność do spłaty zobowiązań",
    "Debt/Assets (Q)": "Zadłużenie/Aktywa. <0.5 = bezpieczny poziom",
    "Signal Score": "Wynik 0-1: BUY≥0.6, HOLD 0.3-0.6, SELL≤0.3",
    "Signal": "Sygnał: 🟢BUY 🟡HOLD 🔴SELL"
}

def tooltip_header(col):
    if col in INDICATOR_DESC:
        return f'<div class="tooltip-wrap">{col}<div class="tooltip-icon">i</div><div class="tooltip-text">{INDICATOR_DESC[col]}</div></div>'
    return col

def format_currency(val, curr="PLN"):
    if pd.isna(val): 
        return "-"
    return f"{val:,.0f} {curr}"

# 📊 DANE DLA INDEKSÓW
INDEX_TICKERS = {
    "WIG20": ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR"],
    "WIG40": ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR", "PLW.WAR", "CCC.WAR"],
    "WIG80": ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR", "PLW.WAR", "CCC.WAR", "ATA.WAR", "BDS.WAR"],
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
        
        sentiment = np.round(np.random.uniform(-0.4, 0.9), 2) if trade_mode == "daily" else np.round(np.random.uniform(-0.2, 0.6), 2)
            
        data.append({
            "Ticker": t, "Price": price, "Target Price": target,
            "Upside %": np.round((target/price - 1)*100, 2),
            "Market Cap": np.random.randint(2e9, 40e9),
            "Dividend Yield": np.round(np.random.uniform(0, 12), 2),
            "PE Ratio": np.round(np.random.uniform(6, 30), 2),
            "PEG Ratio": np.round(np.random.uniform(0.6, 2.8), 2),
            "Quick Ratio (Q)": np.round(np.random.uniform(0.4, 3.2), 2),
            "Debt/Assets (Q)": np.round(np.random.uniform(0.15, 0.75), 2),
            "Revenue (TTM)": np.random.randint(500e6, 25e9),
            "Free Cash Flow (TTM)": np.random.randint(-200e6, 4e9),
            "Net Income (TTM)": np.random.randint(-100e6, 3e9),
            "Sentiment": sentiment
        })
    
    df = pd.DataFrame(data)
    
    if trade_mode == "daily":
        df["Signal Score"] = (
            (df["PE Ratio"] < 18)*0.15 + (df["PEG Ratio"] < 1.0)*0.2 +
            (df["Dividend Yield"] > 2)*0.1 + (df["Quick Ratio (Q)"] > 0.8)*0.15 +
            (df["Upside %"] > 8)*0.25 + (df["Sentiment"] > 0.4)*0.15
        )
    else:
        df["Signal Score"] = (
            (df["PE Ratio"] < 15)*0.2 + (df["PEG Ratio"] < 1.2)*0.15 +
            (df["Dividend Yield"] > 3)*0.2 + (df["Quick Ratio (Q)"] > 1)*0.15 +
            (df["Upside %"] > 10)*0.2 + (df["Debt/Assets (Q)"] < 0.5)*0.1
        )
    
    df["Signal"] = df["Signal Score"].apply(lambda x: "🟢 BUY" if x >= 0.65 else ("🔴 SELL" if x <= 0.35 else "🟡 HOLD"))
    return df

# 💾 STAN APLIKACJI - z czyszczeniem starych danych
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
if "saved_portfolio_values" not in st.session_state:
    st.session_state.saved_portfolio_values = {}

# 🖥️ UI
st.set_page_config(page_title="🤖 AI Giełda Agent", layout="wide", page_icon="📈")

st.markdown("<h1 style='color: #1e3a5f; font-size: 28px; margin-bottom: 8px;'>🤖 AI Giełda Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 20px;'>Paper Trading | GPW & IBKR | Rebalans | Sygnały BUY/HOLD/SELL</p>", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("<h3 style='color: #1e3a5f; margin-bottom: 16px;'>⚙️ Konfiguracja</h3>", unsafe_allow_html=True)
    
    st.markdown("<p style='color: #64748b; font-size: 12px; font-weight: 600; margin-bottom: 8px;'>📍 Giełda / Indeks</p>", unsafe_allow_html=True)
    exchange = st.selectbox("Wybierz indeks", ["WIG20", "WIG40", "WIG80", "IBKR"],
        index=["WIG20", "WIG40", "WIG80", "IBKR"].index(st.session_state.exchange) if st.session_state.exchange in ["WIG20", "WIG40", "WIG80", "IBKR"] else 0,
        label_visibility="collapsed")
    st.session_state.exchange = exchange
    
    badge_class = f"exchange-{exchange.lower()}"
    st.markdown(f'<span class="exchange-badge {badge_class}">📊 {exchange}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("<p style='color: #64748b; font-size: 12px; font-weight: 600; margin-bottom: 8px;'>🎯 Strategia</p>", unsafe_allow_html=True)
    trade_mode = st.radio("Tryb", ["Daily Trade", "Monthly Trade"],
        index=0 if st.session_state.trade_mode == "daily" else 1, label_visibility="collapsed")
    st.session_state.trade_mode = "daily" if trade_mode == "Daily Trade" else "monthly"
    
    badge_text = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    badge_color = "#ef4444" if st.session_state.trade_mode == "daily" else "#10b981"
    st.markdown(f'<span style="background: {badge_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; display: inline-block; margin-top: 8px;">🔴 {badge_text}</span>', unsafe_allow_html=True)
    
    st.divider()
    curr = st.selectbox("💱 Waluta", ["PLN", "USD"], index=0)
    st.session_state.currency = curr
    
    st.divider()
    
    # Przycisk resetu sesji
    if st.button("🔄 Resetuj dane sesji", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.paper_capital = 100000.0
        st.session_state.currency = "PLN"
        st.session_state.exchange = "WIG20"
        st.session_state.trade_mode = "daily"
        st.rerun()
    
    mode_hint = "Szybkie momentum, sentyment" if st.session_state.trade_mode == "daily" else "Wartość, dywidendy"
    st.markdown(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-top: 10px;">
        <p style="color: #3b82f6; font-weight: 600; margin-bottom: 8px; font-size: 12px;">📖 Strategia: {badge_text}</p>
        <p style="color: #64748b; font-size: 11px; margin: 4px 0;">{mode_hint}</p>
    </div>
    """, unsafe_allow_html=True)

# Generuj dane
tickers = INDEX_TICKERS[st.session_state.exchange]
df_all = generate_mock_data(tickers, st.session_state.trade_mode)

cols_display = ["Ticker", "Price", "Target Price", "Upside %", "Market Cap", "Dividend Yield", 
                "PE Ratio", "PEG Ratio", "Quick Ratio (Q)", "Debt/Assets (Q)", "Signal", "Signal Score"]

# ✅ LEGENDA TOOLTIPÓW
def display_tooltip_legend():
    st.markdown("""
    <div class="tooltip-legend">
        <div class="tooltip-legend-title">📖 Legenda wskaźników (najedź myszką)</div>
        <div>
            <span class="tooltip-item" title="Aktualna cena">Price</span>
            <span class="tooltip-item" title="Potencjał wzrostu">Upside %</span>
            <span class="tooltip-item" title="Cena/Zysk">PE Ratio</span>
            <span class="tooltip-item" title="Dywidenda">Div Yield</span>
            <span class="tooltip-item" title="Płynność">Quick Ratio</span>
            <span class="tooltip-item" title="Wynik AI">Signal Score</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 📊 ZAKŁADKI
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Skaner", "📈 Sygnały", "💼 Paper Trading"])

# TAB 1: DASHBOARD
with tab1:
    mode_label = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    st.markdown(f"<h3 class='section-header'>📊 Dashboard — {mode_label} | {st.session_state.exchange}</h3>", unsafe_allow_html=True)
    display_tooltip_legend()
    
    if not st.session_state.portfolio_alloc.empty:
        # ✅ SPRAWDŹ CZY KOLUMNA "Wartość" ISTNIEJE
        if "Wartość" not in st.session_state.portfolio_alloc.columns:
            st.warning("⚠️ Stary format portfela. Zresetuj dane w sidebar lub zatwierdź portfel ponownie.")
            st.session_state.portfolio_alloc = pd.DataFrame()
        else:
            approved_tickers = st.session_state.portfolio_alloc["Ticker"].tolist()
            df_portfolio = df_all[df_all["Ticker"].isin(approved_tickers)]
            
            if not df_portfolio.empty:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("📈 Pozycji w portfelu", f"{len(df_portfolio)}")
                c2.metric("🟢 Śr. Signal Score", f"{df_portfolio['Signal Score'].mean():.2f}")
                c3.metric("📊 Śr. Upside", f"{df_portfolio['Upside %'].mean():.1f}%")
                c4.metric("💰 Zainwestowano", format_currency(st.session_state.portfolio_alloc["Wartość"].sum(), st.session_state.currency))
                
                st.markdown("<h4 style='color: #1e3a5f; margin-top: 24px;'>📦 Zatwierdzone Pozycje</h4>", unsafe_allow_html=True)
                
                df_display = df_portfolio.merge(
                    st.session_state.portfolio_alloc[["Ticker", "Ilość", "Wartość", "%"]],
                    on="Ticker", how="left")
                
                st.dataframe(df_display[["Ticker", "Price", "Ilość", "Wartość", "%", "Upside %", "Signal"]].style.format({
                    "Price": f"{{:,.2f}} {st.session_state.currency}",
                    "Ilość": "{:.2f}",
                    "Wartość": f"{{:,.0f}} {st.session_state.currency}",
                    "%": "{:.1f}%", "Upside %": "{:.1f}%"
                }), use_container_width=True, hide_index=True)
            else:
                st.info("⚠️ Brak zatwierdzonych pozycji. Dodaj w zakładce Paper Trading.")
    else:
        st.info("⚠️ Brak zatwierdzonych pozycji. Dodaj w zakładce Paper Trading.")

# TAB 2: SKANER
with tab2:
    st.markdown("<h3 class='section-header'>🔍 Zaawansowany Skaner</h3>", unsafe_allow_html=True)
    display_tooltip_legend()
    
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
            (df_all["PE Ratio"] <= pe_max) & (df_all["Dividend Yield"] >= dy_min) &
            (df_all["Upside %"] >= upside_min) & (df_all["Quick Ratio (Q)"] >= quick_min) &
            (df_all["Debt/Assets (Q)"] <= debt_max) & (df_all["Market Cap"] >= cap_min*1e9)
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
    display_tooltip_legend()
    
    sig_filter = st.radio("Filtr sygnałów", ["Wszystkie", "🟢 BUY", "🟡 HOLD", "🔴 SELL"], horizontal=True)
    df_sig = df_all[df_all["Signal"] == sig_filter] if sig_filter != "Wszystkie" else df_all
    
    headers_html = " | ".join([tooltip_header(c) for c in cols_display])
    st.markdown(headers_html, unsafe_allow_html=True)
    
    st.dataframe(df_sig[cols_display].style.format({
        "Price": f"{{:,.2f}} {st.session_state.currency}",
        "Target Price": f"{{:,.2f}} {st.session_state.currency}",
        "Upside %": "{:.2f}%",
        "Market Cap": lambda x: format_currency(x, st.session_state.currency),
        "Signal Score": "{:.2f}"
    }), use_container_width=True, hide_index=True)

# TAB 4: PAPER TRADING
with tab4:
    mode_label = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    st.markdown(f"<h3 class='section-header'>💼 Panel Paper Trading — {mode_label} | {st.session_state.exchange}</h3>", unsafe_allow_html=True)
    
    # === KAPITAŁ - EDYTOWALNY ===
    st.markdown("<div class='summary-box'>", unsafe_allow_html=True)
    col_cap1, col_cap2 = st.columns([1, 3])
    with col_cap1:
        st.session_state.paper_capital = st.number_input(
            "💰 Kapitał całkowity", 
            min_value=1000.0, 
            value=float(st.session_state.paper_capital), 
            step=1000.0,
            label_visibility="collapsed"
        )
    with col_cap2:
        st.markdown(f"<p style='color: #64748b; font-size: 13px; margin-top: 10px;'>💡 Edytuj kapitał bezpośrednio w polu powyżej</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # === WYBÓR WALORÓW ===
    default_tickers = st.session_state.portfolio_alloc["Ticker"].tolist() if not st.session_state.portfolio_alloc.empty else df_all["Ticker"].tolist()[:5]
    tickers_list = st.multiselect("📋 Wybierz walory do portfela", df_all["Ticker"].tolist(), default=default_tickers)
    
    if tickers_list:
        # === PRZYGOTOWANIE DANYCH ===
        df_tickers = df_all[df_all["Ticker"].isin(tickers_list)].copy()
        
        # Inicjalizacja danych do edycji
        if "portfolio_edit" not in st.session_state or len(st.session_state.portfolio_edit) != len(tickers_list):
            st.session_state.portfolio_edit = []
            for idx, row in df_tickers.iterrows():
                saved = st.session_state.saved_portfolio_values.get(row["Ticker"], {})
                default_pct = saved.get("pct", 5.0)
                default_qty = saved.get("model_qty", round((5.0/100 * st.session_state.paper_capital) / row["Price"], 2))
                st.session_state.portfolio_edit.append({
                    "Ticker": row["Ticker"],
                    "Cena": row["Price"],
                    "%": default_pct,
                    "Ilość": default_qty,
                    "Wartość": round(default_qty * row["Price"], 0),
                    "Upside %": row["Upside %"],
                    "Signal": row["Signal"]
                })
        
        # === EDYTOWALNA TABELA ===
        st.markdown("**📊 Konfiguracja pozycji**")
        
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.portfolio_edit),
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", disabled=True),
                "Cena": st.column_config.NumberColumn("Cena", format="%.2f", disabled=True),
                "%": st.column_config.NumberColumn("%", min_value=0.0, max_value=100.0, step=0.5),
                "Ilość": st.column_config.NumberColumn("Ilość", min_value=0.0, step=0.01),
                "Wartość": st.column_config.NumberColumn("Wartość", format="%.0f", disabled=True),
                "Upside %": st.column_config.NumberColumn("Upside %", format="%.1f%%", disabled=True),
                "Signal": st.column_config.TextColumn("Signal", disabled=True)
            },
            hide_index=True,
            use_container_width=True,
            key="portfolio_editor"
        )
        
        # === OBLICZANIE WARTOŚCI ===
        edited_df["Wartość"] = (edited_df["Ilość"] * edited_df["Cena"]).round(0)
        edited_df["%"] = ((edited_df["Wartość"] / st.session_state.paper_capital) * 100).round(1)
        
        # === PODSUMOWANIE ===
        st.divider()
        st.markdown("**📈 Podsumowanie**")
        
        total_invested = edited_df["Wartość"].sum()
        remaining = st.session_state.paper_capital - total_invested
        utilization = (total_invested / st.session_state.paper_capital) * 100 if st.session_state.paper_capital > 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📊 Zainwestowano", format_currency(total_invested, st.session_state.currency))
        c2.metric("💵 Pozostało", format_currency(remaining, st.session_state.currency), 
                 delta=f"{(remaining/st.session_state.paper_capital)*100:.1f}%" if remaining >= 0 else "⚠️ Nadpłynięcie")
        c3.metric("📈 Wykorzystanie", f"{utilization:.1f}%")
        c4.metric("📋 Pozycji", f"{len(edited_df)}")
        
        # === PRZYCISKI ===
        st.divider()
        c_btn1, c_btn2 = st.columns([1, 3])
        
        with c_btn1:
            if st.button("💾 Zatwierdź portfel", type="primary", use_container_width=True):
                # ✅ ZAPISZ Z UJEDNOLICONYMI NAZWAMI KOLUMN
                st.session_state.portfolio_alloc = edited_df[["Ticker", "Cena", "%", "Ilość", "Wartość", "Upside %", "Signal"]].copy()
                st.session_state.portfolio_alloc["Data dodania"] = datetime.now().strftime("%Y-%m-%d")
                
                for _, row in edited_df.iterrows():
                    st.session_state.saved_portfolio_values[row["Ticker"]] = {
                        "pct": row["%"],
                        "model_qty": row["Ilość"],
                        "real_qty": row["Ilość"]
                    }
                
                st.success("✅ Portfel zapisany! Sprawdź w Dashboard.")
                st.rerun()
        
        with c_btn2:
            if not edited_df.empty:
                csv = edited_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Eksportuj CSV", csv,
                    f"portfolio_{st.session_state.exchange}_{st.session_state.trade_mode}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv", use_container_width=True)
    else:
        st.info("👈 Wybierz walory z listy powyżej")

# Stopka
st.markdown("---")
st.caption("🤖 AI Giełda Agent | Dane testowe (symulacja) | To narzędzie analityczne, nie doradztwo inwestycyjne")
