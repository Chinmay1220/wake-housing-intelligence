# Wake County Housing Intelligence Dashboard

An end-to-end data project that tracks housing affordability and homelessness across North Carolina — with a focus on Wake County (Raleigh). Built to mirror the data environment at Wake County's Department of Housing Affordability and Community Revitalization (HACR).

Live application - https://wake-housing-intelligence-gfgyydu7fh4kpyg8ghxsbd.streamlit.app/

## What This Project Does

1. **Processes 135,000+ rows** of HUD and Census-style housing and homelessness data
2. **Cleans and validates the data** — standardises formats, clips outliers, flags anomalies
3. **Transforms it into dashboard-ready tables** — flat CSVs optimised for analysis
4. **Visualises everything in an interactive dashboard** — built with Python and Streamlit

## Dashboard Pages

| Page | What You'll See |
|---|---|
| **Wake County Overview** | Key outcomes for Raleigh's homeless system: housing rate, return rate, shelter occupancy |
| **Compare All NC Regions** | How Wake County stacks up against all 20 NC regional homeless systems |
| **Housing Affordability** | How many households are spending too much on rent or a mortgage, by income level |
| **Shelter Capacity & Exits** | How full shelters are, and where people go when they leave |
| **Annual Homeless Count** | HUD's yearly one-night count of homeless people, broken down by group |

## Project Structure

```
wake-housing-intelligence/
├── app.py                     # Interactive dashboard (run this)
├── data/
│   ├── raw/                   # Raw HUD/Census-style datasets (135,000+ rows)
│   ├── clean/                 # Validated and standardised data
│   └── output/                # Dashboard-ready summary tables
├── scripts/
│   ├── generate_data.py       # Step 1: Build the HUD/Census-style dataset
│   ├── clean.py               # Step 2: Validate, clip, and standardise
│   ├── transform.py           # Step 3: Build summary tables for the dashboard
│   └── summary_stats.py       # Step 4: Print headline numbers
└── requirements.txt
```

## Quick Start

```bash
pip install -r requirements.txt

# Run the data pipeline (only needed once)
python scripts/generate_data.py
python scripts/clean.py
python scripts/transform.py

# Launch the dashboard
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

## Data Sources (Modelled After)

| Dataset | What It Tracks |
|---|---|
| HUD System Performance Measures | How well the regional homeless system is working overall |
| HUD Point-in-Time Count | One-night snapshot of how many people are homeless, and where they are |
| HUD Housing Inventory Count | How many shelter beds and housing units exist, and how full they are |
| CHAS (Housing Affordability) | How many households are spending too much of their income on housing |

## Key Findings (2024 Data)

- Wake County consistently outperforms the NC state average on getting people into permanent housing
- About 67% of extremely low-income renters in Wake County are cost-burdened (spending 30%+ on housing)
- Median rent in Wake County rose roughly 86% from 2015 to 2024
- Shelter beds across all programs run at 85%+ occupancy on average

## Why This Project

This portfolio project demonstrates skills directly relevant to housing and homelessness data work:
- Building and automating data pipelines
- Working with HUD reporting formats (SPM, PIT, HIC, CHAS)
- Transforming raw data into clear, actionable dashboards
- Communicating complex housing data in plain language
