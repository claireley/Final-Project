"""
app.py  —  Is the Behavioural Score Dead?
Three-page Streamlit dashboard.
Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from backend import (
    CLUSTER_COLORS, CLUSTER_LABELS, CLUSTER_PERSONAS,
    BG, CARD, BORDER, TEXT, MUTED,
    MODEL_RESULTS, MODEL_COLORS,
    ABLATION, ABLATION_COLORS,
    FEATURE_IMPORTANCES,
    load_real_data, compute_roi,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sci-Kitchen Luxury Foods",
    page_icon="sk_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] {{ font-family:'Inter',sans-serif; background:{BG}; color:{TEXT}; }}
.stApp {{ background:{BG}; }}
section[data-testid="stSidebar"] {{ background:{CARD}; border-right:1px solid {BORDER}; }}
h1,h2,h3 {{ color:{TEXT} !important; }}
.stSelectbox label,.stSlider label,.stRadio label {{ color:{TEXT} !important; font-size:0.8rem !important; }}

.metric-card {{
  background:{MUTED}; border:1px solid {BORDER}; border-radius:10px;
  padding:1.2rem 1.4rem; margin-bottom:0.75rem;
}}
.metric-label {{
  font-size:0.72rem; font-weight:600; letter-spacing:0.08em;
  text-transform:uppercase; color:{CARD}; margin-bottom:0.3rem;
}}
.metric-value {{
  font-family:'JetBrains Mono',monospace; font-size:1.6rem;
  font-weight:500; color:{TEXT}; line-height:1;
}}
.metric-sub {{ font-size:0.75rem; color:{CARD}; margin-top:0.25rem; }}

.cluster-badge {{
  display:inline-block; padding:0.2rem 0.65rem; border-radius:20px;
  font-size:0.7rem; font-weight:600; letter-spacing:0.05em; margin-bottom:0.5rem;
}}
.section-header {{
  font-size:0.7rem; font-weight:700; letter-spacing:0.12em;
  text-transform:uppercase; color:{CARD};
  border-bottom:1px solid {BORDER}; padding-bottom:0.5rem; margin:1.5rem 0 1rem 0;
}}
.insight-box {{
  background:{MUTED}; border-left:3px solid #3B82F6;
  border-radius:0 8px 8px 0; padding:0.9rem 1.1rem; margin:0.75rem 0;
  font-size:0.88rem; line-height:1.6; color:{TEXT};
}}
</style>
""", unsafe_allow_html=True)

# ── Data & sidebar ─────────────────────────────────────────────────────────────
@st.cache_data
def load_real_data() -> pd.DataFrame:
    return pd.read_csv("../data/clean/data_w_cluster.csv", sep=";")


df = load_real_data()
df['Cluster_Label']= df.Cluster+1

with st.sidebar:
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.image("sk_logo.png", width=120)
    st.sidebar.markdown(
    f"""
    <div style="
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-align: center;
        color: {MUTED};
        margin-top: 0.5rem;
        line-height: 1.2;
    ">
        Sci-Kitchen<br><em>Luxury Foods</em>
    </div>
    """,
    unsafe_allow_html=True
)
    st.sidebar.markdown("---")
    st.markdown(f"<div style='font-size:0.65rem;letter-spacing:0.12em;text-transform:uppercase;color:{MUTED};margin-bottom:0.5rem'>Navigation</div>", unsafe_allow_html=True)
    page = st.radio("", ["Customer Insights", "Model Comparison", "ROI Calculator"],
                    label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.65rem;color:{MUTED};line-height:1.8'>Customer Personality Analysis<br>n = {len(df):,} customers<br>3 demographic clusters<br>XGBoost · AUC 0.90</div>",
                unsafe_allow_html=True)
    st.markdown(
    f"""
    <style>
    /* radio option text */
    div[data-testid="stRadio"] div[role="radiogroup"] label span {{
        color: {MUTED} !important;
    }}

    /* also catches newer DOM variants */
    div[data-testid="stRadio"] label p {{
        color: {MUTED} !important;
        margin: 0;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ── Chart helpers ──────────────────────────────────────────────────────────────
def dark_layout(fig, title=None, height=340, **extra):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, size=11),
        title=dict(text=title, font=dict(size=13)) if title else None,
        margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        height=height,
        **extra,
    )
    fig.update_xaxes(gridcolor=BORDER, showline=False)
    fig.update_yaxes(gridcolor=BORDER, showline=False)
    return fig

def kpi(col, label, value, sub, top_color=None):
    border_top = f"border-top:3px solid {top_color};" if top_color else ""
    col.markdown(f"""
    <div class="metric-card" style="{border_top}">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — CUSTOMER INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
if page == "Customer Insights":
    st.markdown("## Customer Insights")
    st.markdown(f"<div style='color:{CARD};font-size:0.9rem;margin-bottom:1.5rem'>"
                "Demographic segmentation via K-Means reveals three distinct buyer profiles. </div>",
                unsafe_allow_html=True)

    selected = st.selectbox("Filter by segment",
                            ["All Segments"] + [CLUSTER_LABELS[i] for i in range(3)])
    if selected == "All Segments":
        view, active_clusters = df, [0, 1, 2]
    else:
        c_idx = next(k for k, v in CLUSTER_LABELS.items() if v == selected)
        view, active_clusters = df[df["Cluster"] == c_idx], [c_idx]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Customers",        f"{len(view):,}",                        "in segment")
    kpi(c2, "Avg Income",       f"€{view['income'].mean():,.0f}",         "annual")
    kpi(c3, "Avg Total Spend",  f"€{view['total_spend'].mean():,.0f}",    "lifetime")
    kpi(c4, "Campaign Response",f"{view['response'].mean()*100:.1f}%",    "conversion rate")

    # Persona cards
    if selected == "All Segments":
        st.markdown('<div class="section-header">Segment Profiles</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for c, col in zip([0, 1, 2], cols):
            p   = CLUSTER_PERSONAS[c]
            clr = CLUSTER_COLORS[c]
            cdf = df[df["Cluster"] == c]
            col.markdown(f"""
            <div class="metric-card" style="border-top:3px solid {clr}">
              <div class="cluster-badge" style="background:{clr}22;color:{clr}">{CLUSTER_LABELS[c]}</div>
              <div style="font-size:1.1rem;font-weight:600;margin-bottom:0.2rem">{p['name']}, {p['age']}</div>
              <div style="font-size:0.8rem;color:{CARD};line-height:1.5;margin-bottom:1rem">{p['bio']}</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem">
                <div><div class="metric-label">Income</div>
                     <div style="font-family:monospace;font-size:1rem">€{cdf['income'].mean():,.0f}</div></div>
                <div><div class="metric-label">Avg Spend</div>
                     <div style="font-family:monospace;font-size:1rem">€{cdf['total_spend'].mean():,.0f}</div></div>
                <div><div class="metric-label">Web Visits/mo</div>
                     <div style="font-family:monospace;font-size:1rem">{cdf['webvisits'].mean():.1f}</div></div>
                <div><div class="metric-label">Response Rate</div>
                     <div style="font-family:monospace;font-size:1rem">{cdf['response'].mean()*100:.1f}%</div></div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Distribution Analysis</div>', unsafe_allow_html=True)

    # Row 1: scatter + response by web visits
    rc1, rc2 = st.columns(2)
    with rc1:
        fig = px.scatter(view, x="income", y="total_spend", color="Cluster_Label",
                         color_discrete_map=CLUSTER_COLORS, 
                         opacity=0.45,
                         labels={"income":"Annual Income (€)","total_spend":"Total Spend (€)","Cluster_Label":"Segment"},
                         title="Income vs Total Spend")
        fig.update_traces(marker=dict(size=5))
        dark_layout(fig, "Total Spend by Income", legend=dict(bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, width="stretch")

    with rc2:
        web_bins = pd.cut(view["webvisits"], bins=[0,2,4,6,8,20],
                          labels=["0–2","2–4","4–6","6–8","8+"])
        wr = view.groupby(web_bins, observed=True)["response"].mean().reset_index()
        fig2 = go.Figure(go.Bar(
            x=wr["webvisits"].astype(str), y=wr["response"],
            marker_color="#3B82F6", marker_line_width=0,
            text=[f"{v:.0%}" for v in wr["response"]], textposition="outside",
            textfont=dict(color=TEXT),
        ))
        dark_layout(fig2, "Response Rate by Monthly Web Visits",
                    yaxis=dict(tickformat=".0%", gridcolor=BORDER),
                    xaxis=dict(title="Web Visits / month", gridcolor=BORDER))
        st.plotly_chart(fig2, width="stretch")

    # Row 2: age violin + radar
    rc3, rc4 = st.columns(2)
    with rc3:
        fig3 = go.Figure()
        for c in active_clusters:
            cdf = df[df["Cluster"] == c]
            fig3.add_trace(go.Violin(
                x=cdf["age"], name=f"Segment {c+1}",
                line_color=CLUSTER_COLORS[c], fillcolor=CLUSTER_COLORS[c],
                box_visible=True, meanline_visible=True,
                orientation="h", side="positive", width=1.8,
            ))
        dark_layout(fig3, "Age Distribution by Segment",
                    xaxis=dict(title="Age", gridcolor=BORDER),
                    yaxis=dict(gridcolor=BORDER), showlegend=False)
        st.plotly_chart(fig3, width="stretch")

    with rc4:
        fig4 = go.Figure()
        for c in active_clusters:
            cdf = df[df["Cluster"] == c]
            fig4.add_trace(go.Scatterpolar(
                r=[cdf["wines"].mean(), cdf["meat"].mean(),
                   cdf["fruits"].mean(), cdf["gold"].mean(),
                   cdf["sweets"].mean()],
                theta=["Wines", "Meat", "Fruits", "Gold", "Sweets"],
                fill="toself", name=f"Segment {c+1}",
                line_color=CLUSTER_COLORS[c], fillcolor=CLUSTER_COLORS[c],
            ))
        fig4.update_layout(
            title=dict(text="Spending & Income Profile", font=dict(size=13)),
            polar=dict(bgcolor="rgba(0,0,0,0)",
                       radialaxis=dict(visible=True, gridcolor=BORDER, color=CARD),
                       angularaxis=dict(gridcolor=BORDER, color=TEXT)),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT, size=11),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=40, b=10), height=340,
        )
        st.plotly_chart(fig4, width="stretch")

    st.markdown("""
    <div class="insight-box">
    <strong>Key finding:</strong> Segment 1 have both the highest-spend, and highest-response rate.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MODEL COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Model Comparison":
    st.markdown("## Model Comparison")
    st.markdown(f"<div style='color:{CARD};font-size:0.9rem;margin-bottom:1.5rem'>"
                "Three classifiers were evaluated on the dataset. "
                "XGBoost significantly outperforms both Logistic Regression "
                "(DeLong's Test, p < 0.01) and Random Forest (Delong's Test, p < 0.05).</div>", unsafe_allow_html=True)

    # Model cards
    mc1, mc2, mc3 = st.columns(3)
    for col, (name, m) in zip([mc1, mc2, mc3], MODEL_RESULTS.items()):
        clr = MODEL_COLORS[name]
        col.markdown(f"""
        <div class="metric-card" style="border-top:3px solid {clr}">
          <div class="metric-label">{name}</div>
          <div class="metric-value">{m['auc']:.3f}</div>
          <div class="metric-sub">ROC-AUC</div>
          <div style="margin-top:0.8rem;display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.3rem;font-size:0.75rem">
            <div><div style="color:{CARD}">Precision</div><div style="font-family:monospace">{m['precision']:.2f}</div></div>
            <div><div style="color:{CARD}">Recall</div><div style="font-family:monospace">{m['recall']:.2f}</div></div>
            <div><div style="color:{CARD}">F1</div><div style="font-family:monospace">{m['f1']:.2f}</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Feature importance + ablation side by side
    st.markdown('<div class="section-header">What Drives Prediction — XGBoost Feature Importance</div>',
                unsafe_allow_html=True)

    fa1, fa2 = st.columns(2)

    with fa1:
        features     = list(FEATURE_IMPORTANCES.keys())
        importances  = list(FEATURE_IMPORTANCES.values())
        feat_colors  = ["#F59E0B" if f == "Segment" else "#3B82F6" for f in features]
        fig_fi = go.Figure(go.Bar(
            x=importances[::-1], y=features[::-1],
            orientation="h",
            marker_color=feat_colors[::-1],
            marker_line_width=0,
            text=[f"{v:.3f}" for v in importances[::-1]],
            textposition="outside",
            textfont=dict(color=TEXT, size=10),
        ))
        dark_layout(fig_fi, "Feature Importances", height=400,
                    xaxis=dict(title="Importance", gridcolor=BORDER),
                    yaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_fi, width="stretch")
        st.markdown(f"<div style='font-size:0.78rem;color:{CARD};margin-top:-0.5rem'>"
                    "<span style='color:#F59E0B'>■</span> Customer segment outranks all but one demographic"
                    " metric, and is the fourth most predictive, showing it's ability to summarise values.</div>",
                    unsafe_allow_html=True)

    with fa2:
        abl_labels = list(ABLATION.keys())
        abl_vals   = list(ABLATION.values())
        fig_abl = go.Figure(go.Bar(
            x=abl_labels, y=abl_vals,
            marker_color=ABLATION_COLORS, marker_line_width=0,
            text=[f"{v:.3f}" for v in abl_vals],
            textposition="outside",
            textfont=dict(color=TEXT, size=12),
        ))
        dark_layout(fig_abl,
                    "Feature Set Ablation — Random Forest (tuned)",
                    height=400,
                    yaxis=dict(title="ROC-AUC", gridcolor=BORDER, range=[0.5, 1.0]),
                    xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10)),
                    showlegend=False)
        st.plotly_chart(fig_abl, width="stretch")
        st.markdown(f"<div style='font-size:0.78rem;color:{CARD};margin-top:-0.5rem'>"
                    "Model C, with only 4 features — customer segment and first-party CRM data — "
                    "comes close to the accuracy of the Global Model (13 features).</div>",
                    unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
    <strong>Ablation note:</strong> Feature set comparison used Random Forest with tuned hyperparameters
    applied consistently across all four models for a fair comparison.
    XGBoost (AUC 0.902) was selected as the final production model based on overall performance.
    DeLong's test confirmed that it significantly outperforms Logistic Regression and Random Forest. There
    was no signficant difference in performance between Logistic Regression and Random Forest.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — ROI CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "ROI Calculator":
    st.markdown("## ROI Calculator")
    st.markdown(f"<div style='color:{CARD};font-size:0.9rem;margin-bottom:1.5rem'>"
                "Translate model precision and recall into business outcomes. "
                "Adjust campaign parameters — all charts update instantly.</div>",
                unsafe_allow_html=True)

    # Sliders
    s1, s2 = st.columns(2)
    with s1:
        sample_size      = st.slider("Campaign audience size",    500,  10000, 2240, 100)
        avg_price        = st.slider("Average product price (€)",  20,    500,  120,    5)
        avg_margin       = st.slider("Product margin (%)",         10,     80,   40,    5)
    with s2:
        base_rate        = st.slider("Predicted conversion rate (%)",   5,     20,   15,    5)
        cost_per_contact = st.slider("Cost per contact (€)",      0.5,   20.0,  3.0,  0.5)
        model_choice     = st.select_slider(
            "Model",
            options=["Logistic Regression", "Random Forest", "XGBoost"],
            value="XGBoost",
        )

    precision = MODEL_RESULTS[model_choice]["precision"]
    recall    = MODEL_RESULTS[model_choice]["recall"]
    m = compute_roi(sample_size, avg_price, avg_margin, cost_per_contact, precision, recall, base_rate)

    # KPIs
    k1,k2,k3,k4,k5 = st.columns(5)
    kpi(k1, "Net Profit",      f"€{m['net_profit']:,.0f}",    "after marketing cost")
    kpi(k2, "Campaign ROI",    f"{m['roi']:.0f}%",             "return on spend")
    kpi(k3, "Customers Reached", f"{m['targeted']:,}",         f"{m['TP']:,} genuine buyers")
    kpi(k4, "Wasted Spend",    f"€{m['wasted_spend']:,.0f}",  f"{m['FP']:,} wrongly included")
    kpi(k5, "Missed Revenue",  f"€{m['missed_profit']:,.0f}", f"{m['FN']:,} buyers not reached")

    # ── Row 1: Waterfall + P&L bar ─────────────────────────────────────────────
    st.markdown('<div class="section-header">Campaign Economics</div>', unsafe_allow_html=True)
    ec1, ec2 = st.columns(2)

    with ec1:
        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Revenue", "Cost of Goods", "Marketing Cost", "Net Profit"],
            y=[m["revenue"], -m["cogs"], -m["mktg_cost"], m["net_profit"]],
            connector=dict(line=dict(color=BORDER, width=1)),
            increasing=dict(marker_color="#10B981"),
            decreasing=dict(marker_color="#EF4444"),
            totals=dict(marker_color="#3B82F6"),
            text=[f"€{m['revenue']:,.0f}", f"−€{m['cogs']:,.0f}",
                  f"−€{m['mktg_cost']:,.0f}", f"€{m['net_profit']:,.0f}"],
            textposition="outside",
            textfont=dict(color=TEXT, size=11),
        ))
        dark_layout(fig_wf, "Campaign P&L Waterfall",
                    yaxis=dict(gridcolor=BORDER, tickprefix="€"),
                    xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                    showlegend=False)
        st.plotly_chart(fig_wf, width="stretch")

    with ec2:
        fig_bar = go.Figure(go.Bar(
            x=["Gross Profit", "Wasted Spend\n(wrong contacts)", "Missed Profit\n(buyers not reached)"],
            y=[m["gross_profit"], m["wasted_spend"], m["missed_profit"]],
            marker_color=["#10B981", "#F59E0B", "#EF4444"],
            marker_line_width=0,
            text=[f"€{m['gross_profit']:,.0f}", f"€{m['wasted_spend']:,.0f}",
                  f"€{m['missed_profit']:,.0f}"],
            textposition="outside",
            textfont=dict(color=TEXT, size=11),
        ))
        dark_layout(fig_bar, "Profit vs Loss Breakdown",
                    yaxis=dict(gridcolor=BORDER, tickprefix="€"),
                    xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                    showlegend=False)
        st.plotly_chart(fig_bar, width="stretch")

    # ── Row 2: Donut full width ────────────────────────────────────────────────
    st.markdown('<div class="section-header">Prediction Outcome Breakdown</div>',
                unsafe_allow_html=True)

    # Marketer-friendly + data-science labels
    cm_labels = [
        f"Correctly Targeted — Converted<br><span style='font-size:0.75rem;opacity:0.7'>True Positive · {m['TP']:,} customers</span>",
        f"Contacted but Didn't Buy<br><span style='font-size:0.75rem;opacity:0.7'>False Positive · {m['FP']:,} wasted contacts</span>",
        f"Buyers We Missed<br><span style='font-size:0.75rem;opacity:0.7'>False Negative · {m['FN']:,} lost sales</span>",
        f"Correctly Left Out<br><span style='font-size:0.75rem;opacity:0.7'>True Negative · {m['TN']:,} non-buyers</span>",
    ]
    fig_cm = go.Figure(go.Pie(
        labels=[
            f"Correctly Targeted — Converted (TP: {m['TP']:,})",
            f"Contacted but Didn't Buy (FP: {m['FP']:,})",
            f"Buyers We Missed (FN: {m['FN']:,})",
            f"Correctly Left Out (TN: {m['TN']:,})",
        ],
        values=[m["TP"], m["FP"], m["FN"], m["TN"]],
        hole=0.52,
        marker_colors=["#10B981", "#F59E0B", "#EF4444", "#374151"],
        textinfo="percent",
        textfont=dict(size=12, color=TEXT),
        hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
        pull=[0.03, 0.03, 0.03, 0],
    ))
    fig_cm.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, size=12),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="v",
            x=1.02, y=0.5,
            xanchor="left",
            font=dict(size=12),
        ),
        margin=dict(l=10, r=280, t=20, b=20),
        height=360,
    )
    st.plotly_chart(fig_cm, width="stretch")

    st.markdown(f"""
    <div class="insight-box">
    At <strong>{precision:.0%} precision</strong>, {m['FP']:,} contacts are targeted unnecessarily —
    costing <strong>€{m['wasted_spend']:,.0f}</strong> in wasted spend.
    At <strong>{recall:.0%} recall</strong>, {m['FN']:,} genuine buyers are missed,
    representing <strong>€{m['missed_profit']:,.0f}</strong> in unrealised margin.
    Switch to a higher-precision model to cut wasted spend; switch to higher recall to capture more revenue.
    XGBoost offers the best balance of both.
    </div>""", unsafe_allow_html=True)
