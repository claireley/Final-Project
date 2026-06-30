"""
backend.py
Data generation, model results, and computation logic.
Swap generate_data() for pd.read_csv() once your real cleaned file is ready.
"""

import numpy as np
import pandas as pd

# ── Design tokens (shared) ─────────────────────────────────────────────────────
CLUSTER_COLORS = {
    0: "#F59E0B",   # amber   — decisive buyers
    1: "#10B981",   # emerald — browsers
    2: "#8B5CF6",   # violet  — family spenders
}
CLUSTER_LABELS = {
    0: "Segment 1 — The Decisive Buyers",
    1: "Segment 2 — The Browsers",
    2: "Segment 3 — The Family Spenders",
}
CLUSTER_PERSONAS = {
    0: {
        "name": "Miguel", "age": "44",
        "bio": (
        "Finance director, no children, owns property. Visits rarely, "
            "doesn't open many emails. When he buys, he spends big. Nearly "
            "invisible to behavioural scoring — your highest-value customer."        
        ),
    },
    1: {
        "name": "Sofia", "age": "35",
        "bio": (
            "Teacher, two kids, rents in Lisbon suburbs. Browses extensively "
            "online — comparing prices, reading reviews, adding to wishlists. "
            "Rarely converts. High digital footprint, low purchase value."
            
        ),
    },
    2: {
        "name": "Ana", "age": "48",
        "bio": (
            "Marketing manager, two teenagers, homeowner. Researches "
            "thoughtfully and converts on clear value propositions. "
            "Responds well to targeted, well-timed campaigns."
        ),
    },
}

BG     = "#F6F1E9"
CARD   = "#2B2B2B"
BORDER = "#988E6E"
TEXT   = "#6D1F3A"
MUTED  = "#e8ecf4"

# ── Model results (from your actual notebook) ──────────────────────────────────
MODEL_RESULTS = {
    "Logistic Regression": {"auc": 0.862, "precision": 0.75, "recall": 0.42, "f1": 0.53},
    "Random Forest":       {"auc": 0.885, "precision": 0.74, "recall": 0.45, "f1": 0.56},
    "XGBoost":             {"auc": 0.902, "precision": 0.74, "recall": 0.45, "f1": 0.56},
}
MODEL_COLORS = {
    "Logistic Regression": "#6B7280",
    "Random Forest":       "#3B82F6",
    "XGBoost":             "#10B981",
}

# Feature ablation results (Random Forest, tuned, same hyperparams across all)
ABLATION = {
    "A — Demographics\n(who they are)":          0.712,
    "B — Digital / Behavioural\n(what we track)": 0.705,
    "C — First-party CRM\n(what we already know)": 0.809,
    "Global — All Features":                       0.873,
}
ABLATION_COLORS = ["#6B7280", "#F59E0B", "#3B82F6", "#10B981"]

# XGBoost feature importances (global model)
FEATURE_IMPORTANCES = {
    "Past Campaign Responses":                  0.215,
    "Days Since Last Purchase":              0.103,
    "Marital Status= Single":  0.091,
    "Segment":         0.077,
    "Total Lifetime Spend":                   0.075,
    "Tenure in days":                      0.075,
    "Marital Status= Separated":                0.073,   
    "Website Visits":                    0.061,
    "Income":                0.057,
    "Education":                  0.051,
    "Number of Children":    0.047,
    "Number of Discounted Purchases": 0.042,
    "Age": 0.034
}

# ── Data ───────────────────────────────────────────────────────────────────────
def load_real_data() -> pd.DataFrame:
    return pd.read_csv("../data/clean/data_w_cluster.csv", sep=";")


# ── ROI computation ────────────────────────────────────────────────────────────
def compute_roi(sample_size, avg_price, avg_margin, cost_per_contact,
                precision, recall, base_rate):
    total_pos = int(sample_size * base_rate / 100)
    total_neg = sample_size - total_pos
    TP = int(total_pos * recall)
    FN = total_pos - TP
    FP = int(TP / precision - TP) if precision > 0 else 0
    TN = max(0, total_neg - FP)
    targeted = TP + FP
    revenue      = TP * avg_price
    cogs         = revenue * (1 - avg_margin / 100)
    gross_profit = revenue - cogs
    mktg_cost    = targeted * cost_per_contact
    net_profit   = gross_profit - mktg_cost
    wasted_spend = FP * cost_per_contact
    missed_profit= FN * avg_price * (avg_margin / 100)
    roi          = (net_profit / mktg_cost * 100) if mktg_cost > 0 else 0
    return dict(
        TP=TP, FP=FP, FN=FN, TN=TN,
        targeted=targeted, not_targeted=FN + TN,
        revenue=revenue, cogs=cogs, gross_profit=gross_profit,
        mktg_cost=mktg_cost, net_profit=net_profit,
        wasted_spend=wasted_spend, missed_profit=missed_profit,
        roi=roi,
    )
