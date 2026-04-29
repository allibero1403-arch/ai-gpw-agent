import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================
# 🎨 STYLIZACJA CSS: Profesjonalny wygląd, Tooltips i Wyrównanie
# ============================================================
st.markdown("""
<style>
/* Tooltips: Stylizowane na małe etykiety pomocnicze */
.tooltip-wrap { 
    position: relative; 
    display: inline-flex; 
    align-items: center; 
    gap: 4px; 
    cursor: help; 
    font-size: 13px; 
    font-weight: 600;
    color: #cbd5e1;
}
.tooltip-icon { 
    width: 14px; height: 14px; 
    background: #3b82f6; color: white; 
    border-radius: 50%; font-size: 9px; 
    display: flex; align-items: center; justify-content: center; 
}
.tooltip-text {
    visibility: hidden; opacity: 0; width: 240px; 
    background: #0f172a; color: #f8fafc;
    text-align: left; border-radius: 6px; padding: 8px 10px; 
    position: absolute; z-index: 1000; bottom: 125%; left: 50%; 
    transform: translateX(-50%); font-size: 11px; line-height: 1.4; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    transition: all 0.2s ease; pointer-events: none;
    border: 1px solid #334155;
}
.tooltip-wrap:hover .tooltip-text { visibility: visible; opacity: 1; bottom: 100%; }

/* Wyrównanie tabel: Środek dla wszystkich poza pierwszą kolumną */
.stDataFrame table th:not(:first-child), .stDataFrame table td:not(:first-child) { text-align: center !important; }
.stDataFrame table th:first-child, .stDataFrame table td:first-child { text-align: left !important; }

/* Sidebar Hint Box - dopasowany do reszty UI */
.sidebar-hint {
    background: #1e293b; 
    border-radius: 8px; padding: 12px; 
    border-left: 4px solid #3b82f6;
    margin-bottom: 10px;
}
.sidebar-hint-text {
    font-size: 12px; color: #94a3b8; line-height: 1.5;
}

/* Styl dla etykiet trybu */
.mode-badge {
    padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;
}
.mode-daily { background: #ef4444; color: white; }
.mode-monthly { background: #10b981; color: white; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 📖 LEGENDA WSKAŹNIKÓW
# ============================================================
INDICATOR_DESC = {
    "Ticker": "Symbol giełdowy spółki",
    "Price": "Aktualna cena rynkowa",
    "Target Price": "Średnia cena docelowa analityków",
    "Upside %": "Potencjał wzrostu (%)",
    "Market Cap": "Kapitalizacja rynkowa",
    "Dividend Yield": "Stopa dywidendy (%)",
    "PE Ratio": "Cena / Zysk (Wycena)",
    "PEG Ratio": "PE / Wzrost (Wycena względem wzrostu)",
    "Quick Ratio (Q)": "Płynność szybka (>1 = bezpiecznie)",
    "Debt/Assets (Q)": "Zadłużenie do aktywów (<0.5 = bezpiecznie)",
    "Signal Score": "Wynik AI (0-1). BUY >= 0.6",
    "Signal": "Sygnał: 🟢Kupuj, 🟡Trzymaj, 🔴Sprzedaj",
    "Ilość (ułamkowa)": "Sugerowana ilość wg modelu AI",
    "Faktyczny portfel": "Realna ilość akcji wprowadzona do brokera"
}

def tooltip_header(col):
    """Zwraca nagłówek z hover-tooltipem"""
    if col in INDICATOR_DESC:
        return f'<div class="tooltip-wrap">{col}<div class="tooltip-icon">i</div><div class="tooltip-text">{INDICATOR_DESC[col]}</div></div>'
    return f'<div style="font-size:13px; font-weight:600; color:#cbd5e1;">{col}</div>'

def format_currency(val, curr="PLN"):
    if pd.isna(val): return "-"
    return f"{val:,.0f} {curr}"

# ============================================================
# 🤖 LOGIKA AGENTA: DAILY vs MONTHLY
# ============================================================
@st.cache_data(ttl=3600)
def generate_mock_data(mode="daily"):
    """Generuje dane zależnie od trybu tradingu"""
    tickers = ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR"]
    data = []
    for t in tickers:
        price = np.round(np.random.uniform(40, 350), 2)
        target = price * np.round(np.random.uniform(0.85, 1.35), 2)
        
        # Różnicowanie danych w zależności od trybu
        if mode == "daily":
            sentiment = np.round(np.random.uniform(-0.5, 1.0), 2)
            upside = np.round((target/price - 1)*100, 2)
            volatility = np.round(np.random.uniform(0.01, 0.05), 3)
        else:
            sentiment = np.round(np.random.uniform(-0.2, 0.6), 2)
            upside = np.round((target/price - 1)*100, 2)
            volatility = np.round(np.random.uniform(0.001, 0.02), 3)

        data.append({
            "Ticker": t, "Price": price, "Target Price": target, "Upside %": upside,
            "Market Cap": np.random.randint(2e9, 40e9),
            "Dividend Yield": np.round(np.random.uniform(0, 12), 2),
            "PE Ratio": np.round(np.random.uniform(6, 30), 2),
            "PEG Ratio": np.round(np.random.uniform(0.6, 2.8), 2),
            "Quick Ratio (Q)": np.round(np.random.uniform(0.4, 3.2), 2),
            "Debt/Assets (Q)": np.round(np.random.uniform(0.15, 0.75), 2),
            "Sentiment": sentiment,
            "Volatility": volatility
        })
    
    df = pd.DataFrame(data)
    
    # --- OBLICZENIE SCORE'A ZALEŻNIE OD TRYBU ---
    if mode == "daily":
        # Day Trade: Większa waga na Sentiment, Upside i Volatility
        df["Signal Score"] = (
            (df["Sentiment"] > 0.3)*0.3 + (df["Upside %"] > 5)*0.3 + (df["PEG Ratio"] < 1.2)*0.2 + (df["Quick Ratio (Q)"] > 1)*0.2
        )
    else:
        # Monthly Trade: Większa waga na PE, Dywidendy i Zadłużenie
        df["Signal Score"] = (
            (df["PE Ratio"] < 15)*0.3 + (df["Dividend Yield"] > 4)*0.3 + (df["Debt/Assets (Q)"] < 0.4)*0.2 + (df["Quick Ratio (Q)"] > 1)*0.2
        )
    
    df["Signal"] = df["Signal Score"].apply(lambda x: "🟢 BUY" if x >= 0.6 else ("🔴 SELL" if x <= 0.3 else "🟡 HOLD"))
    return df

# ============================================================
# 💾 STAN APLIKACJI
# ============================================================
if "paper_capital" not in st.session_state: st.session_state.paper_capital = 100_000.0
if "portfolio_alloc" not in st.session_state: st.session_state.portfolio_alloc = pd.DataFrame()
if "currency" not in st.session_state: st.session_state.currency = "PLN"
if "trade_mode" not in st.session_state: st.session_state.trade_mode = "daily"

# 🖥️ UI
st.set_page_config(page_title="🤖 AI Giełda Agent", layout="wide", page_icon="📈")
st.title("🤖 AI Giełda Agent")

# Sidebar
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    
    # Wybór trybu tradingu
    mode = st.radio("🎯 Strategia Agenta", ["Daily Trade", "Monthly Trade"], 
                    index=0 if st.session_state.trade_mode == "daily" else 1)
    st.session_state.trade_mode = "daily" if mode == "Daily Trade" else "monthly"
    
    curr = st.selectbox("Waluta raportowania", ["PLN", "USD"], index=0)
    st.session_state.currency = curr
    
    capital = st.number_input("💰 Kapitał startowy", min_value=1_000.0, value=100_000.0, step=5_000.0)
    st.session_state.paper_capital = capital
    
    st.divider()
    st.markdown(f"""
    <div class="sidebar-hint">
        <div style="font-weight:bold; color:white; margin-bottom:5px; font-size:13px;">💡 Hint Strategii:</div>
        <div class="sidebar-hint-text">
            {"Szybkie momentum, analiza sentymentu i krótkoterminowy Upside." if st.session_state.trade_mode == "daily" else "Analiza wartości, dywidendy i stabilność finansowa."}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Pobieranie danych dla wybranego trybu
df_all = generate_mock_data(st.session_state.trade_mode)
cols_display = ["Ticker", "Price", "Target Price", "Upside %", "Market Cap", "Dividend Yield", 
                "PE Ratio", "PEG Ratio", "Quick Ratio (Q)", "Debt/Assets (Q)", "Signal", "Signal Score"]

# 📊 ZAKŁADKI
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Skaner", "📈 Sygnały", "💼 Paper Trading"])

# TAB 1: DASHBOARD
with tab1:
    mode_badge = '<span class="mode-badge mode-daily">Day Trade</span>' if st.session_state.trade_mode == "daily" else '<span class="mode-badge mode-monthly">Monthly Trade</span>'
    st.markdown(f"### Dashboard {mode_badge}", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📈 Aktywa w portfelu", "20/30")
    c2.metric("🟢 Sygnały BUY", f"{len(df_all[df_all['Signal']=='🟢 BUY'])}")
    c3.metric("📊 Śr. Upside", f"{df_all['Upside %'].mean():.1f}%")
    c4.metric("🔄 Ostatni rebalans", datetime.now().strftime("%Y-%m-%d"))
    
    st.subheader("🔥 Top Movers")
    movers = df_all.sort_values("Upside %", ascending=False).head(5)
    
    # Nagłówki z tooltipami (Wiersz 1)
    headers_html = " ".join([tooltip_header(c) for c in cols_display])
    st.markdown(f'<div style="display:flex; justify-content:space-between; margin-bottom:0px; padding-left:10px;">{headers_html}</div>', unsafe_allow_html=True)
    
    st.dataframe(movers[cols_display].style.format({
        "Price": f"{{:,.2f}} {curr}", "Target Price": f"{{:,.2f}} {curr}", "Upside %": "{:.2f}%",
        "Market Cap": lambda x: format_currency(x, curr), "Signal Score": "{:.2f}"
    }), use_container_width=True, hide_index=True)

# TAB 2: SKANER
with tab2:
    st.subheader("🔍 Zaawansowany Skaner")
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
        
        headers_html = " ".join([tooltip_header(c) for c in cols_display])
        st.markdown(f'<div style="display:flex; justify-content:space-between; margin-bottom:0px; padding-left:10px;">{headers_html}</div>', unsafe_allow_html=True)
        
        st.dataframe(filt[cols_display].style.format({
            "Price": f"{{:,.2f}} {curr}", "Target Price": f"{{:,.2f}} {curr}", "Upside %": "{:.2f}%",
            "Market Cap": lambda x: format_currency(x, curr), "Signal Score": "{:.2f}"
        }), use_container_width=True, hide_index=True)

# TAB 3: SYGNAŁY
with tab3:
    st.subheader("🎯 Lista Sygnałów")
    sig_filter = st.radio("Filtr sygnałów", ["Wszystkie", "🟢 BUY", "🟡 HOLD", "🔴 SELL"], horizontal=True)
    df_sig = df_all[df_all["Signal"] == sig_filter] if sig_filter != "Wszystkie" else df_all
    
    headers_html = " ".join([tooltip_header(c) for c in cols_display])
    st.markdown(f'<div style="display:flex; justify-content:space-between; margin-bottom:0px; padding-left:10px;">{headers_html}</div>', unsafe_allow_html=True)
    
    st.dataframe(df_sig[cols_display].style.format({
        "Price": f"{{:,.2f}} {curr}", "Target Price": f"{{:,.2f}} {curr}", "Upside %": "{:.2f}%",
        "Market Cap": lambda x: format_currency(x, curr), "Signal Score": "{:.2f}"
    }), use_container_width=True, hide_index=True)

# TAB 4: PAPER TRADING
with tab4:
    st.subheader("💼 Panel Paper Trading")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("💰 Dostępny Kapitał", format_currency(st.session_state.paper_capital, curr))
        alloc_method = st.radio("Metoda alokacji", ["Wg wartości (%)", "Wg ilości akcji"])
        tickers_list = st.multiselect("Wybór walorów", df_all["Ticker"].tolist(), default=df_all["Ticker"].tolist()[:5])
        
    with c2:
        st.markdown("📝 Konfiguracja pozycji: **Model AI vs Realny Portfel**")
        if tickers_list:
            alloc_data = []
            df_tickers = df_all[df_all["Ticker"].isin(tickers_list)]
            
            for idx, row in df_tickers.iterrows():
                cA, cB, cC, cD = st.columns([2, 2, 2, 2])
                with cA:
                    st.markdown(f"**{row['Ticker']}**")
                with cB:
                    if alloc_method == "Wg wartości (%)":
                        pct = st.number_input(f"Model %", 0.0, 100.0, 5.0, step=1.0, key=f"pct_{row['Ticker']}")
                        model_value = (pct/100) * st.session_state.paper_capital
                        model_qty = model_value / row["Price"]
                    else:
                        model_qty = st.number_input(f"Model Ilość", 0.0, 10000.0, 10.0, step=0.5, key=f"qty_{row['Ticker']}")
                        model_value = model_qty * row["Price"]
                        pct = (model_value / st.session_state.paper_capital) * 100
                with cC:
                    # FAKTYCZNY PORTFEL - tutaj użytkownik wpisuje realną liczbę akcji
                    real_qty = st.number_input(f"Real Ilość", 0.0, 10000.0, round(model_qty, 2), step=1.0, key=f"real_{row['Ticker']}")
                with cD:
                    real_value = real_qty * row["Price"]
                    st.metric("Real Value", format_currency(real_value, curr))
                
                alloc_data.append({
                    "Ticker": row["Ticker"], 
                    "Price": row["Price"], 
                    "% Model": pct, 
                    "Ilość (ułamkowa)": model_qty, 
                    "Faktyczny portfel": real_qty, 
                    "Wartość Realna": real_value
                })
            
            df_alloc = pd.DataFrame(alloc_data)
            total_real_alloc = df_alloc["Wartość Realna"].sum()
            remaining = st.session_state.paper_capital - total_real_alloc
            
            st.divider()
            cR1, cR2, cR3 = st.columns(3)
            cR1.metric("📊 Zaalokowano (Real)", format_currency(total_real_alloc, curr))
            cR2.metric("💵 Gotówka", format_currency(remaining, curr), delta=f"{(remaining/st.session_state.paper_capital)*100:.1f}%")
            cR3.metric("⚠️ Nadpłynięcie", "TAK" if remaining < 0 else "NIE", delta=f"{remaining:,.0f} {curr}")
            
            if st.button("💾 Zatwierdź portfel", type="primary"):
                st.session_state.portfolio_alloc = df_alloc
                st.success("✅ Portfel realny zapisany!")
            
            st.dataframe(df_alloc.style.format({
                "Price": f"{{:,.2f}} {curr}", "Ilość (ułamkowa)": "{:.4f}", 
                "Faktyczny portfel": "{:.2f}", "Wartość Realna": f"{{:,.2f}} {curr}", "% Model": "{:.2f}%"
            }), use_container_width=True, hide_index=True)

# Stopka
st.markdown("---")
st.caption("🤖 AI Giełda Agent | System Hybrydowy (Model $\rightarrow$ Real) | Dane testowe")
