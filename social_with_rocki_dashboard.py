import json
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

.stSelectbox > div > div, .stMultiSelect > div, .stTextInput > div > div > input {
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

.hero-card, .glass-card, .post-type-card {
    border-radius: 16px;
    border: 1px solid rgba(255,45,120,0.25);
}
.hero-card {
    background: linear-gradient(135deg, rgba(255,45,120,0.18) 0%, rgba(200,255,0,0.05) 100%);
    padding: 24px 28px;
    margin-bottom: 18px;
}
.glass-card {
    background: rgba(255,45,120,0.06);
    padding: 18px 20px;
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

DEFAULT_POST_TYPES = [
    "Carousel",
    "Reel",
    "Story",
    "Static Post",
    "Thread",
    "Newsletter",
    "Blog Post",
    "Podcast",
    "Short Video",
    "Long Video",
]

DISPLAY_PRIORITY = [
    "Title",
    "Platform",
    "Post Type",
    "Status",
    "Publish Date",
    "Caption",
    "Notes",
    "Tags",
]

ALIASES = {
    "title": ["title", "post title", "name", "topic"],
    "platform": ["platform", "channel", "network"],
    "post_type": ["post type", "content type", "type", "format"],
    "status": ["status", "stage"],
    "publish_date": ["publish date", "date", "scheduled date", "publish"],
    "caption": ["caption", "copy", "description", "post copy"],
    "notes": ["notes", "idea", "brief"],
    "tags": ["tags", "hashtags", "keywords"],
}


def _normalize_header(value: str) -> str:
    return " ".join(str(value).strip().lower().replace("_", " ").split())


def _find_column(df: pd.DataFrame, key: str) -> Optional[str]:
    wanted = {_normalize_header(alias) for alias in ALIASES[key]}
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


def _get_service_account() -> Optional[dict]:
    try:
        return dict(st.secrets["gcp_service_account"])
    except Exception:
        return None


@st.cache_data(ttl=120, show_spinner=False)
def _load_public_sheet(sheet_url: str) -> pd.DataFrame:
    return pd.read_csv(_public_csv_url(sheet_url))


@st.cache_data(ttl=120, show_spinner=False)
def _load_private_sheet(sheet_url: str, creds_json: str) -> pd.DataFrame:
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scopes)
    client = gspread.authorize(creds)
    workbook = client.open_by_url(sheet_url)
    try:
        worksheet_name = st.secrets["gsheets"]["worksheet"]
    except Exception:
        worksheet_name = None
    worksheet = workbook.worksheet(worksheet_name) if worksheet_name else workbook.sheet1
    return pd.DataFrame(worksheet.get_all_records())


def load_live_sheet(sheet_url: str) -> tuple[pd.DataFrame, str]:
    creds = _get_service_account()
    if creds:
        try:
            df = _load_private_sheet(sheet_url, json.dumps(creds))
            return df, "Google service account"
        except Exception as exc:
            st.warning(f"Private sheet login failed, trying public CSV instead: {exc}")

    df = _load_public_sheet(sheet_url)
    return df, "Public CSV feed"


def normalize_sheet(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data.columns = [str(col).strip() for col in data.columns]

    mapped = {}
    for key in ALIASES:
        mapped[key] = _find_column(data, key)

    normalized = pd.DataFrame()
    normalized["Title"] = data[mapped["title"]] if mapped["title"] else ""
    normalized["Platform"] = data[mapped["platform"]] if mapped["platform"] else "Unknown"
    normalized["Post Type"] = data[mapped["post_type"]] if mapped["post_type"] else "Uncategorized"
    normalized["Status"] = data[mapped["status"]] if mapped["status"] else "Live"
    normalized["Publish Date"] = data[mapped["publish_date"]] if mapped["publish_date"] else ""
    normalized["Caption"] = data[mapped["caption"]] if mapped["caption"] else ""
    normalized["Notes"] = data[mapped["notes"]] if mapped["notes"] else ""
    normalized["Tags"] = data[mapped["tags"]] if mapped["tags"] else ""

    normalized = normalized.fillna("")
    normalized["Title"] = normalized["Title"].astype(str).replace("", "Untitled")
    normalized["Platform"] = normalized["Platform"].astype(str).replace("", "Unknown")
    normalized["Post Type"] = normalized["Post Type"].astype(str).replace("", "Uncategorized")
    normalized["Status"] = normalized["Status"].astype(str).replace("", "Live")

    if normalized["Publish Date"].astype(str).str.strip().any():
        normalized["_publish_sort"] = pd.to_datetime(normalized["Publish Date"], errors="coerce")
    else:
        normalized["_publish_sort"] = pd.NaT

    normalized["_row_order"] = range(len(normalized))
    normalized = normalized.sort_values(
        by=["_publish_sort", "_row_order"],
        ascending=[False, False],
        na_position="last",
    )
    return normalized.reset_index(drop=True)


def available_post_types(df: pd.DataFrame) -> list[str]:
    live_types = [
        str(value).strip()
        for value in df.get("Post Type", pd.Series(dtype=str)).dropna().unique().tolist()
        if str(value).strip()
    ]
    chosen = live_types[:10]
    if len(chosen) < 10:
        for fallback in DEFAULT_POST_TYPES:
            if fallback not in chosen:
                chosen.append(fallback)
            if len(chosen) == 10:
                break
    return chosen


def render_sidebar(
    data_source: str,
    sheet_url: str,
    post_types: list[str],
    platforms: list[str],
) -> tuple[list[str], list[str], str]:
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
        platform_filter = st.multiselect(
            "Platform",
            options=platforms,
            default=platforms,
        )
        post_type_filter = st.multiselect(
            "Post Type",
            options=post_types,
            default=post_types,
        )
        search = st.text_input("Search title", placeholder="Search a post title...")
        return platform_filter, post_type_filter, search


def render_post_type_cards(df: pd.DataFrame, selected_types: list[str]) -> None:
    st.markdown("### Top 10 Post Types")
    counts = (
        df[df["Post Type"].isin(selected_types)]["Post Type"]
        .value_counts()
        .reindex(selected_types, fill_value=0)
    )
    cols = st.columns(2)
    for index, (post_type, count) in enumerate(counts.items()):
        with cols[index % 2]:
            st.markdown(
                f"""
                <div class="post-type-card">
                    <div class="eyebrow">Post Type</div>
                    <div style="font-size:1.05rem; font-weight:700; color:#fff; margin:6px 0 4px;">
                        {post_type}
                    </div>
                    <div class="muted">{count} live post{'s' if count != 1 else ''}</div>
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
post_types = available_post_types(post_df)
platform_options = sorted(post_df["Platform"].dropna().astype(str).unique().tolist())
platforms, selected_types, query = render_sidebar(
    source_label,
    sheet_url,
    post_types,
    platform_options,
)

filtered_df = post_df.copy()
if platforms:
    filtered_df = filtered_df[filtered_df["Platform"].isin(platforms)]
if selected_types:
    filtered_df = filtered_df[filtered_df["Post Type"].isin(selected_types)]
if query.strip():
    filtered_df = filtered_df[
        filtered_df["Title"].str.contains(query.strip(), case=False, na=False)
    ]

filtered_df = filtered_df.reset_index(drop=True)
last_sync = datetime.now().strftime("%b %d, %Y %I:%M %p")

st.markdown(
    f"""
    <div class="hero-card">
        <div class="eyebrow">Live Content Dashboard</div>
        <h1 style="margin:6px 0 8px;">Google Sheets, simplified.</h1>
        <div class="muted">
            This version only shows live sheet data, keeps the original Rocki theme,
            and focuses on 10 post types for a cleaner content view.
        </div>
        <div style="margin-top:12px;">
            <span class="pill">{source_label}</span>
            <span class="pill">Synced {last_sync}</span>
            <span class="pill">{len(filtered_df)} visible posts</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Total Posts", len(post_df))
metric_2.metric("Visible Posts", len(filtered_df))
metric_3.metric("Platforms", post_df["Platform"].nunique())
metric_4.metric("Post Types", len(post_types))

left_col, right_col = st.columns([1.4, 1])
with left_col:
    st.markdown("### Live Sheet Data")
    display_columns = [col for col in DISPLAY_PRIORITY if col in filtered_df.columns]
    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )

with right_col:
    render_post_type_cards(post_df, post_types)

st.markdown("### Current Filters")
if selected_types:
    st.markdown(
        "".join(f"<span class='pill'>{post_type}</span>" for post_type in selected_types),
        unsafe_allow_html=True,
    )
else:
    st.info("Select at least one post type to show rows.")
