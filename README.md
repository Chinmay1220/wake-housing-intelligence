# Wake County Housing Intelligence Dashboard

A portfolio project demonstrating end-to-end data pipeline skills for housing and homelessness analytics, built to mirror the data environment at Wake County's Department of Housing Affordability and Community Revitalization (HACR).

## Project Structure

```
wake-housing-intelligence/
├── data/
│   ├── raw/          # Generated mock HUD/Census-style CSVs
│   ├── clean/        # Validated and standardised datasets
│   └── output/       # Analytical tables ready for Power BI
├── scripts/
│   ├── generate_data.py   # Step 1: Creates 135,000+ row mock dataset
│   ├── clean.py           # Step 2: Validates, clips, standardises
│   ├── transform.py       # Step 3: Builds Power BI-ready analytical tables
│   └── summary_stats.py   # Step 4: Prints headline portfolio numbers
└── requirements.txt
```

## Datasets

| File | Rows | Description |
|---|---|---|
| `spm_metrics.csv` | ~3,150 | HUD System Performance Measures — 20 NC CoCs, 2015–2024, by race/ethnicity and age |
| `pit_count.csv` | ~8,400 | Point-in-Time Count — 8 subpopulations × 5 genders × 20 CoCs × 10 years |
| `chas_affordability.csv` | ~120,000 | CHAS Housing Cost Burden — 8 NC counties, 150 tracts each, 5 income tiers |
| `housing_inventory.csv` | ~3,780 | HIC Housing Inventory — 6 program types × 3 providers × 20 CoCs × 10 years |

## Output Tables (Power BI Ready)

| File | Purpose |
|---|---|
| `wake_coc_performance.csv` | NC-506 dashboard — all KPIs, all years |
| `nc_coc_comparison.csv` | Benchmarking Wake vs. all 20 NC CoCs |
| `affordability_summary.csv` | Cost burden by county + income tier + year |
| `inventory_utilization.csv` | Program utilization and exit outcomes |
| `pit_trends.csv` | YoY homeless population by subpopulation |

## Quick Start

```bash
pip install -r requirements.txt
python scripts/generate_data.py   # ~135,000 rows into data/raw/
python scripts/clean.py           # Validate + clean into data/clean/
python scripts/transform.py       # Build analytical tables into data/output/
python scripts/summary_stats.py   # Print headline portfolio numbers
```

## Key Metrics (2024)

- NC-506 (Raleigh/Wake County) consistently outperforms state CoC average on exit-to-permanent-housing rates
- Extremely Low Income renters in Wake County face ~67% cost burden rate
- Wake County median gross rent increased ~86% from 2015 to 2024
- Shelter utilization across all programs averages ~85%+

## Relevance to HACR Role

- **HUD SPM Reporting**: `spm_metrics.csv` mirrors Measures 1–7 used in CAPER and ESG reporting
- **PIT Count Analysis**: `pit_count.csv` follows HUD CoC Program Notice CPD-14-012 structure
- **CHAS Affordability**: Mirrors HUD Comprehensive Housing Affordability Strategy data used in ConPlan/Analysis of Impediments
- **Power BI**: All output tables are flat, Star-schema-friendly CSVs optimised for DirectQuery or import mode
