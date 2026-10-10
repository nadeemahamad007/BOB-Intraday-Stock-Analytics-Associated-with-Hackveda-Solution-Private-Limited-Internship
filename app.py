from pathlib import Path
import base64

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------- Page setup ----------------
st.set_page_config(
    page_title="Bank of Baroda | Intraday Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Palette & styling ----------------
BG = "#F5EBD9"
PANEL = "#FFFCF6"
SIDEBAR = "#EFE1CC"
BROWN = "#713D20"
DARK = "#382719"
MUTED = "#715B47"
BORDER = "#E5D1B7"
BLUE = "#1677D2"
ORANGE = "#E69A35"
GREEN = "#21834A"
RED = "#D94245"

st.markdown(
    f"""
    <style>
    :root {{ color-scheme: light !important; }}
    html, body, [data-testid="stApp"], .stApp,
    [data-testid="stAppViewContainer"], [data-testid="stMain"],
    [data-testid="stMainBlockContainer"], [data-testid="stMainBlockContainer"] > div, .block-container {{
        background: {BG} !important; color: {DARK} !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{
        background: {BG} !important; color: {DARK} !important;
    }}
    .block-container {{ max-width: 1750px; padding-top: .8rem; padding-bottom: 2rem; }}
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {{
        background: {SIDEBAR} !important; border-right: 1px solid #D8C2A4 !important;
    }}
    [data-testid="stSidebar"] * {{ color: {DARK}; }}
    h1, h2, h3, h4, h5 {{ color: {DARK} !important; font-weight: 800 !important; }}
    p, label, [data-testid="stCaptionContainer"] {{ color: {MUTED} !important; }}
    [data-testid="stMetric"] {{ background: {PANEL} !important; border: 1px solid {BORDER} !important;
        border-top: 3px solid #B96D36 !important; padding: 13px 15px !important;
        border-radius: 13px !important; box-shadow: 0 3px 10px rgba(70,40,15,.05) !important; }}
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {{ color: {MUTED} !important; }}
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {{ color: {DARK} !important; font-weight: 800 !important; }}
    .hero {{ background-color: #FFF9F0;
        border: 1px solid {BORDER}; border-radius: 15px; padding: 15px 18px; margin-bottom: 13px;
        background-size: cover; background-position: center right;
        display:flex; align-items:center; justify-content:space-between; gap:18px; }}
    .brand {{ display:flex; align-items:center; gap:14px; min-width:0; }}
    .brand-logo {{ width:60px; height:60px; flex-shrink:0; }}
    .hero-title {{ margin:0; color:{DARK}; font-size:clamp(1.25rem,2vw,2rem); line-height:1.2; font-weight:850; }}
    .hero-sub {{ margin:5px 0 8px; color:{MUTED}; font-size:.82rem; }}
    .badge {{ display:inline-block; padding:4px 9px; margin:2px 5px 0 0; border-radius:999px;
        background:#F4E2C5; border:1px solid #E4C69D; color:{BROWN}; font-size:.72rem; font-weight:700; }}
    .date-chip {{ background:{PANEL}; border:1px solid {BORDER}; border-radius:10px; padding:9px 12px;
        text-align:right; color:{DARK}; min-width:190px; font-size:.82rem; }}
    .stTabs [data-baseweb="tab-list"] {{ gap:5px; background:#E9D9C2 !important; padding:5px;
        border:1px solid #D8C2A4; border-radius:12px; }}
    .stTabs [data-baseweb="tab"] {{ background:{PANEL} !important; border:1px solid {BORDER} !important;
        border-radius:8px !important; color:{DARK} !important; padding:8px 12px !important; }}
    .stTabs [data-baseweb="tab"] p {{ color:{DARK} !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ background:{BROWN} !important; border-color:{BROWN} !important; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] p {{ color:#FFFFFF !important; }}
    .stButton button, .stDownloadButton button {{ background:{BROWN} !important; color:#FFFFFF !important;
        border:1px solid {BROWN} !important; border-radius:9px !important; font-weight:700 !important; }}
    input, textarea, [data-baseweb="select"] > div {{ background:{PANEL} !important; color:{DARK} !important; border-color:#CDB394 !important; }}
    [data-testid="stPlotlyChart"] {{ background:{PANEL} !important; border:1px solid {BORDER} !important;
        border-radius:13px !important; padding:6px !important; box-shadow:0 3px 10px rgba(70,40,15,.04); }}
    [data-testid="stDataFrame"] {{ border:1px solid {BORDER}; border-radius:10px; overflow:hidden; }}
    hr {{ border-color:#D8C2A4 !important; }}
    @media (max-width: 850px) {{ .hero {{ align-items:flex-start; flex-direction:column; }} .date-chip {{ text-align:left; }} }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Inline logo: no external image or internet connection required.
LOGO = """<svg class='brand-logo' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg' role='img' aria-label='Bank of Baroda logo'>
<rect width='100' height='100' rx='16' fill='#EA5514'/><path d='M22 18h27c17 0 28 9 28 22 0 8-5 14-14 17 11 2 18 9 18 20 0 13-12 20-31 20H22V18zm17 13v19h9c7 0 12-4 12-10s-5-9-12-9h-9zm0 32v20h11c8 0 13-4 13-10s-5-10-13-10H39z' fill='#fff'/></svg>"""

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "Bank_of_Baroda_5min_OHLCV.csv"
HERO_PATH = BASE_DIR / "assets" / "bank_of_baroda_header.png"
HERO_IMAGE = base64.b64encode(HERO_PATH.read_bytes()).decode("ascii") if HERO_PATH.exists() else ""
REQUIRED = ["Date", "Open", "High", "Low", "Close", "Volume"]


@st.cache_data(show_spinner=False)
def load_data(file_source):
    raw = pd.read_csv(file_source)
    mapping = {
        "date": "Date", "datetime": "Date", "timestamp": "Date",
        "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume",
    }
    rename = {}
    for column in raw.columns:
        key = str(column).strip().lower().replace(" ", "_")
        if key in mapping:
            rename[column] = mapping[key]
    raw = raw.rename(columns=rename)
    raw = raw.drop(columns=[c for c in raw.columns if str(c).lower().startswith("unnamed")], errors="ignore")
    missing_cols = [c for c in REQUIRED if c not in raw.columns]
    if missing_cols:
        raise ValueError("Missing required CSV columns: " + ", ".join(missing_cols))

    df = raw[REQUIRED].copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in REQUIRED[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    initial_rows = len(df)
    missing_rows = int(df[REQUIRED].isna().any(axis=1).sum())
    df = df.dropna(subset=REQUIRED)
    duplicate_rows = int(df["Date"].duplicated().sum())
    df = df.drop_duplicates("Date").sort_values("Date")
    invalid = (
        (df["High"] < df[["Open", "Low", "Close"]].max(axis=1))
        | (df["Low"] > df[["Open", "High", "Close"]].min(axis=1))
        | (df["High"] < df["Low"])
        | (df[["Open", "High", "Low", "Close"]] <= 0).any(axis=1)
        | (df["Volume"] < 0)
    )
    invalid_rows = int(invalid.sum())
    df = df.loc[~invalid].copy()
    if df.empty:
        raise ValueError("No valid rows remain after data-quality checks.")
    df["Session"] = df["Date"].dt.date
    df["Bar Return %"] = df.groupby("Session")["Close"].pct_change() * 100
    df["MA 20"] = df["Close"].rolling(20, min_periods=1).mean()
    df["MA 50"] = df["Close"].rolling(50, min_periods=1).mean()
    quality = {
        "initial_rows": initial_rows,
        "missing_rows": missing_rows,
        "duplicate_rows": duplicate_rows,
        "invalid_rows": invalid_rows,
    }
    return df, quality


def style_chart(fig, height=360, time_axis=True):
    fig.update_layout(
        template="plotly_white", height=height,
        paper_bgcolor=PANEL, plot_bgcolor=PANEL,
        font=dict(family="Arial, sans-serif", color=DARK, size=12),
        margin=dict(l=55, r=20, t=32, b=48),
        legend=dict(font=dict(color=DARK), bgcolor="rgba(255,252,246,.85)", orientation="h", y=1.12, x=1, xanchor="right"),
        hoverlabel=dict(bgcolor=BROWN, bordercolor=BROWN, font=dict(color="#FFFFFF")),
    )
    fig.update_xaxes(tickfont=dict(color=DARK), title_font=dict(color=DARK), showgrid=True,
                     gridcolor="#E8DCCB", showline=True, linecolor="#C7AD8F", automargin=True)
    fig.update_yaxes(tickfont=dict(color=DARK), title_font=dict(color=DARK), showgrid=True,
                     gridcolor="#E8DCCB", showline=True, linecolor="#C7AD8F", automargin=True)
    if time_axis:
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"]), dict(bounds=[15.5, 9.25], pattern="hour")])
    return fig


def money(value):
    return f"₹{value:,.2f}"


# ---------------- Sidebar and data ----------------
with st.sidebar:
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:10px;background:{PANEL};border:1px solid {BORDER};border-radius:12px;padding:10px;margin-bottom:16px;'>"
        f"{LOGO}<div><div style='font-size:1rem;font-weight:800;color:{DARK};line-height:1.2;'>बैंक ऑफ़ बड़ौदा</div>"
        f"<div style='font-size:.95rem;font-weight:800;color:{BROWN};'>Bank of Baroda</div><div style='font-size:.75rem;color:{MUTED};'>Stock Analytics</div></div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("### ⚙️ Analysis controls")
    uploaded = st.file_uploader("Use another CSV (optional)", type=["csv"])

    source = uploaded if uploaded is not None else (DATA_PATH if DATA_PATH.exists() else None)
    if source is None:
        st.warning("Dataset file not found. Place Bank_of_Baroda_5min_OHLCV.csv inside the data folder, or upload a CSV above.")
        st.stop()
    try:
        df, quality = load_data(source)
    except Exception as exc:
        st.error(f"Could not load the dataset: {exc}")
        st.stop()

    min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
    chosen_dates = st.date_input("Trading date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(chosen_dates, (tuple, list)) and len(chosen_dates) == 2:
        start_date, end_date = chosen_dates
    else:
        start_date = end_date = chosen_dates[0] if isinstance(chosen_dates, (tuple, list)) else chosen_dates
    t_min, t_max = df["Date"].dt.time.min(), df["Date"].dt.time.max()
    time_window = st.slider("Intraday time window", min_value=t_min, max_value=t_max, value=(t_min, t_max), format="HH:mm")
    st.markdown("---")
    st.markdown("### 🗂️ Dataset information")
    st.markdown(f"**Total bars:** {len(df):,}  \n**Trading sessions:** {df['Session'].nunique():,}  \n**Date range:** {min_date:%d %b %Y} – {max_date:%d %b %Y}  \n**Interval:** 5 minutes  \n**Symbol:** Bank of Baroda")

mask = df["Date"].dt.date.between(start_date, end_date)
mask &= df["Date"].dt.time.between(time_window[0], time_window[1])
f = df.loc[mask].copy()
if f.empty:
    st.warning("No records match the selected date and time filters. Please widen the range.")
    st.stop()

# Session summaries and headline metrics
daily = f.groupby("Session", sort=True).agg(
    session_open=("Open", "first"), session_high=("High", "max"),
    session_low=("Low", "min"), session_close=("Close", "last"),
    volume=("Volume", "sum"), bars=("Close", "size"),
).reset_index()
daily["Return %"] = (daily["session_close"] / daily["session_open"] - 1) * 100
first_close, last_close = float(f["Close"].iloc[0]), float(f["Close"].iloc[-1])
period_return = (last_close / first_close - 1) * 100
period_high, period_low = float(f["High"].max()), float(f["Low"].min())
avg_volume = float(f["Volume"].mean())

# ---------------- Main hero ----------------
st.markdown(
    f"<div class='hero' style=\"background-image:linear-gradient(90deg,rgba(255,252,246,.98) 0%,rgba(255,249,240,.94) 58%,rgba(255,249,240,.25) 100%),url(data:image/png;base64,{HERO_IMAGE});\"><div class='brand'>{LOGO}<div><h1 class='hero-title'>Bank of Baroda — Intraday Stock Analytics</h1>"
    f"<p class='hero-sub'>Historical 5-minute OHLCV analysis: price trends, candlesticks, volume, returns and data quality.</p>"
    f"<span class='badge'>5-minute OHLCV</span><span class='badge'>Plotly</span><span class='badge'>Streamlit</span><span class='badge'>Educational analytics</span></div></div>"
    f"<div class='date-chip'><b>📅 {f['Date'].min():%d %b %Y} – {f['Date'].max():%d %b %Y}</b><br><span style='color:{MUTED};font-size:.75rem'>{len(f):,} bars · {daily['Session'].nunique()} sessions</span></div></div>",
    unsafe_allow_html=True,
)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Latest close in range", money(last_close), f"{last_close-first_close:+.2f} ({period_return:+.2f}%)")
m2.metric("Period return", f"{period_return:+.2f}%", "Selected period")
m3.metric("Period high", money(period_high), f"{((period_high/first_close)-1)*100:+.2f}% vs first close")
m4.metric("Period low", money(period_low), f"{((period_low/first_close)-1)*100:+.2f}% vs first close")
m5.metric("Avg. bar volume", f"{avg_volume:,.0f}", "Shares per 5-min bar")
st.caption("Use the sidebar to change the date range, time window, or upload another OHLCV CSV.")

tabs = st.tabs(["🏠 Overview", "🕯️ Candlestick", "📊 Volume", "📈 Returns & Risk", "📅 Session Analysis", "🗄️ Data Quality"])

with tabs[0]:
    st.subheader("📈 Closing price over time")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=f["Date"], y=f["Close"], name="Close", line=dict(color=BLUE, width=2.5)))
    fig.add_trace(go.Scatter(x=f["Date"], y=f["MA 20"], name="20-bar MA", line=dict(color=ORANGE, width=2)))
    fig.add_trace(go.Scatter(x=f["Date"], y=f["MA 50"], name="50-bar MA", line=dict(color=RED, width=2)))
    fig.update_layout(yaxis_title="Price (₹)")
    st.plotly_chart(style_chart(fig, 360), use_container_width=True, key="overview_price")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Session closing price")
        fig = go.Figure(go.Bar(x=daily["Session"].astype(str), y=daily["session_close"], marker_color="#B77A4A"))
        fig.update_layout(yaxis_title="Close (₹)", showlegend=False)
        st.plotly_chart(style_chart(fig, 300, False), use_container_width=True, key="session_close")
    with right:
        st.markdown("#### Session return")
        fig = go.Figure(go.Bar(x=daily["Session"].astype(str), y=daily["Return %"], marker_color=np.where(daily["Return %"] >= 0, GREEN, RED)))
        fig.update_layout(yaxis_title="Return (%)", showlegend=False)
        st.plotly_chart(style_chart(fig, 300, False), use_container_width=True, key="session_return")

with tabs[1]:
    st.subheader("🕯️ Interactive OHLC candlestick")
    candle = go.Figure(go.Candlestick(
        x=f["Date"], open=f["Open"], high=f["High"], low=f["Low"], close=f["Close"],
        name="OHLC", increasing_line_color=GREEN, increasing_fillcolor="#69A879",
        decreasing_line_color=RED, decreasing_fillcolor="#E87570",
    ))
    candle.update_layout(xaxis_rangeslider_visible=False, yaxis_title="Price (₹)")
    st.plotly_chart(style_chart(candle, 500), use_container_width=True, key="candlestick_main")
    st.info("Green candles indicate Close ≥ Open; red candles indicate Close < Open. Hover or zoom to inspect each 5-minute bar.")

with tabs[2]:
    st.subheader("📊 Intraday trading volume")
    fig = go.Figure(go.Bar(x=f["Date"], y=f["Volume"], name="5-minute volume", marker_color="#B98255", marker_line_color="#87552F", marker_line_width=.35))
    fig.update_layout(yaxis_title="Shares traded", showlegend=False)
    st.plotly_chart(style_chart(fig, 380), use_container_width=True, key="intraday_volume")
    st.markdown("#### Session-level volume")
    fig = go.Figure(go.Bar(x=daily["Session"].astype(str), y=daily["volume"], name="Session volume", marker_color="#78945D", marker_line_color="#536D3C", marker_line_width=.35))
    fig.update_layout(yaxis_title="Shares", showlegend=False)
    st.plotly_chart(style_chart(fig, 330, False), use_container_width=True, key="session_volume")

with tabs[3]:
    st.subheader("📈 5-minute return distribution")
    returns = f["Bar Return %"].dropna()
    fig = go.Figure(go.Histogram(x=returns, nbinsx=40, marker_color="#B98255", marker_line_color="#87552F"))
    fig.update_layout(xaxis_title="5-minute return (%)", yaxis_title="Number of bars", showlegend=False)
    st.plotly_chart(style_chart(fig, 330, False), use_container_width=True, key="return_distribution")
    a, b, c, d = st.columns(4)
    a.metric("Return volatility", f"{returns.std():.3f}%" if not returns.empty else "N/A")
    b.metric("Best 5-min return", f"{returns.max():+.2f}%" if not returns.empty else "N/A")
    c.metric("Worst 5-min return", f"{returns.min():+.2f}%" if not returns.empty else "N/A")
    d.metric("Median 5-min return", f"{returns.median():+.3f}%" if not returns.empty else "N/A")
    st.markdown("#### Cumulative intraday return")
    if not returns.empty:
        cumulative = (1 + returns.fillna(0) / 100).cumprod().sub(1) * 100
        fig = go.Figure(go.Scatter(x=f.loc[returns.index, "Date"], y=cumulative, name="Cumulative return", line=dict(color=BLUE, width=2.4), fill="tozeroy", fillcolor="rgba(22,119,210,.10)"))
        fig.update_layout(yaxis_title="Cumulative return (%)", showlegend=False)
        st.plotly_chart(style_chart(fig, 330), use_container_width=True, key="cumulative_return")

with tabs[4]:
    st.subheader("📅 Trading-session analysis")
    best = daily.loc[daily["Return %"].idxmax()]
    worst = daily.loc[daily["Return %"].idxmin()]
    high_day = daily.loc[daily["session_high"].idxmax()]
    volume_day = daily.loc[daily["volume"].idxmax()]
    a, b, c, d = st.columns(4)
    a.metric("Best session", str(best["Session"]), f"{best['Return %']:+.2f}%")
    b.metric("Worst session", str(worst["Session"]), f"{worst['Return %']:+.2f}%")
    c.metric("Highest intraday high", money(high_day["session_high"]))
    d.metric("Highest session volume", f"{volume_day['volume']:,.0f}")
    st.dataframe(daily.sort_values("Session", ascending=False), use_container_width=True, hide_index=True)

with tabs[5]:
    st.subheader("🗄️ Data-quality checks")
    a, b, c, d = st.columns(4)
    a.metric("Valid bars", f"{len(df):,}")
    b.metric("Rows with missing values", f"{quality['missing_rows']:,}")
    c.metric("Duplicate timestamps", f"{quality['duplicate_rows']:,}")
    d.metric("Invalid OHLC rows", f"{quality['invalid_rows']:,}")
    st.caption("Rows with missing required values, duplicate timestamps, or invalid OHLC relationships are excluded from the analysis.")
    display_cols = ["Date", "Open", "High", "Low", "Close", "Volume", "Bar Return %", "MA 20", "MA 50"]
    display = f[display_cols].sort_values("Date", ascending=False)
    st.dataframe(display, use_container_width=True, hide_index=True, height=420)
    st.download_button("⬇️ Download filtered data (CSV)", data=display.to_csv(index=False).encode("utf-8"), file_name="bank_of_baroda_filtered_data.csv", mime="text/csv")

st.divider()
st.caption("Educational analytics only. Historical market data may contain provider-specific adjustments or limitations. This dashboard is not financial advice and does not provide investment recommendations.")
