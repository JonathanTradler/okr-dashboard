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

def plot_segment_trend(okr, seg, label):
    data = combined[(combined["OKR"] == okr) & (combined["Segment"] == seg)]
    if len(data) > 1:
        fig = px.line(
            data, x="Month", y="Value", markers=True,
            title=label, labels={"Value": "%"}, range_y=(0, 100)
        )
        fig.update_layout(xaxis_type='category')
        fig.update_traces(mode="lines+markers", hovertemplate='%{y}%<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

def plot_overall_trend(okr):
    data = combined[combined["OKR"] == okr]
    piv = data.pivot_table(index="Month", columns="Segment", values="Value", aggfunc="first")
    if "Overall" in piv:
        series = piv["Overall"].dropna().reset_index()
        if len(series) > 1:
            fig = px.line(
                series, x="Month", y="Overall", markers=True,
                title=okr, labels={"Overall": "%"}, range_y=(0, 100)
            )
            fig.update_layout(xaxis_type='category')
            fig.update_traces(mode="lines+markers", hovertemplate='%{y}%<extra></extra>')
            st.plotly_chart(fig, use_container_width=True)

if selection == "Overall Dashboard":
    cols = st.columns(2)
    for i, okr in enumerate(sorted(combined["OKR"].unique())):
        with cols[i % 2]:
            if okr == "2.1 Active Platform Usage":
                plot_segment_trend(okr, "Daily", "2.1 Daily Data Upload Tenants Active Usage")
                plot_segment_trend(okr, "Others", "2.1 Non Daily Data Upload (Others) Tenants Active Usage")
            else:
                plot_overall_trend(okr)
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
        plot_segment_trend(okr, "Daily", "2.1 Daily Data Upload Tenants Active Usage")
        plot_segment_trend(okr, "Others", "2.1 Non Daily Data Upload (Others) Tenants Active Usage")
    else:
        plot_overall_trend(okr)













