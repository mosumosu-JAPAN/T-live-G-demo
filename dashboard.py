"""
Creator Behavior Intelligence — TikTok LIVE Ecosystem · Cosplay Vertical
Internal-tool prototype with real numeric callouts for stand-up consumption.
Bilingual (EN / 中文) toggle at top-right.
"""
import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from numpy.linalg import lstsq

st.set_page_config(
    page_title="Creator Behavior Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Palette ──
BG       = "#141420"
SURFACE  = "#1A1A2A"
PANEL    = "#1B1B2A"
BORDER   = "#2A2A3A"
TEXT     = "#ECECF2"
NOTE     = "#C0C0D0"
HI       = "#FFFFFF"
DIM      = "#A8A8B6"
MUTED    = "#7A7A88"
GRID     = "#262636"

CYAN  = "#25F4EE"
PINK  = "#FE2C55"
AMBER = "#FFB84D"
ALERT = "#FF6B7E"

TEAL  = "#5BC6B9"
SAND  = "#C8A35E"
ROSE  = "#D45A78"

MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, monospace"

# ── Language state ──
if "lang" not in st.session_state:
    st.session_state.lang = "EN"
LANG = st.session_state.lang

def t(en, cn):
    return en if LANG == "EN" else cn

st.markdown(f"""
<style>
.stApp {{ background: {BG}; color: {TEXT}; }}
header[data-testid="stHeader"] {{ background: {BG}; }}
.block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1340px; }}
h1, h2, h3, h4 {{ color: {TEXT}; letter-spacing: -0.005em; font-weight: 500; }}

h1.page-title {{ font-size: 22px; font-weight: 500; margin: 0; letter-spacing: -0.01em; color: {TEXT}; }}
.page-subtitle {{ font-family: {MONO}; font-size: 13px; color: {DIM}; margin: 6px 0 22px 0; letter-spacing: 0.02em; }}

h2 {{
    font-size: 17px; text-transform: uppercase; letter-spacing: 0.13em;
    color: {DIM}; font-weight: 500;
    margin: 44px 0 10px 0; padding-top: 26px;
    border-top: 1px solid {BORDER};
}}

.note {{ font-family: {MONO}; font-size: 15px; color: {NOTE}; margin: 6px 0 22px 0; letter-spacing: 0.005em; line-height: 1.8; }}
.note b {{ color: {HI}; font-weight: 500; }}
.note-extra {{
    font-family: {MONO}; font-size: 14.5px; color: {TEXT};
    margin: -10px 0 24px 0; padding: 10px 14px;
    background: {SURFACE}; border-left: 2px solid {CYAN}; border-radius: 0 4px 4px 0;
    line-height: 1.75;
}}
.note-extra b {{ color: {CYAN}; font-weight: 500; }}
.note-warn {{ font-family: {MONO}; font-size: 14px; color: {ALERT}; margin: 8px 0 20px 0; line-height: 1.7; letter-spacing: 0.005em; }}
hr {{ border-color: {BORDER}; margin: 18px 0; }}

/* Audience + lang selectors share button styling */
.audience-row {{ margin-bottom: 4px; padding-bottom: 6px; }}
[data-testid="stButton"] > button {{
    background: transparent !important; color: {MUTED} !important;
    border: none !important; border-bottom: 3px solid transparent !important;
    border-radius: 0 !important; padding: 12px 28px 14px 0 !important;
    font-family: {MONO} !important; font-size: 16px !important;
    font-weight: 400 !important; box-shadow: none !important;
    text-align: left !important; width: auto !important; min-height: 0 !important;
    transition: color 0.14s, border-color 0.14s !important;
}}
[data-testid="stButton"] > button:hover {{ color: {TEXT} !important; border-bottom-color: {DIM} !important; }}
[data-testid="stButton"] > button[kind="primary"],
[data-testid="stButton"] > button[data-testid="stBaseButton-primary"] {{
    color: {CYAN} !important; border-bottom: 3px solid {CYAN} !important;
}}
[data-testid="stButton"] > button[kind="primary"]:hover {{ color: {CYAN} !important; border-bottom-color: {CYAN} !important; }}
.lang-row [data-testid="stButton"] > button {{ font-size: 13px !important; padding: 6px 14px 8px 0 !important; }}

/* Business Impact Summary Bar */
.biz-bar {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 18px 0 8px 0; }}
.biz-stat {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px;
    padding: 18px 20px; border-top: 2px solid {CYAN};
    display: flex; flex-direction: column; gap: 6px; }}
.biz-stat .label {{ color: {CYAN}; font-family: {MONO}; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.16em; font-weight: 500; }}
.biz-stat .num {{ color: {HI}; font-family: {MONO}; font-size: 26px; font-weight: 500;
    letter-spacing: -0.01em; line-height: 1.15; }}
.biz-stat .desc {{ color: {NOTE}; font-family: {MONO}; font-size: 12.5px; line-height: 1.55; margin-top: 2px; }}
.biz-bar-note {{ font-family: {MONO}; font-size: 13.5px; color: {DIM};
    margin: 14px 0 6px 0; letter-spacing: 0.01em; line-height: 1.7; }}
.biz-bar-note b {{ color: {TEXT}; font-weight: 500; }}

/* Risk Alert Panel */
.alert-panel {{ background: {SURFACE}; border: 1px solid {BORDER};
    border-left: 4px solid {ALERT}; border-radius: 0 6px 6px 0;
    padding: 22px 24px; height: 100%;
    font-family: {MONO}; color: {TEXT}; }}
.alert-panel .alert-tag {{ color: {ALERT}; font-size: 12px; text-transform: uppercase; letter-spacing: 0.18em;
    font-weight: 500; margin-bottom: 14px; display: block; }}
.alert-panel .alert-line {{ font-size: 13.5px; color: {NOTE}; line-height: 1.7; margin: 6px 0; }}
.alert-panel .alert-num {{ color: {HI}; font-weight: 500; }}
.alert-panel .alert-divider {{ border-top: 1px solid {BORDER}; margin: 14px 0; }}
.alert-panel .alert-creator {{ color: {ALERT}; font-size: 14px; font-weight: 500; margin-bottom: 6px; }}
.alert-panel .alert-pattern {{ font-size: 12.5px; color: {DIM}; margin-top: 12px; padding: 10px 12px;
    background: {BG}; border-radius: 4px; line-height: 1.7; }}
.alert-panel .alert-action {{ font-size: 13.5px; color: {CYAN}; margin-top: 14px; line-height: 1.7; }}
.alert-panel .alert-action b {{ color: {HI}; font-weight: 500; }}

/* Early Warning System */
.ews-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 12px; }}
.ews-card {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px;
    padding: 20px 22px; position: relative; font-family: {MONO}; line-height: 1.7; }}
.ews-card.amber {{ border-left: 3px solid {AMBER}; }}
.ews-card.red   {{ border-left: 3px solid {ALERT}; }}
.ews-card.cyan  {{ border-left: 3px solid {CYAN}; }}
.ews-card .ews-name {{ color: {TEXT}; font-size: 15px; font-weight: 500; margin-bottom: 4px; letter-spacing: 0.005em; }}
.ews-card.amber .ews-name {{ color: {AMBER}; }}
.ews-card.red   .ews-name {{ color: {ALERT}; }}
.ews-card.cyan  .ews-name {{ color: {CYAN}; }}
.ews-card .ews-tag {{ position: absolute; top: 18px; right: 18px;
    font-size: 10px; padding: 3px 10px; border-radius: 999px;
    text-transform: uppercase; letter-spacing: 0.14em; font-weight: 500; }}
.ews-card .ews-tag.active {{ background: rgba(254,107,126,0.16); color: {ALERT}; border: 1px solid rgba(254,107,126,0.4); }}
.ews-card .ews-tag.historical {{ background: rgba(168,168,182,0.1); color: {DIM}; border: 1px solid {BORDER}; }}
.ews-card .ews-row {{ font-size: 12.5px; color: {NOTE}; margin: 6px 0; }}
.ews-card .ews-row .k {{ color: {MUTED}; display: inline-block; min-width: 80px; }}
.ews-card .ews-row .v {{ color: {TEXT}; }}
.ews-card .ews-creator {{ font-size: 13px; color: {DIM}; margin: 8px 0 4px 0; font-weight: 500; }}
.ews-card .ews-creator .at {{ color: {TEXT}; }}
.ews-card .ews-divider {{ border-top: 1px solid {BORDER}; margin: 12px 0; }}
.ews-card .ews-action {{ font-size: 12.5px; color: {NOTE}; line-height: 1.7; }}
.ews-card .ews-action b {{ color: {TEXT}; font-weight: 500; }}

/* Trajectory Key Stats */
.traj-keystats {{ position: relative; float: right; margin-top: -10px; text-align: right;
    font-family: {MONO}; font-size: 12.5px; color: {NOTE}; line-height: 1.7;
    background: rgba(20,20,32,0.82); padding: 6px 12px; border-radius: 4px;
    border: 1px solid {BORDER}; }}
.traj-keystats .num {{ color: {HI}; font-weight: 500; }}

/* Governance table */
table.gov {{ width: 100%; border-collapse: collapse; font-size: 14px; color: {TEXT}; margin-top: 4px; }}
table.gov th {{ text-align: left; font-weight: 500; font-size: 11.5px;
    text-transform: uppercase; letter-spacing: 0.12em; color: {DIM};
    padding: 14px 18px; border-bottom: 1px solid {BORDER}; }}
table.gov td {{ padding: 22px 18px; border-bottom: 1px solid {BORDER}; vertical-align: top; line-height: 1.7; }}
table.gov td.creator {{ font-family: {MONO}; font-size: 13px; color: {DIM}; width: 18%; }}
table.gov td.creator .name {{ color: {TEXT}; font-weight: 500; display: block; margin-bottom: 4px; font-size: 14px; }}
table.gov td.strategy {{ width: 16%; color: {TEXT}; }}
table.gov td.trained {{ width: 26%; color: {NOTE}; font-size: 14px; }}
table.gov td.intervention {{ color: {TEXT}; font-size: 14px; }}
.swatch {{ display: inline-block; width: 8px; height: 8px; border-radius: 1px; margin-right: 8px; vertical-align: middle; }}
.dataframe {{ background: {PANEL} !important; }}
[data-testid="stDataFrame"] {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 6px; }}

/* Governance Business Case */
.biz-case {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin: 8px 0 18px 0; }}
.biz-case .case {{ background: {SURFACE}; border: 1px solid {BORDER}; border-left: 2px solid {CYAN};
    border-radius: 0 6px 6px 0; padding: 16px 18px; }}
.biz-case .case .num {{ color: {CYAN}; font-family: {MONO}; font-size: 22px; font-weight: 500; line-height: 1.2; letter-spacing: -0.01em; }}
.biz-case .case .desc {{ color: {NOTE}; font-family: {MONO}; font-size: 12.5px; margin-top: 6px; line-height: 1.6; }}
.biz-case-foot {{ font-family: {MONO}; font-size: 12px; color: {DIM}; margin: 4px 0 14px 0; letter-spacing: 0.01em; }}

/* Policy Simulation */
.sim-title {{ font-family: {MONO}; font-size: 16px; color: {TEXT}; margin: 4px 0 6px 0; letter-spacing: 0.005em; line-height: 1.55; font-weight: 500; }}
.sim-subtitle {{ font-family: {MONO}; font-size: 13px; color: {DIM}; margin: 0 0 20px 0; letter-spacing: 0.02em; line-height: 1.6; }}
.sim-caption {{ font-family: {MONO}; font-size: 13px; color: {DIM}; margin: 0 0 8px 0; letter-spacing: 0.005em; line-height: 1.65; }}
.sim-instruction {{ font-family: {MONO}; font-size: 12.5px; color: {CYAN}; margin: 0 0 14px 0; letter-spacing: 0.01em; }}
[data-testid="column"]:has(.policy-sim-marker) {{ background: {SURFACE}; padding: 20px 20px 10px 20px; border-radius: 6px; border: 1px solid {BORDER}; }}
.policy-sim-marker {{ display: none; }}
[data-testid="column"]:has(.policy-sim-marker) [data-testid="stSlider"] label {{
    font-family: {MONO} !important; font-size: 13px !important; color: {TEXT} !important;
    font-weight: 400 !important; letter-spacing: 0 !important;
}}
[data-testid="column"]:has(.policy-sim-marker) [data-testid="stSlider"] {{ margin-bottom: -4px; }}
.sim-footer {{ font-family: {MONO}; font-size: 13px; color: {NOTE}; margin: 4px 0; letter-spacing: 0.01em; text-align: left; line-height: 1.7; }}

/* Policy Impact Summary table */
table.impact {{ width: 100%; border-collapse: collapse; font-size: 13px; color: {TEXT}; font-family: {MONO}; }}
table.impact th {{ text-align: left; font-weight: 500; font-size: 10.5px;
    text-transform: uppercase; letter-spacing: 0.1em; color: {DIM};
    padding: 9px 8px; border-bottom: 1px solid {BORDER}; white-space: nowrap; }}
table.impact td {{ padding: 12px 8px; border-bottom: 1px solid {BORDER}; vertical-align: top; line-height: 1.55; }}
table.impact td.t-creator {{ color: {DIM}; white-space: nowrap; }}
table.impact td.t-creator .name {{ color: {TEXT}; font-weight: 500; display: inline; font-size: 13px; }}
table.impact td.t-creator .sub {{ color: {MUTED}; font-size: 10.5px; display: block; margin-top: 2px; }}
table.impact td.t-now {{ color: {NOTE}; }}
table.impact td.t-after {{ color: {TEXT}; }}
table.impact td.t-meaning {{ color: {NOTE}; font-size: 12px; }}
table.impact td.t-delta {{ font-weight: 500; white-space: nowrap; font-size: 13px; }}
table.impact td.t-delta.positive {{ color: {CYAN}; }}
table.impact td.t-delta.negative {{ color: {ALERT}; }}
table.impact td.t-delta.flat {{ color: {DIM}; }}

/* EXTENDING TO LIVE */
.live-block {{ background: {SURFACE}; border-left: 4px solid {CYAN};
    padding: 22px 26px; margin: 22px 0 6px 0;
    font-family: {MONO}; font-size: 15px; color: {TEXT};
    line-height: 1.85; letter-spacing: 0.005em; border-radius: 0 6px 6px 0; }}
.live-block .live-tag {{ display: inline-block; color: {CYAN}; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.18em;
    margin-bottom: 10px; font-weight: 500; }}

/* Limitations */
.limit-box {{ background: {SURFACE}; border-left: 3px solid {CYAN};
    border-top: 1px solid {BORDER}; border-right: 1px solid {BORDER}; border-bottom: 1px solid {BORDER};
    border-radius: 0 6px 6px 0; padding: 22px 26px; margin-top: 22px;
    font-family: {MONO}; font-size: 14px; color: {NOTE}; line-height: 1.8; }}
.limit-box .lim-label {{ color: {CYAN}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.16em;
    margin-bottom: 14px; display: block; font-weight: 500; }}
.limit-box ul {{ margin: 0; padding-left: 20px; }}
.limit-box li {{ margin: 8px 0; font-size: 14px; line-height: 1.8; }}
.limit-box b {{ color: {HI}; font-weight: 500; }}

/* Bottom credit */
.bottom-credit {{ font-family: {MONO}; font-size: 12px; color: {DIM};
    text-align: left; margin-top: 40px; padding-top: 20px;
    border-top: 1px solid {BORDER}; letter-spacing: 0.04em; }}
</style>
""", unsafe_allow_html=True)

PLOTLY = dict(
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(color=TEXT, family="ui-sans-serif, -apple-system, sans-serif", size=13),
    margin=dict(l=56, r=28, t=24, b=52),
    xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=BORDER, tickfont=dict(family=MONO, size=12, color=DIM), title_font=dict(size=13, color=DIM)),
    yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor=BORDER, tickfont=dict(family=MONO, size=12, color=DIM), title_font=dict(size=13, color=DIM)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=13)),
    hoverlabel=dict(bgcolor=PANEL, bordercolor=BORDER, font=dict(family=MONO, size=12, color=TEXT)),
)

# ── Risk lexicon ──
HIGH_RISK = {"hanime","hmanga","hentai","doujin","doujins","doujinshi","saucegod","sauceking","sauce","fakebody","nsfw","18+","ahegao","ecchi","lewd","thirsttrap","onlyfans","擦边","福利"}
MID_RISK  = {"sexy","hot","body","thicc","waifu","cosplaygirl","bikini","ass","boobs","skin","curvy","tight","wet","性感","身材"}
LOW_RISK  = {"cosplay","cosplayer","coser","anime","fanart","gaming","honkaistarrail","wutheringwaves","honorofkings","genshin","honkaiimpact3rd","robin","elysia","hysilens"}
HASHTAG_RE = re.compile(r"#([A-Za-z0-9_一-鿿]+)")
SOFT_RISK_WORDS = re.compile(r"(sexy|hot|body|thicc|bikini|fakebody|擦边|福利|性感|身材)", re.IGNORECASE)

CREATORS = {
    "vanzzcoser":      dict(strategy_en="Volatile Anchor",   strategy_cn="不稳定的优质创作者",
                            archetype_en="Ecosystem Anchor", archetype_cn="太太型",
                            color=TEAL),
    "cosplaybeauty888":dict(strategy_en="Machine",            strategy_cn="算法机器",
                            archetype_en="Algorithm Exploiter", archetype_cn="SOP型",
                            color=SAND),
    "mommygardevoir69":dict(strategy_en="Gambler",            strategy_cn="赌徒",
                            archetype_en="Boundary Prober",   archetype_cn="边界党",
                            color=ROSE),
}
def color_of(u): return CREATORS.get(u, {}).get("color", "#9C9CFF")
def strategy_of(u): return CREATORS[u]["strategy_en"] if LANG == "EN" else CREATORS[u]["strategy_cn"]
def archetype_of(u): return CREATORS[u]["archetype_en"] if LANG == "EN" else CREATORS[u]["archetype_cn"]

def extract_tags(d): return [x.lower() for x in HASHTAG_RE.findall(d or "")]

def risk_score(desc, tags):
    if not isinstance(desc, str): desc = ""
    text_hits = len(SOFT_RISK_WORDS.findall(desc))
    if not tags: return min(0.05 + 0.15 * text_hits, 1.0)
    s, n = 0.0, 0
    for x in tags:
        if x in HIGH_RISK: s += 1.0
        elif x in MID_RISK: s += 0.5
        elif x in LOW_RISK: s += 0.05
        else: s += 0.15
        n += 1
    return min(s / max(n, 1) + 0.08 * text_hits, 1.0)

@st.cache_data
def load_videos():
    df = pd.concat([pd.read_csv(f) for f in ["vanzzcoser.csv","cosplaybeauty888.csv","mommygardevoir69.csv"]], ignore_index=True)
    df["created_time"] = pd.to_datetime(df["created_time"], errors="coerce")
    df = df.dropna(subset=["created_time"]).sort_values("created_time")
    tags = df["desc"].apply(extract_tags)
    df["content_risk"] = [risk_score(d, t) for d, t in zip(df["desc"], tags)]
    df["engagement_rate"] = (
        (df["like_count"] + df["comment_count"] + df["share_count"])
        / df["play_count"].replace(0, np.nan)
    ).fillna(0).clip(0, 1)
    df["week"] = df["created_time"].dt.to_period("W").dt.start_time
    return df

@st.cache_data
def build_weekly(df):
    g = df.groupby(["username","week"]).agg(
        plays=("play_count","sum"), likes=("like_count","sum"),
        comments=("comment_count","sum"), shares=("share_count","sum"),
        posting_frequency=("video_id","count"),
        engagement_rate=("engagement_rate","mean"),
        content_risk=("content_risk","mean"),
    ).reset_index()
    parts = []
    for u, sub in g.groupby("username"):
        sub = sub.sort_values("week").copy()
        sub["play_growth"] = sub["plays"].pct_change().fillna(0).clip(-1.5, 4)
        sub["eng_change"] = sub["engagement_rate"].diff().fillna(0)
        sub["share_growth"] = sub["shares"].pct_change().fillna(0).clip(-1.5, 4)
        sub["reward_signal"] = 0.5 * sub["play_growth"] + 0.3 * (sub["eng_change"] * 50) + 0.2 * sub["share_growth"]
        parts.append(sub)
    return pd.concat(parts, ignore_index=True)

def fit_irl(weekly):
    feats = ["play_growth","engagement_rate","posting_frequency","content_risk"]
    out = {}
    for u, sub in weekly.groupby("username"):
        if len(sub) < 4:
            out[u] = dict(weights=None, r2=0.0, n=len(sub), fallback=True); continue
        X = sub[feats].values.astype(float); y = sub["reward_signal"].values.astype(float)
        Xs = (X - X.mean(0)) / (X.std(0) + 1e-9); ys = (y - y.mean()) / (y.std() + 1e-9)
        A = np.column_stack([Xs, np.ones(len(Xs))])
        coef, *_ = lstsq(A, ys, rcond=None)
        w = coef[:4]; pred = Xs @ w
        ss_res = np.sum((ys-pred)**2); ss_tot = np.sum((ys-ys.mean())**2) + 1e-9
        out[u] = dict(weights=dict(zip(feats, w)), r2=float(1 - ss_res/ss_tot), n=len(sub), fallback=False)

    valid = [v["weights"] for v in out.values() if v["weights"] is not None]
    if valid:
        avg = {f: float(np.mean([w[f] for w in valid])) for f in feats}
    else:
        avg = {f: 0.0 for f in feats}
    for v in out.values():
        if v["weights"] is None or all(abs(x) < 1e-9 for x in v["weights"].values()):
            v["weights"] = avg.copy()
            v["fallback"] = True
    return out

def detect_hacking(df):
    parts = []
    for u, sub in df.groupby("username"):
        s = sub.copy()
        play_q3 = s["play_count"].quantile(0.75)
        eng_q1  = s["engagement_rate"].quantile(0.25)
        s["is_hacking"] = (s["play_count"] > play_q3) & (s["engagement_rate"] < eng_q1) & (s["content_risk"] >= 0.5)
        parts.append(s)
    return pd.concat(parts, ignore_index=True)

# ── compute ──
df = load_videos()
weekly = build_weekly(df)
irl = fit_irl(weekly)
hacks = detect_hacking(df)

def per_creator_metrics():
    out = {}
    for u in CREATORS:
        df_u = df[df["username"] == u]
        w_u = weekly[weekly["username"] == u]
        h_u = hacks[hacks["username"] == u]
        rs = w_u["reward_signal"]
        out[u] = dict(
            n_videos=len(df_u),
            avg_engagement=df_u["engagement_rate"].mean() if len(df_u) else 0.0,
            avg_play=df_u["play_count"].mean() if len(df_u) else 0.0,
            median_play=df_u["play_count"].median() if len(df_u) else 0.0,
            median_eng=df_u["engagement_rate"].median() if len(df_u) else 0.0,
            reward_std=float(rs.std()) if len(rs) > 1 else 0.0,
            reward_mean=float(rs.mean()) if len(rs) else 0.0,
            reward_peak=float(rs.max()) if len(rs) else 0.0,
            reward_min=float(rs.min()) if len(rs) else 0.0,
            n_hacking=int(h_u["is_hacking"].sum()),
            hacking_pct=(100.0 * h_u["is_hacking"].sum() / len(h_u)) if len(h_u) else 0.0,
            avg_risk=df_u["content_risk"].mean() if len(df_u) else 0.0,
        )
    return out

M = per_creator_metrics()
total_videos = len(df)
total_hacks = int(hacks["is_hacking"].sum())
hacking_share = 100.0 * total_hacks / max(total_videos, 1)

quality_gap = M["vanzzcoser"]["avg_engagement"] / max(M["cosplaybeauty888"]["avg_engagement"], 1e-9)
mommy_peak = M["mommygardevoir69"]["reward_peak"]
mommy_meanabs = max(abs(M["mommygardevoir69"]["reward_mean"]), 1e-6)
gambler_ratio = mommy_peak / mommy_meanabs
stability_gap = M["vanzzcoser"]["reward_std"] / max(M["cosplaybeauty888"]["reward_std"], 1e-9)

# ── Audience state ──
if "audience" not in st.session_state:
    st.session_state.audience = "PM"

# ── INSIGHTS dict — keyed by module → audience → lang ──
INSIGHTS = {
    "trajectory": {
        "PM": {
            "EN": "Three curves show how the platform unintentionally trained three different survival strategies. The Machine type was trained into zero-variance posting, the Boundary Prober into a viral-then-suppressed gambling cycle, and the so-called Anchor into the most volatile of the three — meaning the platform is not protecting its highest-quality creators. This is the starting point for redefining policy.",
            "CN": "三条曲线说明平台在无意中训练出了三种创作者生存策略。SOP型被训练成机器（零方差），边界党被训练成赌徒（爆一次归零再赌），太太型反而最不稳定——说明平台没有在保护高质量创作者。这是 policy 需要重新定义的起点。",
        },
        "Data": {
            "EN": "reward_signal = 0.5×Δplays + 0.3×Δengagement + 0.2×Δshares, weekly aggregation. cosplaybeauty888 sits near zero variance (σ≈0.02), mommygardevoir69 has high peaks over a low baseline (peak/mean > 3×), vanzzcoser shows high-frequency oscillation. Three variance regimes correspond to three different optimization targets.",
            "CN": "reward_signal = 0.5×Δplay + 0.3×Δengagement + 0.2×Δshares，按周聚合。cosplaybeauty888 近零方差（σ≈0.02），mommygardevoir69 高峰值低基线（peak/mean > 3x），vanzzcoser 高频波动。三种方差模式对应三种不同的优化目标函数。",
        },
        "Algorithm": {
            "EN": "IRL fitting shows the three creators optimize for different reward dimensions. The SOP type's w_play is highest; the Anchor's w_engagement is highest. Today's recommender weights play_growth too aggressively, systematically rewarding SOP-style behavior — the root cause of ecosystem homogenization.",
            "CN": "IRL 拟合显示三个创作者在优化不同的 reward 维度。SOP型 w_play 权重最高，太太型 w_engagement 权重最高。当前推荐算法 play_growth 权重过高，正在系统性奖励 SOP 型行为，这是生态同质化的根本原因。",
        },
    },
    "irl": {
        "PM": {
            "EN": "The radar shows the platform thinks it's running one set of rules for everyone, but each creator is responding to a completely different incentive. This is not a creator problem — it's a reward function design problem.",
            "CN": "雷达图展示平台以为自己在用同一套规则管理所有创作者，但每个人在响应完全不同的激励。这不是创作者的问题，是 reward function 设计的问题。",
        },
        "Data": {
            "EN": "OLS fit on standardized features. Caveat: n is small per creator; weight direction matters more than absolute magnitude. R² is shown for transparency, not for causal inference.",
            "CN": "OLS 拟合，标准化特征。注意：n=60，统计显著性有限，权重方向比绝对值更重要。R² 仅供参考，不做因果推断。",
        },
        "Algorithm": {
            "EN": "Simplified linear IRL. For production, use MaxEnt IRL or GAIL to handle nonlinear rewards. Current weights are usable as a feature-engineering prior for creator risk-tier models.",
            "CN": "线性 IRL 简化版。生产环境建议 MaxEnt IRL 或 GAIL 处理非线性奖励。当前权重可作为创作者风险分级模型的特征工程先验。",
        },
    },
    "hacking": {
        "PM": {
            "EN": "Red marks = high plays + low engagement + risky content. These are not policy violations — they are signs the incentive system has failed. Traditional moderation tools cannot catch this because nothing is technically wrong with the content. This is exactly where governance PM matters.",
            "CN": "红色标注 = 高播放 + 低互动 + 高风险内容。这不是违规，但是平台激励失效的信号。传统审核工具发现不了这个，因为这些内容没有违规——这正是治理 PM 存在的价值。",
        },
        "Data": {
            "EN": "Trigger condition: play > 75th pct AND engagement < 25th pct AND risk > 0.5. Rule-based; for production, use Isolation Forest or autoencoder-based unsupervised anomaly detection to remove the manual threshold dependency.",
            "CN": "检测条件：play > 75th pct AND engagement < 25th pct AND risk > 0.5。规则型检测，生产环境建议 Isolation Forest 或 autoencoder 做无监督异常检测，消除人工阈值依赖。",
        },
        "Algorithm": {
            "EN": "Reward hacking is, fundamentally, exploiting the recommender's reward proxy. Monitor the play/engagement ratio distribution; trigger review when a creator drifts >2σ from peer mean for sustained windows. This signal can feed directly into the recommender as negative feedback.",
            "CN": "Reward hacking 本质是 exploit 推荐模型的 reward proxy。监控 play/engagement 比值分布，持续偏离同类均值 2σ 以上触发复核。该信号可直接加入推荐模型负反馈。",
        },
    },
    "ews": {
        "PM": {
            "EN": "Three cards, three creator-archetype early warnings — fired before content moderation would catch anything, because content has not violated yet but behavioral patterns predict risk. This is what governance PM should actually do: shift from reactive enforcement to proactive identification of systemic bias.",
            "CN": "三个 card 对应三种创作者类型的早期预警信号。这套预警在传统内容审核之前触发——内容还没违规，但行为模式已经预示风险。这是治理 PM 真正应该做的事：从被动响应违规，到主动识别系统性偏差。",
        },
        "Data": {
            "EN": "Each signal is one computable trigger condition: variance collapse → rolling-σ; spike-cliff → peak/mean ratio with descent confirmation; quality–volatility divergence → joint condition on engagement-z-score and reward σ. All three can be wired straight into a streaming pipeline.",
            "CN": "每个信号是一个可计算的 trigger condition：variance collapse 用 rolling-σ，spike-cliff 用 peak/mean ratio，quality-volatility divergence 用 engagement-z-score 与 reward-σ 的二维条件。生产环境可直接挂到流式管道上。",
        },
        "Algorithm": {
            "EN": "Three classes of anomaly detector: rolling-window variance monitor; change-point detection (CUSUM / Bayesian online change-point); 2-D conditional trigger. Recommended placement: as a gating layer upstream of the recommender, influencing the candidate set rather than punishing after the fact.",
            "CN": "三类预警对应三类异常检测算子：滑窗方差监控、变点检测（CUSUM/Bayesian online change point）、二维条件触发。建议作为推荐模型上游的 gating layer，影响候选集而非事后惩罚。",
        },
    },
    "simulation": {
        "PM": {
            "EN": "Each slider is a policy intention translated into a model parameter — the shared language between PM and the algorithm team. What you change is not a number, it is the platform's stance toward creator behavior.",
            "CN": "每个 slider 是一个 policy 意图翻译成的模型参数。这是 PM 和算法团队对话的共同语言——你改变的不是数字，是平台对创作者行为的态度。",
        },
        "Data": {
            "EN": "Prediction model: linear response + adaptation lag. delta = Σ(sensitivity_i × Δweight_i). Lag is estimated from behavioral inertia. For production, use a Kalman filter to update trajectories in real time.",
            "CN": "预测模型：线性响应 + adaptation lag。delta = Σ(sensitivity_i × delta_weight_i)。Lag 基于行为惯性估计。生产环境建议 Kalman filter 做实时 trajectory 更新。",
        },
        "Algorithm": {
            "EN": "Sliders adjust the reward function weight vector; the model predicts each creator's policy convergence under the new reward. Memory phase = off-policy interval; adaptation phase = on-policy convergence. Adaptation lag sets the minimum viable A/B test window.",
            "CN": "Slider 调整的是 reward function 权重向量，预测创作者 policy 在新 reward 下的收敛行为。Memory phase = off-policy 阶段，adaptation phase = on-policy 收敛。Adaptation lag 决定 A/B test 最短实验周期。",
        },
    },
    "governance": {
        "PM": {
            "EN": "The same edge-content video should weight differently in moderation depending on whether it came from the Anchor or from the SOP type. This taxonomy can convert directly into a differentiated guideline for the labeling team.",
            "CN": "同一个擦边内容，来自太太型和SOP型的标注权重应该不同。这套 taxonomy 可以直接变成标注团队的差异化指南。",
        },
        "Data": {
            "EN": "Intervention mapping — high w_risk → content classifier fine-tuning; w_play >> w_engagement → ranking weight recalibration; reward cliff → graduated enforcement curve.",
            "CN": "Intervention mapping：w_risk high → content classifier fine-tuning；w_play >> w_engagement → ranking weight recalibration；reward cliff → graduated enforcement curve。",
        },
        "Algorithm": {
            "EN": "Experiment design: stratified A/B test, minimum window = max(adaptation_lag) = 6 weeks. Control keeps current weights; treatment moves per simulation; analyze results stratified by archetype.",
            "CN": "实验设计：分层 A/B test，最短实验周期 = max(adaptation_lag) = 6 weeks。控制组保持当前权重，实验组按 simulation 结果调整，按 archetype 分层分析结果。",
        },
    },
}

def insight(key):
    aud = st.session_state.get("audience", "PM")
    text = INSIGHTS[key][aud][LANG]
    st.markdown(f'<div class="note">{text}</div>', unsafe_allow_html=True)

# ────────────── Header + language toggle ──────────────
n_videos = len(df); n_creators = df["username"].nunique()

title_col, lang_col = st.columns([6, 1])
with title_col:
    st.markdown(
        f'<h1 class="page-title">{t("Creator Behavior Intelligence · TikTok LIVE Ecosystem · Cosplay Vertical", "创作者行为智能 · TikTok LIVE 生态 · Cosplay 垂类")}</h1>'
        f'<div class="page-subtitle">{t(f"{n_creators} creator archetypes · {n_videos} videos · public TikTok data · proof of concept", f"{n_creators} 个创作者原型 · {n_videos} 个视频 · TikTok 公开数据 · 概念验证")}</div>',
        unsafe_allow_html=True,
    )
with lang_col:
    st.markdown('<div class="lang-row" style="text-align:right;">', unsafe_allow_html=True)
    lc1, lc2 = st.columns(2)
    with lc1:
        if st.button("English", key="lang_EN", type=("primary" if LANG == "EN" else "secondary")):
            st.session_state.lang = "EN"; st.rerun()
    with lc2:
        if st.button("中文", key="lang_CN", type=("primary" if LANG == "CN" else "secondary")):
            st.session_state.lang = "CN"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="audience-row">', unsafe_allow_html=True)
a1, a2, a3, _ = st.columns([1.4, 2.0, 2.4, 5.0], gap="small")
audience_options = [
    (t("I'm a PM",                  "我是 PM"),               "PM"),
    (t("I'm a Data Scientist",      "我是数据科学家"),         "Data"),
    (t("I'm an Algorithm Engineer", "我是算法工程师"),         "Algorithm"),
]
for col, (label, value) in zip([a1, a2, a3], audience_options):
    with col:
        is_active = st.session_state.audience == value
        if st.button(label, key=f"aud_{value}", type=("primary" if is_active else "secondary")):
            st.session_state.audience = value
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ────────────── Business Impact Summary Bar ──────────────
st.markdown(f"""
<div class="biz-bar">
  <div class="biz-stat">
    <div class="label">{t("Engagement Inversion", "互动率倒挂")}</div>
    <div class="num">{(1/quality_gap):.1f}×</div>
    <div class="desc">{t(
        f'SOP-type engagement is <b style="color:{HI}">{(1/quality_gap):.1f}×</b> the so-called Anchor — engagement-as-quality is broken',
        f'SOP型 engagement 是太太型的 <b style="color:{HI}">{(1/quality_gap):.1f}×</b> ——「互动率即质量」的假设不成立')}</div>
  </div>
  <div class="biz-stat">
    <div class="label">{t("Hacking Signal", "Hacking 信号")}</div>
    <div class="num">{hacking_share:.1f}%</div>
    <div class="desc">{t(
        f'<b style="color:{HI}">{total_hacks}</b> of <b style="color:{HI}">{total_videos}</b> videos exploiting algorithm',
        f'{total_videos} 个视频中有 <b style="color:{HI}">{total_hacks}</b> 个在 exploit 算法')}</div>
  </div>
  <div class="biz-stat">
    <div class="label">{t("Gambler Cycle", "赌徒周期")}</div>
    <div class="num">{gambler_ratio:.1f}×</div>
    <div class="desc">{t(
        f'Boundary Prober peak reward <b style="color:{HI}">{gambler_ratio:.1f}×</b> above baseline — boom &amp; bust',
        f'边界党 peak reward 是基线的 <b style="color:{HI}">{gambler_ratio:.1f}×</b> ——爆一次归零再赌')}</div>
  </div>
  <div class="biz-stat">
    <div class="label">{t("Stability Gap", "稳定性差距")}</div>
    <div class="num">{stability_gap:.1f}×</div>
    <div class="desc">{t(
        f'Best creator is <b style="color:{HI}">{stability_gap:.1f}×</b> more volatile than the machine',
        f'最优质的创作者波动是机器型的 <b style="color:{HI}">{stability_gap:.1f}×</b>')}</div>
  </div>
</div>
<div class="biz-bar-note">{t(
    'these four numbers point to an <b>incentive alignment gap</b> — the current reward structure is not protecting what the ecosystem needs most.',
    '这四个数字指向<b>激励对齐缺口</b>——当前 reward 结构没有保护到生态最需要保护的部分。')}</div>
""", unsafe_allow_html=True)

order = ["mommygardevoir69", "cosplaybeauty888", "vanzzcoser"]

# ════════════════════════════ MODULE 1 — Trajectory Overview ════════════════════════════
st.markdown(f"<h2>{t('Trajectory Overview', '轨迹概览')}</h2>", unsafe_allow_html=True)

ks_label = t("avg engagement", "平均互动率")
ks_html = '<div class="traj-keystats">'
for u in ["vanzzcoser", "cosplaybeauty888", "mommygardevoir69"]:
    ks_html += f'@{u} {ks_label} <span class="num">{M[u]["avg_engagement"]*100:.1f}%</span><br>'
ks_html += '</div>'
st.markdown(ks_html, unsafe_allow_html=True)

fig1 = go.Figure()
for u in order:
    sub = weekly[weekly["username"] == u].sort_values("week")
    if len(sub) < 2: continue
    smoothed = sub["reward_signal"].rolling(3, min_periods=1).mean()
    c = color_of(u)
    fig1.add_trace(go.Scatter(
        x=sub["week"], y=smoothed, name=f"@{u}",
        mode="lines+markers", line=dict(color=c, width=1.8), marker=dict(size=4, color=c),
        hovertemplate=f"@{u}<br>%{{x|%Y-%m-%d}}<br>reward %{{y:+.3f}}<extra></extra>",
        showlegend=False,
    ))
for u in order:
    sub = weekly[weekly["username"] == u].sort_values("week")
    if len(sub) < 2: continue
    smoothed = sub["reward_signal"].rolling(3, min_periods=1).mean()
    fig1.add_annotation(
        x=sub["week"].iloc[-1], y=smoothed.iloc[-1], text=f"  {strategy_of(u)}",
        showarrow=False, xanchor="left", yanchor="middle",
        font=dict(family=MONO, size=13, color=color_of(u)), xshift=6,
    )

mg = weekly[weekly["username"] == "mommygardevoir69"].sort_values("week").reset_index(drop=True)
if len(mg) >= 3:
    mg_smooth = mg["reward_signal"].rolling(3, min_periods=1).mean()
    peak_i = int(mg_smooth.idxmax())
    fig1.add_annotation(
        x=mg["week"].iloc[peak_i], y=mg_smooth.iloc[peak_i],
        text=t("single viral spike → immediate suppression", "单次爆款 → 立即被压制"),
        showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=ROSE,
        ax=50, ay=-52, font=dict(family=MONO, size=13, color=ROSE), xanchor="left",
        bgcolor=BG, bordercolor=BORDER, borderwidth=0, borderpad=4,
    )

cb = weekly[weekly["username"] == "cosplaybeauty888"].sort_values("week").reset_index(drop=True)
if len(cb) >= 3:
    cb_smooth = cb["reward_signal"].rolling(3, min_periods=1).mean()
    mid_i = len(cb) // 2
    fig1.add_annotation(
        x=cb["week"].iloc[mid_i], y=cb_smooth.iloc[mid_i],
        text=t("zero variance — optimizing for stability, not quality", "零方差 — 优化的是稳定性，不是质量"),
        showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=SAND,
        ax=-40, ay=48, font=dict(family=MONO, size=13, color=SAND), xanchor="right",
        bgcolor=BG, bordercolor=BORDER, borderwidth=0, borderpad=4,
    )

fig1.add_hline(y=0, line_dash="dot", line_color=MUTED, line_width=0.8, opacity=0.5)
fig1.update_layout(height=440, **PLOTLY)
fig1.update_yaxes(title=t("weekly reward signal (smoothed)", "周度 reward signal（平滑）"))
fig1.update_xaxes(title=None)
st.plotly_chart(fig1, use_container_width=True)
insight("trajectory")

eng_inv = 1 / quality_gap  # SOP / Anchor
vol_mult = M["vanzzcoser"]["reward_std"] / max(M["cosplaybeauty888"]["reward_std"], 1e-9)
st.markdown(
    f'<div class="note-extra">'
    f'{t(
        f"SOP-type engagement is <b>{eng_inv:.1f}×</b> the Anchor's, yet the Anchor's reward-signal volatility is <b>{vol_mult:.1f}×</b> the Machine's — the current incentive structure does not adequately protect quality stability.",
        f"SOP型 engagement 是太太型的 <b>{eng_inv:.1f}×</b>，但太太型的 reward signal 波动是 SOP型的 <b>{vol_mult:.1f}×</b>——当前激励结构对质量稳定性的保护不足。"
    )}'
    f'</div>',
    unsafe_allow_html=True,
)

# ════════════════════════════ MODULE 2 — Inferred Reward Functions ════════════════════════════
st.markdown(f"<h2>{t('Inferred Reward Functions', '推导的奖励函数')}</h2>", unsafe_allow_html=True)

feats = ["play_growth","engagement_rate","posting_frequency","content_risk"]
labels_short = (
    ["play growth","engagement","posting freq","content risk"] if LANG == "EN"
    else ["播放增长","互动率","发布频率","内容风险"]
)

cL, cR = st.columns([3, 2], gap="large")
with cL:
    fig2 = go.Figure()
    for u in order:
        w = irl[u]["weights"]
        vals = [w[f] for f in feats]
        c = color_of(u)
        fig2.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=labels_short + [labels_short[0]],
            fill="toself", name=f"@{u}",
            line=dict(color=c, width=1.6), fillcolor=c, opacity=0.18,
            hovertemplate=f"@{u}<br>%{{theta}} %{{r:+.2f}}<extra></extra>",
        ))
    rmax = max([max(abs(v) for v in irl[u]["weights"].values()) for u in order] or [1])
    fig2.update_layout(
        height=440, paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=TEXT, size=13, family=MONO),
        polar=dict(
            bgcolor=BG,
            radialaxis=dict(range=[-rmax*1.15, rmax*1.15], gridcolor=GRID, color=DIM, tickfont=dict(family=MONO, size=11)),
            angularaxis=dict(gridcolor=GRID, color=DIM, tickfont=dict(family=MONO, size=13)),
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color=DIM), orientation="h", yanchor="bottom", y=-0.16, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=14, b=44),
    )
    st.plotly_chart(fig2, use_container_width=True)

with cR:
    rows = []
    for u in order:
        w = irl[u]["weights"]
        rows.append({
            t("creator", "创作者"): f"@{u}",
            "play_growth": f"{w['play_growth']:+.2f}",
            "engagement": f"{w['engagement_rate']:+.2f}",
            "posting_freq": f"{w['posting_frequency']:+.2f}",
            "content_risk": f"{w['content_risk']:+.2f}",
            "R²": f"{irl[u]['r2']:.2f}",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=200)

insight("irl")

# ════════════════════════════ MODULE 3 — Reward Hacking Detection ────────────────────────────
st.markdown(f"<h2>{t('Reward Hacking Detection', 'Reward Hacking 检测')}</h2>", unsafe_allow_html=True)

hack_by_creator = hacks.groupby("username")["is_hacking"].sum().sort_values(ascending=False)
top_hack_user = hack_by_creator.index[0] if hack_by_creator.iloc[0] > 0 else order[0]

if M[top_hack_user]["n_hacking"] > 0:
    bad_u = hacks[(hacks["username"] == top_hack_user) & hacks["is_hacking"]]
    avg_play_mult = bad_u["play_count"].mean() / max(M[top_hack_user]["median_play"], 1)
    avg_eng_def = M[top_hack_user]["median_eng"] / max(bad_u["engagement_rate"].mean(), 1e-9)
    pattern_map = {
        "vanzzcoser":       (t("Quality creator pulled into edge content cycle", "优质创作者被卷入擦边内容循环")),
        "cosplaybeauty888": (t("Zero-variance posting profile — systematic algorithm exploit", "零方差发布——系统性 exploit 算法")),
        "mommygardevoir69": (t("High-risk gambling cycle — boundary probing for reach", "高风险赌徒循环——为流量试探边界")),
    }
    rec_map = {
        "vanzzcoser":       t("Distribution audit — verify the recommender is not pulling tenured creators into risky surfaces.",
                              "分发审计——核查推荐系统是否把资深创作者推向风险面。"),
        "cosplaybeauty888": t("Flag for algo weight recalibration — NOT content removal.",
                              "标记进入算法权重重校准，不要走内容删除。"),
        "mommygardevoir69": t("Graduated throttling + creator education — NOT immediate cliff penalty.",
                              "渐进式限流 + 创作者教育，不要直接断崖处罚。"),
    }
    pattern = pattern_map[top_hack_user]
    rec = rec_map[top_hack_user]
else:
    avg_play_mult = avg_eng_def = 0.0
    pattern = t("No active hacking signals in this cohort window", "当前窗口内无活跃 hacking 信号")
    rec = t("Maintain monitoring", "维持监控")

chart_col, alert_col = st.columns([3.0, 2.0], gap="large")

with chart_col:
    fig3 = go.Figure()
    normal = hacks[~hacks["is_hacking"]]
    fig3.add_trace(go.Scatter(
        x=normal["play_count"], y=normal["engagement_rate"],
        mode="markers", name="videos",
        marker=dict(
            size=7, color=normal["content_risk"],
            colorscale=[[0, TEAL], [0.5, SAND], [1, ROSE]],
            cmin=0, cmax=1, opacity=0.75,
            colorbar=dict(title=dict(text=t("risk", "风险"), font=dict(family=MONO, size=11, color=DIM)),
                          thickness=10, len=0.55, tickfont=dict(family=MONO, size=10, color=MUTED), outlinewidth=0),
            line=dict(width=0),
        ),
        customdata=np.stack([normal["username"], normal["created_time"].dt.strftime("%Y-%m-%d"), normal["content_risk"]], axis=-1),
        hovertemplate="@%{customdata[0]}<br>%{customdata[1]}<br>plays %{x:,}<br>eng %{y:.3f}<br>risk %{customdata[2]:.2f}<extra></extra>",
        showlegend=False,
    ))
    bad = hacks[hacks["is_hacking"]]
    if len(bad):
        fig3.add_trace(go.Scatter(
            x=bad["play_count"], y=bad["engagement_rate"],
            mode="markers", name="hacking signal",
            marker=dict(size=14, color=PINK, symbol="x-thin", line=dict(width=2.4, color=PINK)),
            customdata=np.stack([bad["username"], bad["created_time"].dt.strftime("%Y-%m-%d"), bad["content_risk"]], axis=-1),
            hovertemplate="@%{customdata[0]}<br>%{customdata[1]}<br>plays %{x:,}<br>eng %{y:.3f}<br>risk %{customdata[2]:.2f}<extra></extra>",
        ))
        fig3.add_annotation(
            x=bad["play_count"].max(), y=bad["engagement_rate"].max(),
            text=t(f"reward hacking detected · {len(bad)} videos", f"检测到 reward hacking · {len(bad)} 个视频"),
            showarrow=False, xanchor="right", yanchor="bottom",
            font=dict(family=MONO, size=13, color=PINK),
            xshift=-4, yshift=10,
        )
    fig3.update_layout(height=460, **PLOTLY)
    fig3.update_xaxes(type="log", title=t("play count", "播放量"))
    fig3.update_yaxes(title=t("engagement rate", "互动率"))
    st.plotly_chart(fig3, use_container_width=True)

with alert_col:
    st.markdown(f"""
    <div class="alert-panel">
      <span class="alert-tag">⚠ {t("Risk Alert", "风险预警")}</span>
      <div class="alert-line">{t("Hacking signals detected:", "检测到 Hacking 信号：")}</div>
      <div class="alert-line"><span class="alert-num">{total_hacks}</span> / {total_videos} {t("videos", "视频")} · <span class="alert-num">{hacking_share:.1f}%</span></div>
      <div class="alert-divider"></div>
      <div class="alert-creator">@{top_hack_user}</div>
      <div class="alert-line">{t(
          f'<span class="alert-num">{M[top_hack_user]["hacking_pct"]:.1f}%</span> of their videos trigger hacking signal',
          f'其 <span class="alert-num">{M[top_hack_user]["hacking_pct"]:.1f}%</span> 的视频触发 hacking 信号')}</div>
      <div class="alert-line">{t("avg play count:", "平均播放量：")} <span class="alert-num">{avg_play_mult:.1f}×</span> {t("above their normal", "高于其正常水平")}</div>
      <div class="alert-line">{t("avg engagement:", "平均互动率：")} <span class="alert-num">{avg_eng_def:.1f}×</span> {t("below their normal", "低于其正常水平")}</div>
      <div class="alert-pattern"><b style="color:{TEXT}">{t("Pattern", "模式")}:</b> {pattern}</div>
      <div class="alert-action"><b>{t("Recommended action", "建议动作")}:</b><br>{rec}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    f'<div class="note-warn">'
    f'{t("these videos are not policy violations. they are reward function failures. traditional moderation tools cannot catch this.",
        "这些视频不违规。它们是 reward function 失效的信号。传统审核工具发现不了。")}'
    f'</div>',
    unsafe_allow_html=True,
)
insight("hacking")

# ════════════════════════════ MODULE 4 — Early Warning Signals ════════════════════════════
st.markdown(f"<h2>{t('Early Warning Signals', '早期预警信号')}</h2>", unsafe_allow_html=True)
st.markdown(
    f'<div class="page-subtitle" style="margin-top:-2px;">'
    f'{t("accounts showing pre-violation behavioral patterns · not yet flagged by content moderation",
        "出现违规前行为模式的账号 · 尚未被内容审核标记")}'
    f'</div>',
    unsafe_allow_html=True,
)

sop_4w_std = M["cosplaybeauty888"]["reward_std"]
variance_collapse_active = sop_4w_std < 0.05
spike_cliff_active = gambler_ratio > 3.0
cohort_eng = np.mean([M[u]["avg_engagement"] for u in CREATORS])
vanzz_eng_z = M["vanzzcoser"]["avg_engagement"] / max(cohort_eng, 1e-9)
quality_div_active = (vanzz_eng_z > 2.0) and (M["vanzzcoser"]["reward_std"] > 0.3)

def tag(active):
    if active:
        return f'<span class="ews-tag active">{t("Active", "触发中")}</span>'
    return f'<span class="ews-tag historical">{t("Historical", "历史")}</span>'

triggered_by = t("currently triggered by", "当前触发账号")
trigger_label = t("trigger", "触发条件")
measured_label = t("measured", "实测值")
risk_label = t("Risk", "风险")
rec_label = t("Recommended", "建议")

st.markdown(f"""
<div class="ews-grid">

  <div class="ews-card amber">
    {tag(variance_collapse_active)}
    <div class="ews-name">{t("Variance Collapse", "方差坍缩")}</div>
    <div class="ews-row"><span class="k">{trigger_label}</span><span class="v">σ(reward) &lt; 0.05 {t("over recent window", "近期窗口内")}</span></div>
    <div class="ews-row"><span class="k">{measured_label}</span><span class="v">σ = <b style="color:{HI}">{sop_4w_std:.3f}</b></span></div>
    <div class="ews-creator">{triggered_by} <span class="at">@cosplaybeauty888</span></div>
    <div class="ews-divider"></div>
    <div class="ews-action">
      <b>{risk_label}:</b> {t("systematic algorithm exploit, content homogenization accelerating.", "系统性 exploit 算法，内容同质化加速。")}<br><br>
      <b>{rec_label}:</b> {t("algorithm weight recalibration. No human moderation required.", "算法权重重校准，不需要人工审核。")}
    </div>
  </div>

  <div class="ews-card red">
    {tag(spike_cliff_active)}
    <div class="ews-name">{t("Spike-Cliff Pattern", "尖峰-断崖模式")}</div>
    <div class="ews-row"><span class="k">{trigger_label}</span><span class="v">{t("single peak &gt; 3× mean, followed by descent", "单次峰值 &gt; 3× 均值，后续连续下降")}</span></div>
    <div class="ews-row"><span class="k">{measured_label}</span><span class="v">peak/mean = <b style="color:{HI}">{gambler_ratio:.1f}×</b></span></div>
    <div class="ews-creator">{triggered_by} <span class="at">@mommygardevoir69</span></div>
    <div class="ews-divider"></div>
    <div class="ews-action">
      <b>{risk_label}:</b> {t("creator entered gambling cycle. Probability of next risky probe is high.", "创作者进入赌徒循环，下一次风险试探概率高。")}<br><br>
      <b>{rec_label}:</b> {t("pre-stream risk nudge + graduated intervention. Don't wait for the violation.", "开播前风险提示 + 渐进干预，不要等违规发生。")}
    </div>
  </div>

  <div class="ews-card cyan">
    {tag(quality_div_active)}
    <div class="ews-name">{t("Quality–Volatility Divergence", "质量-波动背离")}</div>
    <div class="ews-row"><span class="k">{trigger_label}</span><span class="v">{t("engagement &gt; 2× cohort avg AND σ(reward) &gt; 0.3", "互动率 &gt; 2× 队列均值 且 σ(reward) &gt; 0.3")}</span></div>
    <div class="ews-row"><span class="k">{measured_label}</span><span class="v">eng z = <b style="color:{HI}">{vanzz_eng_z:.1f}×</b> · σ = <b style="color:{HI}">{M["vanzzcoser"]["reward_std"]:.2f}</b></span></div>
    <div class="ews-creator">{triggered_by} <span class="at">@vanzzcoser</span></div>
    <div class="ews-divider"></div>
    <div class="ews-action">
      <b>{risk_label}:</b> {t("high-quality creator getting unstable returns. Churn risk elevated.", "高质量创作者得不到稳定回报，流失风险升高。")}<br><br>
      <b>{rec_label}:</b> {t("build a quality-protection floor — engagement-weighted distribution for tenured creators.", "建立质量保护底——为资深创作者使用 engagement-weighted 分发。")}
    </div>
  </div>

</div>
""", unsafe_allow_html=True)
insight("ews")

# ════════════════════════════ MODULE 5 — Policy Simulation ════════════════════════════
ADAPTATION_LAG = {"vanzzcoser": 6, "cosplaybeauty888": 2, "mommygardevoir69": 4}
OLD_PLATFORM = dict(play_growth=0.5, engagement_rate=0.3, posting_frequency=0.2, content_risk=0.0)

st.markdown(f"<h2>{t('Policy Simulation', '策略仿真')}</h2>", unsafe_allow_html=True)
st.markdown(f'<div class="sim-title">{t("What happens to each creator archetype in the 12 weeks after a policy change?", "策略调整后的 12 周内，每种创作者原型会怎么演变？")}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sim-subtitle">{t("translating governance intentions into behavioral predictions · bridging policy and algorithm teams", "把治理意图翻译成行为预测 · 连接 policy 和算法团队")}</div>', unsafe_allow_html=True)

ctrl_col, plot_col, impact_col = st.columns([1.0, 2.4, 2.2], gap="medium")

with ctrl_col:
    st.markdown('<div class="policy-sim-marker"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sim-caption">{t("each slider is a policy intention translated into a model parameter.", "每个 slider 是一个 policy 意图翻译成的模型参数。")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sim-instruction">{t("drag to simulate · numbers update in real time", "拖动 slider · 数字实时更新")}</div>', unsafe_allow_html=True)
    new_eng  = st.slider(t("Reward genuine engagement quality more",   "平台更重视真实互动质量"),   0.1, 0.7, 0.3, 0.05, key="sim_eng")
    new_play = st.slider(t("Reward raw play count less",                "平台降低对纯播放量的奖励"), 0.1, 0.7, 0.5, 0.05, key="sim_play")
    new_risk = st.slider(t("Penalize high-risk content more",           "平台主动惩罚高风险内容"),   0.0, 0.5, 0.0, 0.05, key="sim_risk")
    new_post = st.slider(t("Reward consistent posting",                  "平台鼓励稳定持续创作"),     0.1, 0.5, 0.2, 0.05, key="sim_post")

new_platform = dict(
    play_growth=new_play, engagement_rate=new_eng,
    posting_frequency=new_post, content_risk=-new_risk,
)

def converged_delta(u, platform):
    w = irl[u]["weights"]
    delta = sum(w[k] * (platform[k] - OLD_PLATFORM[k]) for k in OLD_PLATFORM)
    lag = ADAPTATION_LAG[u]
    return delta * ((12 - lag) / 12)

with plot_col:
    fig5 = go.Figure()
    horizon = 12
    policy_change = pd.Timestamp(weekly["week"].max())

    for u in order:
        sub = weekly[weekly["username"] == u].sort_values("week").reset_index(drop=True)
        if len(sub) < 2: continue
        c = color_of(u)
        smoothed = sub["reward_signal"].rolling(3, min_periods=1).mean()

        fig5.add_trace(go.Scatter(
            x=sub["week"], y=smoothed,
            mode="lines", line=dict(color=c, width=1.8),
            hovertemplate=f"@{u}<br>%{{x|%Y-%m-%d}}<br>reward %{{y:+.3f}}<extra></extra>",
            showlegend=False,
        ))

        baseline = float(smoothed.iloc[-3:].mean())
        w = irl[u]["weights"]
        delta_reward = sum(w[k] * (new_platform[k] - OLD_PLATFORM[k]) for k in OLD_PLATFORM)
        lag = ADAPTATION_LAG[u]

        future_x = [policy_change + pd.Timedelta(weeks=i) for i in range(horizon + 1)]
        future_y = [baseline]
        for week in range(1, horizon + 1):
            if week < lag:
                future_y.append(baseline)
            else:
                progress = (week - lag) / max(horizon - lag, 1)
                future_y.append(baseline + delta_reward * progress)

        fig5.add_trace(go.Scatter(
            x=future_x, y=future_y,
            mode="lines", line=dict(color=c, width=1.6, dash="dot"),
            opacity=0.55,
            hovertemplate=f"@{u} predicted<br>%{{x|%Y-%m-%d}}<br>reward %{{y:+.3f}}<extra></extra>",
            showlegend=False,
        ))

        if lag <= horizon:
            fig5.add_trace(go.Scatter(
                x=[future_x[lag]], y=[future_y[lag]],
                mode="markers",
                marker=dict(color=c, size=8, symbol="circle", line=dict(color=BG, width=1.5)),
                showlegend=False,
                hovertemplate=f"@{u} memory exhausted · adaptation begins<br>%{{x|%Y-%m-%d}}<extra></extra>",
            ))

    fig5.add_shape(
        type="line", x0=policy_change, x1=policy_change,
        y0=0, y1=1, yref="paper",
        line=dict(color=DIM, width=1, dash="dash"),
    )
    fig5.add_annotation(
        x=policy_change, y=1.03, xref="x", yref="paper",
        text=t("policy change", "策略调整"), showarrow=False, xanchor="center", yanchor="bottom",
        font=dict(family=MONO, size=12, color=DIM),
    )
    fig5.add_annotation(
        x=policy_change + pd.Timedelta(weeks=4), y=1, xref="x", yref="paper",
        text=t("memory exhausted · adaptation begins", "记忆耗尽 · 进入适应阶段"),
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(family=MONO, size=12, color=MUTED),
    )
    fig5.add_hline(y=0, line_dash="dot", line_color=MUTED, line_width=0.8, opacity=0.4)
    fig5.update_layout(height=420, **PLOTLY)
    fig5.update_yaxes(title=t("weekly reward signal", "周度 reward signal"))
    fig5.update_xaxes(title=None)
    st.plotly_chart(fig5, use_container_width=True)

with impact_col:
    d_anchor = converged_delta("vanzzcoser",       new_platform) * 100
    d_sop    = converged_delta("cosplaybeauty888", new_platform) * 100
    d_prober = converged_delta("mommygardevoir69", new_platform) * 100

    def delta_cell(value, label):
        if abs(value) < 0.5:
            cls = "flat"; sign = ""
        elif value > 0:
            cls = "positive"; sign = "+"
        else:
            cls = "negative"; sign = ""
        return f'<td class="t-delta {cls}">{sign}{value:.1f}% {label}</td>'

    th_creator   = t("Creator", "创作者")
    th_now       = t("Today", "当前")
    th_after     = t("After Adapt", "调整后")
    th_meaning   = t("Meaning", "意义")
    th_delta     = t("Predicted Δ", "预测变化")

    name_a = t("Anchor",     "太太型");  sub_a = t("Ecosystem Anchor",    "高质量创作者")
    name_s = t("Machine",    "SOP型");   sub_s = t("Algorithm Exploiter", "算法 exploit 型")
    name_p = t("Prober",     "边界党");   sub_p = t("Boundary Prober",     "边界试探型")

    now_a = t("High quality but unstable", "高质量但不稳定")
    now_s = t("Zero-risk farming", "零风险刷量")
    now_p = t("Gambling cycle", "赌徒循环")

    aft_a = t("Stability up after 6 wks", "6 周后稳定性提升")
    aft_s = t("Quality up within 2 wks",  "2 周内被迫提升质量")
    aft_p = t("Risk probing down at 4 wks", "4 周后试探频率下降")

    mn_a = t("Real protection for top creators", "真正保护优质创作者")
    mn_s = t("Exploit window narrows",            "Exploit 空间收窄")
    mn_p = t("Graduated > cliff penalty",         "渐进干预胜过断崖处罚")

    lbl_stab = t("reward stability",     "reward 稳定性")
    lbl_freq = t("posting frequency",    "发布频率")
    lbl_risk = t("risk content ratio",   "风险内容比例")

    st.markdown(f"""
    <table class="impact">
      <thead>
        <tr><th>{th_creator}</th><th>{th_now}</th><th>{th_after}</th><th>{th_meaning}</th><th>{th_delta}</th></tr>
      </thead>
      <tbody>
        <tr>
          <td class="t-creator"><span class="swatch" style="background:{TEAL};"></span><span class="name">{name_a}</span><span class="sub">{sub_a}</span></td>
          <td class="t-now">{now_a}</td>
          <td class="t-after">{aft_a}</td>
          <td class="t-meaning">{mn_a}</td>
          {delta_cell(d_anchor, lbl_stab)}
        </tr>
        <tr>
          <td class="t-creator"><span class="swatch" style="background:{SAND};"></span><span class="name">{name_s}</span><span class="sub">{sub_s}</span></td>
          <td class="t-now">{now_s}</td>
          <td class="t-after">{aft_s}</td>
          <td class="t-meaning">{mn_s}</td>
          {delta_cell(d_sop, lbl_freq)}
        </tr>
        <tr>
          <td class="t-creator"><span class="swatch" style="background:{ROSE};"></span><span class="name">{name_p}</span><span class="sub">{sub_p}</span></td>
          <td class="t-now">{now_p}</td>
          <td class="t-after">{aft_p}</td>
          <td class="t-meaning">{mn_p}</td>
          {delta_cell(d_prober, lbl_risk)}
        </tr>
      </tbody>
    </table>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div style="margin-top:16px;">
  <div class="sim-footer">{t("Anchor (vanzzcoser) · adaptation lag 6 weeks · engagement-sensitive · slowest to be protected",
                              "太太型 (vanzzcoser) · adaptation lag 6 周 · engagement 敏感 · 受保护最慢")}</div>
  <div class="sim-footer">{t("Machine (cosplaybeauty888) · adaptation lag 2 weeks · play-growth-sensitive · fastest to respond",
                              "SOP型 (cosplaybeauty888) · adaptation lag 2 周 · play_growth 敏感 · 最快响应")}</div>
  <div class="sim-footer">{t("Prober (mommygardevoir69) · adaptation lag 4 weeks · starts probing new boundaries after week 4",
                              "边界党 (mommygardevoir69) · adaptation lag 4 周 · 4 周后开始试探新边界")}</div>
</div>
""", unsafe_allow_html=True)
insight("simulation")

st.markdown(f"""
<div class="live-block">
  <span class="live-tag">{t("Extending to LIVE", "延伸到 LIVE 场景")}</span>
  {t(
    "In short-video, adaptation lag is measured in weeks. In a LIVE session, the same behavioral cycle compresses into a single 90-minute stream — open with safe content to build trust, probe boundaries mid-session, hit the highest-risk point at the gift peak, then snap back to safe content the moment a platform warning fires. The IRL frame applies directly to real-time risk forecasting in LIVE; what is needed is real-time behavioral signal, not weekly aggregates.",
    "短视频的 adaptation lag 是以周计算的。LIVE 里，同样的行为模式压缩在一场直播的 90 分钟内——开播建立安全感，中段试探边界，礼物高峰期达到最高风险点，平台警告触发后立刻切回安全内容。这套 IRL 框架直接适用于 LIVE 实时风险预判，需要的是实时行为信号，而不是周级别的聚合数据。"
  )}
</div>
""", unsafe_allow_html=True)

# ════════════════════════════ MODULE 6 — Governance Intervention ════════════════════════════
st.markdown(f"<h2>{t('Governance Intervention', '治理干预')}</h2>", unsafe_allow_html=True)

SCENARIO = dict(play_growth=0.3, engagement_rate=0.5, posting_frequency=0.2, content_risk=0.0)
sc_anchor = converged_delta("vanzzcoser",       SCENARIO) * 100
sc_sop    = converged_delta("cosplaybeauty888", SCENARIO) * 100
sc_prober = converged_delta("mommygardevoir69", SCENARIO) * 100

st.markdown(f"""
<div class="biz-case">
  <div class="case">
    <div class="num">{sc_anchor:+.1f}%</div>
    <div class="desc">{t(
      f'predicted reward stability lift for <b style="color:{TEXT}">Anchor</b> · 6 weeks',
      f'预测<b style="color:{TEXT}">太太型</b> reward 稳定性提升 · 6 周')}</div>
  </div>
  <div class="case">
    <div class="num">{sc_sop:+.1f}%</div>
    <div class="desc">{t(
      f'predicted posting-frequency change for <b style="color:{TEXT}">Machine</b> · 2 weeks',
      f'预测<b style="color:{TEXT}">SOP型</b>发布频率变化 · 2 周')}</div>
  </div>
  <div class="case">
    <div class="num">{sc_prober:+.1f}%</div>
    <div class="desc">{t(
      f'predicted risk-content-ratio change for <b style="color:{TEXT}">Prober</b> · 4 weeks',
      f'预测<b style="color:{TEXT}">边界党</b>风险内容比例变化 · 4 周')}</div>
  </div>
</div>
<div class="biz-case-foot">{t(
  "scenario: engagement weight raised 0.3 → 0.5 · play weight lowered 0.5 → 0.3 · based on current IRL weights and adaptation-lag estimates",
  "情景：engagement 权重 0.3 → 0.5 · play 权重 0.5 → 0.3 · 基于当前 IRL 权重和 adaptation lag 估计")}</div>
""", unsafe_allow_html=True)

th_c   = t("Creator", "创作者")
th_str = t("Inferred Strategy", "推断的策略")
th_tr  = t("Platform Unintentionally Trained", "平台无意训练出的结果")
th_int = t("Recommended Intervention", "建议干预")

rows_gov = [
    ("vanzzcoser", TEAL, "Ecosystem Anchor", "太太型 · Ecosystem Anchor",
     t("Quality-first", "质量优先"),
     t("Instability — high-quality creator left unprotected; reward signal swings independent of effort.",
       "不稳定 — 高质量创作者未被保护；reward signal 与努力无关。"),
     t("Build a quality signal independent of play count (engagement-depth, retention, repeat-viewer ratio) and weight it into distribution for tenured creators.",
       "建立独立于播放量的质量信号（互动深度、留存、复看率），并把它纳入资深创作者的分发权重。")),
    ("cosplaybeauty888", SAND, "Algorithm Exploiter", "SOP型 · Algorithm Exploiter",
     t("Zero-risk farming", "零风险刷量"),
     t("Content homogenization — flatlined reward at zero variance, no quality differentiation, no creative risk.",
       "内容同质化 — reward 平直在零附近，无质量区分、无创作风险。"),
     t("Adjust recommender weights to penalize low-variance content profiles; reward exploration and format experimentation.",
       "调整推荐权重，惩罚低方差内容画像；奖励内容探索和形式实验。")),
    ("mommygardevoir69", ROSE, "Boundary Prober", "边界党 · Boundary Prober",
     t("High-risk gambling", "高风险赌博"),
     t("Edge → punish → restart cycle — single spikes followed by hard suppression train creators to gamble rather than build.",
       "擦边 → 处罚 → 重启循环 — 单次爆款后紧跟硬压制，把创作者训练成赌徒而不是建设者。"),
     t("Replace cliff penalties with progressive intervention: graded reach throttling, in-product education at first violation, hard action only on repeat.",
       "用渐进干预替代断崖处罚：分级限流、首次违规产品内教育、重复违规才硬处置。")),
]

table_html = f"""
<table class="gov">
  <thead>
    <tr><th>{th_c}</th><th>{th_str}</th><th>{th_tr}</th><th>{th_int}</th></tr>
  </thead>
  <tbody>
"""
for u, c, _, name_label, strat, trained, intervention in rows_gov:
    table_html += f"""
    <tr>
      <td class="creator"><span class="swatch" style="background:{c};"></span><span class="name">@{u}</span>{name_label}</td>
      <td class="strategy">{strat}</td>
      <td class="trained">{trained}</td>
      <td class="intervention">{intervention}</td>
    </tr>
    """
table_html += "</tbody></table>"
st.markdown(table_html, unsafe_allow_html=True)
insight("governance")

# ────────────── Limitations ──────────────
limit_label = t("known limitations · what would change for production",
                "已知局限 · 生产环境会怎么改")

limit_items_en = [
    "<b>Sample size · n ≈ 60 per creator, ~5–10 weekly buckets after aggregation.</b> OLS over 4 features on ~7 points is illustrative, not statistically robust. R² shown for transparency, not as evidence; weight <i>direction</i> is the signal, magnitudes are not.",
    "<b>\"IRL\" is a regression analogy, not formal IRL.</b> Real IRL (MaxEnt, GAIL) recovers a reward function under which expert trajectories are optimal. This dashboard fits a linear regression of reward_signal on behavioral features — directionally useful, but the label is aspirational.",
    "<b>engagement_rate = (likes + comments + shares) / plays</b> — closer to TikTok's real definition than likes/plays, but plays still includes passive scrolls. True engagement requires retention/watch-time, which the public API does not expose.",
    "<b>content_risk_score is a hashtag lexicon, not a multimodal classifier.</b> #hanime, #doujin etc. trigger weight, but the actual videos may be in-genre discussion, not high-risk content. Production needs frame-level + audio + OCR; expect false positives here.",
    "<b>shares as a follower-growth proxy is weak.</b> In the cosplay vertical, much sharing happens via DM, which is not captured. The 0.2 weight on Δshares in reward_signal is a placeholder for follower delta.",
    "<b>adaptation_lag (6/2/4 weeks) is a qualitative estimate, not data-derived.</b> Anchored on creator-archetype intuition. Real lags require longitudinal observation across actual policy events.",
    "<b>Linear response + monotonic adaptation is a strong assumption.</b> Real creators have threshold effects; boundary-probers may respond to penalties by escalating, not retreating. Production needs nonlinear / piecewise models and behavioral-economics priors.",
    "<b>Single-agent simulation — no multi-agent dynamics.</b> When @cosplaybeauty888 wins on a hashtag, @mommygardevoir69 will copy it. Generative-Agents-style memory is referenced; multi-agent contagion is not implemented.",
    "<b>Information asymmetry not modeled.</b> Creators do not see platform weights — they observe outcomes (reach, suppression) and infer. The simulation collapses this inference loop into an instant response after lag.",
    "<b>Most importantly · this is short-video metadata, not LIVE data.</b> The role is LIVE Ecosystem Governance. LIVE-specific signals — gifting flow, PK/co-host behavior, real-time chat density, moderator interventions — require internal data access. This dashboard demonstrates the <i>analytical frame</i>; the real artifact would be built on LIVE event streams.",
]

limit_items_cn = [
    "<b>样本量 · 每个创作者 n ≈ 60，按周聚合后只有 5–10 个数据点。</b>用 4 个特征做 OLS 拟合 ~7 个点，统计上是示意，不是稳健的。R² 仅供透明披露，不作为证据；权重<i>方向</i>是信号，数量级不是。",
    "<b>这里的「IRL」是回归类比，不是真正的 IRL。</b>真正的 IRL（MaxEnt, GAIL）反推出一个让专家轨迹最优的 reward function。本 dashboard 只是把 reward_signal 对行为特征做线性回归——方向上有用，但标签是托词。",
    "<b>engagement_rate = (likes + comments + shares) / plays</b> ——比 likes/plays 更接近 TikTok 真实定义，但播放量仍包含被动滑过的曝光。真实互动需要留存/观看时长，公开 API 拿不到。",
    "<b>content_risk_score 是 hashtag 词典，不是多模态分类器。</b>#hanime、#doujin 等会被打分，但实际视频可能是在讨论同人文化，不是真高风险内容。生产环境需要帧级 + 音频 + OCR；本 demo 会有误报。",
    "<b>用 shares 作为粉丝增长 proxy 很弱。</b>二次元垂类大量分享是私信转发，无法统计。reward_signal 中 Δshares 的 0.2 权重只是粉丝增长的占位。",
    "<b>adaptation_lag（6/2/4 周）是定性估计，不是数据推出来的。</b>基于创作者原型直觉。真实 lag 需要在真实 policy 事件下做纵向观察。",
    "<b>线性响应 + 单调适应是很强的假设。</b>真实创作者有阈值效应；边界党可能对惩罚反向升级而不是退缩。生产环境需要非线性 / 分段模型和行为经济学先验。",
    "<b>单 agent 仿真 — 没有多 agent 动态。</b>当 @cosplaybeauty888 在某个 hashtag 上赢了，@mommygardevoir69 会跟风。引用了 Generative Agents 的记忆概念；多 agent 传染没有实现。",
    "<b>没有建模信息不对称。</b>创作者看不到平台权重，他们观察结果（reach、压制）然后反推。仿真把这个推理回路压缩成 lag 之后的瞬时响应。",
    "<b>最重要的 · 这是短视频 metadata，不是 LIVE 数据。</b>岗位是 LIVE Ecosystem Governance。LIVE 专属信号——礼物流、PK / 连麦、实时弹幕密度、人工干预——需要内部数据。本 dashboard 演示<i>分析框架</i>；真正的产物要建在 LIVE 事件流上。",
]

items_html = "".join(f"<li>{item}</li>" for item in (limit_items_en if LANG == "EN" else limit_items_cn))
st.markdown(f"""
<div class="limit-box">
  <span class="lim-label">{limit_label}</span>
  <ul>{items_html}</ul>
</div>
""", unsafe_allow_html=True)

# ────────────── Bottom credit ──────────────
st.markdown(
    f'<div class="bottom-credit">'
    f'{t("Built by Jayde · with real TikTok public data", "Built by Jayde · 基于真实 TikTok 公开数据")}'
    f'</div>',
    unsafe_allow_html=True,
)
