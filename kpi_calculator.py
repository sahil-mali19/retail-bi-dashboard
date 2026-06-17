"""
kpi_calculator.py
=================
Compute and visualise all retail KPIs. Run directly: python src/kpi_calculator.py
Author: Sahil Mali | MSc Business Analysis & Consulting, Strathclyde
"""

import os
import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(__file__))
from data_generator import load_or_generate

os.makedirs('../reports', exist_ok=True)
plt.style.use('seaborn-v0_8-whitegrid')
NAVY, STEEL, GREEN, RED, AMBER = '#1A3C6E','#2E75B6','#34C759','#FF3B30','#FF9500'
PALETTE = [NAVY, STEEL, GREEN, RED, AMBER, '#9B59B6', '#E67E22',
           '#1ABC9C', '#E74C3C', '#3498DB', '#2ECC71', '#F39C12']


def compute_kpis(df: pd.DataFrame) -> dict:
    """Calculate all business KPIs from retail DataFrame."""
    df = df.copy()
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year']       = df['Order Date'].dt.year
    df['Quarter']    = df['Order Date'].dt.to_period('Q').astype(str)
    df['Month']      = df['Order Date'].dt.to_period('M').astype(str)

    years = sorted(df['Year'].unique())
    kpis  = {}

    for yr in years:
        d = df[df['Year'] == yr]
        kpis[yr] = {
            'total_revenue':     d['Sales'].sum(),
            'total_profit':      d['Profit'].sum(),
            'avg_margin':        d['Profit Margin'].mean(),
            'total_orders':      d['Order ID'].nunique(),
            'total_customers':   d['Customer ID'].nunique(),
            'avg_order_value':   d['Sales'].sum() / max(d['Order ID'].nunique(), 1),
            'inventory_turnover': d['COGS'].sum() / max(d['COGS'].mean() * 30, 1),
        }
        if 'Marketing Spend' in d.columns and 'New Customer' in d.columns:
            new_cust = d['New Customer'].sum()
            mkt_spend = d['Marketing Spend'].sum()
            kpis[yr]['cac'] = mkt_spend / max(new_cust, 1)

    # YoY growth
    if len(years) >= 2:
        y0, y1 = years[-2], years[-1]
        kpis['yoy_growth'] = (kpis[y1]['total_revenue'] - kpis[y0]['total_revenue']) / \
                              max(kpis[y0]['total_revenue'], 1)

    return kpis, df


def print_kpi_dashboard(kpis: dict, years: list):
    """Print executive KPI summary to console."""
    print("\n" + "═"*65)
    print("  RETAIL BUSINESS INTELLIGENCE — EXECUTIVE KPI DASHBOARD")
    print("  Sahil Mali | MSc BA&C | University of Strathclyde")
    print("═"*65)
    for yr in years:
        k = kpis[yr]
        print(f"\n  📅 {yr}")
        print(f"  {'─'*40}")
        print(f"  💰 Total Revenue      : ${k['total_revenue']:>12,.0f}")
        print(f"  📈 Total Profit       : ${k['total_profit']:>12,.0f}")
        print(f"  📊 Avg Profit Margin  : {k['avg_margin']:>12.1%}")
        print(f"  🛒 Total Orders       : {k['total_orders']:>12,}")
        print(f"  👥 Unique Customers   : {k['total_customers']:>12,}")
        print(f"  🧾 Avg Order Value    : ${k['avg_order_value']:>12,.2f}")
        if 'cac' in k:
            print(f"  🎯 Customer Acq. Cost : ${k['cac']:>12,.2f}")
    if 'yoy_growth' in kpis:
        arrow = '📈' if kpis['yoy_growth'] > 0 else '📉'
        print(f"\n  {arrow} YoY Revenue Growth: {kpis['yoy_growth']:+.1%}")
    print("═"*65)


def plot_executive_dashboard(df: pd.DataFrame, kpis: dict, years: list):
    """Generate the full executive BI dashboard (6 panels)."""
    fig = plt.figure(figsize=(22, 14))
    fig.suptitle('Retail Business Intelligence Dashboard',
                 fontsize=18, fontweight='bold', color=NAVY, y=0.98)
    gs = fig.add_gridspec(3, 3, hspace=0.45, wspace=0.35)

    # ── Panel 1: Monthly Revenue Trend ────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :2])
    monthly = df.groupby('Month')['Sales'].sum().reset_index()
    monthly['idx'] = range(len(monthly))
    ax1.plot(monthly['idx'], monthly['Sales']/1e3, color=NAVY, lw=2.5, marker='o', ms=4)
    ax1.fill_between(monthly['idx'], monthly['Sales']/1e3, alpha=0.12, color=STEEL)
    ax1.set_title('Monthly Revenue Trend ($K)', fontweight='bold', color=NAVY)
    ax1.set_xticks(monthly['idx'][::3])
    ax1.set_xticklabels(monthly['Month'].iloc[::3], rotation=30, ha='right', fontsize=8)
    ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}K'))

    # ── Panel 2: KPI Summary Cards ─────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.axis('off')
    yr  = max(years)
    k   = kpis[yr]
    kpi_data = [
        ('Total Revenue',   f"${k['total_revenue']/1e6:.2f}M", NAVY),
        ('Total Profit',    f"${k['total_profit']/1e3:.0f}K",  GREEN),
        ('Avg Margin',      f"{k['avg_margin']:.1%}",          STEEL),
        ('Avg Order Value', f"${k['avg_order_value']:.0f}",    AMBER),
    ]
    for i, (label, value, color) in enumerate(kpi_data):
        y_pos = 0.85 - i * 0.22
        ax2.text(0.1, y_pos, label, transform=ax2.transAxes,
                 fontsize=9, color='gray', va='center')
        ax2.text(0.1, y_pos - 0.08, value, transform=ax2.transAxes,
                 fontsize=16, fontweight='bold', color=color, va='center')
    ax2.set_title(f'KPI Summary ({yr})', fontweight='bold', color=NAVY)

    # ── Panel 3: Revenue by Region ─────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, :2])
    reg = df.groupby('Region')['Sales'].sum().sort_values(ascending=True)
    colors_r = [RED if v < reg.quantile(0.33) else
                AMBER if v < reg.quantile(0.66) else GREEN for v in reg.values]
    bars = ax3.barh(reg.index, reg.values/1e3, color=colors_r, edgecolor='white')
    ax3.set_title('Revenue by Region ($K)', fontweight='bold', color=NAVY)
    ax3.set_xlabel('Revenue ($K)')
    for bar in bars:
        ax3.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                 f'${bar.get_width():.0f}K', va='center', fontsize=8)
    red_patch   = plt.Rectangle((0,0),1,1, color=RED)
    amber_patch = plt.Rectangle((0,0),1,1, color=AMBER)
    green_patch = plt.Rectangle((0,0),1,1, color=GREEN)
    ax3.legend([green_patch, amber_patch, red_patch],
               ['High', 'Mid', 'Underperforming'], loc='lower right', fontsize=8)

    # ── Panel 4: Category Performance ─────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 2])
    cat = df.groupby('Category').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    cat['Margin'] = cat['Profit'] / cat['Sales']
    x = range(len(cat))
    ax4.bar(x, cat['Sales']/1e3, color=PALETTE[:len(cat)], alpha=0.85)
    ax4_twin = ax4.twinx()
    ax4_twin.plot(x, cat['Margin'], 'D--', color=RED, lw=1.5, ms=6)
    ax4_twin.set_ylabel('Margin %', color=RED)
    ax4_twin.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax4.set_xticks(x)
    ax4.set_xticklabels(cat['Category'], rotation=20, ha='right', fontsize=7)
    ax4.set_title('Category: Revenue & Margin', fontweight='bold', color=NAVY)
    ax4.set_ylabel('Revenue ($K)')

    # ── Panel 5: Quarterly Sales ───────────────────────────────────────────────
    ax5 = fig.add_subplot(gs[2, :2])
    qtr = df.groupby('Quarter')['Sales'].sum().reset_index()
    bar_colors = [GREEN if v > qtr['Sales'].mean() else AMBER for v in qtr['Sales']]
    ax5.bar(range(len(qtr)), qtr['Sales']/1e3, color=bar_colors, edgecolor='white')
    ax5.axhline(qtr['Sales'].mean()/1e3, color=RED, linestyle='--',
                lw=1.5, label=f"Avg: ${qtr['Sales'].mean()/1e3:.0f}K")
    ax5.set_xticks(range(len(qtr)))
    ax5.set_xticklabels(qtr['Quarter'], rotation=30, ha='right', fontsize=8)
    ax5.set_title('Quarterly Revenue ($K)', fontweight='bold', color=NAVY)
    ax5.legend()
    ax5.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.0f}K'))

    # ── Panel 6: Discount vs Profit ────────────────────────────────────────────
    ax6 = fig.add_subplot(gs[2, 2])
    disc_grp = df.groupby('Discount').agg({'Sales':'sum','Profit':'sum'}).reset_index()
    disc_grp['Margin'] = disc_grp['Profit'] / disc_grp['Sales']
    ax6.scatter(disc_grp['Discount'], disc_grp['Margin'],
                s=disc_grp['Sales']/disc_grp['Sales'].max()*400,
                color=NAVY, alpha=0.7, edgecolors=STEEL, linewidth=1)
    ax6.axhline(0, color=RED, linestyle='--', lw=1.2, label='Break-even')
    ax6.set_xlabel('Discount Rate')
    ax6.set_ylabel('Profit Margin')
    ax6.set_title('Discount vs Profit Margin', fontweight='bold', color=NAVY)
    ax6.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax6.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax6.legend(fontsize=8)

    plt.savefig('../reports/bi_dashboard.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("📊 Saved: reports/bi_dashboard.png")


def generate_insight_report(df: pd.DataFrame, kpis: dict, years: list):
    """Print automated insight bullets."""
    yr = max(years)
    k  = kpis[yr]
    top_region     = df.groupby('Region')['Sales'].sum().idxmax()
    bottom_region  = df.groupby('Region')['Sales'].sum().idxmin()
    top_category   = df.groupby('Category')['Profit'].sum().idxmax()
    worst_discount = df[df['Discount'] >= 0.30]['Profit Margin'].mean()

    print("\n💡 AUTOMATED STRATEGIC INSIGHTS:")
    print("─"*60)
    print(f"  1. {top_region} leads all regions in revenue — identify best practices to replicate")
    print(f"  2. {bottom_region} is the weakest region — recommend targeted marketing review")
    print(f"  3. {top_category} drives the highest absolute profit — consider capacity expansion")
    print(f"  4. Discounts ≥30% yield avg margin of {worst_discount:.1%} — pricing strategy review needed")
    if 'yoy_growth' in kpis:
        yoy = kpis['yoy_growth']
        msg = "strong growth" if yoy > 0.10 else "moderate growth" if yoy > 0 else "revenue decline"
        print(f"  5. YoY revenue growth of {yoy:+.1%} indicates {msg} — plan accordingly")
    print("─"*60)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    df_raw = load_or_generate('../data/superstore.csv')
    kpis, df = compute_kpis(df_raw)
    years    = sorted(k for k in kpis if isinstance(k, int))
    print_kpi_dashboard(kpis, years)
    plot_executive_dashboard(df, kpis, years)
    generate_insight_report(df, kpis, years)
