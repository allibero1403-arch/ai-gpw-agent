import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 🎨 STYLIZACJA CSS: Tooltips + Wyśrodkowanie tabel
st.markdown("""
<style>
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
/* Wyrównanie tabeli: środek dla wszystkich kolumn poza pierwszą */
.stDataFrame table th:not(:first-child), .stDataFrame table td:not(:first-child) { text-align: center !important; }
.stDataFrame table th:first-child, .stDataFrame table td:first-child { text-align: left !important; }
</style>
""", unsafe_allow_html=True)

# 📖 LEGENDA WS KAŹNIKÓW (do tooltipów)
INDICATOR_DESC = {
    "Price": "Aktualna cena rynkowa akcji",
    "Target Price": "Średnia cena docelowa analityków",
    "Upside %": "Potencjał wzrostu do ceny docelowej (%)",
    "Market Cap": "Kapitalizacja rynkowa spółki",
    "Dividend Yield": "Roczna stopa dywidendy względem ceny (%)",
    "Revenue Est. Growth (2Y)": "Szacowany roczny wzrost przychodów (2 lata)",
    "EPS Est. Growth (2Y)": "Szacowany roczny wzrost zysku/akcję (2 lata)",
    "EPS Long-Term (5Y)": "Długoterminowy szacowany wzrost EPS (5 lat)",
    "PS Ratio": "Cena / Przychody. Niższy = potencjalnie tańszy",
    "PE Ratio": "Cena / Zysk. <15 często uznawane za atrakcyjne",
    "PEG Ratio": "PE / Wzrost zysków. <1 sugeruje niedowycenienie względem wzrostu",
    "Revenue (TTM)": "Przychody z ostatnich 12 miesięcy",
    "Free Cash Flow (TTM)": "Gotówka po odliczeniu nakładów inwestycyjnych (12m)",
    "Net Income (TTM)": "Zysk netto spółki (12m)",
    "Debt/Assets (Q)": "Udział zadłużenia w aktywach (kwartalnie). <0.5 = bezpiecznie",
    "Quick Ratio (Q)": "Płynność szybka. >1 oznacza zdolność do spłaty krótkich zobowiązań",
    "Signal Score": "Wynik kompozytowy 0-1: BUY≥0.6, HOLD 0.3-0.6, SELL≤0.3"
}

def tooltip_header(col):
    """Zwraca nagłówek z hover-tooltipe"""
    if col in INDICATOR_DESC:
        return f'<div class="tooltip-wrap">{col}<div class="tooltip-icon">i</div><div class="tooltip-text">{INDICATOR_DESC[col]}</div></div>'
    return col

def format_currency(val, curr="PLN"):
    """Formatuje liczbę z walutą i odstępami tysięcznymi"""
    if pd.isna(val): return "-"
    return f"{val:,.0f} {curr}"

@st.cache_data(ttl=3600)
def generate_mock_data():
    """Generuje pełny zestaw danych z wszystkimi wskaźnikami"""
    tickers = ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR"]
    data = []
    for t in tickers:
        price = np.round(np.random.uniform(40, 350), 2)
        target = price * np.round(np.random.uniform(0.85, 1.35), 2)
        data.append({
            "Ticker": t, "Price": price, "Target Price": target, "Upside %": np.round((target/price - 1)*100, 2),
            "Market Cap": np.random.randint(2e9, 40e9),
            "Dividend Yield": np.round(np.random.uniform(0, 12), 2),
            "Revenue Est. Growth (2Y)": np.round(np.random.uniform(-2, 20), 2),
            "EPS Est. Growth (2Y)": np.round(np.random.uniform(-3, 25), 2),
            "EPS Long-Term (5Y)": np.round(np.random.uniform(0, 18), 2),
            "PS Ratio": np.round(np.random.uniform(0.8, 6.0), 2),
            "PE Ratio": np.round(np.random.uniform(6, 30), 2),
            "PEG Ratio": np.round(np.random.uniform(0.6, 2.8), 2),
            "Revenue (TTM)": np.random.randint(500e6, 25e9),
            "Free Cash Flow (TTM)": np.random.randint(-200e6, 4e9),
            "Net Income (TTM)": np.random.randint(-100e6, 3e9),
            "Debt/Assets (Q)": np.round(np.random.uniform(0.15, 0.75), 2),
            "Quick Ratio (Q)": np.round(np.random.uniform(0.4, 3.2), 2),
            "Analyst Rating": np.random.choice(["Strong Buy", "Buy", "Hold", "Sell"], p=[0.15, 0.35, 0.4, 0.1]),
            "Sentiment": np.round(np.random.uniform(-0.4, 0.8), 2)
        })
    df = pd.DataFrame(data)
    # Oblicz Score
    df["Signal Score"] = (
        (df["PE Ratio"] < 15)*0.2 + (df["PEG Ratio"] < 1.2)*0.2 + (df["Dividend Yield"] > 3)*0.15 +
        (df["Quick Ratio (Q)"] > 1)*0.15 + (df["Upside %"] > 10)*0.15 + (df["Sentiment"] > 0.3)*0.15
    )
    df["Signal"] = df["Signal Score"].apply(lambda x: "🟢 BUY" if x >= 0.65 else ("🔴 SELL" if x <= 0.35 else "🟡 HOLD"))
    return df

# 💾 STAN APLIKACJI
if "paper_capital" not in st.session_state: st.session_state.paper_capital = 100_000.0
if "portfolio_alloc" not in st.session_state: st.session_state.portfolio_alloc = pd.DataFrame()
if "currency" not in st.session_state: st.session_state.currency = "PLN"

# 🖥️ UI
st.set_page_config(page_title="🤖 AI Giełda Agent", layout="wide", page_icon="📈")
st.title("🤖 AI Giełda Agent")
st.markdown("*Paper Trading | GPW & IBKR | Rebalans | Sygnały BUY/HOLD/SELL*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    curr = st.selectbox("Waluta raportowania", ["PLN", "USD"], index=0)
    st.session_state.currency = curr
    capital = st.number_input("💰 Kapitał startowy (Paper Trade)", min_value=1_000.0, value=100_000.0, step=5_000.0)
    st.session_state.paper_capital = capital
    st.divider()
    st.info("📊 Wskaźniki: PE<15 = tanio | DY>3% = dywidenda | Quick>1 = płynność | Upside>10% = potencjał")

df_all = generate_mock_data()
cols_display = ["Ticker", "Price", "Target Price", "Upside %", "Market Cap", "Dividend Yield", 
                "PE Ratio", "PEG Ratio", "Quick Ratio (Q)", "Debt/Assets (Q)", "Revenue (TTM)", 
                "Free Cash Flow (TTM)", "Net Income (TTM)", "Signal", "Signal Score"]

# 📊 ZAKŁADKI
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Skaner", "📈 Sygnały", "💼 Paper Trading"])

# TAB 1: DASHBOARD
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📈 Aktywa w portfelu", "20/30")
    c2.metric("🟢 Sygnały BUY", f"{len(df_all[df_all['Signal']=='🟢 BUY'])}")
    c3.metric("📊 Śr. Upside", f"{df_all['Upside %'].mean():.1f}%")
    c4.metric("🔄 Ostatni rebalans", "2026-04-28")
    
    st.subheader("🔥 Top Movers")
    movers = df_all.sort_values("Upside %", ascending=False).head(5)
    st.dataframe(movers[cols_display].style.format({
        "Price": f"{{:,.2f}} {curr}", "Target Price": f"{{:,.2f}} {curr}", "Upside %": "{:.2f}%",
        "Market Cap": lambda x: format_currency(x, curr), "Revenue (TTM)": lambda x: format_currency(x, curr),
        "Free Cash Flow (TTM)": lambda x: format_currency(x, curr), "Net Income (TTM)": lambda x: format_currency(x, curr),
        "Signal Score": "{:.2f}"
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
        styled = filt[cols_display].style.format({
            "Price": f"{{:,.2f}} {curr}", "Target Price": f"{{:,.2f}} {curr}", "Upside %": "{:.2f}%",
            "Market Cap": lambda x: format_currency(x, curr), "Revenue (TTM)": lambda x: format_currency(x, curr),
            "Free Cash Flow (TTM)": lambda x: format_currency(x, curr), "Net Income (TTM)": lambda x: format_currency(x, curr),
            "Signal Score": "{:.2f}"
        })
        st.dataframe(styled, use_container_width=True, hide_index=True)

# TAB 3: SYGNAŁY
with tab3:
    st.subheader("🎯 Dzienna Lista Sygnałów")
    sig_filter = st.radio("Filtr sygnałów", ["Wszystkie", "🟢 BUY", "🟡 HOLD", "🔴 SELL"], horizontal=True)
    df_sig = df_all[df_all["Signal"] == sig_filter] if sig_filter != "Wszystkie" else df_all
    
    # Tooltip headers
    headers_html = " | ".join([tooltip_header(c) for c in cols_display])
    st.markdown(headers_html, unsafe_allow_html=True)
    
    styled_sig = df_sig[cols_display].style.format({
        "Price": f"{{:,.2f}} {curr}", "Target Price": f"{{:,.2f}} {curr}", "Upside %": "{:.2f}%",
        "Market Cap": lambda x: format_currency(x, curr), "Revenue (TTM)": lambda x: format_currency(x, curr),
        "Free Cash Flow (TTM)": lambda x: format_currency(x, curr), "Net Income (TTM)": lambda x: format_currency(x, curr),
        "Signal Score": "{:.2f}"
    })
    st.dataframe(styled_sig, use_container_width=True, hide_index=True)

# TAB 4: PAPER TRADING
with tab4:
    st.subheader("💼 Panel Paper Trading")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("💰 Dostępny Kapitał", format_currency(st.session_state.paper_capital, curr))
        alloc_method = st.radio("Metoda alokacji", ["Wg wartości (%)", "Wg ilości akcji"])
        tickers_list = st.multiselect("Wybór walorów", df_all["Ticker"].tolist(), default=df_all["Ticker"].tolist()[:20])
        
    with c2:
        st.markdown("📝 Konfiguracja pozycji (obsługa ułamków)")
        if tickers_list:
            alloc_data = []
            df_tickers = df_all[df_all["Ticker"].isin(tickers_list)]
            
            for idx, row in df_tickers.iterrows():
                cA, cB, cC = st.columns([3, 2, 2])
                with cA:
                    st.markdown(f"**{row['Ticker']}** | Cena: {row['Price']:,.2f} {curr} | Upside: {row['Upside %']:.1f}%")
                with cB:
                    if alloc_method == "Wg wartości (%)":
                        pct = st.number_input(f"% alokacji", 0.0, 100.0, 5.0, step=1.0, key=f"pct_{row['Ticker']}")
                        value = (pct/100) * st.session_state.paper_capital
                        qty = value / row["Price"]
                    else:
                        qty = st.number_input(f"Ilość akcji", 0.0, 10000.0, 10.0, step=0.5, key=f"qty_{row['Ticker']}")
                        value = qty * row["Price"]
                        pct = (value / st.session_state.paper_capital) * 100
                    alloc_data.append({"Ticker": row["Ticker"], "Price": row["Price"], "%": pct, 
                                       "Ilość (ułamkowa)": qty, "Wartość pozycji": value})
                with cC:
                    st.metric(f"Wartość", format_currency(value, curr))
            
            df_alloc = pd.DataFrame(alloc_data)
            total_alloc = df_alloc["Wartość pozycji"].sum()
            remaining = st.session_state.paper_capital - total_alloc
            
            st.divider()
            cR1, cR2, cR3 = st.columns(3)
            cR1.metric("📊 Zaalokowano", format_currency(total_alloc, curr))
            cR2.metric("💵 Gotówka", format_currency(remaining, curr), delta=f"{(remaining/st.session_state.paper_capital)*100:.1f}%")
            cR3.metric("⚠️ Nadpłynięcie", "TAK" if remaining < 0 else "NIE", delta=f"{remaining:,.0f} {curr}")
            
            if st.button("💾 Zatwierdź portfel", type="primary"):
                st.session_state.portfolio_alloc = df_alloc
                st.session_state.portfolio_alloc["Data dodania"] = datetime.now().strftime("%Y-%m-%d")
                st.success("✅ Portfel zapisany w sesji! Możesz teraz śledzić P&L w dashboardzie.")
            
            st.dataframe(df_alloc.style.format({"Price": f"{{:,.2f}} {curr}", "Ilość (ułamkowa)": "{:.4f}", "Wartość pozycji": f"{{:,.2f}} {curr}", "%": "{:.2f}%"}), use_container_width=True, hide_index=True)

# Stopka
st.markdown("---")
st.caption("🤖 AI Giełda Agent | Dane testowe (symulacja) | To narzędzie analityczne, nie doradztwo inwestycyjne")
