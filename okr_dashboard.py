import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- Baseline (June 2025) ---
baseline_data = [
    ["2.1 Active Platform Usage", "Daily", "Active User Rate", 49.47],
    ["2.1 Active Platform Usage", "Others", "Active User Rate", 80.5],
    ["3.1 Manager Participation", "Overall", "% Managers Active", 40.59],
    ["3.2 Metric Hits", "Overall", "% Users Met Targets", 82.25],
    ["4.1 Increase Voucher redemption", "Overall", "% Points Used from Eligible", 8.2],
    ["4.2 Fight unspent points", "Overall", "% Points Redeemed from Available", 4.19],
    ["4.3 Maximize Reached Population", "Overall", "% Active Users with Redemption", 23.17],
]
baseline_df = pd.DataFrame(baseline_data, columns=["OKR", "Segment", "Metric", "Value"])
baseline_df["Month"] = "2025-06"

# --- Load all monthly CSVs ---
def load_all_data():
    all_dfs = [baseline_df]
    data_dir = "data"
    prefix = "okr_summary_"
    suffix = ".csv"
    if not os.path.exists(data_dir):
        return pd.concat(all_dfs, ignore_index=True)

    files = [
        f for f in os.listdir(data_dir)
        if f.startswith(prefix) and f.endswith(suffix)
    ]

    for f in sorted(files):
        try:
            df = pd.read_csv(os.path.join(data_dir, f))
            date_part = f.replace(prefix, "").replace(suffix, "")
            df["Month"] = pd.to_datetime(date_part).strftime('%Y-%m')
            all_dfs.append(df)
        except Exception as e:
            st.warning(f"Failed to load {f}: {e}")

    return pd.concat(all_dfs, ignore_index=True)

combined = load_all_data()

st.title("OKR Dashboard")

# Sidebar Dropdown
okr_options = ["Overall Dashboard"] + sorted(combined["OKR"].unique())
selection = st.sidebar.selectbox("Choose OKR View", okr_options)

# Subheader descriptions
okr_subheaders = {
    "2.1 Active Platform Usage": "Monthly Visits - Mobile app opens + opens on web (split by daily updated tenants vs others)",
    "3.1 Manager Participation": "Increase manager user-type overall engagement on the platform - monthly visits on the web",
    "3.2 Metric Hits": "How many users of the tradler population reach at least one target a month (non internal)",
    "4.1 Increase Voucher redemption": "Improve the rate of % utilised points (points in user balances) / budget distributed (total points available to distribute)",
    "4.2 Fight unspent points": "% points redeemed from eligible at time of check",
    "4.3 Maximize Reached Population": "% active users with at least one redemption"
}

def plot_segment_trend(okr, seg, title_text, subtitle_text=""):
    data = combined[(combined["OKR"] == okr) & (combined["Segment"] == seg)]
    if len(data) > 1:
        fig = px.line(
            data, x="Month", y="Value", markers=True,
            labels={"Value": "%"}, range_y=(0, 100)
        )
        fig.update_layout(
            xaxis_type='category',
            title={
                'text': f"{title_text}<br><sup>{subtitle_text}</sup>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20},
            }
        )
        fig.update_traces(mode="lines+markers", hovertemplate='%{y}%<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

def plot_overall_trend(okr, subtitle_text=""):
    data = combined[combined["OKR"] == okr]
    piv = data.pivot_table(index="Month", columns="Segment", values="Value", aggfunc="first")
    if "Overall" in piv:
        series = piv["Overall"].dropna().reset_index()
        if len(series) > 1:
            fig = px.line(
                series, x="Month", y="Overall", markers=True,
                labels={"Overall": "%"}, range_y=(0, 100)
            )
            fig.update_layout(
                xaxis_type='category',
                title={
                    'text': f"{okr}<br><sup>{subtitle_text}</sup>",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20},
                }
            )
            fig.update_traces(mode="lines+markers", hovertemplate='%{y}%<extra></extra>')
            st.plotly_chart(fig, use_container_width=True)

if selection == "Overall Dashboard":
    cols = st.columns(2)
    for i, okr in enumerate(sorted(combined["OKR"].unique())):
        with cols[i % 2]:
            if okr == "2.1 Active Platform Usage":
                plot_segment_trend(
                    okr, "Daily",
                    "2.1 Active Platform Usage: Daily Data Upload Tenants",
                    okr_subheaders.get(okr, "")
                )
                plot_segment_trend(
                    okr, "Others",
                    "2.1 Active Platform Usage: Non Daily Data Upload (Others) Tenants",
                    okr_subheaders.get(okr, "")
                )
            else:
                plot_overall_trend(okr, okr_subheaders.get(okr, ""))
else:
    okr = selection
    data = combined[combined["OKR"] == okr]
    piv = data.pivot_table(index="Month", columns="Segment", values="Value", aggfunc="first")
    if "Overall" in piv:
        cols = ["Overall"] + [c for c in piv.columns if c != "Overall"]
        piv = piv[cols]
    st.subheader(f"📋 {okr} — Monthly Table")
    st.dataframe(piv.fillna(""))

    if okr == "2.1 Active Platform Usage":
        plot_segment_trend(
            okr, "Daily",
            "2.1 Active Platform Usage: Daily Data Upload Tenants",
            okr_subheaders.get(okr, "")
        )
        plot_segment_trend(
            okr, "Others",
            "2.1 Active Platform Usage: Non Daily Data Upload (Others) Tenants",
            okr_subheaders.get(okr, "")
        )
    else:
        plot_overall_trend(okr, okr_subheaders.get(okr, ""))














