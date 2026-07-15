# Sci-Kitchen Luxury Foods — Predictive Segmentation

Ironhack Data Analytics Final Project | Claire Leyden

A customer segmentation and campaign-response model for a fictional gourmet
food brand, with an external validation study on a real-world marketing
dataset from a different industry.

## The problem

Sci-Kitchen's marketing spend, optimised against standard digital metrics,
wasn't delivering ROI — high website traffic correlated poorly with sales,
signalling casual browsing rather than purchase intent. This project uses
machine learning to identify which data sources actually predict conversion,
and which high-value customer segments exist beneath the noise — then tests
whether the same methodology holds up on an unrelated dataset.

## Datasets

**Primary: [Customer Personality Analysis](https://www.kaggle.com/datasets/imakash3011/customer-personality-analysis)**
(Kaggle) — 2,240 customers, 29 raw features spanning demographics, spending
history across 6 product categories, purchase channels, and past campaign
responses. After cleaning: 2,212 customers.

**Supplementary: UCI Bank Marketing** (Hugging Face) — direct marketing
campaign data from a Portuguese bank, enriched with occupation-level salary
estimates scraped from Paylab.pt and official pension/minimum-wage data from
INE and Eurostat. Used as an independent case study to test whether the
Sci-Kitchen modeling approach generalises to a dataset with limited
behavioural information.

## Pipeline

```
notebooks/
├── CP_data_cleaning.ipynb    # CPA raw → analysis-ready CSV
├── cp_eda.ipynb              # CPA bivariate response drivers, significance testing
├── cp_modeling.ipynb         # CPA: PCA, clustering, ablation, tuning, model comparison
├── data_cleaning_bank.ipynb  # Bank Marketing raw → analysis-ready CSV
├── Web-Scraping-Bank.ipynb   # Paylab.pt occupation salary scrape
├── eda_bank.ipynb            # Bank Marketing EDA
├── Clustering-Bank.ipynb     # Bank Marketing: PCA + HDBSCAN segmentation attempt
└── Modeling-Bank.ipynb       # Bank Marketing: ablation, tuning, model comparison
```

**1. Cleaning (CPA)** — dropped rows with missing income, removed extreme
age outliers, consolidated education (5→3 tiers) and marital status (8→3
tiers), converted enrollment date to customer tenure in days, and collapsed
five historical campaign-acceptance flags into a single `num_camp_success`
count.

**2. EDA (CPA)** — tested response against income, education, marital
status, complaints, children, and past campaign success. Findings: higher
income, higher education, and living alone with no children are all
significantly associated with conversion; prior campaign success is the
single strongest signal of future response.

**3. Modeling (CPA):**

- **PCA** — compressed 6 correlated spend categories into 3 principal
  components (~80% of variance retained), so KMeans wouldn't be dominated by
  raw spend magnitude.
- **KMeans clustering** — applied to the 3 spend components to find 3
  customer segments, chosen via silhouette score and marketing usefulness of
  the resulting groups.
- **Ablation study** — trained a Random Forest on four feature sets to
  isolate which data source actually drives predictive power:

  | Feature set | ROC-AUC |
  |---|---|
  | Demographics only | 0.712 |
  | Digital behaviour only | 0.705 |
  | CRM / Relationship only | 0.809 |
  | Global (all features) | 0.873 |

  CRM/relationship features (tenure, past campaign success) substantially
  outperform demographics or digital behaviour alone, while the global model
  combining all sources performs best.

- **Model comparison** — Logistic Regression, Random Forest, and XGBoost,
  each hyperparameter-tuned via grid search, compared with DeLong's test
  (accounts for correlated ROC curves on the same test set, rather than just
  eyeballing an AUC gap):

  | Model | ROC-AUC |
  |---|---|
  | Logistic Regression | 0.863 |
  | Random Forest | 0.885 |
  | XGBoost | **0.902** |

  XGBoost significantly outperformed both Logistic Regression (p = 0.003) and
  Random Forest (p = 0.031).

**4. Cleaning, EDA, modeling (Bank Marketing)** — same pipeline structure
repeated on the supplementary dataset, enriched with scraped and API-sourced
income data. PCA did not reveal a clean low-dimensional structure (11
components needed for ~77% variance, vs. 3 for CPA), so KMeans was not
pursued here. HDBSCAN was tested instead across several minimum-cluster-size
parameters; results consistently recovered occupation categories rather than
distinct behavioural segments, confirming the dataset lacks the
purchasing/engagement features needed for meaningful segmentation — a data
limitation rather than an algorithm failure. The feature-set ablation and
model comparison were still repeated for predictive validation:

| Feature set | ROC-AUC |
|---|---|
| Demographic only | 0.708 |
| Campaign history only | 0.762 |
| Global (all features) | 0.780 |

| Model | ROC-AUC |
|---|---|
| Logistic Regression | 0.766 |
| Random Forest | 0.780 |
| XGBoost | 0.784 |

The same pattern held: relationship/campaign-history signals outperformed
demographics, and the combined model performed best — though XGBoost's edge
over Random Forest was not statistically significant here.

## Customer segments (CPA)

| Segment | Profile | Conversion |
|---|---|---|
| **The Decisive Buyer** | High income, no children, low digital footprint | 30.2% |
| **The Family Spender** | Mid-to-high income, engaged and considered | 12.3% |
| **The Browser** | Lower income, high web engagement, low spend | 9.4% |

The Decisive Buyer is the highest-value segment by a wide margin, and
appears to be the hardest to reach through digital channels.

## Database & API

Processed data is stored in a normalized MySQL database (7 entities, 5
relationships — see `sql/ERD.PNG`), with SQL queries in `sql/query_tables.sql`
demonstrating joins, aggregation, and filtering across the customer,
behaviour, spend, and Bank Marketing schemas.

Two REST API implementations are included, both exposing the same four
endpoints (`/customer_profile/{id}`, `/customer_lifetime_value/{id}`,
`/cluster/{cluster_number}`, `/bank_job_profiles`):

- **`flask/`** — Flask + PyMySQL, with Swagger documentation via flasgger
  and pagination on `/cluster/{cluster_number}`.
- **`FastAPI/`** — FastAPI equivalent, with automatic OpenAPI documentation.

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
  outperforms both demographics and digital behaviour** — a pattern that
  held on an entirely different dataset (Bank Marketing), suggesting it's not
  specific to Sci-Kitchen's customer base.
- **The highest-value segment (Miguel, "the Decisive Buyer") converts 3x
  more than average but leaves almost no digital footprint.** Build outbound
  audiences from the demographic profile of this segment directly, and
  consider influencer partnerships to reach it without relying on on-site
  engagement.
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
│  │  ├─ bank-ready_to_model.csv
│  │  ├─ CP_ready_to_model.csv
│  │  ├─ data_w_cluster.csv
│  │  ├─ job_salaries_scraped.csv
│  │  └─ marketing_campaign.csv
│  └─ raw
│     └─ marketing_campaign.csv
├─ FastAPI
│  ├─ main.py
│  └─ README.md
├─ figures
│  ├─ bank-cluster-job.png
│  ├─ bigquery.PNG
│  ├─ bigquery_query.PNG
│  ├─ bigquery_table.PNG
│  ├─ cp-model-comparison.png
│  ├─ cpa-campaigns-response.png
│  ├─ cpa-children-response.png
│  ├─ cpa-education-response.png
│  ├─ cpa-income-response.png
│  ├─ cpa-marital_s-response.png
│  ├─ cpa-pca-var.png
│  ├─ feature-set-comparison.png
│  ├─ model-comparison.png
│  ├─ pca_clusters.png
│  ├─ pca_heatmap.png
│  ├─ pca_loadings.png
│  ├─ rf-ablation.png
│  ├─ sql_query_1_table_joins.PNG
│  ├─ sql_query_2_table_joins.PNG
│  ├─ sql_query_3_where_orderby.PNG
│  ├─ sql_query_4_count_groupby.PNG
│  └─ sql_query_5_count_avg_join.PNG
├─ flask
│  ├─ main.py
│  └─ README.md
├─ main.py
├─ notebooks
│  ├─ Clustering-Bank.ipynb
│  ├─ CP_data_cleaning.ipynb
│  ├─ cp_eda.ipynb
│  ├─ cp_modeling.ipynb
│  ├─ data_cleaning_bank.ipynb
│  ├─ eda_bank.ipynb
│  ├─ Modeling-Bank.ipynb
│  └─ Web-Scraping-Bank.ipynb
├─ pyproject.toml
├─ README.md
├─ slides
│  ├─ RNCP_Report_ ClaireLeyden.pdf
│  └─ Sci-Kitchen Predictive Segmentation Ironhack.pdf
├─ sql
│  ├─ Bank_Customer.csv
│  ├─ Bank_Salary.csv
│  ├─ Behaviour.csv
│  ├─ Channels.csv
│  ├─ Cluster.csv
│  ├─ Create_table_csvs.ipynb
│  ├─ Customer.csv
│  ├─ ERD.PNG
│  ├─ load_tables.sql
│  ├─ Product_spend.csv
│  └─ query_tables.sql
├─ Streamlit
│  ├─ app.py
│  ├─ backend.py
│  └─ sk_logo.png
└─ uv.lock
```

## Setup

Run the notebooks in order (cleaning → EDA → modeling, for each dataset);
each writes its output to `data/clean/` for the next stage to pick up.
Load `sql/load_tables.sql` into MySQL before running either API.

## Tools

Python · pandas · scikit-learn · XGBoost · MLstatkit (DeLong's test) ·
HDBSCAN · seaborn · Flask · FastAPI · flasgger · MySQL · BigQuery ·
BeautifulSoup · Streamlit

## Streamlit App:

https://sci-kitchen-marketing.streamlit.app/

## Presentation:

https://docs.google.com/presentation/d/1dWVvAv2vGfaGUOFkyGPvL1H8IeCHtUdMcdxGqaW5QsY/edit?usp=sharing

## Trello:

https://trello.com/invite/b/6a3bc9202267f2d1c89e611e/ATTIadab59b15dc491d32a95f958fd587f8e1B325FD0/final-rncp-project

---
*Ironhack Data Analytics Bootcamp — Final Project*