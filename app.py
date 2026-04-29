import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 🎨 STYLIZACJA CSS: Tooltips + Wyśrodkowanie tabel + Sidebar
st.markdown("""
<style>
.tooltip-wrap { 
    position: relative; 
    display: inline-flex; 
    align-items: center; 
    gap: 4px; 
    cursor: pointer; 
}
.tooltip-icon { 
    width: 16px; 
    height: 16px; 
    background: #3b82f6; 
    color: white; 
    border-radius: 50%; 
    font-size: 10px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
}
.tooltip-text {
    visibility: hidden; 
    opacity: 0; 
    width: 260px; 
    background: #1e293b; 
    color: #f8fafc;
    text-align: left; 
    border-radius: 8px; 
    padding: 8px 12px; 
    position: absolute;
    z-index: 100; 
    bottom: 110%; 
    left: 50%; 
    transform: translateX(-50%);
    font-size: 12px; 
    line-height: 1.5; 
    box-shadow: 0 6px 16px rgba(0,0,0,0.4);
    transition: all 0.25s ease; 
    pointer-events: none;
}
.tooltip-wrap:hover .tooltip-text { 
    visibility: visible; 
    opacity: 1; 
    bottom: 100%; 
}

/* Wyrównanie tabeli: środek dla wszystkich kolumn poza pierwszą */
.stDataFrame table th:not(:first-child), 
.stDataFrame table td:not(:first-child),
[data-testid="stTable"] th:not(:first-child),
[data-testid="stTable"] td:not(:first-child) { 
    text-align: center !important; 
}
.stDataFrame table th:first-child, 
.stDataFrame table td:first-child,
[data-testid="stTable"] th:first-child,
[data-testid="stTable"] td:first-child { 
    text-align: left !important; 
}

/* Styl dla sidebar hint */
.sidebar-hint {
    background: #1e293b;
    color: #f8fafc;
    border-radius: 8px;
    padding: 12px;
    margin-top: 10px;
    border-left: 4px solid #3b82f6;
}
.sidebar-hint-title {
    font-weight: bold;
    margin-bottom: 8px;
    color: #3b82f6;
}

/* Styl dla etykiet trybu */
.mode-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 10px;
}
.mode-daily {
    background: #ef4444;
    color: white;
}
.mode-monthly {
    background: #10b981;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# 📖 LEGENDA WSKAŹNIKÓW (do tooltipów)
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
    "Signal Score": "Wynik kompozytowy 0-1: BUY≥0.6, HOLD 0.3-0.6, SELL≤0.3",
    "Ilość (ułamkowa)": "Proponowana ilość akcji według modelu (może zawierać ułamki)",
    "Faktyczny portfel": "Rzeczywista ilość akcji do wprowadzenia u brokera (bez ułamków)"
}

def tooltip_header(col):
    """Zwraca nagłówek z hover-tooltipem"""
    if col in INDICATOR_DESC:
        return f'<div class="tooltip-wrap">{col}<div class="tooltip-icon">i</div><div class="tooltip-text">{INDICATOR_DESC[col]}</div></div>'
    return col

def format_currency(val, curr="PLN"):
    """Formatuje liczbę z walutą i odstępami tysięcznymi"""
    if pd.isna(val): 
        return "-"
    return f"{val:,.0f} {curr}"

@st.cache_data(ttl=3600)
def generate_mock_data(trade_mode="daily"):
    """Generuje pełny zestaw danych zależnie od trybu tradingu"""
    tickers = ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR"]
    data = []
    for t in tickers:
        price = np.round(np.random.uniform(40, 350), 2)
        target = price * np.round(np.random.uniform(0.85, 1.35), 2)
        
        # Różne parametry w zależności od trybu
        if trade_mode == "daily":
            # Większa zmienność dla day tradingu
            sentiment = np.round(np.random.uniform(-0.4, 0.9), 2)
        else:
            # Mniejsza zmienność dla monthly tradingu
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
    
    # Oblicz Score zależnie od trybu
    if trade_mode == "daily":
        # Day trading: większy nacisk na krótkoterminowe wskaźniki
        df["Signal Score"] = (
            (df["PE Ratio"] < 18) * 0.15 + 
            (df["PEG Ratio"] < 1.0) * 0.2 + 
            (df["Dividend Yield"] > 2) * 0.1 +
            (df["Quick Ratio (Q)"] > 0.8) * 0.15 + 
            (df["Upside %"] > 8) * 0.25 + 
            (df["Sentiment"] > 0.4) * 0.15
        )
    else:
        # Monthly trading: większy nacisk na długoterminowe wskaźniki
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

# 🖥️ UI
st.set_page_config(page_title="🤖 AI Giełda Agent", layout="wide", page_icon="📈")
st.title("🤖 AI Giełda Agent")
st.markdown("*Paper Trading | GPW & IBKR | Rebalans | Sygnały BUY/HOLD/SELL*")

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    
    # Wybór trybu tradingu
    trade_mode = st.radio("🎯 Strategia Agenta", ["Daily Trade", "Monthly Trade"], 
                         index=0 if st.session_state.trade_mode == "daily" else 1)
    st.session_state.trade_mode = "daily" if trade_mode == "Daily Trade" else "monthly"
    
    # Badge trybu
    badge_class = "mode-daily" if st.session_state.trade_mode == "daily" else "mode-monthly"
    badge_text = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    st.markdown(f'<span class="mode-badge {badge_class}">🔴 {badge_text}</span>', unsafe_allow_html=True)
    
    curr = st.selectbox("💱 Waluta raportowania", ["PLN", "USD"], index=0)
    st.session_state.currency = curr
    
    capital = st.number_input("💰 Kapitał startowy", min_value=1000.0, value=100000.0, step=5000.0)
    st.session_state.paper_capital = capital
    
    st.divider()
    
    # Hint w formie podobnej do reszty UI
    mode_hint = "Szybkie momentum, analiza sentymentu i krótkoterminowy Upside" if st.session_state.trade_mode == "daily" else "Analiza wartości, dywidendy i stabilność finansowa"
    st.markdown(f"""
    <div class="sidebar-hint">
        <div class="sidebar-hint-title">📖 Strategia: {badge_text}</div>
        <div>{mode_hint}</div>
        <div>PE&lt;15 = tanio | DY&gt;3% = dywidenda</div>
        <div>Quick&gt;1 = płynność | Upside&gt;10% = potencjał</div>
    </div>
    """, unsafe_allow_html=True)

# Generuj dane zależnie od trybu
df_all = generate_mock_data(st.session_state.trade_mode)
cols_display = ["Ticker", "Price", "Target Price", "Upside %", "Market Cap", "Dividend Yield", 
                "PE Ratio", "PEG Ratio", "Quick Ratio (Q)", "Debt/Assets (Q)", "Signal", "Signal Score"]

# 📊 ZAKŁADKI
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Skaner", "📈 Sygnały", "💼 Paper Trading"])

# TAB 1: DASHBOARD
with tab1:
    mode_label = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    st.subheader(f"📊 Dashboard — {mode_label}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📈 Aktywa w portfelu", "20/30")
    c2.metric("🟢 Sygnały BUY", f"{len(df_all[df_all['Signal']=='🟢 BUY'])}")
    c3.metric("📊 Śr. Upside", f"{df_all['Upside %'].mean():.1f}%")
    c4.metric("🔄 Ostatni rebalans", datetime.now().strftime("%Y-%m-%d"))
    
    st.subheader("🔥 Top Movers")
    movers = df_all.sort_values("Upside %", ascending=False).head(5)
    
    # Nagłówki z tooltipami w pierwszym wierszu
    headers_html = "".join([f'<th style="text-align:{"left" if i==0 else "center"}">{tooltip_header(col)}</th>' 
                           for i, col in enumerate(cols_display)])
    st.markdown(f"""
    <table style="width:100%; border-collapse: collapse; margin-bottom: 0;">
        <thead>
            <tr>{headers_html}</tr>
        </thead>
    </table>
    """, unsafe_allow_html=True)
    
    st.dataframe(movers[cols_display].style.format({
        "Price": f"{{:,.2f}} {st.session_state.currency}", 
        "Target Price": f"{{:,.2f}} {st.session_state.currency}", 
        "Upside %": "{:.2f}%",
        "Market Cap": lambda x: format_currency(x, st.session_state.currency), 
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
            (df_all["PE Ratio"] <= pe_max) & 
            (df_all["Dividend Yield"] >= dy_min) &
            (df_all["Upside %"] >= upside_min) & 
            (df_all["Quick Ratio (Q)"] >= quick_min) &
            (df_all["Debt/Assets (Q)"] <= debt_max) & 
            (df_all["Market Cap"] >= cap_min*1e9)
        ]
        st.success(f"Znaleziono {len(filt)} spółek")
        
        # Nagłówki z tooltipami w pierwszym wierszu
        headers_html = "".join([f'<th style="text-align:{"left" if i==0 else "center"}">{tooltip_header(col)}</th>' 
                               for i, col in enumerate(cols_display)])
        st.markdown(f"""
        <table style="width:100%; border-collapse: collapse; margin-bottom: 0;">
            <thead>
                <tr>{headers_html}</tr>
            </thead>
        </table>
        """, unsafe_allow_html=True)
        
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
    st.subheader(f"🎯 Lista Sygnałów — {mode_label}")
    
    sig_filter = st.radio("Filtr sygnałów", ["Wszystkie", "🟢 BUY", "🟡 HOLD", "🔴 SELL"], horizontal=True)
    df_sig = df_all[df_all["Signal"] == sig_filter] if sig_filter != "Wszystkie" else df_all
    
    # Nagłówki z tooltipami w pierwszym wierszu
    headers_html = "".join([f'<th style="text-align:{"left" if i==0 else "center"}">{tooltip_header(col)}</th>' 
                           for i, col in enumerate(cols_display)])
    st.markdown(f"""
    <table style="width:100%; border-collapse: collapse; margin-bottom: 0;">
        <thead>
            <tr>{headers_html}</tr>
        </thead>
    </table>
    """, unsafe_allow_html=True)
    
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
    st.subheader(f"💼 Panel Paper Trading — {mode_label}")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.metric("💰 Dostępny Kapitał", format_currency(st.session_state.paper_capital, st.session_state.currency))
        alloc_method = st.radio("Metoda alokacji", ["Wg wartości (%)", "Wg ilości akcji"])
        tickers_list = st.multiselect("Wybór walorów", df_all["Ticker"].tolist(), default=df_all["Ticker"].tolist()[:5])
        
    with col_right:
        st.markdown("📝 Konfiguracja pozycji: **Model AI vs Realny Portfel**")
        if tickers_list:
            alloc_data = []
            df_tickers = df_all[df_all["Ticker"].isin(tickers_list)]
            
            for idx, row in df_tickers.iterrows():
                cA, cB, cC, cD = st.columns([3, 2, 2, 2])
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
                    # FAKTYCZNY PORTFEL - użytkownik wprowadza rzeczywistą liczbę akcji
                    real_qty = st.number_input(f"Real Ilość", 0.0, 10000.0, round(model_qty), step=1.0, key=f"real_{row['Ticker']}")
                    real_value = real_qty * row["Price"]
                with cD:
                    st.metric("Real Value", format_currency(real_value, st.session_state.currency))
                
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
            
            # Wyświetl tabelę z odpowiednim wyrównaniem
            display_cols = ["Ticker", "Price", "% Model", "Ilość (ułamkowa)", "Faktyczny portfel", "Wartość Realna"]
            st.dataframe(
                df_alloc[display_cols].style.format({
                    "Price": f"{{:,.2f}} {st.session_state.currency}", 
                    "Ilość (ułamkowa)": "{:.4f}", 
                    "Faktyczny portfel": "{:.2f}",
                    "Wartość Realna": f"{{:,.2f}} {st.session_state.currency}", 
                    "% Model": "{:.2f}%"
                }), 
                use_container_width=True, 
                hide_index=True
            )
            
            st.divider()
            
            # Podsumowanie alokacji
            cR1, cR2, cR3, cR4 = st.columns(4)
            cR1.metric("📊 Zaalokowano (Real)", format_currency(total_real_alloc, st.session_state.currency))
            cR2.metric("💵 Gotówka", format_currency(remaining, st.session_state.currency), 
                       delta=f"{(remaining/st.session_state.paper_capital)*100:.1f}%")
            cR3.metric("📊 Zaalokowano (Model)", format_currency(df_alloc["Ilość (ułamkowa)"].sum() * df_alloc["Price"].mean(), st.session_state.currency))
            cR4.metric("⚠️ Nadpłynięcie", "TAK" if remaining < 0 else "NIE", 
                       delta=f"{remaining:,.0f} {st.session_state.currency}")
            
            if st.button("💾 Zatwierdź portfel", type="primary"):
                st.session_state.portfolio_alloc = df_alloc
                st.session_state.portfolio_alloc["Data dodania"] = datetime.now().strftime("%Y-%m-%d")
                st.success("✅ Portfel zapisany! Śledź P&L w dashboardzie.")
            
            # Eksport do CSV
            if not df_alloc.empty:
                csv = df_alloc.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Eksportuj do CSV",
                    csv,
                    f"portfolio_{st.session_state.trade_mode}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )

# Stopka
st.markdown("---")
st.caption("🤖 AI Giełda Agent | System Hybrydowy (Model → Real) | Dane testowe (symulacja) | To narzędzie analityczne, nie doradztwo inwestycyjne")
