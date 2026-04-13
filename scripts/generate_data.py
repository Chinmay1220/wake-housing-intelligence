"""
generate_data.py
Wake County Housing Intelligence Dashboard
Generates mock HUD/Census-style datasets for portfolio demonstration.
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

# ── paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# ── shared dimensions ──────────────────────────────────────────────────────
YEARS = list(range(2015, 2025))

COC_MAP = {
    "NC-500": "Asheville/Buncombe County CoC",
    "NC-501": "Greensboro/High Point CoC",
    "NC-502": "Durham City & County CoC",
    "NC-503": "Charlotte/Mecklenburg County CoC",
    "NC-504": "Fayetteville/Cumberland County CoC",
    "NC-505": "Winston-Salem/Forsyth County CoC",
    "NC-506": "Raleigh/Wake County CoC",
    "NC-507": "Gastonia/Cleveland/Gaston/Lincoln Counties CoC",
    "NC-508": "Shelby/Cleveland County CoC",
    "NC-509": "Onslow County CoC",
    "NC-510": "Wilmington/Brunswick/New Hanover/Pender Counties CoC",
    "NC-511": "Catawba County CoC",
    "NC-512": "Cabarrus County CoC",
    "NC-513": "Chapel Hill/Orange County CoC",
    "NC-514": "Boone/Watauga County CoC",
    "NC-515": "Greenville/Pitt County CoC",
    "NC-516": "Burlington/Alamance County CoC",
    "NC-517": "Rocky Mount/Wilson/Edgecombe/Wilson Counties CoC",
    "NC-518": "Goldsboro/Wayne County CoC",
    "NC-519": "Hickory/Catawba County CoC",
    "NC-520": "Sanford/Lee/Harnett Counties CoC",
}
COC_IDS = list(COC_MAP.keys())

# ── helper: year trend factor (0=2015, 1=2024) ────────────────────────────
def trend(year, start=2015, end=2024):
    return (year - start) / (end - start)


# ══════════════════════════════════════════════════════════════════════════
# 1. SPM METRICS
# ══════════════════════════════════════════════════════════════════════════
def generate_spm():
    RACE_ETH = [
        "White, Non-Hispanic",
        "Black/African American",
        "Hispanic/Latino",
        "Asian or Pacific Islander",
        "American Indian/Alaska Native",
        "Multiple Races",
        "Unknown/Other",
    ]
    AGE_GROUPS = [
        "Under 18",
        "18-24",
        "25-34",
        "35-44",
        "45-54",
        "55-61",
        "62+",
    ]

    rows = []
    for coc_id, coc_name in COC_MAP.items():
        is_wake = coc_id == "NC-506"
        # CoC-level base performance — Wake is ~15% better than state avg
        perf_boost = 0.15 if is_wake else np.random.uniform(-0.10, 0.10)

        for year in YEARS:
            t = trend(year)  # 0->1 improvement factor

            # Total population for this CoC
            base_pop = int(np.random.uniform(150, 2500))
            if is_wake:
                base_pop = int(np.random.uniform(800, 1400))

            breakdowns = (
                [("Total", "Total")]
                + [("Race/Ethnicity", r) for r in RACE_ETH]
                + [("Age Group", a) for a in AGE_GROUPS]
            )

            for btype, bval in breakdowns:
                # sub-pop share of total
                if btype == "Total":
                    pop = base_pop
                elif btype == "Race/Ethnicity":
                    shares = np.random.dirichlet(np.ones(len(RACE_ETH)) * 2)
                    pop = max(1, int(base_pop * shares[RACE_ETH.index(bval)]))
                else:
                    shares = np.random.dirichlet(np.ones(len(AGE_GROUPS)) * 2)
                    pop = max(1, int(base_pop * shares[AGE_GROUPS.index(bval)]))

                # Metrics trend upward (improvement) over time
                avg_los_es_sh = round(
                    max(10, np.random.normal(90 - 30 * t - 20 * perf_boost, 8)), 1
                )
                avg_los_th = round(avg_los_es_sh + np.random.uniform(20, 60), 1)
                return_6mo = round(
                    np.clip(
                        np.random.normal(0.08 - 0.03 * t - 0.02 * perf_boost, 0.015),
                        0.01, 0.25,
                    ),
                    4,
                )
                return_24mo = round(
                    np.clip(
                        np.random.normal(0.18 - 0.05 * t - 0.03 * perf_boost, 0.02),
                        0.03, 0.40,
                    ),
                    4,
                )
                emp_income_exit = round(
                    np.clip(
                        np.random.normal(0.22 + 0.12 * t + 0.05 * perf_boost, 0.03),
                        0.05, 0.60,
                    ),
                    4,
                )
                exit_ph = round(
                    np.clip(
                        np.random.normal(0.38 + 0.18 * t + 0.08 * perf_boost, 0.04),
                        0.10, 0.85,
                    ),
                    4,
                )
                first_time = round(
                    np.clip(
                        np.random.normal(0.55 + 0.10 * t + 0.04 * perf_boost, 0.04),
                        0.20, 0.90,
                    ),
                    4,
                )
                succ_ph = round(
                    np.clip(
                        np.random.normal(0.60 + 0.15 * t + 0.05 * perf_boost, 0.04),
                        0.20, 0.95,
                    ),
                    4,
                )
                med_income_exit = int(
                    np.clip(
                        np.random.normal(
                            8500 + 4000 * t + 1500 * perf_boost,
                            800,
                        ),
                        3000, 30000,
                    )
                )
                avg_nights = round(
                    np.clip(
                        np.random.normal(55 - 20 * t - 10 * perf_boost, 6),
                        5, 180,
                    ),
                    1,
                )

                rows.append(
                    {
                        "coc_id": coc_id,
                        "coc_name": coc_name,
                        "report_year": year,
                        "breakdown_type": btype,
                        "breakdown_value": bval,
                        "avg_los_es_sh_days": avg_los_es_sh,
                        "avg_los_es_sh_th_days": avg_los_th,
                        "return_6mo_pct": return_6mo,
                        "return_24mo_pct": return_24mo,
                        "total_homeless_persons": pop,
                        "employment_income_exit_pct": emp_income_exit,
                        "exit_permanent_housing_pct": exit_ph,
                        "first_time_homeless_pct": first_time,
                        "successful_ph_placement_pct": succ_ph,
                        "median_income_at_exit": med_income_exit,
                        "avg_nights_in_shelter": avg_nights,
                    }
                )

    df = pd.DataFrame(rows)
    out = os.path.join(RAW_DIR, "spm_metrics.csv")
    df.to_csv(out, index=False)
    size_kb = os.path.getsize(out) / 1024
    print(f"  spm_metrics.csv       -> {len(df):>7,} rows  {size_kb:>8,.1f} KB")
    return df


# ══════════════════════════════════════════════════════════════════════════
# 2. PIT COUNT
# ══════════════════════════════════════════════════════════════════════════
def generate_pit():
    SUBPOPS = [
        "Veterans",
        "Chronically Homeless",
        "Families with Children",
        "Unaccompanied Youth",
        "Fleeing Domestic Violence",
        "Adults Only",
        "Persons with Disabilities",
        "Seniors 62+",
    ]
    GENDERS = ["Male", "Female", "Transgender", "Gender Non-Conforming", "Unknown"]

    rows = []
    for coc_id, coc_name in COC_MAP.items():
        is_wake = coc_id == "NC-506"

        for year in YEARS:
            t = trend(year)
            base_total = (
                int(np.random.uniform(700, 1200))
                if is_wake
                else int(np.random.uniform(80, 2200))
            )

            sub_shares = np.random.dirichlet(
                np.array([0.10, 0.12, 0.18, 0.08, 0.07, 0.25, 0.13, 0.07]) * 5
            )

            for si, subpop in enumerate(SUBPOPS):
                sub_total = max(1, int(base_total * sub_shares[si]))
                # slight downward trend in homelessness
                sub_total = max(1, int(sub_total * (1 - 0.02 * t)))

                gender_shares = np.random.dirichlet([4, 3, 0.2, 0.15, 0.5])

                for gi, gender in enumerate(GENDERS):
                    total = max(0, int(sub_total * gender_shares[gi]))
                    sheltered = int(total * np.clip(np.random.normal(0.68 + 0.10 * t, 0.06), 0.30, 0.98))
                    unsheltered = total - sheltered
                    sheltered_pct = round(sheltered / total, 4) if total > 0 else 0.0

                    es_share = np.random.uniform(0.45, 0.70)
                    in_es = int(sheltered * es_share)
                    in_th = int(sheltered * np.random.uniform(0.15, 0.35))
                    in_sh = sheltered - in_es - in_th
                    in_sh = max(0, in_sh)

                    rows.append(
                        {
                            "coc_id": coc_id,
                            "coc_name": coc_name,
                            "year": year,
                            "subpopulation": subpop,
                            "gender": gender,
                            "total_homeless": total,
                            "sheltered": sheltered,
                            "unsheltered": unsheltered,
                            "sheltered_pct": sheltered_pct,
                            "in_emergency_shelter": in_es,
                            "in_transitional_housing": in_th,
                            "in_safe_haven": in_sh,
                        }
                    )

    df = pd.DataFrame(rows)
    out = os.path.join(RAW_DIR, "pit_count.csv")
    df.to_csv(out, index=False)
    size_kb = os.path.getsize(out) / 1024
    print(f"  pit_count.csv         -> {len(df):>7,} rows  {size_kb:>8,.1f} KB")
    return df


# ══════════════════════════════════════════════════════════════════════════
# 3. CHAS AFFORDABILITY
# ══════════════════════════════════════════════════════════════════════════
def generate_chas():
    COUNTIES = {
        "Wake":     {"base_rent": 1350, "base_value": 320000, "growth": 0.065},
        "Durham":   {"base_rent": 1100, "base_value": 270000, "growth": 0.055},
        "Orange":   {"base_rent": 1050, "base_value": 290000, "growth": 0.050},
        "Johnston": {"base_rent":  850, "base_value": 210000, "growth": 0.045},
        "Franklin": {"base_rent":  780, "base_value": 190000, "growth": 0.040},
        "Chatham":  {"base_rent":  900, "base_value": 240000, "growth": 0.048},
        "Harnett":  {"base_rent":  780, "base_value": 185000, "growth": 0.038},
        "Nash":     {"base_rent":  720, "base_value": 160000, "growth": 0.035},
    }
    TENURE = ["Renter", "Owner"]
    INCOME_TIERS = [
        "Extremely Low Income (<=30% AMI)",
        "Very Low Income (31-50% AMI)",
        "Low Income (51-80% AMI)",
        "Moderate Income (81-120% AMI)",
        "Middle/Upper Income (>120% AMI)",
    ]
    # Base cost burden rates by income tier
    CB_BASE = {
        "Extremely Low Income (<=30% AMI)":   0.675,
        "Very Low Income (31-50% AMI)":        0.510,
        "Low Income (51-80% AMI)":             0.340,
        "Moderate Income (81-120% AMI)":       0.180,
        "Middle/Upper Income (>120% AMI)":     0.065,
    }
    SCB_RATIO = {  # severely cost burdened as share of cost burdened
        "Extremely Low Income (<=30% AMI)":   0.72,
        "Very Low Income (31-50% AMI)":        0.48,
        "Low Income (51-80% AMI)":             0.28,
        "Moderate Income (81-120% AMI)":       0.12,
        "Middle/Upper Income (>120% AMI)":     0.04,
    }

    rows = []
    tract_counter = {c: 1 for c in COUNTIES}

    for county, params in COUNTIES.items():
        n_tracts = 150
        tract_ids = [f"{county[:3].upper()}{str(i).zfill(4)}" for i in range(1, n_tracts + 1)]

        for tract in tract_ids:
            for year in YEARS:
                t = trend(year)
                g = params["growth"]
                rent = int(params["base_rent"] * (1 + g) ** (year - 2015) * np.random.uniform(0.88, 1.12))
                value = int(params["base_value"] * (1 + g) ** (year - 2015) * np.random.uniform(0.85, 1.15))
                vacancy = round(np.clip(np.random.normal(0.055 - 0.008 * t, 0.015), 0.01, 0.18), 4)

                for tenure in TENURE:
                    for tier in INCOME_TIERS:
                        hh_base = int(np.random.uniform(40, 350))
                        cb_rate = np.clip(
                            CB_BASE[tier] + np.random.normal(0, 0.03)
                            + (0.02 * t if tier.startswith("Extremely") else 0),
                            0.01, 0.97,
                        )
                        scb_rate = round(
                            np.clip(cb_rate * SCB_RATIO[tier] + np.random.normal(0, 0.02), 0.01, cb_rate),
                            4,
                        )
                        cb_rate = round(cb_rate, 4)
                        cb_hh = int(hh_base * cb_rate)

                        # affordable units: scarcer at low income tiers, declining over time
                        units_affordable = max(
                            0,
                            int(
                                hh_base
                                * np.clip(
                                    0.40 - 0.15 * CB_BASE[tier] - 0.05 * t + np.random.normal(0, 0.05),
                                    0, 1,
                                )
                            ),
                        )
                        gap = max(0, cb_hh - units_affordable)

                        rows.append(
                            {
                                "census_tract": tract,
                                "county": county,
                                "state": "NC",
                                "year": year,
                                "tenure": tenure,
                                "income_tier": tier,
                                "total_households": hh_base,
                                "cost_burdened_pct": cb_rate,
                                "cost_burdened_households": cb_hh,
                                "severely_cost_burdened_pct": scb_rate,
                                "median_gross_rent": rent if tenure == "Renter" else 0,
                                "median_home_value": value if tenure == "Owner" else 0,
                                "vacancy_rate_pct": vacancy,
                                "units_affordable_available": units_affordable,
                                "affordability_gap": gap,
                            }
                        )

    df = pd.DataFrame(rows)
    out = os.path.join(RAW_DIR, "chas_affordability.csv")
    df.to_csv(out, index=False)
    size_kb = os.path.getsize(out) / 1024
    print(f"  chas_affordability.csv -> {len(df):>7,} rows  {size_kb:>8,.1f} KB")
    return df


# ══════════════════════════════════════════════════════════════════════════
# 4. HOUSING INVENTORY
# ══════════════════════════════════════════════════════════════════════════
def generate_inventory():
    PROGRAM_TYPES = [
        "Emergency Shelter",
        "Transitional Housing",
        "Permanent Supportive Housing",
        "Rapid Rehousing",
        "Safe Haven",
        "Prevention/Diversion",
    ]
    FUNDING_SOURCES = ["ESG", "CoC Program", "HOME", "HOPWA", "Local", "State"]

    rows = []
    for coc_id, coc_name in COC_MAP.items():
        is_wake = coc_id == "NC-506"

        for year in YEARS:
            t = trend(year)
            # 3 providers per program type
            for ptype in PROGRAM_TYPES:
                for pid in range(1, 4):
                    provider_id = f"{coc_id}-{ptype[:2].upper()}-P{pid}"

                    base_beds = int(
                        np.random.uniform(20, 180) if is_wake
                        else np.random.uniform(10, 120)
                    )
                    # beds grow over time (PSH, RRH expand)
                    if ptype in ("Permanent Supportive Housing", "Rapid Rehousing"):
                        base_beds = int(base_beds * (1 + 0.04 * t))

                    util_rate = round(
                        np.clip(np.random.normal(0.78 + 0.08 * t, 0.07), 0.40, 1.00), 4
                    )
                    occupied = int(base_beds * util_rate)
                    vacant = base_beds - occupied

                    vet_beds = int(base_beds * np.random.uniform(0.05, 0.20))
                    youth_beds = int(base_beds * np.random.uniform(0.03, 0.15))
                    dv_beds = int(base_beds * np.random.uniform(0.03, 0.12))

                    exits_total = int(occupied * np.random.uniform(0.55, 0.90))
                    exits_ph = int(exits_total * np.clip(np.random.normal(0.42 + 0.15 * t, 0.06), 0.15, 0.85))
                    exits_tmp = int(exits_total * np.random.uniform(0.10, 0.25))
                    exits_unk = exits_total - exits_ph - exits_tmp

                    avg_los = round(
                        np.clip(np.random.normal(75 - 25 * t, 15), 7, 365), 1
                    )

                    rows.append(
                        {
                            "coc_id": coc_id,
                            "coc_name": coc_name,
                            "year": year,
                            "program_type": ptype,
                            "provider_id": provider_id,
                            "total_beds": base_beds,
                            "occupied_beds": occupied,
                            "vacant_beds": vacant,
                            "utilization_rate_pct": util_rate,
                            "dedicated_veteran_beds": vet_beds,
                            "dedicated_youth_beds": youth_beds,
                            "dedicated_dv_beds": dv_beds,
                            "hmis_participating": np.random.choice([True, True, True, False]),
                            "funding_source": np.random.choice(FUNDING_SOURCES),
                            "avg_length_of_stay_days": avg_los,
                            "exits_to_permanent_housing": exits_ph,
                            "exits_to_temporary": exits_tmp,
                            "exits_unknown": max(0, exits_unk),
                        }
                    )

    df = pd.DataFrame(rows)
    out = os.path.join(RAW_DIR, "housing_inventory.csv")
    df.to_csv(out, index=False)
    size_kb = os.path.getsize(out) / 1024
    print(f"  housing_inventory.csv  -> {len(df):>7,} rows  {size_kb:>8,.1f} KB")
    return df


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\nGenerating Wake County Housing Intelligence mock datasets...\n")

    spm = generate_spm()
    pit = generate_pit()
    chas = generate_chas()
    inv = generate_inventory()

    total = len(spm) + len(pit) + len(chas) + len(inv)
    print(f"\n  {'-' * 45}")
    print(f"  Total rows generated:    {total:>10,}")
    print(f"\nAll files written to: {os.path.abspath(RAW_DIR)}\n")
