
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# Load and prepare data
df = pd.read_excel("Cleaned_Crime_Data_Norfolk.xlsx")
df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.to_period("M").astype(str)

# Streamlit config
st.set_page_config(page_title="Norfolk Crime Dashboard", layout="wide")
st.title("Norfolk Crime Data Dashboard")

# Sidebar filters
st.sidebar.header("Filter Data")
selected_crime = st.sidebar.multiselect("Select Crime Type(s)", df["Crime type"].unique(), default=df["Crime type"].unique())
selected_lsoa = st.sidebar.multiselect("Select LSOA Area(s)", df["LSOA name"].unique(), default=df["LSOA name"].unique())
date_range = st.sidebar.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()])

# Apply filters
filtered_df = df[
    (df["Crime type"].isin(selected_crime)) &
    (df["LSOA name"].isin(selected_lsoa)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

# Scale coordinates to correct decimal form
filtered_df["latitude"] = filtered_df["latitude"] / 1e6
filtered_df["longitude"] = filtered_df["longitude"] / 1e6

# KPIs
st.markdown("### Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Crimes", len(filtered_df))
col2.metric("Unique Crime Types", filtered_df["Crime type"].nunique())
col3.metric("Unique LSOA Areas", filtered_df["LSOA name"].nunique())

# Top crime types
st.markdown("### Top Crime Types")
top_crimes = filtered_df["Crime type"].value_counts().nlargest(10).reset_index()
top_crimes.columns = ["Crime Type", "Count"]
fig_crime_type = px.bar(top_crimes, x="Crime Type", y="Count", color="Count", title="Top 10 Crime Types")
st.plotly_chart(fig_crime_type, use_container_width=True)

# Monthly trend
st.markdown("### Monthly Crime Trend")
monthly_trend = filtered_df.groupby("Month").size().reset_index(name="Crimes")
fig_trend = px.line(monthly_trend, x="Month", y="Crimes", markers=True, title="Crimes Over Time")
st.plotly_chart(fig_trend, use_container_width=True)

# Top LSOA areas
st.markdown("### Top LSOA Areas by Crime Volume")
top_lsoa = filtered_df["LSOA name"].value_counts().nlargest(10).reset_index()
top_lsoa.columns = ["LSOA Area", "Count"]
fig_lsoa = px.bar(top_lsoa, x="LSOA Area", y="Count", color="Count", title="Top 10 LSOA Areas")
st.plotly_chart(fig_lsoa, use_container_width=True)

# Outcome distribution
st.markdown("### Crime Outcome Distribution")
outcome_counts = filtered_df["Last outcome category"].value_counts().nlargest(10).reset_index()
outcome_counts.columns = ["Outcome", "Count"]
fig_outcome = px.pie(outcome_counts, names="Outcome", values="Count", title="Top Crime Outcomes")
st.plotly_chart(fig_outcome, use_container_width=True)

# Map: Crime Heatmap
st.markdown("### 🗺️ Crime Heatmap")
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=filtered_df['latitude'].mean(),
        longitude=filtered_df['longitude'].mean(),
        zoom=9,
        pitch=40,
    ),
    layers=[
        pdk.Layer(
            'HeatmapLayer',
            data=filtered_df,
            get_position='[longitude, latitude]',
            aggregation=pdk.types.String("MEAN"),
            get_weight=1,
            radiusPixels=30,
        )
    ],
))
