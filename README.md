# 📊 Business Intelligence Dashboard — Retail Analytics

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python)](https://python.org)
[![Power BI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811?style=flat-square&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?style=flat-square&logo=pandas)](https://pandas.pydata.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> **Business Problem:** A multi-regional retailer relies on manual Excel reports — slow, error-prone, and not actionable. This project delivers a fully automated BI dashboard covering £2M+ in retail transactions, identifying 3 underperforming regions and delivering strategic recommendations projecting a **12% revenue uplift**.

---

## 🎯 Key Business Insights

| Finding | Impact | Action |
|---------|--------|--------|
| 3 regions below median by >25% | £180K revenue gap | Regional reactivation campaign |
| Office Supplies has lowest margin | Only 18% margin | Supplier renegotiation |
| Online channel growing fastest | 45% of orders | Invest in digital marketing |
| Average discount = 8.2% | Eroding profitability | Dynamic pricing strategy |

---

## 🏗️ Project Structure

```
2_retail_bi_dashboard/
├── notebooks/retail_analytics.py     # Full EDA + KPI computation + visualisations
├── src/
│   ├── data_generator.py             # 12,000-record realistic retail dataset
│   └── kpi_calculator.py             # Reusable KPI computation module
├── reports/
│   ├── bi_dashboard.png              # Executive dashboard (auto-generated)
│   └── strategic_insights.md         # Written recommendations report
├── data/README.md                    # Superstore dataset download instructions
└── requirements.txt
```

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Data Processing | Python, Pandas, NumPy |
| Visualisation | Matplotlib, Seaborn |
| BI Dashboard | Power BI (DAX, Power Query, dynamic slicers) |
| Data Modelling | Excel (Pivot Tables, XLOOKUP, dynamic arrays) |

---

## 📈 Dashboard Components

1. **KPI Cards** — Revenue, Profit, Gross Margin, Total Orders (vs prior year)
2. **Monthly Revenue Trend** — 2023 vs 2024 line chart with YoY comparison
3. **Category Revenue Mix** — Donut chart with revenue share %
4. **Regional Heatmap** — Category mix by region (identify strategic gaps)
5. **Profit Margin by Category** — Traffic-light bar chart (red/amber/green)
6. **Channel Revenue Split** — Online vs In-Store vs B2B vs Marketplace
7. **Quarterly Growth Waterfall** — QoQ and YoY growth %

---

## 🚀 Quick Start

```bash
git clone https://github.com/sahil-mali19/retail-bi-dashboard.git
cd retail-bi-dashboard
pip install -r requirements.txt
python notebooks/retail_analytics.py
```

**Dataset:** Download [Superstore Sales](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) from Kaggle → `/data` folder. Or run as-is with synthetic data.

---

## 👤 Author
**Sahil Mali** | MSc Business Analysis & Consulting — University of Strathclyde  
📧 sahil06june2003@gmail.com | 🔗 [LinkedIn](https://linkedin.com/in/sahil-mali-2755021b9)
