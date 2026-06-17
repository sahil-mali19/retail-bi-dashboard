"""
Retail Data Processor — KPI Calculation & Insight Engine
==========================================================
Author  : Sahil Mali
MSc Business Analysis & Consulting | University of Strathclyde
GitHub  : github.com/sahilmali/retail-bi-dashboard

Purpose:
    - Clean and transform raw retail transaction data
    - Calculate executive KPIs with RAG status
    - Identify underperforming regions and categories
    - Export Power BI-ready CSV files
    - Generate automated insight report

Usage:
    python retail_data_processor.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import os
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────

CONFIG = {
    "revenue_target"   : 2_000_000,
    "margin_target_pct": 30.0,
    "yoy_growth_target": 10.0,
    "low_margin_alert" : 20.0,
    "output_dir"       : "reports",
    "fig_dpi"          : 150,
}

NAVY  = "#1A3C6E"
STEEL = "#2E75B6"
GREEN = "#70AD47"
AMBER = "#ED7D31"
RED   = "#C00000"


# ─────────────────────────────────────────────
#  1. DATA LOADING
# ─────────────────────────────────────────────

def load_data(filepath: str = None) -> pd.DataFrame:
    """Load Superstore data or generate synthetic dataset."""
    if filepath and os.path.exists(filepath):
        print(f"📂  Loading real data from {filepath}")
        df = pd.read_csv(filepath, encoding="latin-1")
        df["OrderDate"] = pd.to_datetime(df["Order Date"])
        df.rename(columns={"Sales": "Sales", "Profit": "Profit",
                            "Quantity": "Quantity", "Discount": "Discount",
                            "Region": "Region", "Category": "Category",
                            "Sub-Category": "SubCategory", "Segment": "Segment",
                            "Ship Mode": "ShipMode", "Order ID": "OrderID"}, inplace=True)
    else:
        print("⚡  Generating synthetic Superstore dataset…")
        df = _generate_synthetic_data()
    return df


def _generate_synthetic_data(n: int = 9994, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    regions    = ["West","East","Central","South","North",
                  "South-East","North-East","Mid-West","South-West",
                  "North-West","Pacific","Mountain"]
    categories = ["Technology","Furniture","Office Supplies","Clothing","Food & Beverage"]
    sub_cats   = {
        "Technology"      : ["Phones","Computers","Accessories","Copiers"],
        "Furniture"       : ["Chairs","Tables","Bookcases","Furnishings"],
        "Office Supplies" : ["Binders","Paper","Art","Envelopes","Fasteners"],
        "Clothing"        : ["Shirts","Trousers","Shoes","Accessories"],
        "Food & Beverage" : ["Snacks","Beverages","Bakery","Dairy"],
    }
    base_sales  = {k: v for k, v in zip(categories, [350,280,90,65,40])}
    margin_base = {k: v for k, v in zip(categories, [0.41,0.26,0.34,0.38,0.22])}
    region_factor = {r: f for r, f in zip(regions,
        [1.20,1.15,0.78,0.92,0.88,1.00,1.05,0.82,0.95,1.10,1.18,0.85])}

    cat_arr  = rng.choice(categories, n, p=[0.27,0.24,0.30,0.11,0.08])
    sub_arr  = [rng.choice(sub_cats[c]) for c in cat_arr]
    reg_arr  = rng.choice(regions, n)

    sales_arr  = np.array([base_sales[c] * rng.uniform(0.3, 3.5) for c in cat_arr])
    profit_arr = np.array([
        sales_arr[i] * margin_base[cat_arr[i]] * rng.uniform(0.6, 1.2) * region_factor[reg_arr[i]]
        for i in range(n)
    ])
    start = datetime(2020, 1, 1)
    dates = [start + timedelta(days=int(x)) for x in rng.choice(range(1461), n)]

    return pd.DataFrame({
        "OrderID"    : [f"CA-{i:06d}" for i in range(n)],
        "OrderDate"  : dates,
        "ShipMode"   : rng.choice(["Standard Class","Second Class","First Class","Same Day"],
                                   n, p=[0.60,0.20,0.15,0.05]),
        "Segment"    : rng.choice(["Consumer","Corporate","Home Office"], n, p=[0.52,0.31,0.17]),
        "Region"     : reg_arr,
        "Category"   : cat_arr,
        "SubCategory": sub_arr,
        "Sales"      : np.round(sales_arr, 2),
        "Quantity"   : rng.integers(1, 15, n),
        "Discount"   : np.round(rng.choice([0,0.1,0.2,0.3,0.4,0.5], n, p=[0.45,0.25,0.15,0.08,0.05,0.02]), 2),
        "Profit"     : np.round(profit_arr, 2),
    })


# ─────────────────────────────────────────────
#  2. FEATURE ENGINEERING
# ─────────────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Year"]          = df["OrderDate"].dt.year
    df["Month"]         = df["OrderDate"].dt.month
    df["Quarter"]       = df["OrderDate"].dt.quarter
    df["ProfitMargin"]  = (df["Profit"] / df["Sales"] * 100).round(2)
    df["IsLossMaking"]  = df["Profit"] < 0
    df["DiscountBand"]  = pd.cut(df["Discount"],
                                  bins=[-0.01, 0.0, 0.15, 0.30, 1.0],
                                  labels=["No Discount","Low","Medium","High"])
    return df


# ─────────────────────────────────────────────
#  3. KPI CALCULATIONS
# ─────────────────────────────────────────────

def rag(value: float, target: float, invert: bool = False) -> str:
    ratio = value / target
    if invert:
        return "🟢 GREEN" if ratio < 0.9 else ("🟡 AMBER" if ratio < 1.1 else "🔴 RED")
    return "🟢 GREEN" if ratio >= 1.0 else ("🟡 AMBER" if ratio >= 0.85 else "🔴 RED")


def calculate_kpis(df: pd.DataFrame) -> dict:
    years    = sorted(df["Year"].unique())
    cur_yr   = years[-1] if len(years) > 0 else 2023
    prev_yr  = years[-2] if len(years) > 1 else 2022

    rev_cur  = df[df["Year"] == cur_yr]["Sales"].sum()
    rev_prev = df[df["Year"] == prev_yr]["Sales"].sum()
    yoy      = (rev_cur - rev_prev) / rev_prev * 100 if rev_prev > 0 else 0

    return {
        "total_revenue"    : df["Sales"].sum(),
        "total_profit"     : df["Profit"].sum(),
        "avg_margin_pct"   : df["ProfitMargin"].mean(),
        "total_orders"     : df["OrderID"].nunique(),
        "avg_order_value"  : df["Sales"].sum() / df["OrderID"].nunique(),
        "yoy_growth_pct"   : yoy,
        "loss_orders_pct"  : df["IsLossMaking"].mean() * 100,
    }


def print_kpi_dashboard(kpis: dict):
    c = CONFIG
    print("\n" + "=" * 65)
    print("           EXECUTIVE BI DASHBOARD — KPI SUMMARY")
    print("=" * 65)
    print(f"  {'Total Revenue':<28} ${kpis['total_revenue']:>12,.0f}   "
          f"{rag(kpis['total_revenue'], c['revenue_target'])}")
    print(f"  {'Total Profit':<28} ${kpis['total_profit']:>12,.0f}")
    print(f"  {'Avg Profit Margin':<28} {kpis['avg_margin_pct']:>11.1f}%   "
          f"{rag(kpis['avg_margin_pct'], c['margin_target_pct'])}")
    print(f"  {'Total Orders':<28} {kpis['total_orders']:>12,}")
    print(f"  {'Avg Order Value':<28} ${kpis['avg_order_value']:>12,.2f}")
    print(f"  {'YoY Revenue Growth':<28} {kpis['yoy_growth_pct']:>11.1f}%   "
          f"{rag(kpis['yoy_growth_pct'], c['yoy_growth_target'])}")
    print(f"  {'Loss-making Order %':<28} {kpis['loss_orders_pct']:>11.1f}%   "
          f"{rag(kpis['loss_orders_pct'], 10, invert=True)}")
    print("=" * 65)


# ─────────────────────────────────────────────
#  4. INSIGHT ENGINE
# ─────────────────────────────────────────────

def generate_insights(df: pd.DataFrame) -> list[str]:
    insights = []

    # Underperforming regions
    reg = df.groupby("Region")["Profit"].sum()
    avg = reg.mean()
    underperf = reg[reg < avg * 0.8].index.tolist()
    if underperf:
        insights.append(
            f"⚠️  Underperforming regions (>20% below avg): {', '.join(underperf)} — "
            "review sales team allocation and pricing strategy")

    # High-discount, low-margin issue
    disc_margin = df.groupby("DiscountBand")["ProfitMargin"].mean()
    if "High" in disc_margin.index and disc_margin.get("High", 0) < 10:
        insights.append(
            f"⚠️  High-discount orders average margin = {disc_margin['High']:.1f}% — "
            "discount policy needs tightening")

    # Best performing category
    best_cat = df.groupby("Category")["Profit"].sum().idxmax()
    insights.append(f"✅  Best category by profit: {best_cat} — consider expanding SKU range")

    # Q4 concentration
    q4_share = df[df["Quarter"] == 4]["Sales"].sum() / df["Sales"].sum()
    if q4_share > 0.35:
        insights.append(
            f"📌  Q4 accounts for {q4_share:.0%} of revenue — develop Q1-Q3 promo strategy "
            "to reduce seasonality risk")

    # Loss-making sub-categories
    sc = df.groupby("SubCategory")["Profit"].sum()
    loss = sc[sc < 0].index.tolist()
    if loss:
        insights.append(
            f"🔴  Loss-making sub-categories: {', '.join(loss)} — "
            "review pricing or consider product discontinuation")

    return insights


# ─────────────────────────────────────────────
#  5. EXPORT
# ─────────────────────────────────────────────

def export_power_bi_files(df: pd.DataFrame, kpis: dict, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    # Main fact table
    df.to_csv(f"{out_dir}/fact_sales.csv", index=False)

    # Regional summary
    reg = df.groupby("Region").agg(
        Revenue=("Sales","sum"), Profit=("Profit","sum"),
        Orders=("OrderID","count"), AvgMargin=("ProfitMargin","mean")
    ).round(2)
    reg["MarginPct"] = (reg["Profit"] / reg["Revenue"] * 100).round(1)
    reg.to_csv(f"{out_dir}/dim_regional.csv")

    # Category summary
    cat = df.groupby(["Category","SubCategory"]).agg(
        Revenue=("Sales","sum"), Profit=("Profit","sum"),
        Orders=("OrderID","count")
    ).round(2)
    cat["MarginPct"] = (cat["Profit"] / cat["Revenue"] * 100).round(1)
    cat.to_csv(f"{out_dir}/dim_category.csv")

    # Monthly time series
    ts = df.groupby(["Year","Month"]).agg(Revenue=("Sales","sum"), Profit=("Profit","sum")).round(2)
    ts.to_csv(f"{out_dir}/fact_monthly.csv")

    # KPI export
    pd.DataFrame([kpis]).to_csv(f"{out_dir}/kpi_summary.csv", index=False)

    print(f"\n📁  Power BI-ready files exported to /{out_dir}/")
    print(f"    fact_sales.csv | dim_regional.csv | dim_category.csv")
    print(f"    fact_monthly.csv | kpi_summary.csv")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("🔄  Loading data…")
    df = load_data()
    df = engineer_features(df)
    print(f"    {len(df):,} records loaded\n")

    kpis = calculate_kpis(df)
    print_kpi_dashboard(kpis)

    print("\n\n💡  AUTOMATED INSIGHTS:")
    print("-" * 65)
    for insight in generate_insights(df):
        print(f"  {insight}")

    export_power_bi_files(df, kpis, CONFIG["output_dir"])
    print("\n🎉  Done! Open /reports files in Power BI Desktop.")
