from datetime import datetime
from typing import Optional
from urllib.parse import parse_qs, urlparse

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Social with Rocki | Live Sheet",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="expanded",
)


THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0d0008 !important;
    font-family: 'Poppins', sans-serif;
    color: #f5d6e8 !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a0012 0%, #2d0020 50%, #1a0012 100%) !important;
    border-right: 1px solid #ff2d78 !important;
}
[data-testid="stSidebar"] * { color: #f9c6df !important; }
[data-testid="stMain"] { background: transparent !important; }

h1 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, #ff2d78, #ff79b0, #c8ff00, #ff2d78);
    background-size: 300% 100%;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    animation: shimmer 4s linear infinite;
}
h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #ff79b0 !important;
}
@keyframes shimmer { 0% { background-position: 0% 50% } 100% { background-position: 300% 50% } }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(255,45,120,0.15) 0%, rgba(200,255,0,0.05) 100%) !important;
    border: 1px solid rgba(255,45,120,0.4) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
[data-testid="stMetricValue"] {
    color: #c8ff00 !important;
    font-family: 'Playfair Display', serif !important;
}
[data-testid="stMetricLabel"] {
    color: #ff79b0 !important;
    font-weight: 600 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff2d78, #ff79b0) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 30px !important;
    font-weight: 700 !important;
    padding: 0.5rem 1.6rem !important;
    box-shadow: 0 4px 20px rgba(255,45,120,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    background: linear-gradient(135deg, #ff79b0, #c8ff00) !important;
    color: #0d0008 !important;
}

.stMultiSelect > div, .stTextInput > div > div > input {
    background: rgba(255,45,120,0.08) !important;
    border: 1px solid rgba(255,45,120,0.35) !important;
    border-radius: 10px !important;
    color: #f5d6e8 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,45,120,0.25) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}

.hero-card, .post-type-card {
    border-radius: 16px;
    border: 1px solid rgba(255,45,120,0.25);
}
.hero-card {
    background: linear-gradient(135deg, rgba(255,45,120,0.18) 0%, rgba(200,255,0,0.05) 100%);
    padding: 24px 28px;
    margin-bottom: 18px;
}
.post-type-card {
    background: linear-gradient(135deg, rgba(255,45,120,0.09) 0%, rgba(20,0,15,0.95) 100%);
    padding: 14px 16px;
    margin-bottom: 10px;
}
.eyebrow {
    color: #c8ff00;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}
.muted { color: #d0a0bf; font-size: 0.88rem; }
.pill {
    display: inline-block;
    border-radius: 999px;
    padding: 4px 10px;
    margin: 3px 6px 3px 0;
    background: rgba(255,45,120,0.14);
    border: 1px solid rgba(255,45,120,0.25);
    color: #ff79b0;
    font-size: 0.75rem;
    font-weight: 600;
}
a { color: #ff79b0 !important; }
</style>
"""
st.markdown(THEME, unsafe_allow_html=True)


DEFAULT_GSHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "13p7C3RIhUZ0yfIcRFbSbfI6YY-P8Lmyn1AWbbQ9K9I8/edit?gid=1657643948#gid=1657643948"
)

CHANNEL_COLUMNS = [
    "Blog",
    "Newsletter",
    "Podcast",
    "Pinterest",
    "Facebook",
    "X",
    "Linkedin",
    "Tiktok",
    "IG",
    "youtube",
]

COLUMN_ALIASES = {
    "trend": ["trend", "topic", "idea", "prompt"],
    "Blog": ["blog"],
    "Newsletter": ["newsletter"],
    "Podcast": ["podcast"],
    "Pinterest": ["pinterest"],
    "Facebook": ["facebook"],
    "X": ["x", "twitter"],
    "Linkedin": ["linkedin"],
    "Tiktok": ["tiktok", "tik tok", "tik-tok"],
    "IG": ["ig", "instagram"],
    "youtube": ["youtube", "you tube"],
}


def _normalize_header(value: str) -> str:
    return " ".join(str(value).strip().lower().replace("_", " ").split())


def _find_alias_column(df: pd.DataFrame, aliases: list[str]) -> Optional[str]:
    wanted = {_normalize_header(alias) for alias in aliases}
    for col in df.columns:
        if _normalize_header(col) in wanted:
            return col
    return None


def _extract_sheet_parts(sheet_url: str) -> tuple[str, Optional[str]]:
    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
    parsed = urlparse(sheet_url)
    query_gid = parse_qs(parsed.query).get("gid", [None])[0]
    hash_gid = parsed.fragment.replace("gid=", "") if "gid=" in parsed.fragment else None
    return sheet_id, query_gid or hash_gid


def _public_csv_url(sheet_url: str) -> str:
    sheet_id, gid = _extract_sheet_parts(sheet_url)
    gid_part = f"&gid={gid}" if gid else ""
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv{gid_part}"


def _get_sheet_url() -> str:
    try:
        return st.secrets["gsheets"]["url"]
    except Exception:
        return DEFAULT_GSHEET_URL


@st.cache_data(ttl=120, show_spinner=False)
def _load_public_sheet(sheet_url: str) -> pd.DataFrame:
    return pd.read_csv(_public_csv_url(sheet_url))


def load_live_sheet(sheet_url: str) -> tuple[pd.DataFrame, str]:
    df = _load_public_sheet(sheet_url)
    return df, "Public Google Sheet"


def normalize_sheet(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data.columns = [str(col).strip() for col in data.columns]

    normalized = pd.DataFrame()
    trend_col = _find_alias_column(data, COLUMN_ALIASES["trend"])
    normalized["trend"] = data[trend_col] if trend_col else ""

    for column in CHANNEL_COLUMNS:
        source_col = _find_alias_column(data, COLUMN_ALIASES[column])
        normalized[column] = data[source_col] if source_col else ""

    normalized = normalized.fillna("").astype(str)
    normalized.insert(0, "Row", range(1, len(normalized) + 1))
    return normalized.reset_index(drop=True)


def count_filled_cells(df: pd.DataFrame, columns: list[str]) -> int:
    if not columns:
        return 0
    return int(df[columns].apply(lambda col: col.astype(str).str.strip().ne("")).sum().sum())


def render_sidebar(
    data_source: str,
    sheet_url: str,
    channel_columns: list[str],
) -> tuple[list[str], str]:
    with st.sidebar:
        st.markdown(
            """
            <div style='text-align:center; padding: 1rem 0 0.5rem;'>
                <div style='font-family:"Playfair Display",serif; font-size:1.7rem;
                            background:linear-gradient(90deg,#ff2d78,#ff79b0,#c8ff00);
                            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                            font-weight:900; line-height:1.15;'>
                    Social with<br>Rocki 💗
                </div>
                <div style='color:#ff79b0; font-size:0.7rem; letter-spacing:0.15em;
                            text-transform:uppercase; margin-top:4px;'>
                    Live Google Sheet View
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.caption(f"Source: {data_source}")
        st.markdown(f"[Open Google Sheet]({sheet_url})")

        if st.button("Refresh Live Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")
        selected_columns = st.multiselect(
            "Live Columns",
            options=channel_columns,
            default=channel_columns,
        )
        search = st.text_input("Search trend or content", placeholder="Search across live sheet...")
        return selected_columns, search


def render_channel_cards(df: pd.DataFrame, selected_columns: list[str]) -> None:
    st.markdown("### Live Column Counts")
    cols = st.columns(2)
    for index, column in enumerate(selected_columns):
        count = int(df[column].astype(str).str.strip().ne("").sum())
        with cols[index % 2]:
            st.markdown(
                f"""
                <div class="post-type-card">
                    <div class="eyebrow">Live Column</div>
                    <div style="font-size:1.05rem; font-weight:700; color:#fff; margin:6px 0 4px;">
                        {column}
                    </div>
                    <div class="muted">{count} filled cell{'s' if count != 1 else ''}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


sheet_url = _get_sheet_url()

try:
    raw_df, source_label = load_live_sheet(sheet_url)
except Exception as exc:
    st.markdown("# Social with Rocki")
    st.error(f"Could not load Google Sheets data: {exc}")
    st.stop()

post_df = normalize_sheet(raw_df)
selected_columns, query = render_sidebar(source_label, sheet_url, CHANNEL_COLUMNS)

filtered_df = post_df.copy()
if query.strip():
    searchable_columns = ["trend"] + selected_columns
    search_mask = filtered_df[searchable_columns].apply(
        lambda col: col.astype(str).str.contains(query.strip(), case=False, na=False)
    )
    filtered_df = filtered_df[search_mask.any(axis=1)]

filtered_df = filtered_df.reset_index(drop=True)
last_sync = datetime.now().strftime("%b %d, %Y %I:%M %p")

st.markdown(
    f"""
    <div class="hero-card">
        <div class="eyebrow">Live Content Dashboard</div>
        <h1 style="margin:6px 0 8px;">Google Sheets, simplified.</h1>
        <div class="muted">
            This version uses the exact live sheet columns you shared:
            Blog, Newsletter, Podcast, Pinterest, Facebook, X, Linkedin, Tiktok, IG, youtube, and trend.
        </div>
        <div style="margin-top:12px;">
            <span class="pill">{source_label}</span>
            <span class="pill">Synced {last_sync}</span>
            <span class="pill">{len(filtered_df)} visible rows</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Total Rows", len(post_df))
metric_2.metric("Visible Rows", len(filtered_df))
metric_3.metric("Live Columns", len(CHANNEL_COLUMNS))
metric_4.metric("Filled Cells", count_filled_cells(post_df, selected_columns))

left_col, right_col = st.columns([1.4, 1])
with left_col:
    st.markdown("### Live Sheet Data")
    display_columns = ["Row", "trend"] + selected_columns
    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )

with right_col:
    render_channel_cards(post_df, selected_columns)

st.markdown("### Active Columns")
if selected_columns:
    st.markdown(
        "".join(f"<span class='pill'>{column}</span>" for column in selected_columns),
        unsafe_allow_html=True,
    )
else:
    st.info("Select at least one live column to show data.")

