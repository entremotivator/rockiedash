import hashlib
from datetime import datetime
from html import escape
from typing import Optional
from urllib.parse import parse_qs, urlparse

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Social with Rocki | Private Dashboard",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="expanded",
)


THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top right, rgba(255,45,120,0.16), transparent 34%),
        radial-gradient(circle at top left, rgba(200,255,0,0.07), transparent 26%),
        linear-gradient(180deg, #12000c 0%, #0d0008 100%) !important;
    font-family: 'Poppins', sans-serif;
    color: #f5d6e8 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #18000f 0%, #28001d 50%, #14000e 100%) !important;
    border-right: 1px solid rgba(255,45,120,0.35) !important;
}
[data-testid="stSidebar"] * { color: #f8cade !important; }
[data-testid="stMain"] { background: transparent !important; }

header, footer, #MainMenu,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeaderActionElements"],
.viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_,
.viewerBadge_link__1S137,
.embeddedAppMetaInfoBar_container__DxxL1 {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

div.block-container {
    padding-top: 1.75rem !important;
    padding-bottom: 2rem !important;
}

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
    border-radius: 14px !important;
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
    border-radius: 999px !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.6rem !important;
    box-shadow: 0 8px 24px rgba(255,45,120,0.28) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    background: linear-gradient(135deg, #ff79b0, #c8ff00) !important;
    color: #0d0008 !important;
}

.stTextInput > div > div > input,
.stMultiSelect > div {
    background: rgba(255,45,120,0.08) !important;
    border: 1px solid rgba(255,45,120,0.35) !important;
    border-radius: 12px !important;
    color: #f5d6e8 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,45,120,0.08) !important;
    border: 1px solid rgba(255,45,120,0.18) !important;
    border-radius: 14px !important;
    padding: 6px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: #ff94be !important;
    font-weight: 700 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #ff2d78, #ff79b0) !important;
    color: #fff !important;
}

.hero-card, .mini-card, .content-card, .login-shell, .login-card {
    border-radius: 20px;
    border: 1px solid rgba(255,45,120,0.22);
}
.hero-card {
    background: linear-gradient(135deg, rgba(255,45,120,0.16) 0%, rgba(200,255,0,0.05) 100%);
    padding: 28px 30px;
    margin-bottom: 18px;
}
.mini-card {
    background: linear-gradient(135deg, rgba(255,45,120,0.1) 0%, rgba(18,0,12,0.98) 100%);
    padding: 14px 16px;
    margin-bottom: 12px;
}
.content-card {
    background: linear-gradient(135deg, rgba(255,45,120,0.1) 0%, rgba(18,0,12,0.98) 100%);
    padding: 20px 22px;
    margin-bottom: 16px;
    box-shadow: 0 12px 36px rgba(0,0,0,0.22);
}
.login-shell {
    max-width: 980px;
    margin: 3rem auto 0;
    padding: 1px;
    background: linear-gradient(135deg, rgba(255,45,120,0.45), rgba(200,255,0,0.18));
}
.login-card {
    background:
        radial-gradient(circle at top right, rgba(255,45,120,0.12), transparent 30%),
        linear-gradient(180deg, #17000f 0%, #0d0008 100%);
    padding: 28px;
}
.eyebrow {
    color: #c8ff00;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}
.muted { color: #d0a0bf; font-size: 0.9rem; }
.content-title {
    color: #fff;
    font-size: 1.02rem;
    font-weight: 700;
    margin: 6px 0 10px;
}
.content-copy {
    color: #f7d7e6;
    line-height: 1.78;
    font-size: 0.91rem;
    white-space: pre-wrap;
    word-break: break-word;
}
.trend-copy {
    color: #ffb3d0;
    line-height: 1.68;
    font-size: 0.83rem;
    white-space: pre-wrap;
    word-break: break-word;
    border-left: 2px solid rgba(255,121,176,0.45);
    padding-left: 12px;
    margin: 10px 0 14px;
}
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
.login-stat {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,45,120,0.12);
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 12px;
}
a { color: #ff79b0 !important; text-decoration: none !important; }
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


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _init_state() -> None:
    defaults = {
        "auth_ok": False,
        "auth_user": None,
        "auth_name": None,
        "auth_role": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _get_sheet_url() -> str:
    try:
        return st.secrets["gsheets"]["url"]
    except Exception:
        return DEFAULT_GSHEET_URL


def _get_auth_users() -> dict[str, dict[str, str]]:
    try:
        users = st.secrets["auth"]["users"]
    except Exception:
        users = {
            "rocki": {
                "name": "Rocki Demo",
                "password": "rocki2026",
                "role": "Admin",
            },
            "maya": {
                "name": "Maya Demo",
                "password": "maya2026",
                "role": "Editor",
            },
            "nina": {
                "name": "Nina Demo",
                "password": "nina2026",
                "role": "Viewer",
            },
        }
    return {str(key): dict(value) for key, value in users.items()}


def _check_login(username: str, password: str) -> bool:
    users = _get_auth_users()
    record = users.get(username.strip())
    if not record:
        return False

    stored_password = str(record.get("password", ""))
    stored_hash = str(record.get("password_hash", ""))
    if stored_hash:
        return _hash_password(password) == stored_hash
    return password == stored_password


def _sign_in(username: str) -> None:
    record = _get_auth_users()[username]
    st.session_state.auth_ok = True
    st.session_state.auth_user = username
    st.session_state.auth_name = record.get("name", username)
    st.session_state.auth_role = record.get("role", "Member")


def _sign_out() -> None:
    for key in ("auth_ok", "auth_user", "auth_name", "auth_role"):
        st.session_state[key] = False if key == "auth_ok" else None
    st.rerun()


@st.cache_data(ttl=120, show_spinner=False)
def _load_public_sheet(sheet_url: str) -> pd.DataFrame:
    return pd.read_csv(_public_csv_url(sheet_url))


def load_live_sheet(sheet_url: str) -> tuple[pd.DataFrame, str]:
    df = _load_public_sheet(sheet_url)
    return df, "Private Access Enabled"


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


def render_login_page() -> None:
    st.markdown(
        """
        <div class="login-shell">
            <div class="login-card">
                <div class="eyebrow">Private Access</div>
                <h1 style="margin:8px 0 10px;">Content vault login</h1>
                <div class="muted">
                    Sign in to access the protected Social with Rocki dashboard.
                    Credentials are loaded from <code>st.secrets</code> so nothing is hard-coded in the app UI.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        st.markdown("### Sign In")
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Unlock Dashboard", use_container_width=True)

        if submitted:
            if _check_login(username, password):
                _sign_in(username.strip())
                st.rerun()
            st.error("Invalid username or password.")

    with right_col:
        users = _get_auth_users()
        st.markdown("### Demo Access")
        st.markdown(
            f"""
            <div class="login-stat">
                <div class="eyebrow">Users In Secrets</div>
                <div class="content-title">{len(users)} demo accounts configured</div>
                <div class="muted">
                    The package includes 3 sample users in the secrets example file.
                    You can replace or remove them before deployment.
                </div>
            </div>
            <div class="login-stat">
                <div class="eyebrow">Secret Keys</div>
                <div class="muted">
                    <code>[auth.users.rocki]</code><br>
                    <code>[auth.users.maya]</code><br>
                    <code>[auth.users.nina]</code>
                </div>
            </div>
            <div class="login-stat">
                <div class="eyebrow">Sheet Access</div>
                <div class="muted">
                    The dashboard still reads the live public Google Sheet in the background,
                    but the link and hosting chrome are hidden from the interface.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar(channel_columns: list[str]) -> tuple[list[str], str]:
    with st.sidebar:
        st.markdown(
            f"""
            <div style='padding:0.5rem 0 0.25rem;'>
                <div class='eyebrow'>Authenticated</div>
                <div style='font-family:"Playfair Display",serif;font-size:1.5rem;color:#fff;margin-top:4px;'>
                    {escape(str(st.session_state.auth_name or "Member"))}
                </div>
                <div class='muted'>{escape(str(st.session_state.auth_role or "User"))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        if st.button("Refresh Live Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        selected_columns = st.multiselect(
            "Visible Categories",
            options=channel_columns,
            default=channel_columns,
        )
        search = st.text_input("Search content", placeholder="Search trend or post text...")

        st.markdown("---")
        if st.button("Sign Out", use_container_width=True):
            _sign_out()

        return selected_columns, search


def render_channel_cards(df: pd.DataFrame, selected_columns: list[str]) -> None:
    st.markdown("### Category Pulse")
    cols = st.columns(2)
    for index, column in enumerate(selected_columns):
        count = int(df[column].astype(str).str.strip().ne("").sum())
        with cols[index % 2]:
            st.markdown(
                f"""
                <div class="mini-card">
                    <div class="eyebrow">Category</div>
                    <div class="content-title">{escape(column)}</div>
                    <div class="muted">{count} full post{'s' if count != 1 else ''} live now</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_post_browser(df: pd.DataFrame, selected_columns: list[str]) -> None:
    st.markdown("### Full Post Cards")

    if not selected_columns:
        st.info("Select at least one category to browse cards.")
        return

    tabs = st.tabs(selected_columns)
    for tab, column in zip(tabs, selected_columns):
        with tab:
            column_df = df[df[column].astype(str).str.strip().ne("")].copy()
            if column_df.empty:
                st.info(f"No posts found for {column}.")
                continue

            for _, row in column_df.iterrows():
                trend_text = str(row.get("trend", "")).strip()
                content_text = str(row.get(column, "")).strip()
                trend_html = escape(trend_text).replace("\n", "<br>")
                content_html = escape(content_text).replace("\n", "<br>")

                trend_block = (
                    f"<div class='trend-copy'>{trend_html}</div>"
                    if trend_text
                    else "<div class='trend-copy'>No trend summary for this row.</div>"
                )

                st.markdown(
                    f"""
                    <div class="content-card">
                        <div class="eyebrow">{escape(column)} Post</div>
                        <div class="content-title">Content Row {row['Row']}</div>
                        {trend_block}
                        <div class="content-copy">{content_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_dashboard() -> None:
    sheet_url = _get_sheet_url()

    try:
        raw_df, source_label = load_live_sheet(sheet_url)
    except Exception as exc:
        st.error(f"Could not load live Google Sheets data: {exc}")
        st.stop()

    post_df = normalize_sheet(raw_df)
    selected_columns, query = render_sidebar(CHANNEL_COLUMNS)

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
            <div class="eyebrow">Protected Dashboard</div>
            <h1 style="margin:8px 0 10px;">Private content command center</h1>
            <div class="muted">
                The public sheet powers the content, but the interface is now gated behind a secrets-based login
                and stripped of visible external branding, chrome, and sheet links.
            </div>
            <div style="margin-top:12px;">
                <span class="pill">{escape(source_label)}</span>
                <span class="pill">Synced {last_sync}</span>
                <span class="pill">{len(filtered_df)} visible rows</span>
                <span class="pill">{escape(str(st.session_state.auth_role or "Member"))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Total Rows", len(post_df))
    metric_2.metric("Visible Rows", len(filtered_df))
    metric_3.metric("Categories", len(CHANNEL_COLUMNS))
    metric_4.metric("Filled Cells", count_filled_cells(post_df, selected_columns))

    left_col, right_col = st.columns([1.45, 0.9], gap="large")
    with left_col:
        render_post_browser(filtered_df, selected_columns)

    with right_col:
        render_channel_cards(post_df, selected_columns)
        st.markdown("### Active Categories")
        if selected_columns:
            st.markdown(
                "".join(f"<span class='pill'>{escape(column)}</span>" for column in selected_columns),
                unsafe_allow_html=True,
            )
        else:
            st.info("Select at least one category to show content.")


_init_state()

if not st.session_state.auth_ok:
    render_login_page()
else:
    render_dashboard()
