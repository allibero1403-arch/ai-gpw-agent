import streamlit as st

# Konfiguracja strony
st.set_page_config(page_title="Trading Dashboard", layout="wide")

# 1. Definicja Stylów CSS (Naprawiony blok)
# Zauważ: dodałem ) na końcu oraz unsafe_allow_html=True
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .card-container {
        padding: 20px;
        border-radius: 10px;
        background-color: #161b22;
        border: 1px solid #30363d;
    }
    .metric-label {
        font-size: 14px;
        color: #8b949e;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# 2. Dane testowe (Symulacja danych z bazy/API)
data = [
    {"ticker": "BTC/USDT", "price": 64250.50, "change": 2.5, "volume": "1.2B"},
    {"ticker": "ETH/USDT", "price": 3450.20, "change": -1.2, "volume": "850M"},
    {"ticker": "SOL/USDT", "price": 145.15, "change": 5.8, "volume": "400M"},
    {"ticker": "BNB/USDT", "price": 580.00, "change": 0.4, "volume": "210M"},
]

# 3. Interfejs użytkownika
st.title("📈 Crypto Market Dashboard")
st.write("Real-time market overview and performance tracking.")

# Układ kolumnowy dla metryk (Cards)
cols = st.columns(len(data))

for i, item in enumerate(data):
    with cols[i]:
        # Generowanie HTML dla każdej karty
        color = "#26a69a" if item["change"] >= 0 else "#ef5350"
        symbol = "+" if item["change"] >= 0 else ""
        
        st.markdown(f"""
        <div class="card-container">
            <div class="metric-label">{item['ticker']}</div>
            <div class="metric-value">${item['price']:,.2f}</div>
            <div style="color: {color}; font-weight: bold;">
                {symbol}{item['change']}%
            </div>
            <div class="metric-label" style="margin-top: 10px; font-size: 12px;">
                Vol: {item['volume']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# 4. Tabela szczegółowa
st.subheader("Detailed Market Data")
st.table(data)

# 5. Sidebar z kontrolami
st.sidebar.header("Settings")
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 10)
st.sidebar.info(f"Dashboard will refresh every {refresh_rate} seconds.")

if st.sidebar.button("Force Refresh"):
    st.rerun()
