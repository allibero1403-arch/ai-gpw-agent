import streamlit as st
import pandas as pd
import numpy.random as np # Do generowania danych demo

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Pro Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- 1. KOMPLETNY STYL CSS (Klucz do sukcesu) ---
st.markdown("""
<style>
    /* Import czcionki dla profesjonalnego wyglądu */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Stylizacja kontenerów metryk (górny pasek) */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e6e9ef;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        text-align: center;
    }
    .metric-card .label {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
    }

    /* --- KLUCZOWA STRUKTURA TABELI (GRID) --- */
    
    /* Definicja kolumn - musi być identyczna w Header i w Row */
    /* Podział: Ticker(1.5) | Price(1) | Model%(1.5) | ModelQty(1) | ResQty(1) | Exit(1.5) | Status(1.5) */
    .grid-container {
        display: grid;
        grid-template-columns: 1.5fr 1fr 1.5fr 1fr 1fr 1.5fr 1.5fr;
        gap: 10px;
        align-items: center;
    }

    /* Styl nagłówka */
    .trading-header {
        display: grid;
        grid-template-columns: 1.5fr 1fr 1.5fr 1fr 1fr 1.5fr 1.5fr;
        gap: 10px;
        padding: 12px 15px;
        background-color: #f3f4f6;
        border-radius: 8px 8px 0 0;
        font-weight: 700;
        font-size: 0.75rem;
        color: #4b5563;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Styl wiersza danych */
    .trading-row {
        display: grid;
        grid-template-columns: 1.5fr 1fr 1.5fr 1fr 1fr 1.5fr 1.5fr;
        gap: 10px;
        padding: 15px;
        background-color: #ffffff;
        border-bottom: 1px solid #f0f0f0;
        align-items: center;
        transition: background-color 0.2s ease;
    }

    .trading-row:hover {
        background-color: #f8f9fa;
    }

    /* Styl komórek (Label + Value) */
    .cell-group {
        display: flex;
        flex-direction: column;
    }

    .cell-label {
        font-size: 0.7rem;
        color: #9ca3af;
        text-transform: uppercase;
        font-weight: 600;
    }

    .cell-value {
        font-size: 0.95rem;
                font-weight: 500;
        color: #1f2937;
    }

    /* Kolory statusów */
    .text-up { color: #10b981; font-weight: 600; }
    .text-down { color: #ef4444; font-weight: 600; }
    .text-neutral { color: #6b7280; }

</style>

"""

# --- LOGIKA APLIKACJI ---

def main():
    st.title("🚀 ProTrader Dashboard")
    st.markdown("---")

    # 1. Sekcja Dashboardu (Podsumowanie)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Equity", "$45,230.00", "+1.2%")
    with col2:
        st.metric("Daily PnL", "$420.50", "+0.8%")
    with col3:
        st.metric("Open Positions", "12", "0")
    with col4:
        st.metric("Buying Power", "$12,000", "-2.4%")

    st.markdown("### 📊 Active Trades & Portfolio")

    # 2. Przygotowanie danych (Symulacja bazy danych)
    # W realnej aplikacji to byłoby: df = pd.read_sql(...)
    trades_data = [
        {"symbol": "AAPL", "price": 189.45, "change": 1.2, "qty": 50, "target": 200.0, "stop": 185.0, "status": "long"},
        {"symbol": "TSLA", "price": 175.20, "change": -3.5, "qty": 20, "target": 190.0, "stop": 170.0, "status": "long"},
        {"symbol": "NVDA", "price": 880.12, "change": 4.8, "qty": 15, "target": 950.0, "stop": 850.0, "status": "long"},
        {"symbol": "MSFT", "price": 415.50, "change": 0.2, "qty": 30, "target": 430.0, "stop": 405.0, "status": "long"},
        {"symbol": "AMD", "price": 170.33, "change": -1.1, "qty": 100, "target": 190.0, "stop": 160.0, "status": "short"},
    ]

    # 3. Budowanie Tabeli HTML
    # Zaczynamy nagłówek tabeli
    table_html = """
    <div style="border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
        <div style="background-color: #f8f9fa; padding: 10px; font-weight: bold; border-bottom: 2px solid #eee;">
            Live Trading Monitor
        </div>
    """
    
    # Nagłówek kolumn (Wizualny tylko dla użytkownika, w HTML robimy to przez cell-label)
    # Budujemy wiersze danych
    for trade in trades_data:
        # Logika kolorów
        change_class = "text-up" if trade['change'] > 0 else "text-margin"
        change_class = "text-up" if trade['change'] > 0 else "text-down"
        
        # Budowanie wiersza
        row = f"""
        <div class="trading-row">
            <div class="cell-group">
                <span class="cell-label">Asset</span>
                <span class="cell-value" style="font-weight:bold;">{trade['symbol']}</span>
            </div>
            <div class="cell-group">
                <span class="cell-label">Price</span>
                <span class="cell-value">${trade['price']:.2f}</span>
            </div>
            <div class="cell-group">
                <span class="cell-label">24h Change</span>
                <span class="cell-value {change_class}">{trade['change']:+.2f}%</span>
            </div>
            <div class="cell-group">
                <span class="cell-label">Quantity</span>
                <span class="cell-value">{trade['qty']}</span>
            </div>
            <div class="cell-group">
                <span class="cell-label">Target</span>
                <span class="cell-value">${trade['target']:.2f}</span>
            </div>
            <div class="cell-group">
                <span class="cell-label">Stop Loss</span>
                <span class="cell-value" style="color:#ef4444;">${trade['stop']:.2f}</span>
            </div>
            <div class="cell-group">
                <span class="cell-label">Side</span>
                <span class="cell-value" style="text-transform:uppercase; font-size:0.75rem;">{trade['status']}</span>
            </div>
        </div>
        """
        table_html += row

    table_html += "</div>"

    # Wyświetlenie tabeli w Streamlit
    st.markdown(table_html, unsafe_allow_html=True)

    # 4. Sekcja dodatkowa
    st.markdown("---")
    st.info("💡 **Tip:** Use the filters above to narrow down your active positions.")

if __name__ == "__main__":
    main()
