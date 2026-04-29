import streamlit as st
import pandas as pd
import numpy as np
import requests
import yaml
from datetime import datetime

# Konfiguracja strony
st.set_page_config(page_title="🤖 AI Giełda Agent", layout="wide", page_icon="📈")

# Nagłówek
st.title("🤖 AI Giełda Agent")
st.markdown("*Analiza GPW + IBKR | Sygnały BUY/HOLD/SELL | Rebalans portfela*")

# Sidebar - konfiguracja
with st.sidebar:
    st.header("⚙️ Ustawienia")
    
    # Wybór rynku
    market = st.selectbox("Rynek", ["GPW - WIG20", "GPW - WIG40", "GPW - WIG80", "IBKR - US"])
    
    # Tryb pracy
    mode = st.radio("Tryb", ["📊 Podgląd", "🔄 Rebalans miesięczny", "⚡ Daily Trade"])
    
    # Filtry szybkie
    st.subheader("🔍 Filtry")
    min_cap = st.number_input("Min Market Cap (USD)", min_value=0, value=500_000_000, step=100_000_000)
    max_pe = st.number_input("Max P/E Ratio", min_value=1, value=30, step=1)
    min_dividend = st.number_input("Min Dividend Yield %", min_value=0.0, value=0.0, step=0.5)
    
    st.info("💡 Wskaźniki: PE<15 = tanio, DY>3% = dobra dywidenda, Quick>1 = płynność OK")

# Funkcja pobierania danych (symulacja - w produkcji: EODHD API)
@st.cache_data(ttl=3600)
def load_mock_data():
    """Generuje przykładowe dane GPW dla demonstracji"""
    tickers = ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR"]
    data = []
    for t in tickers:
        data.append({
            "Ticker": t,
            "Price": np.round(np.random.uniform(50, 300), 2),
            "Change_%": np.round(np.random.uniform(-5, 8), 2),
            "MarketCap_USD": np.random.randint(1_000_000_000, 50_000_000_000),
            "PE_Ratio": np.round(np.random.uniform(8, 25), 1),
            "PEG_Ratio": np.round(np.random.uniform(0.5, 2.5), 2),
            "Dividend_Yield": np.round(np.random.uniform(0, 8), 2),
            "Quick_Ratio": np.round(np.random.uniform(0.5, 3.0), 2),
            "Debt_to_Assets": np.round(np.random.uniform(0.2, 0.7), 2),
            "Revenue_TTM": np.random.randint(1_000_000_000, 30_000_000_000),
            "FCF_TTM": np.random.randint(-500_000_000, 5_000_000_000),
            "EPS_Growth_2Y": np.round(np.random.uniform(-5, 25), 1),
            "Analyst_Rating": np.random.choice(["Strong Buy", "Buy", "Hold", "Sell"], p=[0.15, 0.35, 0.4, 0.1]),
            "Sentiment_Score": np.round(np.random.uniform(-0.3, 0.8), 2),
        })
    df = pd.DataFrame(data)
    # Oblicz sygnał (uproszczona logika)
    df["Signal_Score"] = (
        (df["PE_Ratio"] < 15) * 0.2 +
        (df["PEG_Ratio"] < 1.2) * 0.2 +
        (df["Dividend_Yield"] > 3) * 0.15 +
        (df["Quick_Ratio"] > 1) * 0.15 +
        (df["Analyst_Rating"].isin(["Strong Buy", "Buy"])) * 0.2 +
        (df["Sentiment_Score"] > 0.3) * 0.1
    )
    df["Signal"] = df["Signal_Score"].apply(lambda x: "🟢 BUY" if x >= 0.6 else ("🔴 SELL" if x <= 0.3 else "🟡 HOLD"))
    return df

# Zakładki aplikacji
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Skaner", "📈 Sygnały", "💼 Portfel"])

# TAB 1: Dashboard
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📈 Aktywa w portfelu", "24/30")
    with col2: st.metric("🟢 Sygnały BUY dziś", "5")
    with col3: st.metric("📊 Średni Score", "0.64")
    with col4: st.metric("🔄 Ostatni rebalans", "2026-04-01")
    
    st.subheader("📉 Equity Curve (symulacja)")
    chart_data = pd.DataFrame({
        "Dzień": range(30),
        "Wartość portfela": 100000 + np.cumsum(np.random.normal(200, 800, 30))
    })
    st.line_chart(chart_data.set_index("Dzień"))
    
    st.subheader("🔥 Top Movers dziś")
    movers = load_mock_data().sort_values("Change_%", ascending=False).head(5)[["Ticker", "Price", "Change_%", "Signal"]]
    st.dataframe(movers, use_container_width=True, hide_index=True)

# TAB 2: Skaner
with tab2:
    st.subheader("🔍 Zaawansowany Skaner")
    
    # Filtry expandable
    with st.expander("🌍 Geografia i Giełdy", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            countries = st.multiselect("Kraje (Include)", ["PL", "US", "DE", "UK"], default=["PL"])
            exclude_countries = st.multiselect("Kraje (Exclude)", ["RU", "BY", "CN"])
        with col2:
            exchanges = st.multiselect("Giełdy", ["WAR", "NASDAQ", "NYSE", "XETRA"], default=["WAR"])
    
    with st.expander("🏭 Sektory i Branże"):
        sectors = st.multiselect("Sektory (Include)", ["Financials", "Technology", "Energy", "Healthcare"], default=["Financials"])
        exclude_sectors = st.multiselect("Sektory (Exclude)", ["Utilities", "Real Estate"])
    
    with st.expander("📊 Wskaźniki Fundamentalne"):
        col1, col2, col3 = st.columns(3)
        with col1:
            pe_min = st.number_input("P/E Min", 0, 100, 5)
            pe_max = st.number_input("P/E Max", 0, 100, 30)
        with col2:
            pb_min = st.number_input("P/B Min", 0.0, 20.0, 0.5)
            pb_max = st.number_input("P/B Max", 0.0, 20.0, 3.0)
        with col3:
            dy_min = st.number_input("Div Yield Min %", 0.0, 15.0, 2.0)
    
    if st.button("🔎 Uruchom Skaner", type="primary"):
        df = load_mock_data()
        # Aplikacja filtrów (przykład)
        filtered = df[
            (df["PE_Ratio"] >= pe_min) & (df["PE_Ratio"] <= pe_max) &
            (df["Dividend_Yield"] >= dy_min)
        ]
        st.success(f"Znaleziono {len(filtered)} spółek")
        st.dataframe(filtered, use_container_width=True, hide_index=True)

# TAB 3: Sygnały
with tab3:
    st.subheader("🎯 Dzisiejsze Sygnały")
    
    df = load_mock_data()
    
    # Filtr sygnałów
    signal_filter = st.radio("Pokaż", ["Wszystkie", "🟢 BUY", "🟡 HOLD", "🔴 SELL"], horizontal=True)
    if signal_filter != "Wszystkie":
        df = df[df["Signal"] == signal_filter]
    
    # Tabela sygnałów
    display_cols = ["Ticker", "Price", "Change_%", "PE_Ratio", "Dividend_Yield", "Analyst_Rating", "Sentiment_Score", "Signal", "Signal_Score"]
    st.dataframe(df[display_cols].sort_values("Signal_Score", ascending=False), use_container_width=True, hide_index=True)
    
    # Legenda wskaźników
    with st.expander("📚 Legenda wskaźników"):
        st.markdown("""
        | Wskaźnik | Opis |
        |----------|------|
        | **Price** | Aktualna cena rynkowa akcji |
        | **PE Ratio** | Cena / Zysk. <15 = potencjalnie tanio |
        | **PEG Ratio** | PE / Wzrost zysków. <1 = atrakcyjne względem wzrostu |
        | **Dividend Yield** | Roczna stopa dywidendy (%) |
        | **Quick Ratio** | Płynność szybka. >1 = dobra płynność |
        | **Debt to Assets** | Zadłużenie w aktywach. <0.5 = niskie ryzyko |
        | **Sentiment Score** | Analiza newsów: -1 (negatywny) do +1 (pozytywny) |
        | **Signal Score** | Kompozytowy wynik 0-1: BUY≥0.6, SELL≤0.3 |
        """)

# TAB 4: Portfel
with tab4:
    st.subheader("💼 Mój Portfel (max 30 aktywów)")
    
    # Symulacja portfela
    portfolio_data = pd.DataFrame({
        "Ticker": ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "CDR.WAR"] + [f"SYM{i}.WAR" for i in range(25)],
        "Waga %": [15, 12, 10, 8, 7] + [1]*25,
        "Sygnał": ["🟢 BUY", "🟡 HOLD", "🟢 BUY", "🔴 SELL", "🟡 HOLD"] + ["🟡 HOLD"]*25,
        "P&L %": np.round(np.random.uniform(-8, 15, 30), 2)
    })
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("📊 Wartość portfela", "$124,580")
        st.metric("📈 Dzisiejszy P&L", "+$1,240 (1.0%)")
        st.metric("🎯 Sharpe Ratio", "1.42")
        if st.button("🔄 Wykonaj Monthly Rebalance"):
            st.success("✅ Rebalans zakończony! Zaktualizowano wagi.")
    
    with col2:
        st.dataframe(portfolio_data, use_container_width=True, hide_index=True)
    
    # Eksport
    st.download_button(
        "📥 Pobierz portfel jako CSV",
        data=portfolio_data.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Stopka
st.markdown("---")
st.caption("🤖 AI Giełda Agent | Dane: EODHD (opóźnione) | To narzędzie analityczne, nie doradztwo inwestycyjne")
