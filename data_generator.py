"""
data_generator.py
=================
Generates a realistic retail sales dataset (or loads Kaggle Superstore CSV).
Author: Sahil Mali | MSc Business Analysis & Consulting, Strathclyde
"""

import pandas as pd
import numpy as np
import os


REGIONS     = ['West', 'East', 'Central', 'South', 'North-East',
               'South-West', 'Mountain', 'Pacific', 'Mid-West',
               'South-East', 'New England', 'Great Plains']
CATEGORIES  = ['Technology', 'Office Supplies', 'Furniture', 'Clothing', 'Home & Kitchen']
SEGMENTS    = ['Consumer', 'Corporate', 'Home Office']
SHIP_MODES  = ['Standard Class', 'Second Class', 'First Class', 'Same Day']

PRODUCTS = {
    'Technology':      ['Laptop', 'Monitor', 'Keyboard', 'Mouse', 'Webcam',
                        'Headset', 'Tablet', 'Printer', 'Router', 'USB Hub'],
    'Office Supplies': ['Paper', 'Binder', 'Pen Set', 'Stapler', 'Scissors',
                        'Highlighter', 'Notebook', 'Tape', 'Labels', 'Folders'],
    'Furniture':       ['Chair', 'Desk', 'Bookcase', 'Cabinet', 'Sofa',
                        'Table', 'Shelf', 'Lamp', 'Rug', 'Curtains'],
    'Clothing':        ['T-Shirt', 'Jeans', 'Jacket', 'Shoes', 'Socks',
                        'Cap', 'Belt', 'Gloves', 'Scarf', 'Sweater'],
    'Home & Kitchen':  ['Blender', 'Toaster', 'Coffee Maker', 'Microwave',
                        'Pot Set', 'Knife Set', 'Cutting Board', 'Mixer',
                        'Air Fryer', 'Rice Cooker'],
}

BASE_PRICES = {
    'Technology': (80, 1200), 'Office Supplies': (3, 80),
    'Furniture': (50, 800),   'Clothing': (15, 150),
    'Home & Kitchen': (20, 300),
}
MARGINS = {
    'Technology': 0.28, 'Office Supplies': 0.42,
    'Furniture': 0.35,  'Clothing': 0.48,
    'Home & Kitchen': 0.38,
}


def generate_retail_data(n_orders: int = 9994, seed: int = 42) -> pd.DataFrame:
    """
    Generate a Superstore-like retail dataset.

    Args:
        n_orders: Number of order rows
        seed:     Random seed

    Returns:
        DataFrame with 20 retail columns
    """
    np.random.seed(seed)
    rng = np.random.default_rng(seed)

    categories = np.random.choice(CATEGORIES, n_orders,
                                  p=[0.30, 0.35, 0.18, 0.10, 0.07])
    products   = [np.random.choice(PRODUCTS[c]) for c in categories]

    # Prices based on category
    unit_prices = np.array([
        round(rng.uniform(*BASE_PRICES[c]), 2) for c in categories
    ])
    quantities  = np.random.choice(range(1, 15), n_orders)
    discounts   = np.random.choice([0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50],
                                   n_orders, p=[0.45, 0.15, 0.12, 0.10, 0.08, 0.05, 0.03, 0.02])
    sales       = np.round(unit_prices * quantities * (1 - discounts), 2)
    margins     = np.array([MARGINS[c] for c in categories])

    # Simulate seasonal pattern (Q4 boost)
    dates = pd.date_range('2022-01-01', '2023-12-31', periods=n_orders)
    seasonal = np.where(dates.month.isin([11, 12]), 1.35,
               np.where(dates.month.isin([9, 10]),  1.15, 1.0))
    sales = np.round(sales * seasonal, 2)

    cogs   = np.round(sales * (1 - margins), 2)
    profit = np.round(sales - cogs - (sales * discounts * 0.5), 2)

    # Regional bias (West & East perform better)
    region_weights = [0.14, 0.14, 0.07, 0.09, 0.06,
                      0.09, 0.06, 0.12, 0.08, 0.08, 0.04, 0.03]
    regions = np.random.choice(REGIONS, n_orders, p=region_weights)

    df = pd.DataFrame({
        'Order ID':        [f'CA-{2022 + i//5000}-{100000+i}' for i in range(n_orders)],
        'Order Date':      dates,
        'Ship Date':       dates + pd.to_timedelta(np.random.choice(range(1,8), n_orders), 'd'),
        'Ship Mode':       np.random.choice(SHIP_MODES, n_orders, p=[0.60,0.19,0.15,0.06]),
        'Customer ID':     [f'CG-{10000+i%1500}' for i in range(n_orders)],
        'Customer Name':   [f'Customer_{i%1500:04d}' for i in range(n_orders)],
        'Segment':         np.random.choice(SEGMENTS, n_orders, p=[0.52, 0.30, 0.18]),
        'Region':          regions,
        'Category':        categories,
        'Sub-Category':    products,
        'Product Name':    [f'{p} - Model {chr(65+j%26)}{j%100:02d}' for j, p in enumerate(products)],
        'Quantity':        quantities,
        'Unit Price':      unit_prices,
        'Discount':        discounts,
        'Sales':           sales,
        'COGS':            cogs,
        'Profit':          profit,
        'Profit Margin':   np.round(profit / np.where(sales > 0, sales, 1), 4),
        'Marketing Spend': np.round(sales * np.random.uniform(0.05, 0.15, n_orders), 2),
        'New Customer':    np.random.choice([1, 0], n_orders, p=[0.35, 0.65]),
    })

    print(f"✅ Retail dataset generated: {df.shape}")
    print(f"   Date range: {df['Order Date'].min().date()} to {df['Order Date'].max().date()}")
    print(f"   Total Sales: ${df['Sales'].sum():,.0f}")
    print(f"   Total Profit: ${df['Profit'].sum():,.0f}")
    print(f"   Avg Profit Margin: {df['Profit Margin'].mean():.1%}")
    return df


def load_or_generate(filepath: str = '../data/superstore.csv') -> pd.DataFrame:
    """Load Kaggle Superstore CSV or generate synthetic data."""
    if os.path.exists(filepath):
        print(f"✅ Loading Kaggle Superstore: {filepath}")
        return pd.read_csv(filepath, encoding='latin-1')
    print("ℹ️  Kaggle file not found — generating synthetic retail data...")
    return generate_retail_data()


if __name__ == "__main__":
    df = generate_retail_data()
    df.to_csv('../data/sample_retail_data.csv', index=False)
    print("📁 Saved: data/sample_retail_data.csv")
    print(df.head())
