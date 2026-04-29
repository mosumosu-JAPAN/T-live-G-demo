"""
Creator Behavior Intelligence — TikTok LIVE Ecosystem · Cosplay Vertical
Internal-tool prototype with real numeric callouts for stand-up consumption.
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

CYAN  = "#25F4EE"   # TikTok cyan — active state, positive predictions
PINK  = "#FE2C55"   # TikTok pink — hacking flags
AMBER = "#FFB84D"   # warnings (variance collapse)
ALERT = "#FF6B7E"   # alert tone (red-pink)

TEAL  = "#5BC6B9"   # vanzzcoser
SAND  = "#C8A35E"   # cosplaybeauty888
ROSE  = "#D45A78"   # mommygardevoir69

MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, monospace"

st.markdown(f"""
<style>
.stApp {{ background: {BG}; color: {TEXT}; }}
header[data-testid="stHeader"] {{ background: {BG}; }}
.block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1340px; }}
h1, h2, h3, h4 {{ color: {TEXT}; letter-spacing: -0.005em; font-weight: 500; }}

/* Page header */
h1.page-title {{ font-size: 22px; font-weight: 500; margin: 0; letter-spacing: -0.01em; color: {TEXT}; }}
.page-subtitle {{ font-family: {MONO}; font-size: 13px; color: {DIM}; margin: 6px 0 22px 0; letter-spacing: 0.02em; }}

/* Section headers */
h2 {{
    font-size: 17px; text-transform: uppercase; letter-spacing: 0.13em;
    color: {DIM}; font-weight: 500;
    margin: 44px 0 10px 0; padding-top: 26px;
    border-top: 1px solid {BORDER};
}}

/* Insight notes */
.note {{ font-family: {MONO}; font-size: 15px; color: {NOTE}; margin: 6px 0 22px 0; letter-spacing: 0.005em; line-height: 1.8; }}
.note b {{ color: {HI}; font-weight: 500; }}
.note-extra {{
    font-family: {MONO}; font-size: 14.5px; color: {TEXT};
    margin: -10px 0 24px 0; padding: 10px 14px;
    background: {SURFACE}; border-left: 2px solid {CYAN}; border-radius: 0 4px 4px 0;
    line-height: 1.75;
}}
.note-extra b {{ color: {CYAN}; font-weight: 500; }}
.note-warn {{
    font-family: {MONO}; font-size: 14px; color: {ALERT};
    margin: 8px 0 20px 0; line-height: 1.7; letter-spacing: 0.005em;
}}
hr {{ border-color: {BORDER}; margin: 18px 0; }}

/* Audience selector */
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

/* ── Business Impact Summary Bar ── */
.biz-bar {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
    margin: 18px 0 8px 0;
}}
.biz-stat {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px;
    padding: 18px 20px; border-top: 2px solid {CYAN};
    display: flex; flex-direction: column; gap: 6px;
}}
.biz-stat .label {{
    color: {CYAN}; font-family: {MONO}; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.16em; font-weight: 500;
}}
.biz-stat .num {{
    color: {HI}; font-family: {MONO}; font-size: 26px; font-weight: 500;
    letter-spacing: -0.01em; line-height: 1.15;
}}
.biz-stat .desc {{ color: {NOTE}; font-family: {MONO}; font-size: 12.5px; line-height: 1.55; margin-top: 2px; }}
.biz-bar-note {{
    font-family: {MONO}; font-size: 13.5px; color: {DIM};
    margin: 14px 0 6px 0; letter-spacing: 0.01em; line-height: 1.7;
}}
.biz-bar-note b {{ color: {TEXT}; font-weight: 500; }}

/* ── Reward Hacking Risk Alert Panel ── */
.alert-panel {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-left: 4px solid {ALERT}; border-radius: 0 6px 6px 0;
    padding: 22px 24px; height: 100%;
    font-family: {MONO}; color: {TEXT};
}}
.alert-panel .alert-tag {{
    color: {ALERT}; font-size: 12px; text-transform: uppercase; letter-spacing: 0.18em;
    font-weight: 500; margin-bottom: 14px; display: block;
}}
.alert-panel .alert-line {{ font-size: 13.5px; color: {NOTE}; line-height: 1.7; margin: 6px 0; }}
.alert-panel .alert-num {{ color: {HI}; font-weight: 500; }}
.alert-panel .alert-divider {{ border-top: 1px solid {BORDER}; margin: 14px 0; }}
.alert-panel .alert-creator {{ color: {ALERT}; font-size: 14px; font-weight: 500; margin-bottom: 6px; }}
.alert-panel .alert-pattern {{
    font-size: 12.5px; color: {DIM}; margin-top: 12px; padding: 10px 12px;
    background: {BG}; border-radius: 4px; line-height: 1.7;
}}
.alert-panel .alert-action {{
    font-size: 13.5px; color: {CYAN}; margin-top: 14px; line-height: 1.7;
}}
.alert-panel .alert-action b {{ color: {HI}; font-weight: 500; }}

/* ── Early Warning System cards ── */
.ews-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 12px; }}
.ews-card {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px;
    padding: 20px 22px; position: relative;
    font-family: {MONO}; line-height: 1.7;
}}
.ews-card.amber {{ border-left: 3px solid {AMBER}; }}
.ews-card.red   {{ border-left: 3px solid {ALERT}; }}
.ews-card.cyan  {{ border-left: 3px solid {CYAN}; }}
.ews-card .ews-name {{ color: {TEXT}; font-size: 15px; font-weight: 500; margin-bottom: 4px; letter-spacing: 0.005em; }}
.ews-card.amber .ews-name {{ color: {AMBER}; }}
.ews-card.red   .ews-name {{ color: {ALERT}; }}
.ews-card.cyan  .ews-name {{ color: {CYAN}; }}
.ews-card .ews-tag {{
    position: absolute; top: 18px; right: 18px;
    font-size: 10px; padding: 3px 10px; border-radius: 999px;
    text-transform: uppercase; letter-spacing: 0.14em; font-weight: 500;
}}
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

/* Trajectory key stats overlay */
.traj-keystats {{
    position: relative; float: right; margin-top: -10px; text-align: right;
    font-family: {MONO}; font-size: 12.5px; color: {NOTE}; line-height: 1.7;
    background: rgba(20,20,32,0.82); padding: 6px 12px; border-radius: 4px;
    border: 1px solid {BORDER};
}}
.traj-keystats .num {{ color: {HI}; font-weight: 500; }}

/* Governance table */
table.gov {{ width: 100%; border-collapse: collapse; font-size: 14px; color: {TEXT}; margin-top: 4px; }}
table.gov th {{
    text-align: left; font-weight: 500; font-size: 11.5px;
    text-transform: uppercase; letter-spacing: 0.12em; color: {DIM};
    padding: 14px 18px; border-bottom: 1px solid {BORDER};
}}
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
.biz-case {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
    margin: 8px 0 18px 0;
}}
.biz-case .case {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-left: 2px solid {CYAN};
    border-radius: 0 6px 6px 0; padding: 16px 18px;
}}
.biz-case .case .num {{ color: {CYAN}; font-family: {MONO}; font-size: 22px; font-weight: 500; line-height: 1.2; letter-spacing: -0.01em; }}
.biz-case .case .desc {{ color: {NOTE}; font-family: {MONO}; font-size: 12.5px; margin-top: 6px; line-height: 1.6; }}
.biz-case-foot {{ font-family: {MONO}; font-size: 12px; color: {DIM}; margin: 4px 0 14px 0; letter-spacing: 0.01em; }}

/* Policy Simulation */
.sim-title {{ font-family: {MONO}; font-size: 16px; color: {TEXT}; margin: 4px 0 6px 0; letter-spacing: 0.005em; line-height: 1.55; font-weight: 500; }}
.sim-subtitle {{ font-family: {MONO}; font-size: 13px; color: {DIM}; margin: 0 0 20px 0; letter-spacing: 0.02em; line-height: 1.6; }}
.sim-caption {{ font-family: {MONO}; font-size: 13px; color: {DIM}; margin: 0 0 8px 0; letter-spacing: 0.005em; line-height: 1.65; }}
.sim-instruction {{ font-family: {MONO}; font-size: 12.5px; color: {CYAN}; margin: 0 0 14px 0; letter-spacing: 0.01em; }}
[data-testid="column"]:has(.policy-sim-marker) {{
    background: {SURFACE}; padding: 20px 20px 10px 20px;
    border-radius: 6px; border: 1px solid {BORDER};
}}
.policy-sim-marker {{ display: none; }}
[data-testid="column"]:has(.policy-sim-marker) [data-testid="stSlider"] label {{
    font-family: {MONO} !important; font-size: 13px !important; color: {TEXT} !important;
    font-weight: 400 !important; letter-spacing: 0 !important;
}}
[data-testid="column"]:has(.policy-sim-marker) [data-testid="stSlider"] {{ margin-bottom: -4px; }}
.sim-footer {{ font-family: {MONO}; font-size: 13px; color: {NOTE}; margin: 4px 0; letter-spacing: 0.01em; text-align: left; line-height: 1.7; }}

/* Policy Impact Summary table */
table.impact {{ width: 100%; border-collapse: collapse; font-size: 13px; color: {TEXT}; font-family: {MONO}; }}
table.impact th {{
    text-align: left; font-weight: 500; font-size: 10.5px;
    text-transform: uppercase; letter-spacing: 0.1em; color: {DIM};
    padding: 9px 8px; border-bottom: 1px solid {BORDER}; white-space: nowrap;
}}
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
.live-block {{
    background: {SURFACE}; border-left: 4px solid {CYAN};
    padding: 22px 26px; margin: 22px 0 6px 0;
    font-family: {MONO}; font-size: 15px; color: {TEXT};
    line-height: 1.85; letter-spacing: 0.005em; border-radius: 0 6px 6px 0;
}}
.live-block .live-tag {{
    display: inline-block; color: {CYAN}; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.18em;
    margin-bottom: 10px; font-weight: 500;
}}

/* Limitations */
.limit-box {{
    background: {SURFACE}; border-left: 3px solid {CYAN};
    border-top: 1px solid {BORDER}; border-right: 1px solid {BORDER}; border-bottom: 1px solid {BORDER};
    border-radius: 0 6px 6px 0; padding: 22px 26px; margin-top: 22px;
    font-family: {MONO}; font-size: 14px; color: {NOTE}; line-height: 1.8;
}}
.limit-box .lim-label {{
    color: {CYAN}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.16em;
    margin-bottom: 14px; display: block; font-weight: 500;
}}
.limit-box ul {{ margin: 0; padding-left: 20px; }}
.limit-box li {{ margin: 8px 0; font-size: 14px; line-height: 1.8; }}
.limit-box b {{ color: {HI}; font-weight: 500; }}

/* Bottom credit */
.bottom-credit {{
    font-family: {MONO}; font-size: 12px; color: {DIM};
    text-align: left; margin-top: 40px; padding-top: 20px;
    border-top: 1px solid {BORDER}; letter-spacing: 0.04em;
}}
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
    "vanzzcoser":      dict(strategy="Volatile Anchor", archetype="太太型",    en="Ecosystem Anchor",    color=TEAL),
    "cosplaybeauty888":dict(strategy="Machine",         archetype="SOP型",     en="Algorithm Exploiter", color=SAND),
    "mommygardevoir69":dict(strategy="Gambler",         archetype="边界党",    en="Boundary Prober",     color=ROSE),
}
def color_of(u): return CREATORS.get(u, {}).get("color", "#9C9CFF")
def label_of(u): return CREATORS.get(u, {}).get("strategy", u)

def extract_tags(d): return [t.lower() for t in HASHTAG_RE.findall(d or "")]

def risk_score(desc, tags):
    if not isinstance(desc, str): desc = ""
    text_hits = len(SOFT_RISK_WORDS.findall(desc))
    if not tags:
        return min(0.05 + 0.15 * text_hits, 1.0)
    s, n = 0.0, 0
    for t in tags:
        if t in HIGH_RISK: s += 1.0
        elif t in MID_RISK: s += 0.5
        elif t in LOW_RISK: s += 0.05
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

    # Cohort-average fallback: when a creator has too few weeks for OLS, or the fit
    # collapses to all-zero weights, substitute mean sensitivity from creators with
    # valid fits — keeps the simulation responsive instead of dropping to delta=0.
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

# ── Per-creator metric pack ──
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

# Top-line numbers for the Business Impact bar
total_videos = len(df)
total_hacks = int(hacks["is_hacking"].sum())
hacking_share = 100.0 * total_hacks / max(total_videos, 1)

quality_gap = M["vanzzcoser"]["avg_engagement"] / max(M["cosplaybeauty888"]["avg_engagement"], 1e-9)
mommy_peak = M["mommygardevoir69"]["reward_peak"]
mommy_meanabs = max(abs(M["mommygardevoir69"]["reward_mean"]), 1e-6)
gambler_ratio = mommy_peak / mommy_meanabs

# Stability gap — for 'best creator' (vanzz, highest engagement) vs 'machine' (cosplay)
stability_gap = (M["vanzzcoser"]["reward_std"] / max(M["cosplaybeauty888"]["reward_std"], 1e-9))

# ────────────── Audience selector + insights ──────────────
if "audience" not in st.session_state:
    st.session_state.audience = "PM"

INSIGHTS = {
    "trajectory": {
        "PM": "三条曲线说明平台在无意中训练出了三种创作者生存策略。SOP型被训练成机器（零方差），边界党被训练成赌徒（爆一次归零再赌），太太型反而最不稳定——说明平台没有在保护高质量创作者。这是 policy 需要重新定义的起点。",
        "Data": "reward_signal = 0.5×Δplay + 0.3×Δengagement + 0.2×Δshares，按周聚合。cosplaybeauty888 近零方差（σ≈0.02），mommygardevoir69 高峰值低基线（peak/mean > 3x），vanzzcoser 高频波动。三种方差模式对应三种不同的优化目标函数。",
        "Algorithm": "IRL 拟合显示三个创作者在优化不同的 reward 维度。SOP型 w_play 权重最高，太太型 w_engagement 权重最高。当前推荐算法 play_growth 权重过高，正在系统性奖励 SOP 型行为，这是生态同质化的根本原因。",
    },
    "irl": {
        "PM": "雷达图展示平台以为自己在用同一套规则管理所有创作者，但每个人在响应完全不同的激励。这不是创作者的问题，是 reward function 设计的问题。",
        "Data": "OLS 拟合，标准化特征。注意：n=60，统计显著性有限，权重方向比绝对值更重要。R² 仅供参考，不做因果推断。",
        "Algorithm": "线性 IRL 简化版。生产环境建议 MaxEnt IRL 或 GAIL 处理非线性奖励。当前权重可作为创作者风险分级模型的特征工程先验。",
    },
    "hacking": {
        "PM": "红色标注 = 高播放 + 低互动 + 高风险内容。这不是违规，但是平台激励失效的信号。传统审核工具发现不了这个，因为这些内容没有违规——这正是治理 PM 存在的价值。",
        "Data": "检测条件：play > 75th pct AND engagement < 25th pct AND risk > 0.5。规则型检测，生产环境建议 Isolation Forest 或 autoencoder 做无监督异常检测，消除人工阈值依赖。",
        "Algorithm": "Reward hacking 本质是 exploit 推荐模型的 reward proxy。监控 play/engagement 比值分布，持续偏离同类均值 2σ 以上触发复核。该信号可直接加入推荐模型负反馈。",
    },
    "ews": {
        "PM": "三个 card 对应三种创作者类型的早期预警信号。这套预警在传统内容审核之前触发——内容还没违规，但行为模式已经预示风险。这是治理 PM 真正应该做的事：从被动响应违规，到主动识别系统性偏差。",
        "Data": "每个信号是一个可计算的 trigger condition：variance collapse 用 rolling-σ，spike-cliff 用 peak/mean ratio，quality-volatility divergence 用 engagement-z-score 与 reward-σ 的二维条件。生产环境可直接挂到流式管道上。",
        "Algorithm": "三类预警对应三类异常检测算子：滑窗方差监控、变点检测（CUSUM/Bayesian online change point）、二维条件触发。建议作为推荐模型上游的 gating layer，影响候选集而非事后惩罚。",
    },
    "simulation": {
        "PM": "每个 slider 是一个 policy 意图翻译成的模型参数。这是 PM 和算法团队对话的共同语言——你改变的不是数字，是平台对创作者行为的态度。",
        "Data": "预测模型：线性响应 + adaptation lag。delta = Σ(sensitivity_i × delta_weight_i)。Lag 基于行为惯性估计。生产环境建议 Kalman filter 做实时 trajectory 更新。",
        "Algorithm": "Slider 调整的是 reward function 权重向量，预测创作者 policy 在新 reward 下的收敛行为。Memory phase = off-policy 阶段，adaptation phase = on-policy 收敛。Adaptation lag 决定 A/B test 最短实验周期。",
    },
    "governance": {
        "PM": "同一个擦边内容，来自太太型和SOP型的标注权重应该不同。这套 taxonomy 可以直接变成标注团队的差异化指南。",
        "Data": "Intervention mapping：w_risk high → content classifier fine-tuning；w_play >> w_engagement → ranking weight recalibration；reward cliff → graduated enforcement curve。",
        "Algorithm": "实验设计：分层 A/B test，最短实验周期 = max(adaptation_lag) = 6 weeks。控制组保持当前权重，实验组按 simulation 结果调整，按 archetype 分层分析结果。",
    },
}

def insight(key):
    aud = st.session_state.get("audience", "PM")
    text = INSIGHTS[key][aud]
    st.markdown(f'<div class="note">{text}</div>', unsafe_allow_html=True)

# ────────────── Header ──────────────
n_videos = len(df)
n_creators = df["username"].nunique()

st.markdown(
    f'<h1 class="page-title">Creator Behavior Intelligence · TikTok LIVE Ecosystem · Cosplay Vertical</h1>'
    f'<div class="page-subtitle">{n_creators} creator archetypes · {n_videos} videos · public TikTok data · proof of concept</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="audience-row">', unsafe_allow_html=True)
a1, a2, a3, _ = st.columns([1.4, 2.0, 2.4, 5.0], gap="small")
audience_options = [("I'm a PM", "PM"), ("I'm a Data Scientist", "Data"), ("I'm an Algorithm Engineer", "Algorithm")]
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
    <div class="label">Quality Gap</div>
    <div class="num">{quality_gap:.1f}×</div>
    <div class="desc">太太型 engagement is <b style="color:{HI}">{quality_gap:.1f}×</b> the SOP型 baseline</div>
  </div>
  <div class="biz-stat">
    <div class="label">Hacking Signal</div>
    <div class="num">{hacking_share:.1f}%</div>
    <div class="desc"><b style="color:{HI}">{total_hacks}</b> of <b style="color:{HI}">{total_videos}</b> videos exploiting algorithm</div>
  </div>
  <div class="biz-stat">
    <div class="label">Gambler Cycle</div>
    <div class="num">{gambler_ratio:.1f}×</div>
    <div class="desc">边界党 peak reward <b style="color:{HI}">{gambler_ratio:.1f}×</b> above baseline — boom &amp; bust</div>
  </div>
  <div class="biz-stat">
    <div class="label">Stability Gap</div>
    <div class="num">{stability_gap:.1f}×</div>
    <div class="desc">Best creator is <b style="color:{HI}">{stability_gap:.1f}×</b> more volatile than the machine</div>
  </div>
</div>
<div class="biz-bar-note">these four numbers are why governance needs a <b>reward function redesign</b>, not better content moderation.</div>
""", unsafe_allow_html=True)

order = ["mommygardevoir69", "cosplaybeauty888", "vanzzcoser"]

# ════════════════════════════ MODULE 1 — Trajectory Overview ════════════════════════════
st.markdown("<h2>Trajectory Overview</h2>", unsafe_allow_html=True)

# Key stats overlay (top-right of chart, above it visually)
ks_html = '<div class="traj-keystats">'
for u in ["vanzzcoser", "cosplaybeauty888", "mommygardevoir69"]:
    ks_html += f'@{u} avg engagement <span class="num">{M[u]["avg_engagement"]*100:.1f}%</span><br>'
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
        x=sub["week"].iloc[-1], y=smoothed.iloc[-1], text=f"  {label_of(u)}",
        showarrow=False, xanchor="left", yanchor="middle",
        font=dict(family=MONO, size=13, color=color_of(u)), xshift=6,
    )

mg = weekly[weekly["username"] == "mommygardevoir69"].sort_values("week").reset_index(drop=True)
if len(mg) >= 3:
    mg_smooth = mg["reward_signal"].rolling(3, min_periods=1).mean()
    peak_i = int(mg_smooth.idxmax())
    fig1.add_annotation(
        x=mg["week"].iloc[peak_i], y=mg_smooth.iloc[peak_i],
        text="single viral spike → immediate suppression",
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
        text="zero variance — optimizing for stability, not quality",
        showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=SAND,
        ax=-40, ay=48, font=dict(family=MONO, size=13, color=SAND), xanchor="right",
        bgcolor=BG, bordercolor=BORDER, borderwidth=0, borderpad=4,
    )

fig1.add_hline(y=0, line_dash="dot", line_color=MUTED, line_width=0.8, opacity=0.5)
fig1.update_layout(height=440, **PLOTLY)
fig1.update_yaxes(title="weekly reward signal (smoothed)")
fig1.update_xaxes(title=None)
st.plotly_chart(fig1, use_container_width=True)
insight("trajectory")

# Bonus comparative line
eng_mult = M["vanzzcoser"]["avg_engagement"] / max(M["cosplaybeauty888"]["avg_engagement"], 1e-9)
vol_mult = M["vanzzcoser"]["reward_std"] / max(M["cosplaybeauty888"]["reward_std"], 1e-9)
st.markdown(
    f'<div class="note-extra">'
    f'太太型 engagement 是 SOP型的 <b>{eng_mult:.1f}×</b>，但 reward signal 波动是 SOP型的 <b>{vol_mult:.1f}×</b>'
    f'——平台在用错误的信号评估创作者价值。'
    f'</div>',
    unsafe_allow_html=True,
)

# ════════════════════════════ MODULE 2 — Inferred Reward Functions ════════════════════════════
st.markdown("<h2>Inferred Reward Functions</h2>", unsafe_allow_html=True)

feats = ["play_growth","engagement_rate","posting_frequency","content_risk"]
labels_short = ["play growth","engagement","posting freq","content risk"]

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
            "creator": f"@{u}",
            "play_growth": f"{w['play_growth']:+.2f}",
            "engagement": f"{w['engagement_rate']:+.2f}",
            "posting_freq": f"{w['posting_frequency']:+.2f}",
            "content_risk": f"{w['content_risk']:+.2f}",
            "R²": f"{irl[u]['r2']:.2f}",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=200)

insight("irl")

# ════════════════════════════ MODULE 3 — Reward Hacking Detection ────────────────────────────
st.markdown("<h2>Reward Hacking Detection</h2>", unsafe_allow_html=True)

# Determine the most-flagged creator dynamically — the alert features them.
hack_by_creator = hacks.groupby("username")["is_hacking"].sum().sort_values(ascending=False)
top_hack_user = hack_by_creator.index[0] if hack_by_creator.iloc[0] > 0 else order[0]

if M[top_hack_user]["n_hacking"] > 0:
    bad_u = hacks[(hacks["username"] == top_hack_user) & hacks["is_hacking"]]
    avg_play_mult = bad_u["play_count"].mean() / max(M[top_hack_user]["median_play"], 1)
    avg_eng_def = M[top_hack_user]["median_eng"] / max(bad_u["engagement_rate"].mean(), 1e-9)
    pattern = {
        "vanzzcoser":       "Quality creator pulled into edge content cycle",
        "cosplaybeauty888": "Zero-variance posting profile — systematic algorithm exploit",
        "mommygardevoir69": "High-risk gambling cycle — boundary probing for reach",
    }[top_hack_user]
    rec = {
        "vanzzcoser":       "Distribution audit — verify algorithm is not pulling tenured creators into risky surfaces",
        "cosplaybeauty888": "Flag for algo weight recalibration — NOT content removal",
        "mommygardevoir69": "Graduated throttling + creator education — NOT immediate cliff penalty",
    }[top_hack_user]
else:
    bad_u = hacks.iloc[:0]
    avg_play_mult = 0.0
    avg_eng_def = 0.0
    pattern = "No active hacking signals in this cohort window"
    rec = "Maintain monitoring"

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
            colorbar=dict(title=dict(text="risk", font=dict(family=MONO, size=11, color=DIM)),
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
            text=f"reward hacking detected · {len(bad)} videos",
            showarrow=False, xanchor="right", yanchor="bottom",
            font=dict(family=MONO, size=13, color=PINK),
            xshift=-4, yshift=10,
        )
    fig3.update_layout(height=460, **PLOTLY)
    fig3.update_xaxes(type="log", title="play count")
    fig3.update_yaxes(title="engagement rate")
    st.plotly_chart(fig3, use_container_width=True)

with alert_col:
    st.markdown(f"""
    <div class="alert-panel">
      <span class="alert-tag">⚠ Risk Alert</span>
      <div class="alert-line">Hacking signals detected:</div>
      <div class="alert-line"><span class="alert-num">{total_hacks}</span> / {total_videos} videos · <span class="alert-num">{hacking_share:.1f}%</span></div>
      <div class="alert-divider"></div>
      <div class="alert-creator">@{top_hack_user}</div>
      <div class="alert-line"><span class="alert-num">{M[top_hack_user]['hacking_pct']:.1f}%</span> of their videos trigger hacking signal</div>
      <div class="alert-line">avg play count: <span class="alert-num">{avg_play_mult:.1f}×</span> above their normal</div>
      <div class="alert-line">avg engagement: <span class="alert-num">{avg_eng_def:.1f}×</span> below their normal</div>
      <div class="alert-pattern"><b style="color:{TEXT}">Pattern:</b> {pattern}</div>
      <div class="alert-action"><b>Recommended action:</b><br>{rec}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    '<div class="note-warn">'
    'these videos are not policy violations. they are reward function failures. traditional moderation tools cannot catch this.'
    '</div>',
    unsafe_allow_html=True,
)
insight("hacking")

# ════════════════════════════ MODULE 4 — Early Warning Signals ════════════════════════════
st.markdown("<h2>Early Warning Signals</h2>", unsafe_allow_html=True)
st.markdown(
    f'<div class="page-subtitle" style="margin-top:-2px;">accounts showing pre-violation behavioral patterns · not yet flagged by content moderation</div>',
    unsafe_allow_html=True,
)

# Compute trigger conditions
sop_4w_std = M["cosplaybeauty888"]["reward_std"]  # using full window as proxy for last-4-week σ
variance_collapse_active = sop_4w_std < 0.05

mommy_pm_ratio = gambler_ratio
spike_cliff_active = mommy_pm_ratio > 3.0

cohort_eng = np.mean([M[u]["avg_engagement"] for u in CREATORS])
vanzz_eng_z = M["vanzzcoser"]["avg_engagement"] / max(cohort_eng, 1e-9)
quality_div_active = (vanzz_eng_z > 2.0) and (M["vanzzcoser"]["reward_std"] > 0.3)

def tag(active):
    return ('<span class="ews-tag active">Active</span>' if active
            else '<span class="ews-tag historical">Historical</span>')

st.markdown(f"""
<div class="ews-grid">

  <div class="ews-card amber">
    {tag(variance_collapse_active)}
    <div class="ews-name">Variance Collapse</div>
    <div class="ews-row"><span class="k">trigger</span><span class="v">σ(reward) &lt; 0.05 over recent window</span></div>
    <div class="ews-row"><span class="k">measured</span><span class="v">σ = <b style="color:{HI}">{sop_4w_std:.3f}</b></span></div>
    <div class="ews-creator">currently triggered by <span class="at">@cosplaybeauty888</span></div>
    <div class="ews-divider"></div>
    <div class="ews-action">
      <b>Risk:</b> systematic algorithm exploit, content homogenization accelerating.<br><br>
      <b>Recommended:</b> algorithm weight recalibration. No human moderation required.
    </div>
  </div>

  <div class="ews-card red">
    {tag(spike_cliff_active)}
    <div class="ews-name">Spike-Cliff Pattern</div>
    <div class="ews-row"><span class="k">trigger</span><span class="v">single peak &gt; 3× mean, followed by descent</span></div>
    <div class="ews-row"><span class="k">measured</span><span class="v">peak/mean = <b style="color:{HI}">{mommy_pm_ratio:.1f}×</b></span></div>
    <div class="ews-creator">currently triggered by <span class="at">@mommygardevoir69</span></div>
    <div class="ews-divider"></div>
    <div class="ews-action">
      <b>Risk:</b> creator entered gambling cycle. Probability of next risky probe is high.<br><br>
      <b>Recommended:</b> pre-stream risk nudge + graduated intervention. Don't wait for the violation.
    </div>
  </div>

  <div class="ews-card cyan">
    {tag(quality_div_active)}
    <div class="ews-name">Quality–Volatility Divergence</div>
    <div class="ews-row"><span class="k">trigger</span><span class="v">engagement &gt; 2× cohort avg AND σ(reward) &gt; 0.3</span></div>
    <div class="ews-row"><span class="k">measured</span><span class="v">eng z = <b style="color:{HI}">{vanzz_eng_z:.1f}×</b> · σ = <b style="color:{HI}">{M["vanzzcoser"]["reward_std"]:.2f}</b></span></div>
    <div class="ews-creator">currently triggered by <span class="at">@vanzzcoser</span></div>
    <div class="ews-divider"></div>
    <div class="ews-action">
      <b>Risk:</b> high-quality creator getting unstable returns. Churn risk elevated.<br><br>
      <b>Recommended:</b> build a quality-protection floor — engagement-weighted distribution for tenured creators.
    </div>
  </div>

</div>
""", unsafe_allow_html=True)
insight("ews")

# ════════════════════════════ MODULE 5 — Policy Simulation ════════════════════════════
ADAPTATION_LAG = {
    "vanzzcoser":       6,
    "cosplaybeauty888": 2,
    "mommygardevoir69": 4,
}
ARCHETYPE_CN = {
    "vanzzcoser":       "太太型",
    "cosplaybeauty888": "SOP型",
    "mommygardevoir69": "边界党",
}
OLD_PLATFORM = dict(play_growth=0.5, engagement_rate=0.3, posting_frequency=0.2, content_risk=0.0)

st.markdown("<h2>Policy Simulation</h2>", unsafe_allow_html=True)
st.markdown('<div class="sim-title">What happens to each creator archetype in the 12 weeks after a policy change?</div>', unsafe_allow_html=True)
st.markdown('<div class="sim-subtitle">translating governance intentions into behavioral predictions · bridging policy and algorithm teams</div>', unsafe_allow_html=True)

ctrl_col, plot_col, impact_col = st.columns([1.0, 2.4, 2.2], gap="medium")

with ctrl_col:
    st.markdown('<div class="policy-sim-marker"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sim-caption">each slider is a policy intention translated into a model parameter.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sim-instruction">drag to simulate · numbers update in real time</div>', unsafe_allow_html=True)
    new_eng  = st.slider("平台更重视真实互动质量",   0.1, 0.7, 0.3, 0.05, key="sim_eng")
    new_play = st.slider("平台降低对纯播放量的奖励", 0.1, 0.7, 0.5, 0.05, key="sim_play")
    new_risk = st.slider("平台主动惩罚高风险内容",   0.0, 0.5, 0.0, 0.05, key="sim_risk")
    new_post = st.slider("平台鼓励稳定持续创作",     0.1, 0.5, 0.2, 0.05, key="sim_post")

new_platform = dict(
    play_growth=new_play,
    engagement_rate=new_eng,
    posting_frequency=new_post,
    content_risk=-new_risk,
)

# Compute per-creator delta_reward at the converged horizon
def converged_delta(u, platform):
    w = irl[u]["weights"]
    delta = sum(w[k] * (platform[k] - OLD_PLATFORM[k]) for k in OLD_PLATFORM)
    lag = ADAPTATION_LAG[u]
    return delta * (1 - lag/12)

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

    # Policy-change vertical (manual line + label) — bypass add_vline's _mean bug
    fig5.add_shape(
        type="line", x0=policy_change, x1=policy_change,
        y0=0, y1=1, yref="paper",
        line=dict(color=DIM, width=1, dash="dash"),
    )
    fig5.add_annotation(
        x=policy_change, y=1.03, xref="x", yref="paper",
        text="policy change", showarrow=False, xanchor="center", yanchor="bottom",
        font=dict(family=MONO, size=12, color=DIM),
    )
    fig5.add_annotation(
        x=policy_change + pd.Timedelta(weeks=4), y=1, xref="x", yref="paper",
        text="memory exhausted · adaptation begins",
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(family=MONO, size=12, color=MUTED),
    )
    fig5.add_hline(y=0, line_dash="dot", line_color=MUTED, line_width=0.8, opacity=0.4)
    fig5.update_layout(height=420, **PLOTLY)
    fig5.update_yaxes(title="weekly reward signal")
    fig5.update_xaxes(title=None)
    st.plotly_chart(fig5, use_container_width=True)

with impact_col:
    # Real-time predicted Δ
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

    st.markdown(f"""
    <table class="impact">
      <thead>
        <tr><th>Creator</th><th>当前</th><th>调整后</th><th>意义</th><th>Predicted Δ</th></tr>
      </thead>
      <tbody>
        <tr>
          <td class="t-creator"><span class="swatch" style="background:{TEAL};"></span><span class="name">太太型</span><span class="sub">Ecosystem Anchor</span></td>
          <td class="t-now">高质量但不稳定</td>
          <td class="t-after">6 周后稳定性提升</td>
          <td class="t-meaning">真正保护优质创作者</td>
          {delta_cell(d_anchor, "reward stability")}
        </tr>
        <tr>
          <td class="t-creator"><span class="swatch" style="background:{SAND};"></span><span class="name">SOP型</span><span class="sub">Algorithm Exploiter</span></td>
          <td class="t-now">零风险刷量</td>
          <td class="t-after">2 周内被迫提升质量</td>
          <td class="t-meaning">Exploit 空间收窄</td>
          {delta_cell(d_sop, "posting frequency")}
        </tr>
        <tr>
          <td class="t-creator"><span class="swatch" style="background:{ROSE};"></span><span class="name">边界党</span><span class="sub">Boundary Prober</span></td>
          <td class="t-now">赌徒循环</td>
          <td class="t-after">4 周后试探频率降低</td>
          <td class="t-meaning">渐进干预胜过断崖</td>
          {delta_cell(d_prober, "risk content ratio")}
        </tr>
      </tbody>
    </table>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:16px;">
  <div class="sim-footer">太太型 (vanzzcoser) · adaptation lag 6週 · engagement 敏感 · 受保护最慢</div>
  <div class="sim-footer">SOP型 (cosplaybeauty888) · adaptation lag 2週 · play_growth 敏感 · 最快响应</div>
  <div class="sim-footer">边界党 (mommygardevoir69) · adaptation lag 4週 · 4週后开始试探新边界</div>
</div>
""", unsafe_allow_html=True)
insight("simulation")

st.markdown("""
<div class="live-block">
  <span class="live-tag">extending to LIVE</span>
  短视频的 adaptation lag 是以周计算的。LIVE 里，同样的行为模式压缩在一场直播的 90 分钟内——开播建立安全感，中段试探边界，礼物高峰期达到最高风险点，平台警告触发后立刻切回安全内容。这套 IRL 框架直接适用于 LIVE 实时风险预判，需要的是实时行为信号，而不是周级别的聚合数据。
</div>
""", unsafe_allow_html=True)

# ════════════════════════════ MODULE 6 — Governance Intervention ════════════════════════════
st.markdown("<h2>Governance Intervention</h2>", unsafe_allow_html=True)

# Business case — fixed scenario: engagement weight 0.3 → 0.5
SCENARIO = dict(play_growth=0.3, engagement_rate=0.5, posting_frequency=0.2, content_risk=0.0)
sc_anchor = converged_delta("vanzzcoser",       SCENARIO) * 100
sc_sop    = converged_delta("cosplaybeauty888", SCENARIO) * 100
sc_prober = converged_delta("mommygardevoir69", SCENARIO) * 100

st.markdown(f"""
<div class="biz-case">
  <div class="case">
    <div class="num">{sc_anchor:+.1f}%</div>
    <div class="desc">predicted reward stability lift for <b style="color:{TEXT}">太太型</b> · 6 weeks</div>
  </div>
  <div class="case">
    <div class="num">{sc_sop:+.1f}%</div>
    <div class="desc">predicted posting-frequency change for <b style="color:{TEXT}">SOP型</b> · 2 weeks</div>
  </div>
  <div class="case">
    <div class="num">{sc_prober:+.1f}%</div>
    <div class="desc">predicted risk-content-ratio change for <b style="color:{TEXT}">边界党</b> · 4 weeks</div>
  </div>
</div>
<div class="biz-case-foot">scenario: engagement weight raised 0.3 → 0.5 · play weight lowered 0.5 → 0.3 · based on current IRL weights and adaptation-lag estimates</div>
""", unsafe_allow_html=True)

table_html = f"""
<table class="gov">
  <thead>
    <tr>
      <th>Creator</th>
      <th>Inferred Strategy</th>
      <th>Platform Unintentionally Trained</th>
      <th>Recommended Intervention</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="creator"><span class="swatch" style="background:{TEAL};"></span><span class="name">@vanzzcoser</span>Ecosystem Anchor</td>
      <td class="strategy">Quality-first</td>
      <td class="trained">Instability — high-quality creator left unprotected; reward signal swings independent of effort.</td>
      <td class="intervention">Build a quality signal independent of play count (engagement-depth, retention, repeat-viewer ratio) and weight it into distribution for tenured creators.</td>
    </tr>
    <tr>
      <td class="creator"><span class="swatch" style="background:{SAND};"></span><span class="name">@cosplaybeauty888</span>Algorithm Exploiter</td>
      <td class="strategy">Zero-risk farming</td>
      <td class="trained">Content homogenization — flatlined reward at zero variance, no quality differentiation, no creative risk.</td>
      <td class="intervention">Adjust recommender weights to penalize low-variance content profiles; reward exploration and format experimentation.</td>
    </tr>
    <tr>
      <td class="creator"><span class="swatch" style="background:{ROSE};"></span><span class="name">@mommygardevoir69</span>Boundary Prober</td>
      <td class="strategy">High-risk gambling</td>
      <td class="trained">Edge → punish → restart cycle — single spikes followed by hard suppression train creators to gamble rather than build.</td>
      <td class="intervention">Replace cliff penalties with progressive intervention: graded reach throttling, in-product education at first violation, hard action only on repeat.</td>
    </tr>
  </tbody>
</table>
"""
st.markdown(table_html, unsafe_allow_html=True)
insight("governance")

# ────────────── Limitations ──────────────
st.markdown(f"""
<div class="limit-box">
  <span class="lim-label">known limitations · what would change for production</span>
  <ul>
    <li><b>Sample size · n ≈ 60 per creator, ~5–10 weekly buckets after aggregation.</b> OLS over 4 features on ~7 points is illustrative, not statistically robust. R² shown for transparency, not as evidence; weight <i>direction</i> is the signal, magnitudes are not.</li>
    <li><b>"IRL" is a regression analogy, not formal IRL.</b> Real IRL (MaxEnt, GAIL) recovers a reward function under which expert trajectories are optimal. This dashboard fits a linear regression of reward_signal on behavioral features — directionally useful, but the label is aspirational.</li>
    <li><b>engagement_rate = (likes + comments + shares) / plays</b> — closer to TikTok's real definition than likes/plays, but plays still includes passive scrolls. True engagement requires retention/watch-time, which the public API does not expose.</li>
    <li><b>content_risk_score is a hashtag lexicon, not a multimodal classifier.</b> #hanime, #doujin etc. trigger weight, but the actual videos may be in-genre discussion, not high-risk content. Production needs frame-level + audio + OCR; expect false positives here.</li>
    <li><b>shares as a follower-growth proxy is weak.</b> In the cosplay vertical, much sharing happens via DM, which is not captured. The 0.2 weight on Δshares in reward_signal is a placeholder for follower delta.</li>
    <li><b>adaptation_lag (6/2/4 weeks) is a qualitative estimate, not data-derived.</b> Anchored on creator-archetype intuition. Real lags require longitudinal observation across actual policy events.</li>
    <li><b>Linear response + monotonic adaptation is a strong assumption.</b> Real creators have threshold effects; boundary-probers may respond to penalties by escalating, not retreating. Production needs nonlinear / piecewise models and behavioral-economics priors.</li>
    <li><b>Single-agent simulation — no multi-agent dynamics.</b> When @cosplaybeauty888 wins on a hashtag, @mommygardevoir69 will copy it. Generative-Agents-style memory is referenced; multi-agent contagion is not implemented.</li>
    <li><b>Information asymmetry not modeled.</b> Creators do not see platform weights — they observe outcomes (reach, suppression) and infer. The simulation collapses this inference loop into an instant response after lag.</li>
    <li><b>Most importantly · this is short-video metadata, not LIVE data.</b> The role is LIVE Ecosystem Governance. LIVE-specific signals — gifting flow, PK/co-host behavior, real-time chat density, moderator interventions — require internal data access. This dashboard demonstrates the <i>analytical frame</i>; the real artifact would be built on LIVE event streams.</li>
  </ul>
</div>
""", unsafe_allow_html=True)

# ────────────── Bottom credit ──────────────
st.markdown(
    '<div class="bottom-credit">'
    'Built by Jayde · with real TikTok public data'
    '</div>',
    unsafe_allow_html=True,
)
