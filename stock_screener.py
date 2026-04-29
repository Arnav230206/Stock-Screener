import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Nifty Stock Screener",
    page_icon="📈",
    layout="wide"
)

# ── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1c1f26;
        border: 1px solid #2d3139;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        text-align: center;
    }
    .metric-val { font-size: 2rem; font-weight: 600; color: #00d4aa; }
    .metric-label { font-size: 0.75rem; color: #8b8fa8; text-transform: uppercase; letter-spacing: 0.08em; }
    .header-tag {
        display: inline-block;
        background: #1a3a2a;
        color: #00d4aa;
        font-size: 0.7rem;
        padding: 2px 10px;
        border-radius: 20px;
        border: 1px solid #00d4aa44;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .stDataFrame { border-radius: 10px; }
    div[data-testid="stMetric"] {
        background: #1c1f26;
        border: 1px solid #2d3139;
        border-radius: 10px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── UNIVERSE ──────────────────────────────────────────────────
TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS",
    "SBIN.NS", "HINDUNILVR.NS", "ITC.NS", "LT.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "BAJFINANCE.NS", "MARUTI.NS", "ASIANPAINT.NS", "HCLTECH.NS",
    "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS", "ULTRACEMCO.NS", "ONGC.NS",
    "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS", "BAJAJFINSV.NS", "NESTLEIND.NS",
    "TECHM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "ADANIPORTS.NS",
    "HINDALCO.NS", "DRREDDY.NS", "CIPLA.NS", "BRITANNIA.NS", "GRASIM.NS",
    "DIVISLAB.NS", "EICHERMOT.NS", "BPCL.NS", "TATACONSUM.NS", "APOLLOHOSP.NS",
    "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS", "HDFCLIFE.NS", "INDUSINDBK.NS",
    "VEDL.NS", "PIDILITIND.NS", "GODREJCP.NS", "HAVELLS.NS", "DABUR.NS",
    "MARICO.NS", "LUPIN.NS", "TORNTPHARM.NS", "AMBUJACEM.NS", "ICICIPRULI.NS",
    "BOSCHLTD.NS", "CHOLAFIN.NS", "NAUKRI.NS", "BERGEPAINT.NS", "TRENT.NS",
    "ALKEM.NS", "LTIM.NS", "PERSISTENT.NS", "COFORGE.NS", "POLYCAB.NS",
    "BANKBARODA.NS", "CANBK.NS", "PNB.NS", "GAIL.NS", "IOC.NS",
    "RECLTD.NS", "PFC.NS", "HAL.NS", "BEL.NS", "NMDC.NS",
    "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPOWER.NS", "ZOMATO.NS", "JIOFIN.NS",
]

TICKER_NAMES = {
    "RELIANCE.NS": "Reliance Industries", "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank", "BHARTIARTL.NS": "Bharti Airtel",
    "ICICIBANK.NS": "ICICI Bank", "SBIN.NS": "State Bank of India",
    "HINDUNILVR.NS": "Hindustan Unilever", "ITC.NS": "ITC Ltd",
    "LT.NS": "Larsen & Toubro", "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "AXISBANK.NS": "Axis Bank", "BAJFINANCE.NS": "Bajaj Finance",
    "MARUTI.NS": "Maruti Suzuki", "ASIANPAINT.NS": "Asian Paints",
    "HCLTECH.NS": "HCL Technologies", "SUNPHARMA.NS": "Sun Pharmaceutical",
    "TITAN.NS": "Titan Company", "WIPRO.NS": "Wipro",
    "ULTRACEMCO.NS": "UltraTech Cement", "ONGC.NS": "ONGC",
    "NTPC.NS": "NTPC", "POWERGRID.NS": "Power Grid Corp",
    "COALINDIA.NS": "Coal India", "BAJAJFINSV.NS": "Bajaj Finserv",
    "NESTLEIND.NS": "Nestle India", "TECHM.NS": "Tech Mahindra",
    "TATAMOTORS.NS": "Tata Motors", "TATASTEEL.NS": "Tata Steel",
    "JSWSTEEL.NS": "JSW Steel", "ADANIPORTS.NS": "Adani Ports",
    "HINDALCO.NS": "Hindalco", "DRREDDY.NS": "Dr Reddy's Labs",
    "CIPLA.NS": "Cipla", "BRITANNIA.NS": "Britannia Industries",
    "GRASIM.NS": "Grasim Industries", "DIVISLAB.NS": "Divi's Laboratories",
    "EICHERMOT.NS": "Eicher Motors", "BPCL.NS": "BPCL",
    "TATACONSUM.NS": "Tata Consumer", "APOLLOHOSP.NS": "Apollo Hospitals",
    "HEROMOTOCO.NS": "Hero MotoCorp", "BAJAJ-AUTO.NS": "Bajaj Auto",
    "SBILIFE.NS": "SBI Life Insurance", "HDFCLIFE.NS": "HDFC Life",
    "INDUSINDBK.NS": "IndusInd Bank", "VEDL.NS": "Vedanta",
    "PIDILITIND.NS": "Pidilite Industries", "GODREJCP.NS": "Godrej Consumer",
    "HAVELLS.NS": "Havells India", "DABUR.NS": "Dabur India",
    "MARICO.NS": "Marico", "LUPIN.NS": "Lupin",
    "TORNTPHARM.NS": "Torrent Pharma", "AMBUJACEM.NS": "Ambuja Cements",
    "ICICIPRULI.NS": "ICICI Prudential", "BOSCHLTD.NS": "Bosch",
    "CHOLAFIN.NS": "Cholamandalam Finance", "NAUKRI.NS": "Info Edge (Naukri)",
    "BERGEPAINT.NS": "Berger Paints", "TRENT.NS": "Trent",
    "ALKEM.NS": "Alkem Laboratories", "LTIM.NS": "LTIMindtree",
    "PERSISTENT.NS": "Persistent Systems", "COFORGE.NS": "Coforge",
    "POLYCAB.NS": "Polycab India", "BANKBARODA.NS": "Bank of Baroda",
    "CANBK.NS": "Canara Bank", "PNB.NS": "Punjab National Bank",
    "GAIL.NS": "GAIL India", "IOC.NS": "Indian Oil Corp",
    "RECLTD.NS": "REC Ltd", "PFC.NS": "Power Finance Corp",
    "HAL.NS": "Hindustan Aeronautics", "BEL.NS": "Bharat Electronics",
    "NMDC.NS": "NMDC", "ADANIENT.NS": "Adani Enterprises",
    "ADANIGREEN.NS": "Adani Green Energy", "ADANIPOWER.NS": "Adani Power",
    "ZOMATO.NS": "Zomato", "JIOFIN.NS": "Jio Financial Services",
}

SECTORS = {
    "RELIANCE.NS": "Energy", "TCS.NS": "IT", "HDFCBANK.NS": "Banking",
    "BHARTIARTL.NS": "Telecom", "ICICIBANK.NS": "Banking", "SBIN.NS": "Banking",
    "HINDUNILVR.NS": "FMCG", "ITC.NS": "FMCG", "LT.NS": "Industrials",
    "KOTAKBANK.NS": "Banking", "AXISBANK.NS": "Banking", "BAJFINANCE.NS": "NBFC",
    "MARUTI.NS": "Auto", "ASIANPAINT.NS": "Paints", "HCLTECH.NS": "IT",
    "SUNPHARMA.NS": "Pharma", "TITAN.NS": "Consumer", "WIPRO.NS": "IT",
    "ULTRACEMCO.NS": "Cement", "ONGC.NS": "Energy", "NTPC.NS": "Utilities",
    "POWERGRID.NS": "Utilities", "COALINDIA.NS": "Energy", "BAJAJFINSV.NS": "NBFC",
    "NESTLEIND.NS": "FMCG", "TECHM.NS": "IT", "TATAMOTORS.NS": "Auto",
    "TATASTEEL.NS": "Metals", "JSWSTEEL.NS": "Metals", "ADANIPORTS.NS": "Logistics",
    "HINDALCO.NS": "Metals", "DRREDDY.NS": "Pharma", "CIPLA.NS": "Pharma",
    "BRITANNIA.NS": "FMCG", "GRASIM.NS": "Diversified", "DIVISLAB.NS": "Pharma",
    "EICHERMOT.NS": "Auto", "BPCL.NS": "Energy", "TATACONSUM.NS": "FMCG",
    "APOLLOHOSP.NS": "Healthcare", "HEROMOTOCO.NS": "Auto", "BAJAJ-AUTO.NS": "Auto",
    "SBILIFE.NS": "Insurance", "HDFCLIFE.NS": "Insurance", "INDUSINDBK.NS": "Banking",
    "VEDL.NS": "Metals", "PIDILITIND.NS": "Chemicals", "GODREJCP.NS": "FMCG",
    "HAVELLS.NS": "Electricals", "DABUR.NS": "FMCG", "MARICO.NS": "FMCG",
    "LUPIN.NS": "Pharma", "TORNTPHARM.NS": "Pharma", "AMBUJACEM.NS": "Cement",
    "ICICIPRULI.NS": "Insurance", "BOSCHLTD.NS": "Auto Ancillary",
    "CHOLAFIN.NS": "NBFC", "NAUKRI.NS": "Technology", "BERGEPAINT.NS": "Paints",
    "TRENT.NS": "Retail", "ALKEM.NS": "Pharma", "LTIM.NS": "IT",
    "PERSISTENT.NS": "IT", "COFORGE.NS": "IT", "POLYCAB.NS": "Electricals",
    "BANKBARODA.NS": "Banking", "CANBK.NS": "Banking", "PNB.NS": "Banking",
    "GAIL.NS": "Energy", "IOC.NS": "Energy", "RECLTD.NS": "Finance",
    "PFC.NS": "Finance", "HAL.NS": "Defence", "BEL.NS": "Defence",
    "NMDC.NS": "Metals", "ADANIENT.NS": "Diversified", "ADANIGREEN.NS": "Utilities",
    "ADANIPOWER.NS": "Utilities", "ZOMATO.NS": "Technology", "JIOFIN.NS": "Finance",
}

# ── DATA FETCH ────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(tickers):
    results = []
    end = datetime.today()
    start_1y = end - timedelta(days=400)

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Price & 52W
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            week52_high = info.get("fiftyTwoWeekHigh")
            week52_low = info.get("fiftyTwoWeekLow")

            if not current_price or not week52_high:
                continue

            pct_from_52w_high = ((current_price - week52_high) / week52_high) * 100

            # Fundamentals
            pe = info.get("trailingPE")
            div_yield = (info.get("dividendYield") or 0) * 100
            roe = (info.get("returnOnEquity") or 0) * 100
            market_cap = info.get("marketCap", 0)

            # 6-month momentum
            hist = stock.history(start=start_1y, end=end)
            if len(hist) < 120:
                momentum_6m = None
            else:
                price_6m_ago = hist["Close"].iloc[-130] if len(hist) >= 130 else hist["Close"].iloc[0]
                price_1m_ago = hist["Close"].iloc[-22]
                momentum_6m = ((price_1m_ago - price_6m_ago) / price_6m_ago) * 100

            results.append({
                "Ticker": ticker.replace(".NS", ""),
                "Company": TICKER_NAMES.get(ticker, ticker),
                "Sector": SECTORS.get(ticker, "—"),
                "Price (₹)": round(current_price, 1),
                "P/E": round(pe, 1) if pe else None,
                "Div Yield (%)": round(div_yield, 2),
                "ROE (%)": round(roe, 1) if roe else None,
                "6M Momentum (%)": round(momentum_6m, 1) if momentum_6m else None,
                "% from 52W High": round(pct_from_52w_high, 1),
                "52W High (₹)": round(week52_high, 1),
                "Mkt Cap (₹Cr)": round(market_cap / 1e7, 0) if market_cap else None,
            })
        except Exception:
            continue

    return pd.DataFrame(results)


# ── SCORING ───────────────────────────────────────────────────
def compute_score(row, max_pe, min_dy, max_from_52w, min_roe, min_momentum):
    score = 0
    if pd.notna(row["P/E"]) and row["P/E"] > 0:
        score += max(0, (max_pe - row["P/E"]) / max_pe) * 30
    if pd.notna(row["Div Yield (%)"]):
        score += min(row["Div Yield (%)"] / 6, 1) * 20
    score += max(0, (max_from_52w - abs(row["% from 52W High"])) / max_from_52w) * 20
    if pd.notna(row["ROE (%)"]):
        score += min(row["ROE (%)"] / 40, 1) * 15
    if pd.notna(row["6M Momentum (%)"]):
        score += min(max(row["6M Momentum (%)"] / 50, 0), 1) * 15
    return round(score, 1)


# ── HEADER ────────────────────────────────────────────────────
st.markdown('<div class="header-tag">Live · NSE · Nifty Universe</div>', unsafe_allow_html=True)
st.title("📈 Nifty Stock Screener")
st.markdown("Filter Nifty large-caps by fundamentals and momentum. Data refreshes every hour.")
st.divider()

# ── SIDEBAR FILTERS ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Filters")
    st.markdown("---")

    st.markdown("**Valuation**")
    max_pe = st.slider("Max P/E Ratio", 5, 80, 30, 1)
    min_dy = st.slider("Min Dividend Yield (%)", 0.0, 6.0, 1.0, 0.1)

    st.markdown("**Quality**")
    min_roe = st.slider("Min ROE (%)", 0, 40, 10, 1)

    st.markdown("**Price & Momentum**")
    max_from_52w = st.slider("Max % below 52W High", 5, 60, 25, 1)
    min_momentum = st.slider("Min 6M Momentum (%)", -30, 50, 0, 1)

    st.markdown("**Sector Filter**")
    all_sectors = ["All"] + sorted(list(set(SECTORS.values())))
    selected_sector = st.selectbox("Sector", all_sectors)

    st.markdown("---")
    run = st.button("🔍 Run Screener", use_container_width=True, type="primary")
    st.caption("First load takes ~2 min to fetch live data for 75+ stocks.")

# ── MAIN AREA ─────────────────────────────────────────────────
if run or "df_raw" in st.session_state:

    if run or "df_raw" not in st.session_state:
        with st.spinner("Fetching live data for 75+ Nifty stocks... (~90 seconds)"):
            df_raw = fetch_stock_data(TICKERS)
            st.session_state["df_raw"] = df_raw
    else:
        df_raw = st.session_state["df_raw"]

    df = df_raw.copy()

    # Apply filters
    if selected_sector != "All":
        df = df[df["Sector"] == selected_sector]
    df = df[df["P/E"].notna() & (df["P/E"] > 0) & (df["P/E"] < max_pe)]
    df = df[df["Div Yield (%)"] >= min_dy]
    df = df[df["ROE (%)"].notna() & (df["ROE (%)"] >= min_roe)]
    df = df[df["% from 52W High"] >= -max_from_52w]
    df = df[df["6M Momentum (%)"].notna() & (df["6M Momentum (%)"] >= min_momentum)]

    # Compute score
    df["Score"] = df.apply(
        lambda r: compute_score(r, max_pe, min_dy, max_from_52w, min_roe, min_momentum), axis=1
    )
    df = df.sort_values("Score", ascending=False).reset_index(drop=True)
    df.index += 1

    # ── METRICS ROW ───────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Universe", f"{len(df_raw)} stocks")
    col2.metric("Passed Filters", f"{len(df)} stocks")
    col3.metric("Pass Rate", f"{round(len(df)/len(df_raw)*100, 1)}%" if len(df_raw) > 0 else "—")
    col4.metric("Top Score", f"{df['Score'].max():.1f} / 100" if len(df) > 0 else "—")

    st.markdown("")

    if len(df) == 0:
        st.warning("No stocks passed your filters. Try loosening the criteria.")
    else:
        st.markdown(f"### {len(df)} stock{'s' if len(df) != 1 else ''} passed all filters")

        # Format display
        display_cols = ["Company", "Sector", "Price (₹)", "P/E", "Div Yield (%)",
                        "ROE (%)", "6M Momentum (%)", "% from 52W High", "Score"]
        display_df = df[display_cols].copy()

        st.dataframe(
            display_df.style
                .background_gradient(subset=["Score"], cmap="Greens")
                .background_gradient(subset=["6M Momentum (%)"], cmap="RdYlGn")
                .format({
                    "Price (₹)": "₹{:.1f}",
                    "P/E": "{:.1f}x",
                    "Div Yield (%)": "{:.2f}%",
                    "ROE (%)": "{:.1f}%",
                    "6M Momentum (%)": "{:+.1f}%",
                    "% from 52W High": "{:.1f}%",
                    "Score": "{:.1f}",
                }),
            use_container_width=True,
            height=500
        )

        # ── EXPORT ────────────────────────────────────────────
        st.markdown("")
        csv = df[display_cols].to_csv().encode("utf-8")
        st.download_button(
            "⬇️ Export to CSV",
            csv,
            f"screener_results_{datetime.today().strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=False
        )

        # ── SECTOR BREAKDOWN ──────────────────────────────────
        if len(df) > 1:
            st.markdown("---")
            st.markdown("### Sector Breakdown")
            sector_counts = df["Sector"].value_counts()
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.dataframe(
                    sector_counts.rename("Stocks Passed").reset_index().rename(columns={"index": "Sector"}),
                    use_container_width=True,
                    hide_index=True
                )
            with col_b:
                st.bar_chart(sector_counts)

else:
    # Landing state
    st.markdown("""
    <div style='text-align:center; padding: 4rem 2rem; color: #8b8fa8;'>
        <div style='font-size: 3rem; margin-bottom: 1rem'>📊</div>
        <div style='font-size: 1.1rem; margin-bottom: 0.5rem; color: #e0e0e0'>Set your filters and click <b>Run Screener</b></div>
        <div style='font-size: 0.85rem'>Screens 75+ Nifty stocks live using P/E, Dividend Yield, ROE, Momentum, and 52-Week proximity</div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────
st.divider()
st.caption("Data sourced from Yahoo Finance via yfinance. Refreshed every hour. Not investment advice.")
