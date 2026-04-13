"""
summary_stats.py
Wake County Housing Intelligence Dashboard
Prints headline numbers for the project write-up / portfolio README.
Reads from /data/output/ (run transform.py first).
"""

import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "data", "output")
CLEAN_DIR  = os.path.join(SCRIPT_DIR, "..", "data", "clean")


def load_output(name):
    return pd.read_csv(os.path.join(OUTPUT_DIR, name))


def load_clean(name):
    return pd.read_csv(os.path.join(CLEAN_DIR, name))


def section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    section("WAKE COUNTY HOUSING INTELLIGENCE - HEADLINE STATS (2024)")

    # ── 1. Wake County 2024 homeless population (PIT) ─────────────────────
    wake_perf = load_output("wake_coc_performance.csv")
    pit_2024 = wake_perf.loc[wake_perf["year"] == 2024, "pit_total_homeless"]
    if not pit_2024.empty:
        print(f"\n  1. Wake County (NC-506) 2024 homeless population:")
        print(f"     {int(pit_2024.values[0]):,} persons (PIT count)")

    # ── 2. % improvement exit to permanent housing 2015 vs 2024 ──────────
    ph_2015 = wake_perf.loc[wake_perf["year"] == 2015, "exit_permanent_housing_pct"]
    ph_2024 = wake_perf.loc[wake_perf["year"] == 2024, "exit_permanent_housing_pct"]
    if not ph_2015.empty and not ph_2024.empty:
        pct_2015 = ph_2015.values[0]
        pct_2024 = ph_2024.values[0]
        improvement = ((pct_2024 - pct_2015) / pct_2015) * 100
        print(f"\n  2. Exit to permanent housing rate improvement (2015 -> 2024):")
        print(f"     2015: {pct_2015:.1%}  ->  2024: {pct_2024:.1%}")
        print(f"     Improvement: +{improvement:.1f}%")

    # ── 3. Cost burden rate for extremely low income renters, Wake 2024 ───
    afford = load_output("affordability_summary.csv")
    eli_wake_2024 = afford[
        (afford["county"] == "Wake")
        & (afford["income_tier"] == "Extremely Low Income (<=30% AMI)")
        & (afford["year"] == 2024)
        & (afford["tenure"] == "Renter")
    ]
    if not eli_wake_2024.empty:
        cb_rate = eli_wake_2024["avg_cost_burdened_pct"].mean()
        print(f"\n  3. Cost burden rate - Wake County ELI renters (2024):")
        print(f"     {cb_rate:.1%} cost burdened")

    # ── 4. Average shelter utilization rate across all programs ───────────
    inv_util = load_output("inventory_utilization.csv")
    inv_2024 = inv_util[inv_util["year"] == 2024]
    if not inv_2024.empty:
        avg_util = inv_2024["avg_utilization_rate"].mean()
        print(f"\n  4. Average shelter utilization rate (all programs, 2024):")
        print(f"     {avg_util:.1%}")

    # ── 5. Top 3 subpopulations by total homeless count (2024, NC-wide) ──
    pit_trends = load_output("pit_trends.csv")
    pit_2024_sub = (
        pit_trends[pit_trends["year"] == 2024]
        .sort_values("total_homeless", ascending=False)
        .head(3)
    )
    print(f"\n  5. Top 3 subpopulations by total homeless count (NC, 2024):")
    for _, row in pit_2024_sub.iterrows():
        print(f"     {row['subpopulation']:<35} {int(row['total_homeless']):>6,} persons")

    # ── 6. Cost-burdened households in Wake County (all income tiers, 2024)
    wake_burden_2024 = afford[
        (afford["county"] == "Wake")
        & (afford["year"] == 2024)
    ]
    if not wake_burden_2024.empty:
        total_cb = wake_burden_2024["cost_burdened_households"].sum()
        total_hh = wake_burden_2024["total_households"].sum()
        print(f"\n  6. Cost-burdened households in Wake County (2024):")
        print(f"     {int(total_cb):,} cost-burdened out of {int(total_hh):,} total households")
        print(f"     ({total_cb/total_hh:.1%} of all households)")

    # ── Bonus: median home value + rent trends (Wake) ─────────────────────
    wake_afford = afford[
        (afford["county"] == "Wake")
        & (afford["tenure"] == "Renter")
        & (afford["year"].isin([2015, 2024]))
    ].groupby("year").agg(median_rent=("median_gross_rent", "median")).reset_index()
    if len(wake_afford) == 2:
        r2015 = wake_afford.loc[wake_afford["year"] == 2015, "median_rent"].values[0]
        r2024 = wake_afford.loc[wake_afford["year"] == 2024, "median_rent"].values[0]
        rent_change = ((r2024 - r2015) / r2015) * 100
        print(f"\n  Bonus: Wake County median gross rent:")
        print(f"     2015: ${r2015:,.0f}/mo  ->  2024: ${r2024:,.0f}/mo  (+{rent_change:.1f}%)")

    print(f"\n{'=' * 60}\n")
