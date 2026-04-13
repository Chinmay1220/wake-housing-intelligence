import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wake County Housing Intelligence",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA = Path(__file__).parent / "data" / "output"

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    wake   = pd.read_csv(DATA / "wake_coc_performance.csv")
    coc    = pd.read_csv(DATA / "nc_coc_comparison.csv")
    afford = pd.read_csv(DATA / "affordability_summary.csv")
    inv    = pd.read_csv(DATA / "inventory_utilization.csv")
    pit    = pd.read_csv(DATA / "pit_trends.csv")
    return wake, coc, afford, inv, pit

wake, coc, afford, inv, pit = load()

# ── Colours ───────────────────────────────────────────────────────────────────
BLUE   = "#1f77b4"
ORANGE = "#ff7f0e"
GREEN  = "#2ca02c"
RED    = "#d62728"
GRAY   = "#7f7f7f"

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Wake_County_seal.png/200px-Wake_County_seal.png",
    width=80,
)
st.sidebar.title("Wake County\nHousing Intelligence")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Go to",
    [
        "Wake County Overview",
        "Compare All NC Regions",
        "Housing Affordability",
        "Shelter Capacity & Exits",
        "Annual Homeless Count",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption("Data: HUD / Census-style dataset  \nWake County HACR")


# ── Helpers ───────────────────────────────────────────────────────────────────
def metric_row(metrics: list[tuple]):
    cols = st.columns(len(metrics))
    for col, (label, value, delta) in zip(cols, metrics):
        col.metric(label, value, delta)

def pct(val, decimals=1):
    return f"{val * 100:.{decimals}f}%"


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Wake County Overview
# ═════════════════════════════════════════════════════════════════════════════
if page == "Wake County Overview":
    st.title("Wake County Homeless System Performance")
    st.markdown(
        "Key outcomes for the **Raleigh / Wake County Continuum of Care (NC-506)** "
        "— the regional network of shelters, housing programs, and services."
    )

    year = st.slider("Select Year", int(wake.year.min()), int(wake.year.max()), int(wake.year.max()))
    row  = wake[wake.year == year].iloc[0]
    prev = wake[wake.year == year - 1].iloc[0] if year > wake.year.min() else None

    def delta(col):
        if prev is None:
            return None
        return pct(row[col] - prev[col])

    st.markdown("### At a Glance")
    metric_row([
        ("People Housed Successfully", pct(row.exit_permanent_housing_pct),  delta("exit_permanent_housing_pct")),
        ("Returned to Homelessness within 2 Years", pct(row.return_24mo_pct), delta("return_24mo_pct")),
        ("Avg. Nights in Shelter Before Exit", f"{row.avg_los_es_sh_days:.0f} nights", None),
        ("Shelter Beds Occupied", pct(row.inv_util_rate), delta("inv_util_rate")),
        ("Experiencing Homelessness for First Time", pct(row.first_time_homeless_pct), delta("first_time_homeless_pct")),
    ])

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            wake, x="year", y="exit_permanent_housing_pct",
            title="People Successfully Housed (% of Exits)",
            markers=True, color_discrete_sequence=[BLUE],
        )
        fig.update_yaxes(tickformat=".0%", title="")
        fig.update_xaxes(title="Year")
        fig.add_vline(x=year, line_dash="dot", line_color=ORANGE)
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.line(
            wake, x="year", y="return_24mo_pct",
            title="Returned to Homelessness Within 2 Years (% of Exits)",
            markers=True, color_discrete_sequence=[RED],
        )
        fig.update_yaxes(tickformat=".0%", title="")
        fig.update_xaxes(title="Year")
        fig.add_vline(x=year, line_dash="dot", line_color=ORANGE)
        st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)

    with col3:
        fig = px.bar(
            wake, x="year", y="total_homeless_persons",
            title="Total People Experiencing Homelessness",
            color_discrete_sequence=[BLUE],
        )
        fig.update_yaxes(title="People")
        fig.update_xaxes(title="Year")
        st.plotly_chart(fig, width="stretch")

    with col4:
        los = wake[["year", "avg_los_es_sh_days", "avg_los_es_sh_th_days"]].copy()
        los = los.rename(columns={
            "avg_los_es_sh_days":    "Emergency Shelter only",
            "avg_los_es_sh_th_days": "Including Transitional Housing",
        })
        fig = px.line(
            los.melt("year", var_name="Program", value_name="Nights"),
            x="year", y="Nights", color="Program",
            title="Average Nights in Shelter Before Exit",
            markers=True,
            color_discrete_sequence=[BLUE, ORANGE],
        )
        fig.update_yaxes(title="Nights")
        fig.update_xaxes(title="Year")
        st.plotly_chart(fig, width="stretch")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Compare All NC Regions
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Compare All NC Regions":
    st.title("How Does Wake County Compare?")
    st.markdown(
        "Wake County (NC-506) benchmarked against all **20 North Carolina regional homeless systems** "
        "(called Continuums of Care, or CoCs)."
    )

    year = st.slider("Select Year", int(coc.year.min()), int(coc.year.max()), int(coc.year.max()))
    df   = coc[coc.year == year].copy()
    df["Region"] = df["is_wake_county"].map({True: "Wake County", False: "Other NC Regions"})

    col1, col2 = st.columns(2)

    with col1:
        df_s = df.sort_values("exit_ph_pct", ascending=True)
        fig = px.bar(
            df_s, x="exit_ph_pct", y="coc_name",
            orientation="h",
            title="People Successfully Housed (% of Exits)",
            color="Region",
            color_discrete_map={"Wake County": ORANGE, "Other NC Regions": BLUE},
        )
        fig.update_xaxes(tickformat=".0%", title="")
        fig.update_yaxes(title="", tickfont_size=9)
        fig.update_layout(legend_title="")
        st.plotly_chart(fig, width="stretch")

    with col2:
        df_s = df.sort_values("utilization_rate", ascending=True)
        fig = px.bar(
            df_s, x="utilization_rate", y="coc_name",
            orientation="h",
            title="Shelter Bed Occupancy Rate",
            color="Region",
            color_discrete_map={"Wake County": ORANGE, "Other NC Regions": BLUE},
        )
        fig.update_xaxes(tickformat=".0%", title="")
        fig.update_yaxes(title="", tickfont_size=9)
        fig.update_layout(legend_title="", showlegend=False)
        st.plotly_chart(fig, width="stretch")

    st.markdown("### Trend Over Time — Wake County vs. NC Average")

    METRIC_OPTIONS = {
        "exit_ph_pct":      "People Successfully Housed (%)",
        "return_24mo_pct":  "Returned to Homelessness within 2 Years (%)",
        "utilization_rate": "Shelter Bed Occupancy Rate (%)",
        "sheltered_pct":    "Share of Homeless Who Are Sheltered (%)",
    }
    col_key = st.selectbox("Metric", list(METRIC_OPTIONS.keys()), format_func=lambda k: METRIC_OPTIONS[k])
    col_label = METRIC_OPTIONS[col_key]

    nc_avg = coc[~coc.is_wake_county].groupby("year")[col_key].mean().reset_index()
    nc_avg["Series"] = "NC Average (all other regions)"
    wake_t = coc[coc.is_wake_county][["year", col_key]].copy()
    wake_t["Series"] = "Wake County"
    combined = pd.concat([nc_avg, wake_t])

    fig = px.line(
        combined, x="year", y=col_key, color="Series",
        markers=True,
        color_discrete_map={"Wake County": ORANGE, "NC Average (all other regions)": BLUE},
        title=f"{col_label} — Wake County vs NC Average",
    )
    fig.update_yaxes(tickformat=".0%", title="")
    fig.update_xaxes(title="Year")
    fig.update_layout(legend_title="")
    st.plotly_chart(fig, width="stretch")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Housing Affordability
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Housing Affordability":
    st.title("Housing Affordability in North Carolina")
    st.markdown(
        "Based on HUD's Comprehensive Housing Affordability Strategy (CHAS) data — "
        "showing how many households spend more than 30% of their income on housing costs."
    )

    col_f1, col_f2 = st.columns(2)
    counties    = sorted(afford.county.unique())
    sel_counties = col_f1.multiselect("Select Counties", counties, default=["Wake"])
    tenure_opt  = col_f2.radio("Housing Type", ["Both", "Renters", "Owners"], horizontal=True)

    df = afford[afford.county.isin(sel_counties)].copy()
    if tenure_opt == "Renters":
        df = df[df.tenure == "Renter"]
    elif tenure_opt == "Owners":
        df = df[df.tenure == "Owner"]

    TIER_ORDER = [
        "Extremely Low Income (<=30% AMI)",
        "Very Low Income (31-50% AMI)",
        "Low Income (51-80% AMI)",
        "Moderate Income (81-100% AMI)",
        "Above Moderate (>100% AMI)",
    ]
    TIER_LABELS = {
        "Extremely Low Income (<=30% AMI)": "Extremely Low Income\n(≤30% of Area Median)",
        "Very Low Income (31-50% AMI)":     "Very Low Income\n(31–50% of Area Median)",
        "Low Income (51-80% AMI)":          "Low Income\n(51–80% of Area Median)",
        "Moderate Income (81-100% AMI)":    "Moderate Income\n(81–100% of Area Median)",
        "Above Moderate (>100% AMI)":       "Above Median Income\n(>100% of Area Median)",
    }

    st.markdown("### What Share of Households Are Cost-Burdened?")
    st.caption("Cost-burdened = spending more than 30% of income on housing")
    year_aff = st.slider("Select Year", int(afford.year.min()), int(afford.year.max()), int(afford.year.max()), key="aff_yr")

    df_yr   = df[df.year == year_aff].copy()
    df_tier = df_yr.groupby("income_tier")["cost_burden_rate_calc"].mean().reindex(TIER_ORDER).reset_index()
    df_tier["income_tier"] = df_tier["income_tier"].map(TIER_LABELS)

    fig = px.bar(
        df_tier, x="income_tier", y="cost_burden_rate_calc",
        title=f"Share of Households Spending 30%+ of Income on Housing ({year_aff})",
        color="cost_burden_rate_calc",
        color_continuous_scale="Reds",
    )
    fig.update_yaxes(tickformat=".0%", title="Share of Households")
    fig.update_xaxes(title="")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        rent_df = (
            afford[afford.county.isin(sel_counties) & (afford.median_gross_rent > 0)]
            .groupby(["county", "year"])["median_gross_rent"].mean().reset_index()
        )
        fig = px.line(
            rent_df, x="year", y="median_gross_rent", color="county",
            title="Median Monthly Rent Over Time", markers=True,
        )
        fig.update_yaxes(tickprefix="$", title="Median Monthly Rent")
        fig.update_xaxes(title="Year")
        st.plotly_chart(fig, width="stretch")

    with col2:
        gap_df = (
            afford[afford.county.isin(sel_counties)]
            .groupby(["county", "year"])["total_affordability_gap"].sum().reset_index()
        )
        fig = px.area(
            gap_df, x="year", y="total_affordability_gap", color="county",
            title="Shortage of Affordable Housing Units",
        )
        fig.update_yaxes(title="Units Short of Need")
        fig.update_xaxes(title="Year")
        st.plotly_chart(fig, width="stretch")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Shelter Capacity & Exits
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Shelter Capacity & Exits":
    st.title("Shelter Capacity & Exit Outcomes")
    st.markdown(
        "How full are shelters, and where do people go when they leave? "
        "Data covers all NC shelter and housing programs."
    )

    PROG_LABELS = {
        "Emergency Shelter":        "Emergency Shelter",
        "Transitional Housing":     "Transitional Housing",
        "Permanent Supportive":     "Permanent Supportive Housing",
        "Rapid Rehousing":          "Rapid Re-Housing",
        "Safe Haven":               "Safe Haven",
        "Street Outreach":          "Street Outreach",
    }

    programs = sorted(inv.program_type.unique())
    sel_prog = st.multiselect("Select Program Types", programs, default=programs)
    df = inv[inv.program_type.isin(sel_prog)].copy()
    df["program_type"] = df["program_type"].map(PROG_LABELS).fillna(df["program_type"])

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            df, x="year", y="avg_utilization_rate", color="program_type",
            title="Shelter Bed Occupancy Rate by Program Type",
            markers=True,
        )
        fig.update_yaxes(tickformat=".0%", title="Occupancy Rate")
        fig.update_xaxes(title="Year")
        fig.add_hline(y=0.85, line_dash="dot", line_color=GRAY,
                      annotation_text="85% capacity target",
                      annotation_position="bottom right")
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.line(
            df, x="year", y="exits_ph_rate", color="program_type",
            title="Share of Exits That Go to Permanent Housing",
            markers=True,
        )
        fig.update_yaxes(tickformat=".0%", title="% Exiting to Permanent Housing")
        fig.update_xaxes(title="Year")
        st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)

    with col3:
        exit_df = df.groupby("year")[
            ["exits_to_permanent_housing", "exits_to_temporary", "exits_unknown"]
        ].sum().reset_index()
        exit_df = exit_df.rename(columns={
            "exits_to_permanent_housing": "Moved to Permanent Housing",
            "exits_to_temporary":         "Moved to Temporary Housing",
            "exits_unknown":              "Unknown / No Destination",
        })
        fig = px.bar(
            exit_df.melt("year", var_name="Exit Type", value_name="People"),
            x="year", y="People", color="Exit Type",
            title="Where Did People Go After Leaving Shelter?",
            barmode="stack",
            color_discrete_map={
                "Moved to Permanent Housing": GREEN,
                "Moved to Temporary Housing": ORANGE,
                "Unknown / No Destination":   GRAY,
            },
        )
        fig.update_xaxes(title="Year")
        st.plotly_chart(fig, width="stretch")

    with col4:
        fig = px.line(
            df, x="year", y="avg_los_days", color="program_type",
            title="Average Nights Stayed Before Leaving",
            markers=True,
        )
        fig.update_yaxes(title="Nights")
        fig.update_xaxes(title="Year")
        st.plotly_chart(fig, width="stretch")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5 — Annual Homeless Count
# ═════════════════════════════════════════════════════════════════════════════
elif page == "Annual Homeless Count":
    st.title("Annual Point-in-Time Homeless Count")
    st.markdown(
        "HUD's annual one-night count of people experiencing homelessness across North Carolina. "
        "Broken down by group type (subpopulation) and whether people were sheltered or unsheltered."
    )

    GROUP_LABELS = {
        "Adults Only":                  "Adults Only (no children)",
        "Adults with Children":         "Families with Children",
        "Unaccompanied Youth":          "Youth Under 25 (Alone)",
        "Chronically Homeless":         "Chronically Homeless",
        "Veterans":                     "Veterans",
        "Survivors of Domestic Violence": "Survivors of Domestic Violence",
    }

    subpops  = sorted(pit.subpopulation.unique())
    sel_sub  = st.multiselect("Select Groups", subpops, default=subpops)
    df = pit[pit.subpopulation.isin(sel_sub)].copy()
    df["subpopulation"] = df["subpopulation"].map(GROUP_LABELS).fillna(df["subpopulation"])

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            df, x="year", y="total_homeless", color="subpopulation",
            title="People Experiencing Homelessness — by Group (NC Total)",
            markers=True,
        )
        fig.update_yaxes(title="People")
        fig.update_xaxes(title="Year")
        fig.update_layout(legend_title="Group")
        st.plotly_chart(fig, width="stretch")

    with col2:
        nc_total = df.groupby("year")[["sheltered", "unsheltered"]].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(name="In a Shelter or Program",
                             x=nc_total.year, y=nc_total.sheltered, marker_color=BLUE))
        fig.add_trace(go.Bar(name="Sleeping Outside / Unsheltered",
                             x=nc_total.year, y=nc_total.unsheltered, marker_color=ORANGE))
        fig.update_layout(
            barmode="stack",
            title="Sheltered vs. Unsheltered Homeless (NC Total)",
            legend_title="",
            xaxis_title="Year",
            yaxis_title="People",
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown("### Wake County's Share of North Carolina Homelessness")
    wake_pit = df.groupby("year")[["wake_total_homeless", "total_homeless"]].sum().reset_index()
    wake_pit["wake_share"] = wake_pit.wake_total_homeless / wake_pit.total_homeless

    col3, col4 = st.columns(2)

    with col3:
        fig = px.line(
            wake_pit, x="year", y="wake_total_homeless",
            title="Wake County — Total People Counted as Homeless",
            markers=True, color_discrete_sequence=[ORANGE],
        )
        fig.update_yaxes(title="People")
        fig.update_xaxes(title="Year")
        st.plotly_chart(fig, width="stretch")

    with col4:
        fig = px.line(
            wake_pit, x="year", y="wake_share",
            title="Wake County as a Share of NC's Total Homeless Population",
            markers=True, color_discrete_sequence=[ORANGE],
        )
        fig.update_yaxes(tickformat=".1%", title="Share of NC Total")
        fig.update_xaxes(title="Year")
        st.plotly_chart(fig, width="stretch")
