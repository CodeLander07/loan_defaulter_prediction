"""
Maps common user-facing financial ratio names to Polish XGBoost feature columns (5 clean features)
Returns all 64 columns (59 default to 0) for direct model inference.
"""

import re
import pandas as pd

ALL_COLS = [
    'X1_net_profit_total_assets', 'X2_total_liabilities_total_assets',
    'X3_working_capital_total_assets', 'X4_current_assets_short_term_liabilities',
    'X5_cash_short_term_securities_receivables_short_term_liabilities_opex_depreciation_365',
    'X6_retained_earnings_total_assets', 'X7_ebit_total_assets',
    'X8_book_value_equity_total_liabilities', 'X9_sales_total_assets',
    'X10_equity_total_assets', 'X11_gross_profit_extraordinary_items_financial_expenses_total_assets',
    'X12_gross_profit_short_term_liabilities', 'X13_gross_profit_depreciation_sales',
    'X14_gross_profit_interest_total_assets',
    'X15_total_liabilities_365_gross_profit_depreciation',
    'X16_gross_profit_depreciation_total_liabilities',
    'X17_total_assets_total_liabilities', 'X18_gross_profit_total_assets',
    'X19_gross_profit_sales', 'X20_inventory_365_sales',
    'X21_sales_n_sales_n1', 'X22_profit_on_operating_activities_total_assets',
    'X23_net_profit_sales', 'X24_gross_profit_in_3_years_total_assets',
    'X25_equity_share_capital_total_assets',
    'X26_net_profit_depreciation_total_liabilities',
    'X27_profit_on_operating_activities_financial_expenses',
    'X28_working_capital_fixed_assets', 'X29_log_total_assets',
    'X30_total_liabilities_cash_sales', 'X31_gross_profit_interest_sales',
    'X32_current_liabilities_365_cost_of_products_sold',
    'X33_operating_expenses_short_term_liabilities',
    'X34_operating_expenses_total_liabilities',
    'X35_profit_on_sales_total_assets', 'X36_total_sales_total_assets',
    'X37_current_assets_inventories_long_term_liabilities',
    'X38_constant_capital_total_assets', 'X39_profit_on_sales_sales',
    'X40_current_assets_inventory_receivables_short_term_liabilities',
    'X41_total_liabilities_profit_on_operating_activities_depreciation_12_365',
    'X42_profit_on_operating_activities_sales',
    'X43_rotation_receivables_inventory_turnover_in_days',
    'X44_receivables_365_sales', 'X45_net_profit_inventory',
    'X46_current_assets_inventory_short_term_liabilities',
    'X47_inventory_365_cost_of_products_sold',
    'X48_ebitda_profit_on_operating_activities_depreciation_total_assets',
    'X49_ebitda_profit_on_operating_activities_depreciation_sales',
    'X50_current_assets_total_liabilities',
    'X51_short_term_liabilities_total_assets',
    'X52_short_term_liabilities_365_cost_of_products_sold',
    'X53_equity_fixed_assets', 'X54_constant_capital_fixed_assets',
    'X55_working_capital', 'X56_sales_cost_of_products_sold_sales',
    'X57_current_assets_inventory_short_term_liabilities_sales_gross_profit_depreciation',
    'X58_total_costs_total_sales', 'X59_long_term_liabilities_equity',
    'X60_sales_inventory', 'X61_sales_receivables',
    'X62_short_term_liabilities_365_sales', 'X63_sales_short_term_liabilities',
    'X64_sales_fixed_assets',
]

RATIO_MAP = {
    'roa': 'X1_net_profit_total_assets',
    'return_on_assets': 'X1_net_profit_total_assets',
    'current_ratio': 'X4_current_assets_short_term_liabilities',
    'liquidity_ratio': 'X4_current_assets_short_term_liabilities',
    'revenue_growth': ('X21_sales_n_sales_n1', lambda x: 1.0 + x),
    'sales_growth': ('X21_sales_n_sales_n1', lambda x: 1.0 + x),
    'profit_sales': 'X39_profit_on_sales_sales',
    'profit_margin': 'X39_profit_on_sales_sales',
    'operating_margin': 'X42_profit_on_operating_activities_sales',
    'ebit_margin': 'X42_profit_on_operating_activities_sales',
}

EXACT_ALIASES = {
    'roe': 'roa', 'return_on_equity': 'roa', 'net_margin': 'profit_margin',
    'gross_margin': 'profit_margin', 'ebitda_margin': 'operating_margin',
    'debt_to_equity': 'current_ratio', 'debt_ratio': 'current_ratio',
    'asset_turnover': 'revenue_growth', 'inventory_turnover': 'revenue_growth',
    'quick_ratio': 'current_ratio', 'cash_ratio': 'current_ratio',
}


def _normalize_key(key):
    k = key.strip().lower()
    k = re.sub(r'[^a-z0-9_/]', '_', k)
    return re.sub(r'_+', '_', k).strip('_')


def fuzzy_match_key(user_key):
    normalized = _normalize_key(user_key)
    if normalized in RATIO_MAP:
        return normalized
    if normalized in EXACT_ALIASES:
        return EXACT_ALIASES[normalized]
    for alias in RATIO_MAP:
        if alias in normalized or normalized in alias:
            return alias
    return None


def map_ratios(ratios_dict):
    """Map user-provided financial ratios to 64-column Polish feature DataFrame.
    Returns (df with all 64 cols, list of matched feature names)."""
    df = pd.DataFrame({c: [0.0] for c in ALL_COLS})
    matched = []
    for user_key, value in ratios_dict.items():
        if value is None:
            continue
        val = float(value)
        alias = fuzzy_match_key(user_key)
        if alias is None:
            continue
        entry = RATIO_MAP[alias]
        if isinstance(entry, tuple):
            col, transform = entry
            val = transform(val)
        else:
            col = entry
        if col in ALL_COLS:
            df[col] = val
            matched.append(col)
    return df, matched
