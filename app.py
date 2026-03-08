"""
app.py — Safeguard AI v2.0  |  Business-Ready Cyber Harassment Detection Platform
"""

import io
import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analyzer import analyze_comments
from fir_generator import generate_fir_pdf, generate_batch_fir_pdf
from scraper import DEMO_COMMENTS

# ═══════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Safeguard AI — Cyber Harassment Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Hero ─────────────────────────────────────────────────────────── */
.hero-wrap {
    background: linear-gradient(135deg, #0a0118 0%, #1a0533 40%, #0f1a3a 100%);
    border-radius: 20px;
    padding: 2.8rem 3rem 2.2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 48px rgba(0,0,0,.5);
    border: 1px solid rgba(138,43,226,.25);
}
.hero-wrap::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(138,43,226,.35) 0%, transparent 70%);
}
.hero-wrap::after {
    content: '';
    position: absolute;
    bottom: -80px; left: 20%;
    width: 320px; height: 200px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(30,80,200,.25) 0%, transparent 70%);
}
.hero-title {
    font-size: 2.7rem;
    font-weight: 900;
    background: linear-gradient(90deg, #ffffff 0%, #c084fc 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0; letter-spacing: -1px;
}
.hero-sub {
    color: #9ca3af;
    font-size: 1rem;
    margin-top: .5rem;
    font-weight: 400;
}
.hero-badges {
    margin-top: 1.2rem;
    display: flex;
    gap: .6rem;
    flex-wrap: wrap;
}
.badge-pill {
    background: rgba(138,43,226,.18);
    border: 1px solid rgba(138,43,226,.4);
    color: #c084fc;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: .78rem;
    font-weight: 600;
    letter-spacing: .4px;
}

/* ── Metric Cards ─────────────────────────────────────────────────── */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.kpi-card {
    background: linear-gradient(145deg, #111827, #1f2937);
    border: 1px solid #374151;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,.3);
    transition: transform .2s;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-label { color: #6b7280; font-size: .75rem; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600; }
.kpi-value { font-size: 2.2rem; font-weight: 800; margin-top: .3rem; }
.kpi-delta { font-size: .78rem; margin-top: .2rem; font-weight: 500; }

/* ── Severity Badges ──────────────────────────────────────────────── */
.sev-badge {
    display: inline-block; padding: 4px 14px;
    border-radius: 20px; font-size: .8rem; font-weight: 700; letter-spacing: .5px;
}
.sev-low    { background: rgba(34,197,94,.12);  color: #4ade80; border: 1px solid rgba(34,197,94,.3); }
.sev-medium { background: rgba(234,179,8,.12);  color: #facc15; border: 1px solid rgba(234,179,8,.3); }
.sev-high   { background: rgba(249,115,22,.12); color: #fb923c; border: 1px solid rgba(249,115,22,.3); }
.sev-vulgar { background: rgba(239,68,68,.15);  color: #f87171; border: 1px solid rgba(239,68,68,.4); }

/* ── Comments Table ───────────────────────────────────────────────── */
.ct { width:100%; border-collapse:separate; border-spacing:0 5px; }
.ct th { color:#6b7280; font-size:.75rem; text-transform:uppercase; letter-spacing:1px;
         padding:8px 14px; border-bottom:1px solid #374151; }
.ct td { padding:12px 14px; color:#d1d5db; font-size:.88rem; background:#111827; vertical-align:middle; }
.ct tr.vrow td { background:linear-gradient(90deg,rgba(127,29,29,.3) 0%,#111827 100%); border-left:3px solid #ef4444; }
.ct tr td:first-child { border-radius:10px 0 0 10px; }
.ct tr td:last-child  { border-radius:0 10px 10px 0; }

/* ── Alert Banner ─────────────────────────────────────────────────── */
.alert-danger {
    background: linear-gradient(90deg, rgba(239,68,68,.15), rgba(239,68,68,.05));
    border: 1px solid rgba(239,68,68,.4); border-left: 4px solid #ef4444;
    border-radius: 10px; padding: 1rem 1.5rem; margin-bottom: 1rem;
    color: #fca5a5;
}
.alert-ok {
    background: linear-gradient(90deg, rgba(34,197,94,.12), rgba(34,197,94,.05));
    border: 1px solid rgba(34,197,94,.3); border-left: 4px solid #22c55e;
    border-radius: 10px; padding: 1rem 1.5rem; margin-bottom: 1rem;
    color: #86efac;
}

/* ── Sidebar ──────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0118 0%, #0f1a3a 100%) !important;
    border-right: 1px solid rgba(138,43,226,.2);
}
section[data-testid="stSidebar"] * { color: #d1d5db !important; }
section[data-testid="stSidebar"] .stRadio label { color: #d1d5db !important; }

/* ── Download Buttons ─────────────────────────────────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #dc2626, #991b1b) !important;
    color:#fff !important; border:none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(220,38,38,.3) !important;
}
/* ── Tabs ─────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; }
.block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════
if "df" not in st.session_state:
    st.session_state.df = None
if "cases" not in st.session_state:
    st.session_state.cases = []
if "post_url" not in st.session_state:
    st.session_state.post_url = "N/A"

# ═══════════════════════════════════════════════════════════════════════
#  HERO BANNER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">🛡️ Safeguard AI</div>
    <div class="hero-sub">Enterprise Cyber Harassment Detection & Legal Evidence Platform</div>
    <div class="hero-badges">
        <span class="badge-pill">🤖 AI-Powered</span>
        <span class="badge-pill">📄 FIR Auto-Generator</span>
        <span class="badge-pill">📊 Real-Time Analytics</span>
        <span class="badge-pill">⚖️ Legal Compliance</span>
        <span class="badge-pill">🔒 Privacy Safe</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    st.markdown("---")

    input_mode = st.radio(
        "**📥 Data Source**",
        ["✏️ Manual Entry", "▶️ YouTube Video", "🎭 Demo Data", "📸 Instagram (cookies.txt)"],
    )

    post_url_input = ""
    browser_choice = "chrome"
    ig_user = ""
    ig_pass = ""
    manual_text = ""
    cookies_file_path = ""
    yt_url = ""
    yt_api_key = ""

    if input_mode == "✏️ Manual Entry":
        st.markdown("**Paste comments below:**")
        st.caption("Formats supported per line:")
        st.caption("`username: comment text` **or** just `comment text`")
        manual_text = st.text_area(
            "comments",
            height=220,
            placeholder=(
                "rahul_k: Great photo! 🔥\n"
                "toxic99: You're the worst, go disappear\n"
                "sneha_v: So inspiring, keep going!\n"
                "hater_x: Ugly and stupid, be ashamed\n"
                "art_fan: Amazing composition!"
            ),
            label_visibility="collapsed",
        )
        st.caption("💡 Copy comments from Instagram/YouTube and paste here, one per line.")

    elif input_mode == "▶️ YouTube Video":
        st.markdown("**🔗 YouTube Video URL**")
        yt_url = st.text_input("yt_url", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")
        st.markdown("**🔑 YouTube API Key**")
        yt_api_key = st.text_input("yt_key", type="password", placeholder="AIzaSy...", label_visibility="collapsed")
        with st.expander("💡 How to get a FREE API Key"):
            st.markdown("""
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project (or select existing)
3. Click **Enable APIs** → search **YouTube Data API v3** → Enable
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy the key and paste above

It's free! 10,000 requests/day quota.
            """)
        st.success("✅ YouTube comments work reliably — no login needed!", icon="🎉")

    elif input_mode == "📸 Instagram (cookies.txt)":
        st.markdown("**🔗 Post URL**")
        post_url_input = st.text_input("url", placeholder="https://www.instagram.com/p/XXXXX/", label_visibility="collapsed")
        st.markdown("**🍪 Upload cookies.txt**")
        uploaded_cookies = st.file_uploader(
            "cookies_upload",
            type=["txt"],
            label_visibility="collapsed",
            help="Export from Chrome using 'Get cookies.txt LOCALLY' extension",
        )
        if uploaded_cookies:
            import tempfile, os
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="wb")
            tmp.write(uploaded_cookies.read())
            tmp.close()
            cookies_file_path = tmp.name
            ig_keys = []
            with open(tmp.name, "r", encoding="utf-8", errors="ignore") as _f:
                for _line in _f:
                    _line = _line.strip()
                    if not _line or _line.startswith("#"):
                        continue
                    _parts = _line.split("\t")
                    if len(_parts) >= 7 and "instagram.com" in _parts[0]:
                        ig_keys.append(_parts[5])
            if "sessionid" in ig_keys:
                st.success(f"✅ {len(ig_keys)} Instagram cookies loaded (sessionid ✓)")
            elif ig_keys:
                st.warning(f"⚠️ sessionid missing — log into Instagram first, then export.")
            else:
                st.error("❌ No Instagram cookies found. Export from instagram.com.")
        with st.expander("🔐 Use Password Instead"):
            ig_user = st.text_input("Instagram Username")
            ig_pass = st.text_input("Instagram Password", type="password")
        st.info("⚠️ Instagram scraping may be blocked. If it fails, use **✏️ Manual Entry** instead.", icon="ℹ️")

    max_comments = st.slider("Max comments to fetch", 5, 100, 30)

    st.markdown("---")
    analyze_btn = st.button("🔍  Run Analysis", use_container_width=True, type="primary")
    if st.session_state.df is not None:
        if st.button("🗑️  Clear Results", use_container_width=True):
            st.session_state.df = None
            st.session_state.cases = []
            st.rerun()

    st.markdown("---")
    st.markdown("""
**About Safeguard AI**
AI-powered platform for detecting and reporting cyber harassment on social media.

- Powered by **Detoxify NLP**
- Legal framework: IT Act 2000, IPC
- Auto-generates court-ready FIR PDFs
- Exportable case logs
""")

# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS ENGINE
# ═══════════════════════════════════════════════════════════════════════
if analyze_btn:
    comments = None
    st.session_state.post_url = post_url_input or "N/A"

    if input_mode == "📸 Instagram (cookies.txt)":
        if not post_url_input.strip():
            st.error("❌ Please enter a post URL.")
            st.stop()
        try:
            method = "cookies.txt" if cookies_file_path else f"{browser_choice} session"
            with st.spinner(f"🌐 Authenticating via {method} and scraping comments…"):
                from scraper import scrape_comments
                comments = scrape_comments(
                    post_url_input,
                    max_comments=max_comments,
                    browser=browser_choice if not cookies_file_path else "none",
                    ig_username=ig_user.strip(),
                    ig_password=ig_pass,
                    cookies_file_path=cookies_file_path,
                )
            st.sidebar.success(f"✅ Scraped {len(comments)} real comments!")
        except Exception as exc:
            err = str(exc)
            st.error(f"❌ Scraping failed: **{err}**")
            st.warning(
                "**How to fix this (Recommended):**\n"
                "1. Install **Get cookies.txt LOCALLY** extension in Chrome\n"
                "2. Open [Instagram.com](https://www.instagram.com) and log in\n"
                "3. Click the extension icon → **Export** → save the `.txt` file\n"
                "4. Upload that file using the **🍪 Upload cookies.txt** box in the sidebar\n\n"
                "Or switch to **✏️ Manual Entry** mode to paste comments directly."
            )
            st.stop()

    elif input_mode == "▶️ YouTube Video":
        if not yt_url.strip():
            st.error("❌ Please enter a YouTube video URL.")
            st.stop()
        if not yt_api_key.strip():
            st.error("❌ Please enter your YouTube API Key.")
            st.stop()
        try:
            with st.spinner("📺 Fetching YouTube comments…"):
                from youtube_scraper import fetch_youtube_comments
                comments = fetch_youtube_comments(yt_url, yt_api_key, max_comments)
            st.sidebar.success(f"✅ Fetched {len(comments)} YouTube comments!")
            st.session_state.post_url = yt_url
        except Exception as exc:
            st.error(f"❌ YouTube fetch failed: **{exc}**")
            st.stop()

    elif input_mode == "✏️ Manual Entry":
        lines = [l.strip() for l in manual_text.strip().splitlines() if l.strip()]
        if not lines:
            st.error("❌ Please enter at least one comment.")
            st.stop()
        parsed = []
        for i, l in enumerate(lines):
            if ":" in l:
                parts = l.split(":", 1)
                uname = parts[0].strip().lstrip("@") or f"user_{i+1}"
                comment = parts[1].strip()
            else:
                uname = f"user_{i+1}"
                comment = l
            if comment:
                parsed.append({"username": uname, "comment": comment})
        comments = parsed
        st.sidebar.success(f"✅ Loaded {len(comments)} comments")

    else:  # Demo Data
        comments = DEMO_COMMENTS[:max_comments]
        st.sidebar.info(f"Using {len(comments)} demo comments")

    with st.spinner("🧠 Analyzing toxicity (Detoxify model running…)"):
        df = analyze_comments(comments)

    st.session_state.df = df

    # Auto-add vulgar comments to case log
    for _, row in df[df["Severity"] == "Vulgar"].iterrows():
        case = {
            "Case ID": f"SG-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{row['Username'][:6].upper()}",
            "Username": row["Username"],
            "Comment": row["Comment"][:60] + "…" if len(row["Comment"]) > 60 else row["Comment"],
            "Score": row["Toxicity Score"],
            "Severity": row["Severity"],
            "Status": "Open",
            "Timestamp": datetime.datetime.now().strftime("%d %b %Y, %H:%M"),
        }
        if not any(c["Username"] == row["Username"] and c["Comment"] == case["Comment"] for c in st.session_state.cases):
            st.session_state.cases.append(case)

df = st.session_state.df

# ═══════════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD  (only shown after analysis)
# ═══════════════════════════════════════════════════════════════════════
if df is None:
    st.markdown("""
    <div style="text-align:center;padding:5rem 1rem;color:#4b5563">
        <div style="font-size:4rem">🛡️</div>
        <div style="font-size:1.4rem;font-weight:700;color:#9ca3af;margin-top:.8rem">
            Select a data source and click <em>Run Analysis</em></div>
        <div style="font-size:.95rem;margin-top:.5rem">
            Supports Instagram scraping, manual entry, and demo data</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── KPI Strip ─────────────────────────────────────────────────────────
total      = len(df)
vulgar_n   = int((df["Severity"] == "Vulgar").sum())
high_n     = int((df["Severity"] == "High").sum())
avg_score  = df["Toxicity Score"].mean()
vulgar_pct = vulgar_n / total * 100 if total else 0

alert_html = (
    f'<div class="alert-danger">🚨 <b>High Harassment Alert:</b> {vulgar_pct:.0f}% of comments are classified as <b>Vulgar</b>. Immediate action recommended.</div>'
    if vulgar_pct > 20 else
    f'<div class="alert-ok">✅ <b>Moderate Activity:</b> {vulgar_pct:.0f}% vulgar content detected. Monitor and review flagged comments.</div>'
)
st.markdown(alert_html, unsafe_allow_html=True)

sev_color = "#f87171" if vulgar_pct > 30 else "#facc15" if vulgar_pct > 10 else "#4ade80"
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Total Comments</div>
    <div class="kpi-value" style="color:#818cf8">{total}</div>
    <div class="kpi-delta" style="color:#6b7280">Analyzed this session</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Vulgar</div>
    <div class="kpi-value" style="color:#f87171">{vulgar_n}</div>
    <div class="kpi-delta" style="color:#f87171">{vulgar_pct:.1f}% of total</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">High Severity</div>
    <div class="kpi-value" style="color:#fb923c">{high_n}</div>
    <div class="kpi-delta" style="color:#6b7280">Needs review</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Avg Toxicity</div>
    <div class="kpi-value" style="color:{sev_color}">{avg_score:.1%}</div>
    <div class="kpi-delta" style="color:#6b7280">Across all comments</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💬 Comments", "🚨 FIR Reports", "📁 Case Manager"])

# ════════════════════════════════════
#  TAB 1 — Dashboard (Charts)
# ════════════════════════════════════
with tab1:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Severity Distribution")
        sev_counts = df["Severity"].value_counts().reset_index()
        sev_counts.columns = ["Severity", "Count"]
        color_map = {"Vulgar": "#ef4444", "High": "#f97316", "Medium": "#eab308", "Low": "#22c55e"}
        fig_pie = px.pie(
            sev_counts, names="Severity", values="Count",
            color="Severity", color_discrete_map=color_map,
            hole=0.55,
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#d1d5db", showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            margin=dict(t=20, b=20, l=0, r=0),
        )
        fig_pie.update_traces(textfont_color="#fff", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_r:
        st.markdown("#### Toxicity Scores per Comment")
        df_sorted = df.sort_values("Toxicity Score", ascending=True).tail(20)
        bar_colors = [color_map.get(s, "#818cf8") for s in df_sorted["Severity"]]
        fig_bar = go.Figure(go.Bar(
            x=df_sorted["Toxicity Score"],
            y=df_sorted["Username"],
            orientation="h",
            marker_color=bar_colors,
            text=[f"{s:.2f}" for s in df_sorted["Toxicity Score"]],
            textposition="outside",
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0, 1.1], color="#6b7280"),
            yaxis=dict(color="#d1d5db"),
            font_color="#d1d5db",
            margin=dict(t=10, b=10, l=0, r=60),
            height=420,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Sub-label radar / grouped bar
    st.markdown("#### Toxicity Sub-Label Breakdown")
    sub_cols = ["Toxic", "Obscene", "Threat", "Insult", "Identity Attack"]
    sub_means = df[sub_cols].mean().reset_index()
    sub_means.columns = ["Label", "Score"]

    fig_sub = go.Figure(go.Bar(
        x=sub_means["Label"], y=sub_means["Score"],
        marker_color=["#818cf8","#a78bfa","#f472b6","#fb923c","#f87171"],
        text=[f"{v:.3f}" for v in sub_means["Score"]],
        textposition="outside",
    ))
    fig_sub.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 1], color="#6b7280", gridcolor="rgba(55,65,81,.5)"),
        xaxis=dict(color="#d1d5db"),
        font_color="#d1d5db",
        margin=dict(t=10, b=10),
        height=260,
    )
    st.plotly_chart(fig_sub, use_container_width=True)

    # Top Offenders
    st.markdown("#### 🏴 Top Offenders")
    top = (
        df[df["Severity"].isin(["Vulgar", "High"])]
        .groupby("Username")
        .agg(Count=("Toxicity Score", "count"), Max_Score=("Toxicity Score", "max"))
        .sort_values("Max_Score", ascending=False)
        .head(10)
        .reset_index()
    )
    if top.empty:
        st.info("No high-severity offenders found.")
    else:
        top["Risk Level"] = top["Max_Score"].apply(
            lambda s: "🔴 Critical" if s > 0.75 else "🟠 High" if s > 0.5 else "🟡 Medium"
        )
        st.dataframe(top, use_container_width=True, hide_index=True)

# ════════════════════════════════════
#  TAB 2 — Comments Table
# ════════════════════════════════════
with tab2:
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        filter_sev = st.multiselect(
            "Filter by Severity",
            ["Low", "Medium", "High", "Vulgar"],
            default=["Low", "Medium", "High", "Vulgar"],
        )
    with c2:
        search_q = st.text_input("🔍 Search comments", placeholder="Search keyword…")
    with c3:
        # CSV export
        csv_bytes = df.to_csv(index=False).encode()
        st.download_button("📥 Export CSV", data=csv_bytes, file_name="safeguard_analysis.csv", mime="text/csv", use_container_width=True)

    filtered = df[df["Severity"].isin(filter_sev)]
    if search_q:
        filtered = filtered[filtered["Comment"].str.contains(search_q, case=False, na=False)]

    def sev_badge(sev):
        cls = f"sev-{sev.lower()}"
        return f'<span class="sev-badge {cls}">{sev}</span>'

    rows_html = ""
    for _, row in filtered.iterrows():
        vrow = 'class="vrow"' if row["Severity"] == "Vulgar" else ""
        comment_safe = row["Comment"].replace("<", "&lt;").replace(">", "&gt;")
        rows_html += (
            f'<tr {vrow}>'
            f'<td><b>@{row["Username"]}</b></td>'
            f'<td>{comment_safe}</td>'
            f'<td style="text-align:center"><b>{row["Toxicity Score"]:.4f}</b></td>'
            f'<td style="text-align:center">{sev_badge(row["Severity"])}</td>'
            f'<td style="text-align:center">{row["Toxic"]:.2f}</td>'
            f'<td style="text-align:center">{row["Threat"]:.2f}</td>'
            f'<td style="text-align:center">{row["Insult"]:.2f}</td>'
            f'</tr>'
        )

    st.markdown(
        f'<table class="ct"><thead><tr>'
        f'<th>Username</th><th>Comment</th><th>Score</th><th>Severity</th>'
        f'<th>Toxic</th><th>Threat</th><th>Insult</th>'
        f'</tr></thead><tbody>{rows_html}</tbody></table>',
        unsafe_allow_html=True,
    )
    st.caption(f"{len(filtered)} of {total} comments shown")

# ════════════════════════════════════
#  TAB 3 — FIR Reports
# ════════════════════════════════════
with tab3:
    vulgar_df = df[df["Severity"] == "Vulgar"].reset_index(drop=True)

    if vulgar_df.empty:
        st.markdown('<div class="alert-ok">✅ No vulgar comments detected — no FIR required!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-danger">🚨 {len(vulgar_df)} comment(s) require FIR action.</div>', unsafe_allow_html=True)

        # Batch download
        batch_rows = vulgar_df.to_dict("records")
        batch_bytes = generate_batch_fir_pdf(batch_rows, post_url=st.session_state.post_url)
        st.download_button(
            "📦 Download All FIRs (Batch PDF)",
            data=batch_bytes,
            file_name=f"Safeguard_Batch_FIR_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
        )
        st.markdown("---")

        for idx, row in vulgar_df.iterrows():
            with st.expander(f"🚨  @{row['Username']}  —  Score: {row['Toxicity Score']:.4f}", expanded=False):
                col_info, col_btn = st.columns([5, 1])
                with col_info:
                    st.markdown(f"**Comment:** {row['Comment']}")

                    # Mini sub-label bars
                    sub_data = {
                        "Toxic": row.get("Toxic", 0), "Obscene": row.get("Obscene", 0),
                        "Threat": row.get("Threat", 0), "Insult": row.get("Insult", 0),
                        "Identity Attack": row.get("Identity Attack", 0),
                    }
                    fig_mini = go.Figure(go.Bar(
                        x=list(sub_data.values()), y=list(sub_data.keys()),
                        orientation="h",
                        marker_color=["#818cf8","#a78bfa","#f87171","#fb923c","#f472b6"],
                    ))
                    fig_mini.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        height=160, margin=dict(t=0, b=0, l=0, r=0),
                        xaxis=dict(range=[0, 1], color="#6b7280"),
                        yaxis=dict(color="#d1d5db"), font_color="#d1d5db", showlegend=False,
                    )
                    st.plotly_chart(fig_mini, use_container_width=True)

                with col_btn:
                    sub_scores = {
                        "Toxic": row.get("Toxic", 0), "Obscene": row.get("Obscene", 0),
                        "Threat": row.get("Threat", 0), "Insult": row.get("Insult", 0),
                        "Identity Atk": row.get("Identity Attack", 0),
                    }
                    pdf_bytes = generate_fir_pdf(
                        comment=row["Comment"], username=row["Username"],
                        toxicity_score=row["Toxicity Score"], severity=row["Severity"],
                        sub_scores=sub_scores, post_url=st.session_state.post_url,
                    )
                    pdf_filename = f"FIR_{row['Username']}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
                    st.download_button(
                        "📄 FIR PDF",
                        data=pdf_bytes,
                        file_name=pdf_filename,
                        mime="application/pdf",
                        key=f"fir_dl_{idx}",
                    )

                # Email to Cybercrime Cell
                with st.container(border=True):
                    st.markdown(f"**📧 Email FIR to Cybercrime Cell — @{row['Username']}**")
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        sender_email = st.text_input("Your Gmail", placeholder="you@gmail.com", key=f"email_{idx}")
                        app_pwd = st.text_input("Gmail App Password", type="password",
                            placeholder="16-char app password", key=f"pwd_{idx}")
                    with ec2:
                        recipient = st.text_input("Recipient Email",
                            value="cybercrime@gov.in", key=f"recip_{idx}")
                        st.caption("Default: National Cybercrime Portal")

                    st.markdown("""
                        <details>
                        <summary><b>ℹ️ How to get Gmail App Password</b></summary>
                        <ol>
                            <li>Go to <a href="https://myaccount.google.com" target="_blank">myaccount.google.com</a></li>
                            <li><b>Security</b> → Enable <b>2-Step Verification</b></li>
                            <li>Search <b>App Passwords</b> → Select <b>Mail</b> → Generate</li>
                            <li>Copy the 16-character password and paste above</li>
                        </ol>
                        </details>
                    """, unsafe_allow_html=True)

                    if st.button(f"🚀 Send Email", key=f"send_email_{idx}"):
                        if not sender_email or not app_pwd or not recipient:
                            st.error("❌ Please fill in all email fields.")
                        else:
                            try:
                                from email_sender import send_fir_email, build_fir_email_body
                                case_id = f"SG-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                                body = build_fir_email_body(
                                    username=row["Username"],
                                    comment=row["Comment"],
                                    toxicity_score=row["Toxicity Score"],
                                    case_id=case_id,
                                    post_url=st.session_state.post_url,
                                )
                                with st.spinner("📧 Sending email..."):
                                    send_fir_email(
                                        sender_email=sender_email,
                                        sender_app_password=app_pwd,
                                        recipient_email=recipient,
                                        subject=f"Cyber Harassment FIR — Case {case_id} — @{row['Username']}",
                                        body=body,
                                        pdf_bytes=pdf_bytes,
                                        pdf_filename=pdf_filename,
                                    )
                                st.success(f"✅ FIR emailed to **{recipient}** successfully!")
                            except Exception as e:
                                st.error(f"❌ Email failed: {e}")
                                st.caption("Check your Gmail App Password and make sure 2FA is enabled.")


# ════════════════════════════════════
#  TAB 4 — Case Manager
# ════════════════════════════════════
with tab4:
    st.markdown("### 📁 Case Management Dashboard")
    st.caption("All vulgar-severity cases are automatically logged here. Update status as you review each case.")

    if not st.session_state.cases:
        st.info("No cases logged yet. Run an analysis to auto-populate cases from vulgar comments.")
    else:
        status_options = ["Open", "Under Review", "Reported to Police", "Resolved", "Dismissed"]

        cases_df = pd.DataFrame(st.session_state.cases)
        st.markdown(f"**{len(cases_df)} active case(s)**")

        # Summary mini-metrics
        open_n   = int((cases_df["Status"] == "Open").sum())
        review_n = int((cases_df["Status"] == "Under Review").sum())
        done_n   = int((cases_df["Status"].isin(["Reported to Police", "Resolved"])).sum())
        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 Open", open_n)
        c2.metric("🟡 Under Review", review_n)
        c3.metric("🟢 Resolved/Reported", done_n)
        st.markdown("---")

        for i, case in enumerate(st.session_state.cases):
            with st.expander(f"📋 {case['Case ID']}  |  @{case['Username']}  |  {case['Status']}", expanded=(case['Status'] == 'Open')):
                col_d, col_s = st.columns([4, 2])
                with col_d:
                    st.markdown(f"**Comment:** {case['Comment']}")
                    st.markdown(f"**Score:** `{case['Score']:.4f}`  |  **Severity:** `{case['Severity']}`")
                    st.caption(f"Logged: {case['Timestamp']}")
                with col_s:
                    new_status = st.selectbox(
                        "Update Status",
                        status_options,
                        index=status_options.index(case["Status"]),
                        key=f"status_{i}",
                    )
                    if new_status != case["Status"]:
                        st.session_state.cases[i]["Status"] = new_status
                        st.rerun()

        # Export case log
        st.markdown("---")
        case_csv = pd.DataFrame(st.session_state.cases).to_csv(index=False).encode()
        st.download_button(
            "📥 Export Case Log (CSV)",
            data=case_csv,
            file_name=f"Safeguard_CaseLog_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
