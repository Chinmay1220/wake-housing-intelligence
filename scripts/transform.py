"""
transform.py
Wake County Housing Intelligence Dashboard
Builds analytical / Power BI-ready tables from clean CSV files.
Outputs to /data/output/.
"""

import pandas as pd
import os

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CLEAN_DIR   = os.path.join(SCRIPT_DIR, "..", "data", "clean")
OUTPUT_DIR  = os.path.join(SCRIPT_DIR, "..", "data", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load(name):
    return pd.read_csv(os.path.join(CLEAN_DIR, name))


def save(df, name):
    out = os.path.join(OUTPUT_DIR, name)
    df.to_csv(out, index=False)
    kb = os.path.getsize(out) / 1024
    print(f"  {name:<40} {len(df):>8,} rows   {kb:>8,.1f} KB")
    return df


# ══════════════════════════════════════════════════════════════════════════
# 1. wake_coc_performance.csv
#    NC-506 only, all years, all metrics — primary dashboard table
# ══════════════════════════════════════════════════════════════════════════
def build_wake_performance(spm, pit, inv):
    # SPM: NC-506, Total breakdown only
    wake_spm = (
        spm[(spm["coc_id"] == "NC-506") & (spm["breakdown_type"] == "Total")]
        .drop(columns=["breakdown_type", "breakdown_value"])
        .copy()
    )

    # PIT: NC-506, aggregate across subpopulations and genders
    wake_pit = (
        pit[pit["coc_id"] == "NC-506"]
        .groupby(["coc_id", "year"], as_index=False)
        .agg(
            pit_total_homeless=("total_homeless", "sum"),
            pit_sheltered=("sheltered", "sum"),
            pit_unsheltered=("unsheltered", "sum"),
            pit_in_es=("in_emergency_shelter", "sum"),
            pit_in_th=("in_transitional_housing", "sum"),
        )
    )
    wake_pit["pit_sheltered_pct"] = (
        wake_pit["pit_sheltered"] / wake_pit["pit_total_homeless"].replace(0, pd.NA)
    ).round(4)

    # Inventory: NC-506, aggregate utilisation
    wake_inv = (
        inv[inv["coc_id"] == "NC-506"]
        .groupby(["coc_id", "year"], as_index=False)
        .agg(
            total_beds=("total_beds", "sum"),
            occupied_beds=("occupied_beds", "sum"),
            exits_ph=("exits_to_permanent_housing", "sum"),
            exits_tmp=("exits_to_temporary", "sum"),
        )
    )
    wake_inv["inv_util_rate"] = (
        wake_inv["occupied_beds"] / wake_inv["total_beds"].replace(0, pd.NA)
    ).round(4)

    # Merge on coc_id + year (spm uses report_year)
    wake_spm = wake_spm.rename(columns={"report_year": "year"})
    df = (
        wake_spm
        .merge(wake_pit.drop(columns="coc_id"), on="year", how="left")
        .merge(wake_inv.drop(columns="coc_id"), on="year", how="left")
    )
    df = df.sort_values("year").reset_index(drop=True)
    return save(df, "wake_coc_performance.csv")


# ══════════════════════════════════════════════════════════════════════════
# 2. nc_coc_comparison.csv
#    All CoCs, all years — aggregated for benchmarking
# ══════════════════════════════════════════════════════════════════════════
def build_nc_comparison(spm, pit, inv):
    spm_agg = (
        spm[spm["breakdown_type"] == "Total"]
        .rename(columns={"report_year": "year"})
        .groupby(["coc_id", "coc_name", "year"], as_index=False)
        .agg(
            avg_los_es_sh=("avg_los_es_sh_days", "mean"),
            return_24mo_pct=("return_24mo_pct", "mean"),
            exit_ph_pct=("exit_permanent_housing_pct", "mean"),
            total_homeless=("total_homeless_persons", "sum"),
            emp_income_exit_pct=("employment_income_exit_pct", "mean"),
            succ_ph_pct=("successful_ph_placement_pct", "mean"),
            median_income_at_exit=("median_income_at_exit", "median"),
        )
        .round(4)
    )

    pit_agg = (
        pit.groupby(["coc_id", "year"], as_index=False)
        .agg(
            pit_total=("total_homeless", "sum"),
            pit_sheltered=("sheltered", "sum"),
            pit_unsheltered=("unsheltered", "sum"),
        )
    )
    pit_agg["sheltered_pct"] = (
        pit_agg["pit_sheltered"] / pit_agg["pit_total"].replace(0, pd.NA)
    ).round(4)

    inv_agg = (
        inv.groupby(["coc_id", "year"], as_index=False)
        .agg(
            total_beds=("total_beds", "sum"),
            occupied_beds=("occupied_beds", "sum"),
            exits_ph=("exits_to_permanent_housing", "sum"),
        )
    )
    inv_agg["utilization_rate"] = (
        inv_agg["occupied_beds"] / inv_agg["total_beds"].replace(0, pd.NA)
    ).round(4)

    df = (
        spm_agg
        .merge(pit_agg.drop(columns=[], errors="ignore"), on=["coc_id", "year"], how="left")
        .merge(inv_agg.drop(columns=[], errors="ignore"), on=["coc_id", "year"], how="left")
    )
    df["is_wake_county"] = df["coc_id"] == "NC-506"
    df = df.sort_values(["year", "coc_id"]).reset_index(drop=True)
    return save(df, "nc_coc_comparison.csv")


# ══════════════════════════════════════════════════════════════════════════
# 3. affordability_summary.csv
#    Cost burden aggregated by county + income tier + year
# ══════════════════════════════════════════════════════════════════════════
def build_affordability_summary(chas):
    df = (
        chas.groupby(["county", "income_tier", "year", "tenure"], as_index=False)
        .agg(
            total_households=("total_households", "sum"),
            cost_burdened_households=("cost_burdened_households", "sum"),
            avg_cost_burdened_pct=("cost_burdened_pct", "mean"),
            avg_severely_cb_pct=("severely_cost_burdened_pct", "mean"),
            median_gross_rent=("median_gross_rent", lambda x: x[x > 0].median() if (x > 0).any() else 0),
            median_home_value=("median_home_value", lambda x: x[x > 0].median() if (x > 0).any() else 0),
            avg_vacancy_rate=("vacancy_rate_pct", "mean"),
            total_affordable_units=("units_affordable_available", "sum"),
            total_affordability_gap=("affordability_gap", "sum"),
        )
    )
    df["cost_burden_rate_calc"] = (
        df["cost_burdened_households"] / df["total_households"].replace(0, pd.NA)
    ).round(4)
    df["avg_cost_burdened_pct"] = df["avg_cost_burdened_pct"].round(4)
    df["avg_severely_cb_pct"] = df["avg_severely_cb_pct"].round(4)
    df["avg_vacancy_rate"] = df["avg_vacancy_rate"].round(4)
    df = df.sort_values(["county", "year", "income_tier"]).reset_index(drop=True)
    return save(df, "affordability_summary.csv")


# ══════════════════════════════════════════════════════════════════════════
# 4. inventory_utilization.csv
#    Utilization and exits by program type and year (all CoCs)
# ══════════════════════════════════════════════════════════════════════════
def build_inventory_utilization(inv):
    df = (
        inv.groupby(["program_type", "year"], as_index=False)
        .agg(
            total_beds=("total_beds", "sum"),
            occupied_beds=("occupied_beds", "sum"),
            vacant_beds=("vacant_beds", "sum"),
            avg_utilization_rate=("utilization_rate_pct", "mean"),
            exits_to_permanent_housing=("exits_to_permanent_housing", "sum"),
            exits_to_temporary=("exits_to_temporary", "sum"),
            exits_unknown=("exits_unknown", "sum"),
            avg_los_days=("avg_length_of_stay_days", "mean"),
            dedicated_vet_beds=("dedicated_veteran_beds", "sum"),
            dedicated_youth_beds=("dedicated_youth_beds", "sum"),
            dedicated_dv_beds=("dedicated_dv_beds", "sum"),
            hmis_programs=("hmis_participating", "sum"),
        )
    )
    total_exits = (
        df["exits_to_permanent_housing"]
        + df["exits_to_temporary"]
        + df["exits_unknown"]
    )
    df["exits_ph_rate"] = (
        df["exits_to_permanent_housing"] / total_exits.replace(0, pd.NA)
    ).round(4)
    df["avg_utilization_rate"] = df["avg_utilization_rate"].round(4)
    df["avg_los_days"] = df["avg_los_days"].round(1)
    df = df.sort_values(["program_type", "year"]).reset_index(drop=True)
    return save(df, "inventory_utilization.csv")


# ══════════════════════════════════════════════════════════════════════════
# 5. pit_trends.csv
#    YoY homeless population by subpopulation (all CoCs)
# ══════════════════════════════════════════════════════════════════════════
def build_pit_trends(pit):
    df = (
        pit.groupby(["year", "subpopulation"], as_index=False)
        .agg(
            total_homeless=("total_homeless", "sum"),
            sheltered=("sheltered", "sum"),
            unsheltered=("unsheltered", "sum"),
            in_emergency_shelter=("in_emergency_shelter", "sum"),
            in_transitional_housing=("in_transitional_housing", "sum"),
        )
    )
    df["sheltered_pct"] = (
        df["sheltered"] / df["total_homeless"].replace(0, pd.NA)
    ).round(4)

    # Year-over-year change
    df = df.sort_values(["subpopulation", "year"]).reset_index(drop=True)
    df["yoy_change"] = df.groupby("subpopulation")["total_homeless"].diff()
    df["yoy_pct_change"] = (
        df["yoy_change"] / df.groupby("subpopulation")["total_homeless"].shift(1)
    ).round(4)

    # Wake County breakdown
    wake_pit = (
        pit[pit["coc_id"] == "NC-506"]
        .groupby(["year", "subpopulation"], as_index=False)
        .agg(wake_total_homeless=("total_homeless", "sum"))
    )
    df = df.merge(wake_pit, on=["year", "subpopulation"], how="left")
    df["wake_share_of_nc"] = (
        df["wake_total_homeless"] / df["total_homeless"].replace(0, pd.NA)
    ).round(4)

    df = df.sort_values(["subpopulation", "year"]).reset_index(drop=True)
    return save(df, "pit_trends.csv")


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\nLoading clean data...")
    spm  = load("spm_metrics.csv")
    pit  = load("pit_count.csv")
    chas = load("chas_affordability.csv")
    inv  = load("housing_inventory.csv")

    print("\nBuilding analytical tables...\n")
    build_wake_performance(spm, pit, inv)
    build_nc_comparison(spm, pit, inv)
    build_affordability_summary(chas)
    build_inventory_utilization(inv)
    build_pit_trends(pit)

    print(f"\nAll output files written to: {os.path.abspath(OUTPUT_DIR)}\n")
