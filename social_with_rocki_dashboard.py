
import hashlib
import re
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Rocki Dual Brand Content Studio",
    page_icon="💗",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent
LOCAL_CSV_PATH = APP_DIR / "data" / "rocki_dual_brand_20_trend_content.csv"
LEGACY_CSV_PATH = APP_DIR / "data" / "rocki_cosmetology_7_day_demo_content.csv"
DEFAULT_GSHEET_URL = "https://docs.google.com/spreadsheets/d/13p7C3RIhUZ0yfIcRFbSbfI6YY-P8Lmyn1AWbbQ9K9I8/edit?gid=835739923#gid=835739923"

CHANNEL_COLUMNS = ["Blog", "Newsletter", "Podcast", "Pinterest", "Facebook", "X", "Linkedin", "Tiktok", "IG", "youtube"]
DISPLAY_NAMES = {"Blog":"Blog", "Newsletter":"Newsletter", "Podcast":"Podcast", "Pinterest":"Pinterest", "Facebook":"Facebook", "X":"X / Twitter", "Linkedin":"LinkedIn", "Tiktok":"TikTok", "IG":"Instagram", "youtube":"YouTube"}
PLATFORM_ICONS = {"Blog":"📝", "Newsletter":"💌", "Podcast":"🎙️", "Pinterest":"📌", "Facebook":"👥", "X":"⚡", "Linkedin":"💼", "Tiktok":"🎬", "IG":"📸", "youtube":"▶️"}

BRAND_COLORS = {
    "Social With Rocki": "#8b5cf6",
    "Cosmetology With Rocki": "#e11d74",
    "Both Brands": "#14b8a6",
}

BRAND_STRATEGY = {
    "Social With Rocki": {
        "tagline": "Marketing, content systems, social strategy, and monetization for beauty entrepreneurs.",
        "audience": "Beauty entrepreneurs, salon owners, creators, coaches, service providers, future stylists building visibility.",
        "promise": "Turn ideas into content systems, content into trust, and trust into booked calls, subscribers, clients, and offers.",
        "pillars": ["AI Content Systems", "Search-First Social", "Human Brand Building", "Creator ROI", "Client Proof Content", "Newsletter + Community", "Social Commerce", "AI + Local SEO", "Offer Ladder"],
        "offers": ["7-Day Beauty Content Batch Kit", "Search-First Caption Bank", "Beauty Collaboration ROI Planner", "Salon FAQ + AEO Pack", "LinkedIn Authority Pack", "Human Brand Audit"],
    },
    "Cosmetology With Rocki": {
        "tagline": "Beauty school diary, student survival, salon business lessons, and client-attraction confidence.",
        "audience": "New cosmetology students, beauty school students, future hairstylists, student stylists, future salon owners.",
        "promise": "Help students survive school, build confidence, document the journey, and understand business before graduation.",
        "pillars": ["Student Diary Series", "Hair + Scalp Wellness", "Affordable Haircare Education", "Cut + Consultation Trends", "Beauty School Survival", "Business Behind The Chair", "Marketing Meets Cosmetology"],
        "offers": ["Beauty School Starter Checklist", "Cosmetology Kit Audit Sheet", "State Board Study Habit Planner", "Career Path Comparison Sheet", "Student Stylist Content Confidence Kit"],
    },
}

THEME = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@300;400;500;600;700;800&display=swap');
:root{--bg:#fff7fb;--ink:#24151f;--muted:#765a6d;--pink:#e11d74;--purple:#8b5cf6;--teal:#14b8a6;--cream:#fffaf2;--line:rgba(225,29,116,.16);--shadow:0 18px 48px rgba(120,30,85,.12)}
html, body, [data-testid="stAppViewContainer"]{background:radial-gradient(circle at 8% 0%,rgba(225,29,116,.18),transparent 27%),radial-gradient(circle at 90% 7%,rgba(139,92,246,.17),transparent 30%),linear-gradient(180deg,#fff7fb 0%,#fffaf2 52%,#fff7fb 100%)!important;font-family:'Poppins',sans-serif!important;color:var(--ink)!important}
[data-testid="stMain"]{background:transparent!important} [data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(255,255,255,.97),rgba(255,239,247,.98))!important;border-right:1px solid var(--line)!important;box-shadow:8px 0 36px rgba(225,29,116,.07)}
[data-testid="stSidebar"] *{color:var(--ink)!important} header,footer,#MainMenu,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],[data-testid="stHeaderActionElements"]{display:none!important;visibility:hidden!important;height:0!important}
div.block-container{padding-top:1.25rem!important;padding-bottom:2rem!important;max-width:1560px!important} h1,h2,h3{font-family:'Playfair Display',serif!important;letter-spacing:-.03em} h1{font-size:clamp(2.1rem,4vw,4.9rem)!important;line-height:.95!important;color:var(--ink)!important} h2{color:#3a1630!important} h3{color:var(--pink)!important}
[data-testid="stMetric"]{background:rgba(255,255,255,.78)!important;border:1px solid var(--line)!important;border-radius:24px!important;padding:18px 20px!important;box-shadow:var(--shadow)!important}[data-testid="stMetricValue"]{color:var(--pink)!important;font-family:'Playfair Display',serif!important;font-size:2.28rem!important}[data-testid="stMetricLabel"]{color:var(--muted)!important;font-weight:800!important}
.stButton>button,.stDownloadButton>button,button[kind="primary"]{background:linear-gradient(135deg,var(--pink),var(--purple))!important;color:#fff!important;border:0!important;border-radius:999px!important;font-weight:800!important;padding:.68rem 1.2rem!important;box-shadow:0 10px 28px rgba(225,29,116,.22)!important}.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div{background:rgba(255,255,255,.9)!important;border:1px solid rgba(225,29,116,.18)!important;border-radius:16px!important;color:var(--ink)!important}
.hero-card,.glass-card,.mini-card,.content-card,.action-card{border-radius:28px;border:1px solid var(--line)}.hero-card{position:relative;overflow:hidden;background:radial-gradient(circle at 88% 12%,rgba(20,184,166,.19),transparent 21%),radial-gradient(circle at 10% 8%,rgba(251,113,133,.24),transparent 24%),linear-gradient(135deg,rgba(255,255,255,.93),rgba(255,232,243,.84));padding:clamp(24px,4vw,46px);margin-bottom:18px;box-shadow:var(--shadow)}.glass-card,.mini-card,.content-card,.action-card{background:rgba(255,255,255,.78);box-shadow:var(--shadow);backdrop-filter:blur(14px)}.glass-card{padding:24px;margin-bottom:18px}.mini-card{padding:18px;margin-bottom:14px}.content-card{padding:22px;margin-bottom:18px}.action-card{padding:18px 20px;margin-bottom:14px}
.login-shell{max-width:1050px;margin:3rem auto 0;padding:1px;background:linear-gradient(135deg,rgba(225,29,116,.35),rgba(139,92,246,.26),rgba(20,184,166,.22));box-shadow:var(--shadow);border-radius:28px}.login-card{background:radial-gradient(circle at top right,rgba(225,29,116,.18),transparent 30%),linear-gradient(180deg,#fff,#fff0f7);padding:34px;border-radius:28px}.login-title{font-family:'Playfair Display',serif;font-size:clamp(2.5rem,6vw,5.3rem);font-weight:900;line-height:.92;margin:8px 0 14px;color:var(--ink)}
.eyebrow{color:var(--pink);font-size:.72rem;font-weight:900;letter-spacing:.16em;text-transform:uppercase}.muted{color:var(--muted);font-size:.93rem;line-height:1.65}.content-title{color:var(--ink);font-size:1.08rem;font-weight:900;margin:6px 0 10px}.content-copy{color:#3d2333;line-height:1.78;font-size:.93rem;white-space:pre-wrap;word-break:break-word}.trend-copy{color:#7b365e;line-height:1.66;font-size:.86rem;white-space:pre-wrap;word-break:break-word;border-left:3px solid rgba(225,29,116,.32);padding-left:12px;margin:10px 0 14px}.pill{display:inline-block;border-radius:999px;padding:6px 11px;margin:4px 6px 4px 0;background:rgba(225,29,116,.08);border:1px solid rgba(225,29,116,.16);color:#a41454;font-size:.76rem;font-weight:900}.pill.green{background:rgba(20,184,166,.12);border-color:rgba(20,184,166,.22);color:#0f766e}.pill.purple{background:rgba(139,92,246,.12);border-color:rgba(139,92,246,.2);color:#5b2fc7}.pill.gold{background:rgba(245,158,11,.12);border-color:rgba(245,158,11,.25);color:#92400e}
.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:12px 0 20px}.platform-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin:12px 0 20px}.big-number{font-family:'Playfair Display',serif;font-size:2.25rem;font-weight:900;color:var(--pink);line-height:1}.check-list{margin:0;padding-left:1.1rem}.check-list li{margin-bottom:.55rem;color:#48283b;line-height:1.6}.progress-wrap{width:100%;height:10px;border-radius:999px;background:#f6d9e8;overflow:hidden;margin-top:10px}.progress-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--pink),var(--purple),var(--teal))}.brand-band{height:8px;border-radius:999px;margin-bottom:12px;background:linear-gradient(90deg,var(--pink),var(--purple),var(--teal))}.copybox{font-size:.85rem!important}
@media(max-width:760px){div.block-container{padding-left:1rem!important;padding-right:1rem!important}.hero-card,.glass-card,.content-card{border-radius:22px;padding:20px}.platform-grid,.card-grid{grid-template-columns:1fr}[data-testid="stMetric"]{padding:14px!important}}
</style>
"""
st.markdown(THEME, unsafe_allow_html=True)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _init_state() -> None:
    defaults = {"auth_ok": False, "auth_user": None, "auth_name": None, "auth_role": None, "manual_posts": []}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _get_auth_users() -> dict[str, dict[str, str]]:
    try:
        users = st.secrets["auth"]["users"]
    except Exception:
        users = {"rocki": {"name": "Rocki Demo", "password": "rocki2026", "role": "Admin"}, "maya": {"name": "Maya Demo", "password": "maya2026", "role": "Editor"}}
    return {str(key): dict(value) for key, value in users.items()}


def _check_login(username: str, password: str) -> bool:
    record = _get_auth_users().get(username.strip())
    if not record:
        return False
    stored_hash = str(record.get("password_hash", ""))
    return _hash_password(password) == stored_hash if stored_hash else password == str(record.get("password", ""))


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


def safe_html(text: object) -> str:
    return escape(str(text)).replace("\n", "<br>")


def shorten(text: object, limit: int = 220) -> str:
    clean = " ".join(str(text).split())
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


def extract_hashtags(text: object) -> list[str]:
    return sorted(set(re.findall(r"#[A-Za-z0-9_]+", str(text))))


def score_text(row: pd.Series) -> int:
    blob = " ".join(str(row.get(c, "")) for c in CHANNEL_COLUMNS + ["Trend", "Content Angle", "CTA", "Offer"])
    filled = sum(1 for c in CHANNEL_COLUMNS if str(row.get(c, "")).strip())
    keyword_bonus = sum(1 for k in ["client", "marketing", "student", "business", "school", "content", "brand", "confidence", "search", "offer"] if k in blob.lower())
    return min(10, 2 + min(4, filled // 3) + min(3, len(blob) // 1600) + min(1, keyword_bonus // 4))


@st.cache_data(ttl=120, show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def load_data() -> pd.DataFrame:
    if LOCAL_CSV_PATH.exists():
        df = load_csv(str(LOCAL_CSV_PATH))
    elif LEGACY_CSV_PATH.exists():
        df = load_csv(str(LEGACY_CSV_PATH))
        if "Brand" not in df.columns:
            df.insert(0, "Brand", "Cosmetology With Rocki")
    else:
        df = pd.DataFrame(columns=["Brand", "Trend", "Pillar"] + CHANNEL_COLUMNS)
    for col in ["Brand", "Week", "Day Number", "Pillar", "Trend", "Trend Source", "Search Intent", "Target Audience", "Content Angle", "Hook", "CTA", "Offer"] + CHANNEL_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df.fillna("").astype(str)
    df["Row"] = range(1, len(df) + 1)
    df["Brand"] = df["Brand"].replace({"": "Cosmetology With Rocki"})
    df["Day"] = df.apply(lambda r: f"Week {r.get('Week','1')} • Day {r.get('Day Number', r['Row'])}", axis=1)
    df["Content Pieces"] = df[CHANNEL_COLUMNS].apply(lambda r: int(r.astype(str).str.strip().ne("").sum()), axis=1)
    df["Opportunity Score"] = df.apply(score_text, axis=1)
    manual = pd.DataFrame(st.session_state.get("manual_posts", []))
    if not manual.empty:
        for col in df.columns:
            if col not in manual.columns:
                manual[col] = ""
        manual["Row"] = range(len(df) + 1, len(df) + len(manual) + 1)
        manual["Day"] = manual.apply(lambda r: f"Manual • {r.get('Platform', 'Post')}", axis=1)
        manual["Content Pieces"] = 1
        manual["Opportunity Score"] = 7
        df = pd.concat([df, manual[df.columns]], ignore_index=True)
    return df


def build_long_df(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        for column in CHANNEL_COLUMNS:
            content = str(row.get(column, "")).strip()
            if content:
                rows.append({
                    "Row": row.get("Row", ""),
                    "Day": row.get("Day", ""),
                    "Brand": row.get("Brand", ""),
                    "Pillar": row.get("Pillar", ""),
                    "Platform Key": column,
                    "Platform": DISPLAY_NAMES.get(column, column),
                    "Trend": row.get("Trend", ""),
                    "Trend Source": row.get("Trend Source", ""),
                    "Search Intent": row.get("Search Intent", ""),
                    "Target Audience": row.get("Target Audience", ""),
                    "Content Angle": row.get("Content Angle", ""),
                    "Hook": row.get("Hook", ""),
                    "CTA": row.get("CTA", ""),
                    "Offer": row.get("Offer", ""),
                    "Content": content,
                    "Characters": len(content),
                    "Hashtags": ", ".join(extract_hashtags(content)),
                    "Opportunity Score": int(row.get("Opportunity Score", 0) or 0),
                })
    return pd.DataFrame(rows)


def render_login_page() -> None:
    st.markdown("""
    <div class="login-shell"><div class="login-card">
    <div class="eyebrow">Private Dual Brand Content Studio</div>
    <div class="login-title">Rocki Content System</div>
    <div class="muted">A mobile-friendly Streamlit dashboard for Social With Rocki and Cosmetology With Rocki. Plan trends, write posts, filter platforms, copy captions, and export content batches.</div>
    <div style="margin-top:16px"><span class="pill">Social With Rocki</span><span class="pill green">Cosmetology With Rocki</span><span class="pill purple">20 Trend Rows</span><span class="pill gold">200 Platform Assets</span></div>
    </div></div>
    """, unsafe_allow_html=True)
    left, center, right = st.columns([1,1.1,1])
    with center:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="rocki")
            password = st.text_input("Password", type="password", placeholder="rocki2026")
            submitted = st.form_submit_button("Open Content Studio", use_container_width=True)
        st.caption("Demo login: rocki / rocki2026")
        if submitted:
            if _check_login(username, password):
                _sign_in(username.strip())
                st.rerun()
            st.error("Invalid username or password.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar(df: pd.DataFrame):
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:.5rem 0 .25rem'><div class='eyebrow'>Signed in</div>
        <div style='font-family:"Playfair Display",serif;font-size:1.55rem;color:#27151f;margin-top:4px;font-weight:900'>{escape(str(st.session_state.auth_name or 'Member'))}</div>
        <div class='muted'>{escape(str(st.session_state.auth_role or 'User'))}</div></div>
        """, unsafe_allow_html=True)
        page = st.radio("Pages", ["Dashboard", "Social With Rocki", "Cosmetology With Rocki", "Trend Finder", "Social Content Library", "Content Calendar"], label_visibility="collapsed")
        st.markdown("---")
        brand_options = sorted(df["Brand"].unique()) if not df.empty else ["Social With Rocki", "Cosmetology With Rocki"]
        brands = st.multiselect("Brands", brand_options, default=brand_options)
        platforms = st.multiselect("Platforms", CHANNEL_COLUMNS, default=CHANNEL_COLUMNS, format_func=lambda v: f"{PLATFORM_ICONS.get(v, '•')} {DISPLAY_NAMES.get(v, v)}")
        query = st.text_input("Search", placeholder="AI, kit, clients, state board, TikTok...")
        st.markdown("---")
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear(); st.rerun()
        if st.button("Sign Out", use_container_width=True):
            _sign_out()
    return page, brands, platforms, query


def filtered_rows(df: pd.DataFrame, brands: list[str], query: str) -> pd.DataFrame:
    active = df[df["Brand"].isin(brands)].copy() if brands else df.copy()
    if query.strip():
        cols = ["Brand", "Pillar", "Trend", "Search Intent", "Target Audience", "Content Angle", "Hook", "CTA", "Offer"] + CHANNEL_COLUMNS
        mask = active[cols].apply(lambda c: c.astype(str).str.contains(query.strip(), case=False, na=False))
        active = active[mask.any(axis=1)]
    return active.reset_index(drop=True)


def render_hero(title: str, subtitle: str, badges: list[str]) -> None:
    badge_html = "".join(f"<span class='pill'>{escape(str(b))}</span>" for b in badges)
    st.markdown(f"""
    <div class="hero-card"><div class="eyebrow">Rocki Dual Brand Studio</div>
    <h1 style="margin:8px 0 12px">{escape(title)}</h1>
    <div class="muted" style="max-width:920px">{escape(subtitle)}</div>
    <div style="margin-top:14px">{badge_html}</div></div>
    """, unsafe_allow_html=True)


def render_metrics(df: pd.DataFrame, long_df: pd.DataFrame) -> None:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Trend Rows", len(df))
    c2.metric("Platform Assets", len(long_df))
    c3.metric("Brands", df["Brand"].nunique() if not df.empty else 0)
    c4.metric("Avg Score", round(float(df["Opportunity Score"].mean()), 1) if not df.empty else 0)
    c5.metric("Total Chars", f"{int(long_df['Characters'].sum()):,}" if not long_df.empty else "0")


def render_dashboard(df: pd.DataFrame, brands: list[str], platforms: list[str], query: str) -> None:
    active = filtered_rows(df, brands, query)
    long_df = build_long_df(active)
    if platforms:
        long_df = long_df[long_df["Platform Key"].isin(platforms)] if not long_df.empty else long_df
    render_hero("Dual Brand Command Center", "Plan and manage two connected content lanes: Social With Rocki for marketing systems and Cosmetology With Rocki for beauty school, student survival, and salon business education.", ["Social + Cosmetology", "Trend-ready", f"Updated {datetime.now().strftime('%b %d, %Y')}"])
    render_metrics(active, long_df)
    left, right = st.columns([1.35, .95], gap="large")
    with left:
        st.markdown("### Brand Content Mix")
        if not active.empty:
            chart = active.groupby("Brand")[["Content Pieces", "Opportunity Score"]].mean()
            st.bar_chart(chart)
        st.markdown("### Highest Opportunity Trends")
        table = active.sort_values("Opportunity Score", ascending=False)[["Brand", "Pillar", "Trend", "Search Intent", "Offer", "Opportunity Score"]]
        st.dataframe(table, use_container_width=True, hide_index=True, column_config={"Trend": st.column_config.TextColumn(width="large"), "Search Intent": st.column_config.TextColumn(width="large"), "Opportunity Score": st.column_config.ProgressColumn(min_value=0, max_value=10)})
    with right:
        st.markdown("### What To Post Next")
        actions = [
            ("Social With Rocki", "Post AI-assisted content batching first. It connects the marketing audience to an immediate workflow and a sellable template."),
            ("Cosmetology With Rocki", "Post the student diary and kit audit first. These are highly relatable and beginner-friendly."),
            ("Both Brands", "Cross-link the lanes: every beauty school lesson becomes a marketing lesson, and every marketing lesson becomes a student content prompt."),
            ("Monetization", "Attach one freebie to every 3-5 posts: checklist, caption bank, study planner, or offer ladder."),
        ]
        for title, body in actions:
            st.markdown(f"<div class='action-card'><div class='content-title'>{escape(title)}</div><div class='muted'>{escape(body)}</div></div>", unsafe_allow_html=True)
        st.markdown("### Platform Count")
        if not long_df.empty:
            st.dataframe(long_df["Platform"].value_counts().reset_index().rename(columns={"Platform":"Platform", "count":"Assets"}), use_container_width=True, hide_index=True)


def render_brand_page(df: pd.DataFrame, brand: str) -> None:
    active = df[df["Brand"] == brand].copy()
    info = BRAND_STRATEGY[brand]
    render_hero(brand, info["tagline"], ["Audience: " + info["audience"][:45] + "...", f"{len(active)} Trend Rows", f"{sum(active['Content Pieces'].astype(int))} Assets"])
    st.markdown("### Brand Positioning")
    st.markdown(f"""
    <div class='glass-card'><div class='brand-band'></div>
    <div class='content-title'>Promise</div><div class='content-copy'>{safe_html(info['promise'])}</div>
    <div style='margin-top:12px'><span class='pill green'>{safe_html(info['audience'])}</span></div></div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([1,1], gap="large")
    with col1:
        st.markdown("### Pillars")
        html = "<div class='card-grid'>"
        for p in info["pillars"]:
            count = int((active["Pillar"] == p).sum())
            html += f"<div class='mini-card'><div class='big-number'>{count}</div><div class='content-title'>{escape(p)}</div><div class='muted'>Content lane for {escape(brand)}.</div></div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
    with col2:
        st.markdown("### Offer Ladder")
        st.markdown("<div class='glass-card'>" + "".join(f"<span class='pill purple'>{escape(o)}</span>" for o in info["offers"]) + "</div>", unsafe_allow_html=True)
        st.markdown("### Best CTA Framework")
        st.markdown("""
        <div class='glass-card'><ul class='check-list'>
        <li>Hook the exact pain point.</li><li>Make one useful promise.</li><li>Teach one practical step.</li><li>Invite a comment keyword.</li><li>Send the audience to a checklist, template, planner, or audit.</li>
        </ul></div>
        """, unsafe_allow_html=True)
    st.markdown("### Trend Cards")
    for _, row in active.iterrows():
        st.markdown(f"""
        <div class='content-card'><div class='eyebrow'>{safe_html(row['Pillar'])}</div>
        <div class='content-title'>{safe_html(row['Trend'])}</div>
        <div class='trend-copy'><b>Hook:</b> {safe_html(row['Hook'])}<br><b>Angle:</b> {safe_html(row['Content Angle'])}<br><b>Offer:</b> {safe_html(row['Offer'])}</div>
        <span class='pill'>Score {safe_html(row['Opportunity Score'])}/10</span><span class='pill green'>{safe_html(row['Content Pieces'])} assets</span></div>
        """, unsafe_allow_html=True)


def render_trend_finder(df: pd.DataFrame) -> None:
    render_hero("Trend Finder", "A ranked trend board with search intent, content angle, CTA, offer, and brand fit for both Rocki content lanes.", ["10 Social Trends", "10 Cosmetology Trends", "Ready to post"])
    b1, b2, b3 = st.columns([1,1,1])
    with b1: brand_filter = st.multiselect("Brand", sorted(df["Brand"].unique()), default=sorted(df["Brand"].unique()))
    with b2: pillar_filter = st.multiselect("Pillar", sorted(df["Pillar"].unique()), default=sorted(df["Pillar"].unique()))
    with b3: min_score = st.slider("Minimum Score", 0, 10, 0)
    active = df[df["Brand"].isin(brand_filter) & df["Pillar"].isin(pillar_filter) & (df["Opportunity Score"].astype(int) >= min_score)].copy()
    st.download_button("Download Trend Board CSV", data=active.to_csv(index=False).encode("utf-8"), file_name="rocki_dual_brand_trend_board.csv", mime="text/csv", use_container_width=True)
    for _, row in active.sort_values(["Brand", "Opportunity Score"], ascending=[True, False]).iterrows():
        st.markdown(f"""
        <div class='content-card'><div class='eyebrow'>{safe_html(row['Brand'])} • {safe_html(row['Pillar'])}</div>
        <div class='content-title'>{safe_html(row['Trend'])}</div>
        <div class='trend-copy'><b>Trend signal:</b> {safe_html(row['Trend Source'])}<br><b>Search intent:</b> {safe_html(row['Search Intent'])}<br><b>Audience:</b> {safe_html(row['Target Audience'])}<br><b>Content angle:</b> {safe_html(row['Content Angle'])}<br><b>CTA:</b> {safe_html(row['CTA'])}</div>
        <span class='pill purple'>Offer: {safe_html(row['Offer'])}</span><span class='pill'>Score {safe_html(row['Opportunity Score'])}/10</span></div>
        """, unsafe_allow_html=True)


def render_social_library(df: pd.DataFrame, brands: list[str], platforms: list[str], query: str) -> None:
    active_rows = filtered_rows(df, brands, query)
    long_df = build_long_df(active_rows)
    if platforms:
        long_df = long_df[long_df["Platform Key"].isin(platforms)] if not long_df.empty else long_df
    render_hero("Social Content Library", "Copy-ready posts for both brands across Blog, Newsletter, Podcast, Pinterest, Facebook, X, LinkedIn, TikTok, Instagram, and YouTube.", ["Copy-ready", "Exportable", "Longer captions", "Mobile-first"])
    if long_df.empty:
        st.info("No content matches the current filters."); return
    left, mid, right = st.columns([1,1,1])
    with left: pfilter = st.multiselect("Library Platform", sorted(long_df["Platform"].unique()), default=sorted(long_df["Platform"].unique()))
    with mid: brand_filter = st.multiselect("Library Brand", sorted(long_df["Brand"].unique()), default=sorted(long_df["Brand"].unique()))
    with right: min_chars = st.slider("Minimum Characters", 0, int(max(1000, long_df["Characters"].max())), 0)
    active = long_df[long_df["Platform"].isin(pfilter) & long_df["Brand"].isin(brand_filter) & (long_df["Characters"] >= min_chars)].copy()
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Active Assets", len(active)); m2.metric("Brands", active["Brand"].nunique()); m3.metric("Platforms", active["Platform"].nunique()); m4.metric("Avg Chars", int(active["Characters"].mean()) if not active.empty else 0)
    export_cols = ["Day", "Brand", "Platform", "Pillar", "Trend", "Hook", "CTA", "Offer", "Content", "Characters", "Hashtags", "Opportunity Score"]
    st.download_button("Download Active Social Content CSV", data=active[export_cols].to_csv(index=False).encode("utf-8"), file_name="rocki_dual_brand_social_content.csv", mime="text/csv", use_container_width=True)
    st.markdown("### Add New Post To This Session")
    with st.expander("Create a manual social post", expanded=False):
        with st.form("manual_post_form"):
            c1,c2,c3 = st.columns(3)
            brand = c1.selectbox("Brand", ["Social With Rocki", "Cosmetology With Rocki"])
            platform = c2.selectbox("Platform", CHANNEL_COLUMNS, format_func=lambda v: DISPLAY_NAMES.get(v, v))
            pillar = c3.text_input("Pillar", value="Manual Post")
            trend = st.text_input("Trend / Topic", value="")
            content = st.text_area("Post Content", height=190, value="")
            cta = st.text_input("CTA", value="")
            submitted = st.form_submit_button("Add Post To Social Content", use_container_width=True)
        if submitted and content.strip():
            record = {"Brand": brand, "Week": "Manual", "Day Number": str(len(st.session_state.manual_posts)+1), "Pillar": pillar, "Trend": trend, "CTA": cta, "Offer": "Manual", "Content Pieces": 1, "Opportunity Score": 7}
            for col in CHANNEL_COLUMNS: record[col] = content if col == platform else ""
            st.session_state.manual_posts.append(record)
            st.success("Post added to this session. It will appear in the library and exports.")
            st.rerun()
    st.markdown("### Copy-Ready Cards")
    for idx, row in active.reset_index(drop=True).iterrows():
        icon = PLATFORM_ICONS.get(str(row.get("Platform Key", "")), "✨")
        st.markdown(f"""
        <div class='content-card'><div class='eyebrow'>{safe_html(row['Brand'])} • {safe_html(row['Day'])} • {safe_html(row['Pillar'])}</div>
        <div class='content-title'>{icon} {safe_html(row['Platform'])}: {safe_html(row['Trend'])}</div>
        <div class='trend-copy'><b>Hook:</b> {safe_html(row['Hook'])}<br><b>CTA:</b> {safe_html(row['CTA'])}<br><b>Offer:</b> {safe_html(row['Offer'])}</div>
        <span class='pill purple'>{safe_html(row['Characters'])} chars</span><span class='pill'>Score {safe_html(row['Opportunity Score'])}/10</span><span class='pill green'>{safe_html(row['Hashtags'])}</span></div>
        """, unsafe_allow_html=True)
        st.text_area("Copy content", value=str(row["Content"]), height=240 if int(row["Characters"]) > 900 else 170, key=f"copy_{row['Row']}_{row['Platform Key']}_{idx}", label_visibility="collapsed")
    st.markdown("### Planning Table")
    st.dataframe(active[export_cols], use_container_width=True, hide_index=True, column_config={"Trend": st.column_config.TextColumn(width="large"), "Content": st.column_config.TextColumn(width="large"), "Opportunity Score": st.column_config.ProgressColumn(min_value=0, max_value=10)})


def render_calendar(df: pd.DataFrame) -> None:
    render_hero("Content Calendar", "A simple two-week publishing plan that balances Social With Rocki and Cosmetology With Rocki without overwhelming the audience.", ["2-week plan", "Daily priority", "Repurpose-friendly"])
    records = []
    for _, row in df.iterrows():
        records.append({
            "Week": row.get("Week", ""), "Day": row.get("Day Number", ""), "Brand": row.get("Brand", ""), "Primary Platform": "TikTok + IG" if row.get("Brand") == "Cosmetology With Rocki" else "LinkedIn + IG", "Trend": row.get("Trend", ""), "Repurpose": "Carousel, newsletter, YouTube short, Pinterest pin", "CTA": row.get("CTA", ""), "Offer": row.get("Offer", "")
        })
    cal = pd.DataFrame(records)
    st.dataframe(cal, use_container_width=True, hide_index=True, column_config={"Trend": st.column_config.TextColumn(width="large"), "Repurpose": st.column_config.TextColumn(width="medium")})
    st.download_button("Download Content Calendar CSV", data=cal.to_csv(index=False).encode("utf-8"), file_name="rocki_dual_brand_content_calendar.csv", mime="text/csv", use_container_width=True)


def render_app():
    df = load_data()
    page, brands, platforms, query = render_sidebar(df)
    if page == "Dashboard": render_dashboard(df, brands, platforms, query)
    elif page == "Social With Rocki": render_brand_page(df, "Social With Rocki")
    elif page == "Cosmetology With Rocki": render_brand_page(df, "Cosmetology With Rocki")
    elif page == "Trend Finder": render_trend_finder(df)
    elif page == "Social Content Library": render_social_library(df, brands, platforms, query)
    else: render_calendar(filtered_rows(df, brands, query))


_init_state()
if not st.session_state.auth_ok:
    render_login_page()
else:
    render_app()

