import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 🎨 STYLIZACJA CSS + JavaScript dla tooltipów
st.markdown("""
<style>
/* Tooltip na nagłówkach tabel */
[data-testid="stDataFrame"] table th,
[data-testid="stTable"] table th {
    position: relative;
    cursor: help;
    color: #f8fafc !important;
    border-bottom: 1px dotted #3b82f6 !important;
}

[data-testid="stDataFrame"] table th:hover,
[data-testid="stTable"] table th:hover {
    color: #3b82f6 !important;
}

/* Tooltip content */
.th-tooltip-box {
    visibility: hidden;
    opacity: 0;
    width: 200px;
    background: #0f172a;
    color: #f8fafc;
    text-align: center;
    border-radius: 6px;
    padding: 6px 10px;
    position: absolute;
    z-index: 1000;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    font-size: 11px;
    line-height: 1.3;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    transition: all 0.2s ease;
    pointer-events: none;
    border: 1px solid #334155;
}

[data-testid="stDataFrame"] table th:hover .th-tooltip-box,
[data-testid="stTable"] table th:hover .th-tooltip-box {
    visibility: visible;
    opacity: 1;
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

/* Paper Trading - wyrównany layout */
.pt-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 8px;
    border-bottom: 1px solid #334155;
    gap: 8px;
}
.pt-row:last-child {
    border-bottom: none;
}
.pt-col {
    flex: 1;
    text-align: center;
    padding: 4px;
}
.pt-col:first-child {
    text-align: left;
    flex: 1.5;
}
.pt-label {
    font-size: 11px;
    color: #94a3b8;
    margin-bottom: 4px;
}
.pt-value {
    font-size: 13px;
    color: #f8fafc;
    font-weight: 600;
}
.pt-input {
    width: 100%;
}

/* Sidebar hint */
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

/* Mode badge */
.mode-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 10px;
}
.mode-daily { background: #ef4444; color: white; }
.mode-monthly { background: #10b981; color: white; }
</style>

<script>
// JavaScript do dodania tooltipów
function addTableTooltips() {
    const tooltips = {
        'Ticker': 'Symbol giełdowy spółki',
        'Price': 'Aktualna cena rynkowa akcji',
        'Target Price': 'Średnia cena docelowa analityków',
        'Upside %': 'Potencjał wzrostu (%)',
        'Market Cap': 'Kapitalizacja rynkowa',
        'Dividend Yield': 'Stopa dywidendy (%)',
        'PE Ratio': 'Cena/Zysk (<15 = tanio)',
        'PEG Ratio': 'PE/Wzrost (<1 = niedowyceniony)',
        'Quick Ratio (Q)': 'Płynność szybka (>1 = OK)',
        'Debt/Assets (Q)': 'Zadłużenie/Aktywa (<0.5 = bezpiecznie)',
        'Signal Score': 'Wynik AI (0-1). BUY≥0.6',
        'Signal': 'Sygnał: BUY/HOLD/SELL',
        'Cena': 'Cena pojedynczej akcji',
        '% Model': 'Procent alokacji wg modelu AI',
        'Ilość (ułamkowa)': 'Sugerowana ilość z modelu',
        'Faktyczny portfel': 'Realna ilość do brokera',
        'Wartość Realna': 'Rzeczywista wartość pozycji'
    };
    
    document.querySelectorAll('[data-testid="stDataFrame"] table th, [data-testid="stTable"] table th').forEach(function(th) {
        const text = th.textContent.trim().split('\\n')[0];
        if (tooltips[text] && !th.querySelector('.th-tooltip-box')) {
            const tooltip = document.createElement('span');
            tooltip.className = 'th-tooltip-box';
            tooltip.textContent = tooltips[text];
            th.appendChild(tooltip);
        }
    });
}

// Uruchom po załadowaniu i przy zmianach
document.addEventListener('DOMContentLoaded', addTableTooltips);
setTimeout(addTableTooltips, 500);
setTimeout(addTableTooltips, 1500);
</script>
""", unsafe_allow_html=True)

# 📖 LEGENDA WSKAŹNIKÓW
INDICATOR_DESC = {
    "Ticker": "Symbol giełdowy spółki",
    "Price": "Aktualna cena rynkowa akcji",
    "Target Price": "Średnia cena docelowa analityków",
    "Upside %": "Potencjał wzrostu (%)",
    "Market Cap": "Kapitalizacja rynkowa",
    "Dividend Yield": "Stopa dywidendy (%)",
    "PE Ratio": "Cena/Zysk (<15 = tanio)",
    "PEG Ratio": "PE/Wzrost (<1 = niedowyceniony)",
    "Quick Ratio (Q)": "Płynność szybka (>1 = OK)",
    "Debt/Assets (Q)": "Zadłużenie/Aktywa (<0.5 = bezpiecznie)",
    "Signal Score": "Wynik AI (0-1)",
    "Signal": "Sygnał: BUY/HOLD/SELL",
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

@st.cache_data(ttl=3600)
def generate_mock_data(trade_mode="daily"):
    tickers = ["PKO.WAR", "PEO.WAR", "PZU.WAR", "KGH.WAR", "LTS.WAR", "CDR.WAR", "DNP.WAR", "ALR.WAR", "JSW.WAR", "MBK.WAR"]
    data = []
    for t in tickers:
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

# 🖥️ UI
st.set_page_config(page_title="🤖 AI Giełda Agent", layout="wide", page_icon="📈")
st.title("🤖 AI Giełda Agent")
st.markdown("*Paper Trading | GPW & IBKR | Rebalans | Sygnały BUY/HOLD/SELL*")

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    
    trade_mode = st.radio("🎯 Strategia Agenta", ["Daily Trade", "Monthly Trade"], 
                         index=0 if st.session_state.trade_mode == "daily" else 1)
    st.session_state.trade_mode = "daily" if trade_mode == "Daily Trade" else "monthly"
    
    badge_class = "mode-daily" if st.session_state.trade_mode == "daily" else "mode-monthly"
    badge_text = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    st.markdown(f'<span class="mode-badge {badge_class}">🔴 {badge_text}</span>', unsafe_allow_html=True)
    
    curr = st.selectbox("💱 Waluta raportowania", ["PLN", "USD"], index=0)
    st.session_state.currency = curr
    
    capital = st.number_input("💰 Kapitał startowy", min_value=1000.0, value=100000.0, step=5000.0)
    st.session_state.paper_capital = capital
    
    st.divider()
    
    mode_hint = "Szybkie momentum, analiza sentymentu" if st.session_state.trade_mode == "daily" else "Wartość, dywidendy, stabilność"
    st.markdown(f"""
    <div class="sidebar-hint">
        <div class="sidebar-hint-title">📖 Strategia: {badge_text}</div>
        <div>{mode_hint}</div>
        <div style="margin-top:6px;font-size:11px;color:#94a3b8;">PE&lt;15 | DY&gt;3% | Quick&gt;1 | Upside&gt;10%</div>
    </div>
    """, unsafe_allow_html=True)

# Generuj dane
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
    
    st.dataframe(df_sig[cols_display].style.format({
        "Price": f"{{:,.2f}} {st.session_state.currency}", 
        "Target Price": f"{{:,.2f}} {st.session_state.currency}", 
        "Upside %": "{:.2f}%",
        "Market Cap": lambda x: format_currency(x, st.session_state.currency), 
        "Signal Score": "{:.2f}"
    }), use_container_width=True, hide_index=True)

# TAB 4: PAPER TRADING - POPRAWIONY LAYOUT
with tab4:
    mode_label = "Day Trade" if st.session_state.trade_mode == "daily" else "Swing/Monthly"
    st.subheader(f"💼 Panel Paper Trading — {mode_label}")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.metric("💰 Dostępny Kapitał", format_currency(st.session_state.paper_capital, st.session_state.currency))
        alloc_method = st.radio("Metoda alokacji", ["Wg wartości (%)", "Wg ilości akcji"])
        tickers_list = st.multiselect("Wybór walorów", df_all["Ticker"].tolist(), default=df_all["Ticker"].tolist()[:5])
        
    with col_right:
        st.markdown("📝 Konfiguracja pozycji")
        st.caption("💡 Ułamkowe części akcji dozwolone (2 miejsca po przecinku)")
        
        if tickers_list:
            alloc_data = []
            df_tickers = df_all[df_all["Ticker"].isin(tickers_list)]
            
            # ✅ NAGŁÓWEK TABELI
            st.markdown("""
            <div class="pt-row" style="background:#1e293b;border-radius:6px 6px 0 0;font-weight:bold;">
                <div class="pt-col" style="text-align:left;flex:1.5;">Ticker</div>
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
                    pct_key = f"pct_{idx}_{row['Ticker']}"
                    pct = st.session_state.get(pct_key, 5.0)
                    pct = st.number_input("Model %", 0.0, 100.0, pct, step=1.0, key=pct_key, label_visibility="collapsed")
                    model_value = (pct/100) * st.session_state.paper_capital
                    model_qty = model_value / row["Price"]
                else:
                    qty_key = f"qty_{idx}_{row['Ticker']}"
                    model_qty = st.session_state.get(qty_key, 10.0)
                    model_qty = st.number_input("Model szt.", 0.0, 10000.0, model_qty, step=0.5, key=qty_key, label_visibility="collapsed")
                    model_value = model_qty * row["Price"]
                    pct = (model_value / st.session_state.paper_capital) * 100
                
                # Faktyczny portfel
                real_key = f"real_{idx}_{row['Ticker']}"
                real_qty = st.session_state.get(real_key, round(model_qty, 2))
                real_qty = st.number_input("Faktyczny", 0.0, 10000.0, float(round(model_qty, 2)), step=0.01, key=real_key, label_visibility="collapsed")
                real_value = real_qty * row["Price"]
                
                # ✅ SPÓJNY WIERZ - wszystkie kolumny jako markdown
                st.markdown(f"""
                <div class="pt-row" style="background:#0f172a;border-radius:0;">
                    <div class="pt-col" style="text-align:left;flex:1.5;"><b>{row['Ticker']}</b></div>
                    <div class="pt-col"><span class="pt-value">{row['Price']:,.2f}</span><br><span class="pt-label">{st.session_state.currency}</span></div>
                    <div class="pt-col"><span class="pt-value">{pct:.1f}%</span></div>
                    <div class="pt-col"><span class="pt-value">{model_qty:.2f}</span><br><span class="pt-label">szt</span></div>
                    <div class="pt-col"><span class="pt-value" style="color:#3b82f6;">{real_qty:.2f}</span><br><span class="pt-label">szt</span></div>
                    <div class="pt-col"><span class="pt-value">{real_value:,.0f}</span><br><span class="pt-label">{st.session_state.currency}</span></div>
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
                    f"portfolio_{st.session_state.trade_mode}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )

# Stopka
st.markdown("---")
st.caption("🤖 AI Giełda Agent | Dane testowe (symulacja) | To narzędzie analityczne, nie doradztwo inwestycyjne")

# ✅ Refresh tooltipów po renderowaniu
st.experimental_rerun = False
