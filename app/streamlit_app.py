import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="WDI + EIA Explorer", layout="wide")

# ---------------------------
# TITLU SIMPLU
# ---------------------------
st.markdown("# WDI + EIA EXPLORER")
st.markdown("### Indicatori globali de dezvoltare economică și tranziție energetică")

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load():
    return pd.read_csv(r"C:\\PROJECTS\\AID\\data\\all_data_long.csv")

df = load()

# ---------------------------
# SIDEBAR SIMPLU
# ---------------------------
st.sidebar.header("Setări")

indicator = st.sidebar.selectbox("Indicator", sorted(df["indicator_name"].unique()))

scale_mode = st.sidebar.radio("Scalare", ["Brut", "Min–Max", "Log"], index=1)

palette = st.sidebar.selectbox(
    "Culori pastel",
    ["Blues", "Greens", "Purples", "Oranges", "Teal", "Tealgrn", "Aggrnyl", "YlGnBu", "Sunset"],
    index=6  # Aggrnyl = super pastel
)

animate = st.sidebar.checkbox("Animație", value=False)

df_ind = df[df["indicator_name"] == indicator]
unit = df_ind["unit_name"].iloc[0]
years = sorted(df_ind["year"].unique())

# ---------------------------
# SELECTARE AN
# ---------------------------

if not animate:
    year = st.sidebar.slider("An", min(years), max(years), min(years))
    df_plot = df_ind[df_ind["year"] == year].copy()
    df_plot = df_plot.sort_values("year")
else:
    df_plot = df_ind.copy()
    df_plot = df_plot.sort_values("year")

# ---------------------------
# SCALARE VALORI
# ---------------------------
def scale(x):
    if scale_mode == "Brut":
        return x
    if scale_mode == "Min–Max":
        return (x - x.min()) / (x.max() - x.min() + 1e-9)
    if scale_mode == "Log":
        return np.log1p(x)

df_plot["plot_value"] = scale(df_plot["value"])

# ---------------------------
# TITLU SECTIUNE HARTĂ
# ---------------------------
if animate:
    subtitle = f"{indicator} ({unit}) – evoluție în timp"
else:
    subtitle = f"{indicator} ({unit}) — {year}"

st.markdown(f"#### {subtitle}")

# ---------------------------
# LAYOUT PENTRU HARTĂ + TOP 10
# ---------------------------
col_map, col_bar = st.columns([2.5, 1.5])

# ---------------------------
# HARTA PLOTLY – pastel + border gri
# ---------------------------
if animate:
    fig_map = px.choropleth(
        df_plot,
        locations="country",
        color="plot_value",
        animation_frame="year",
        hover_name="country",
        color_continuous_scale=palette,
        projection="natural earth",
    )
else:
    fig_map = px.choropleth(
        df_plot,
        locations="country",
        color="plot_value",
        hover_name="country",
        color_continuous_scale=palette,
        projection="natural earth",
    )

# Border gri profesionist + reducere contrast
fig_map.update_geos(
    showcountries=True,
    countrycolor="#B5B5B5",    # gri pastel
    showcoastlines=False,
    showsubunits=False,
    fitbounds="locations"
)

fig_map.update_traces(
    marker_line_width=0.45,
    marker_line_color="#B5B5B5"
)

fig_map.update_layout(
    height=550,
    margin=dict(l=0, r=0, t=10, b=0),
    coloraxis_colorbar=dict(
        title="",
        thickness=10,
        len=0.55
    )
)

col_map.plotly_chart(fig_map, use_container_width=True)

# ---------------------------
# TOP 10 – BAR CHART cu aceeași paletă
# ---------------------------
from plotly.colors import sequential

# selectăm paleta reală folosită
palette_dict = {
    "Aggrnyl": px.colors.sequential.Aggrnyl,
    "Blues": px.colors.sequential.Blues,
    "Greens": px.colors.sequential.Greens,
    "Purples": px.colors.sequential.Purples,
    "Tealgrn": px.colors.sequential.Tealgrn,
    "YlGnBu": px.colors.sequential.YlGnBu,
    "Sunset": px.colors.sequential.Sunset,
}

# culoarea pastel selectată
base_color = palette_dict[palette][3]   # mijloc paletă

if not animate:
    df_top = df_plot.nlargest(10, "value").sort_values("value", ascending=True)

    fig_bar = px.bar(
        df_top,
        x="value",
        y="country",
        orientation="h",
        title="Top 10 țări",
    )

    # aplicăm culoarea pastel unică
    fig_bar.update_traces(marker_color=base_color)

    fig_bar.update_layout(
        height=550,
        margin=dict(l=10, r=0, t=40, b=0),
        xaxis_title="Valoare",
        yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False
    )

    col_bar.plotly_chart(fig_bar, use_container_width=True)

