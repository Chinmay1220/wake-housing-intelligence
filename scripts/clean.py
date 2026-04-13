"""
clean.py
Wake County Housing Intelligence Dashboard
Validates, cleans, and standardises the four raw CSV files.
Outputs clean versions to /data/clean/ and prints a data quality report.
"""

import numpy as np
import pandas as pd
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR  = os.path.join(SCRIPT_DIR, "..", "data", "raw")
CLEAN_DIR = os.path.join(SCRIPT_DIR, "..", "data", "clean")
os.makedirs(CLEAN_DIR, exist_ok=True)

# ── helpers ────────────────────────────────────────────────────────────────
def load(name):
    path = os.path.join(RAW_DIR, name)
    if not os.path.exists(path):
        print(f"  [ERROR] {name} not found at {path}")
        sys.exit(1)
    return pd.read_csv(path)


def report_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def null_report(df, name):
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if nulls.empty:
        print(f"  {name}: no nulls")
    else:
        print(f"  {name}: nulls found:")
        for col, cnt in nulls.items():
            print(f"    {col}: {cnt}")


def clip_col(df, col, lo, hi, label=""):
    before = ((df[col] < lo) | (df[col] > hi)).sum()
    df[col] = df[col].clip(lower=lo, upper=hi)
    if before:
        print(f"  Clipped {before} out-of-range values in {label or col}")
    return df


def standardise_str_cols(df):
    """Strip whitespace and title-case object columns."""
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df


def pct_cols(df, cols):
    """Ensure percentage columns stay in [0, 1]."""
    for col in cols:
        if col in df.columns:
            df = clip_col(df, col, 0.0, 1.0)
    return df


# ══════════════════════════════════════════════════════════════════════════
# 1. SPM METRICS
# ══════════════════════════════════════════════════════════════════════════
def clean_spm():
    df = load("spm_metrics.csv")
    original_rows = len(df)

    # Dtypes
    df["report_year"] = df["report_year"].astype(int)
    df["total_homeless_persons"] = df["total_homeless_persons"].astype(int)
    df["median_income_at_exit"] = df["median_income_at_exit"].astype(int)

    # Standardise strings
    df = standardise_str_cols(df)

    # Null check
    null_report(df, "spm_metrics")

    # Range validation & clipping
    df = clip_col(df, "avg_los_es_sh_days",        1,   730, "avg_los_es_sh_days")
    df = clip_col(df, "avg_los_es_sh_th_days",      1,   900, "avg_los_es_sh_th_days")
    df = clip_col(df, "total_homeless_persons",     0, 50000, "total_homeless_persons")
    df = clip_col(df, "median_income_at_exit",    500, 75000, "median_income_at_exit")
    df = clip_col(df, "avg_nights_in_shelter",      1,   365, "avg_nights_in_shelter")

    pct_columns = [
        "return_6mo_pct", "return_24mo_pct", "employment_income_exit_pct",
        "exit_permanent_housing_pct", "first_time_homeless_pct",
        "successful_ph_placement_pct",
    ]
    df = pct_cols(df, pct_columns)

    # Valid year range
    invalid_year = df[~df["report_year"].between(2015, 2024)]
    if not invalid_year.empty:
        print(f"  Dropping {len(invalid_year)} rows with invalid report_year")
        df = df[df["report_year"].between(2015, 2024)]

    # Valid CoC IDs
    valid_cocs = [f"NC-{i}" for i in range(500, 521)]
    invalid_coc = df[~df["coc_id"].isin(valid_cocs)]
    if not invalid_coc.empty:
        print(f"  Dropping {len(invalid_coc)} rows with invalid coc_id")
        df = df[df["coc_id"].isin(valid_cocs)]

    out = os.path.join(CLEAN_DIR, "spm_metrics.csv")
    df.to_csv(out, index=False)
    print(f"  spm_metrics: {original_rows:,} -> {len(df):,} rows  (clean)")
    return df


# ══════════════════════════════════════════════════════════════════════════
# 2. PIT COUNT
# ══════════════════════════════════════════════════════════════════════════
def clean_pit():
    df = load("pit_count.csv")
    original_rows = len(df)

    df["year"] = df["year"].astype(int)
    df = standardise_str_cols(df)
    null_report(df, "pit_count")

    numeric_non_neg = [
        "total_homeless", "sheltered", "unsheltered",
        "in_emergency_shelter", "in_transitional_housing", "in_safe_haven",
    ]
    for col in numeric_non_neg:
        df = clip_col(df, col, 0, 100000, col)

    df = pct_cols(df, ["sheltered_pct"])

    # Logical consistency: sheltered + unsheltered should equal total_homeless
    df["sheltered"] = df[["sheltered", "total_homeless"]].min(axis=1)
    df["unsheltered"] = df["total_homeless"] - df["sheltered"]

    # ES + TH + SH should not exceed sheltered
    shelter_sum = df["in_emergency_shelter"] + df["in_transitional_housing"] + df["in_safe_haven"]
    over = shelter_sum > df["sheltered"]
    if over.any():
        scale = df.loc[over, "sheltered"] / shelter_sum[over]
        df.loc[over, "in_emergency_shelter"] = (df.loc[over, "in_emergency_shelter"] * scale).astype(int)
        df.loc[over, "in_transitional_housing"] = (df.loc[over, "in_transitional_housing"] * scale).astype(int)
        df.loc[over, "in_safe_haven"] = (df.loc[over, "in_safe_haven"] * scale).astype(int)
        print(f"  Rescaled {over.sum()} rows where ES+TH+SH exceeded sheltered count")

    out = os.path.join(CLEAN_DIR, "pit_count.csv")
    df.to_csv(out, index=False)
    print(f"  pit_count:   {original_rows:,} -> {len(df):,} rows  (clean)")
    return df


# ══════════════════════════════════════════════════════════════════════════
# 3. CHAS AFFORDABILITY
# ══════════════════════════════════════════════════════════════════════════
def clean_chas():
    df = load("chas_affordability.csv")
    original_rows = len(df)

    df["year"] = df["year"].astype(int)
    df["total_households"] = df["total_households"].astype(int)
    df["cost_burdened_households"] = df["cost_burdened_households"].astype(int)
    df["units_affordable_available"] = df["units_affordable_available"].astype(int)
    df["affordability_gap"] = df["affordability_gap"].astype(int)

    df = standardise_str_cols(df)
    null_report(df, "chas_affordability")

    df = clip_col(df, "total_households",          0, 10000,  "total_households")
    df = clip_col(df, "cost_burdened_households",  0, 10000,  "cost_burdened_households")
    df = clip_col(df, "median_gross_rent",         0, 15000,  "median_gross_rent")
    df = clip_col(df, "median_home_value",         0, 5000000,"median_home_value")
    df = clip_col(df, "units_affordable_available",0, 10000,  "units_affordable_available")
    df = clip_col(df, "affordability_gap",         0, 10000,  "affordability_gap")

    df = pct_cols(df, ["cost_burdened_pct", "severely_cost_burdened_pct", "vacancy_rate_pct"])

    # Severely cost burdened cannot exceed cost burdened
    over = df["severely_cost_burdened_pct"] > df["cost_burdened_pct"]
    if over.any():
        df.loc[over, "severely_cost_burdened_pct"] = df.loc[over, "cost_burdened_pct"]
        print(f"  Capped severely_cost_burdened_pct in {over.sum()} rows")

    # Ensure cost_burdened_households <= total_households
    over2 = df["cost_burdened_households"] > df["total_households"]
    if over2.any():
        df.loc[over2, "cost_burdened_households"] = df.loc[over2, "total_households"]
        print(f"  Capped cost_burdened_households in {over2.sum()} rows")

    out = os.path.join(CLEAN_DIR, "chas_affordability.csv")
    df.to_csv(out, index=False)
    print(f"  chas_affordability: {original_rows:,} -> {len(df):,} rows  (clean)")
    return df


# ══════════════════════════════════════════════════════════════════════════
# 4. HOUSING INVENTORY
# ══════════════════════════════════════════════════════════════════════════
def clean_inventory():
    df = load("housing_inventory.csv")
    original_rows = len(df)

    df["year"] = df["year"].astype(int)
    df["hmis_participating"] = df["hmis_participating"].astype(bool)
    df = standardise_str_cols(df)

    null_report(df, "housing_inventory")

    df = clip_col(df, "total_beds",                  0, 2000, "total_beds")
    df = clip_col(df, "occupied_beds",               0, 2000, "occupied_beds")
    df = clip_col(df, "vacant_beds",                 0, 2000, "vacant_beds")
    df = clip_col(df, "avg_length_of_stay_days",     1,  730, "avg_length_of_stay_days")
    df = clip_col(df, "exits_to_permanent_housing",  0, 5000, "exits_to_permanent_housing")
    df = clip_col(df, "exits_to_temporary",          0, 5000, "exits_to_temporary")
    df = clip_col(df, "exits_unknown",               0, 5000, "exits_unknown")

    df = pct_cols(df, ["utilization_rate_pct"])

    # occupied_beds cannot exceed total_beds
    over = df["occupied_beds"] > df["total_beds"]
    if over.any():
        df.loc[over, "occupied_beds"] = df.loc[over, "total_beds"]
        df.loc[over, "vacant_beds"] = 0
        print(f"  Fixed {over.sum()} rows where occupied_beds > total_beds")

    # Dedicated beds cannot exceed total_beds
    for col in ["dedicated_veteran_beds", "dedicated_youth_beds", "dedicated_dv_beds"]:
        over = df[col] > df["total_beds"]
        if over.any():
            df.loc[over, col] = df.loc[over, "total_beds"]
            print(f"  Capped {col} in {over.sum()} rows")

    out = os.path.join(CLEAN_DIR, "housing_inventory.csv")
    df.to_csv(out, index=False)
    print(f"  housing_inventory: {original_rows:,} -> {len(df):,} rows  (clean)")
    return df


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    report_section("DATA QUALITY REPORT - Wake County Housing Intelligence")

    print("\n[1/4] spm_metrics")
    spm = clean_spm()

    print("\n[2/4] pit_count")
    pit = clean_pit()

    print("\n[3/4] chas_affordability")
    chas = clean_chas()

    print("\n[4/4] housing_inventory")
    inv = clean_inventory()

    report_section("SUMMARY")
    for name, df in [("spm_metrics", spm), ("pit_count", pit),
                     ("chas_affordability", chas), ("housing_inventory", inv)]:
        nulls = df.isnull().sum().sum()
        print(f"  {name:<25} {len(df):>8,} rows   {df.shape[1]:>3} cols   nulls: {nulls}")

    print(f"\nClean files written to: {os.path.abspath(CLEAN_DIR)}\n")
