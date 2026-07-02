# Sci-Kitchen Luxury Foods — Predictive Segmentation

Ironhack Data Analytics Final Project | Claire Leyden

A customer segmentation and campaign-response model for a fictional gourmet
food brand.

## The problem

Sci-Kitchen's marketing spend, optimised against standard digital metrics, wasn't
delivering ROI — high website traffic correlated poorly with sales, signalling
casual browsing rather than purchase intent. This project uses machine learning
to identify which data sources actually predict conversion, and which
high-value customer segments exist beneath the noise.

## Dataset

[Customer Personality Analysis](https://www.kaggle.com/datasets/imakash3011/customer-personality-analysis)
(Kaggle) — 2,240 customers, 29 raw features spanning demographics, spending
history across 6 product categories, purchase channels, and past campaign
responses. After cleaning: 2,212 customers.

## Pipeline

```
notebooks/
├── CP_data_cleaning.ipynb   # raw → analysis-ready CSV
├── cp_eda.ipynb             # bivariate response drivers, significance testing
└── cp_modeling.ipynb        # PCA, clustering, ablation, tuning, model comparison
```

**1. Cleaning** — dropped rows with missing income, removed one extreme income
outlier, consolidated education (5→3 tiers) and marital status (8→3 tiers),
converted enrollment date to customer tenure in days, and collapsed five
historical campaign-acceptance flags into a single `num_camp_success` count.

**2. EDA** —  tested response against income, education, marital
status, complaints, children, and past campaign success. Findings: age and
income aren't correlated; conversion is significantly higher for higher
income, higher education, and customers living alone with no children; prior
campaign success is the single strongest signal of future response.

**3. Modeling:**

- **PCA** — compressed 6 correlated spend categories into 3 principal
  components (~80% of variance retained), so KMeans wouldn't be dominated by
  raw spend magnitude.
- **KMeans clustering** — combined the 3 spend components with income,
  has-child, and channel-engagement features (web/catalogue/store) to find
  3 customer segments, chosen via silhouette score, inertia, and marketing
  usefulness of the resulting groups.
- **Ablation study** — trained a Random Forest on four feature sets to isolate
  which data source actually drives predictive power:

  | Feature set | ROC-AUC |
  |---|---|
  | Demographics only | 0.7120 |
  | Digital behaviour only | 0.7054 |
  | CRM / Hybrid (tenure, past success, cluster, spend) | 0.8086 |
  | Global (all features) | 0.8729 |

  *(hyperparameters held constant across feature sets — tuned once on the CRM
  model — to isolate the feature-set effect from tuning variance)*

  The 4-feature CRM/hybrid model gets most of the way to the Global model's
  performance using a fraction of the inputs, while digital behaviour alone
  barely beats demographics.

- **Model comparison** — Logistic Regression, Random Forest, and XGBoost,
  each hyperparameter-tuned via grid search, compared with DeLong's test
  (accounts for correlated ROC curves on the same test set, rather than just
  eyeballing an AUC gap):

  | Model | ROC-AUC |
  |---|---|
  | Logistic Regression | 0.8630 |
  | Random Forest | 0.8850 |
  | XGBoost | **0.9015** |

  No significant difference between Logistic Regression and Random Forest.
  XGBoost significantly outperformed both (p < 0.01 vs. LR, p < 0.05 vs. RF)
  — it also relied more heavily on the cluster feature than the other models,
  suggesting a nonlinear interaction between segment and campaign response.

## Customer segments

| Segment | Profile | Conversion |
|---|---|---|
| **The Decisive Buyer** | High income, no children, low digital footprint | 30.2% |
| **The Family Spender** | Mid income, children, engaged and considered | 9.4% |
| **The Browser** | Low income, two kids, high web engagement, low spend | 12.2% |

The Decisive Buyer is the highest-value segment by a wide margin, and appears to be the hardest to reach
through digital channels.

## Interactive app

A Streamlit app translates the model output into business decisions:

- Customer intelligence dashboard (segment profiles)
- Model comparison page (AUC, precision, recall across the three algorithms)
- ROI calculator — adjust campaign size, conversion rate, price, margin, and
  cost-per-contact to see projected net profit, wasted spend, and missed
  revenue by model choice

**Live app:** `https://sci-kitchen-marketing.streamlit.app/`

## Recommendations

- **Digital tracking is the weakest predictor of conversion.** Web visits
  signal browsing, not intent.
- **CRM data (tenure, past campaign success) plus segment membership
  outperforms both demographics and digital behaviour.** Prioritise CRM data
  hygiene and enrichment over investment in digital marketing/tracking tools.
- **The highest-value segment (Miguel) converts 3x more than average but
  leaves almost no digital footprint.** Build outbound audiences from the
  demographic profile of this segment directly, and consider influencer
  partnerships to reach it without relying on on-site engagement.
- **Open question:** where does Miguel actually discover new promotions?
  Worth a targeted follow-up study — the current dataset can't answer it.

## Project structure

```
Final-Project
├─ .devcontainer
│  └─ devcontainer.json
├─ .python-version
├─ config.yaml
├─ data
│  ├─ clean
│  │  ├─ bank-full.csv
│  │  ├─ CP_ready_to_model.csv
│  │  ├─ data_w_cluster.csv
│  │  └─ marketing_campaign.csv
│  └─ raw
│     └─ marketing_campaign.csv
├─ figures
│  ├─ model-comparison.png
│  ├─ pca_clusters.png
│  ├─ pca_heatmap.png
│  ├─ pca_loadings.png
│  └─ rf-ablation.png
├─ main.py
├─ notebooks
│  ├─ CP_data_cleaning.ipynb
│  ├─ cp_eda.ipynb
│  ├─ cp_modeling.ipynb
│  ├─ data_cleaning_bank.ipynb
│  ├─ eda_bank.ipynb
│  └─ Modeling-Bank.ipynb
├─ pyproject.toml
├─ README.md
├─ slides
│  └─ Sci-Kitchen Predictive Segmentation Ironhack.pdf
├─ sql
│  └─ ERD.PNG
├─ Streamlit
│  ├─ app.py
│  ├─ backend.py
│  └─ sk_logo.png
└─ uv.lock
```

## Setup


Run the three notebooks in order (cleaning → EDA → modeling); each writes its
output to `data/clean/` for the next stage to pick up.

## Tools

Python · pandas · scikit-learn · XGBoost · MLstatkit (DeLong's test) · seaborn
· Streamlit

## Streamlit App:

https://sci-kitchen-marketing.streamlit.app/

## Presentation:

https://docs.google.com/presentation/d/1dWVvAv2vGfaGUOFkyGPvL1H8IeCHtUdMcdxGqaW5QsY/edit?usp=sharing

## Trello:

https://trello.com/invite/b/6a3bc9202267f2d1c89e611e/ATTIadab59b15dc491d32a95f958fd587f8e1B325FD0/final-rncp-project

---
*Ironhack Data Analytics Bootcamp — Final Project*
