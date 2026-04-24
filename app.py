"""
economic-viz-latam
==================
Dashboard interactivo con datos macroeconómicos reales de LATAM.
Fuente: API del Banco Mundial (World Bank Open Data)

Uso:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import warnings
warnings.filterwarnings("ignore")

# ── Configuración ──
st.set_page_config(
    page_title="LATAM Macro Dashboard · DatabyFede",
    page_icon="🌎",
    layout="wide"
)

st.markdown("""
<style>
    .kpi-box {
        background: #F8FAFC;
        border-left: 4px solid #2563EB;
        border-radius: 6px;
        padding: 0.8rem 1rem;
    }
    .kpi-value { font-size: 1.6rem; font-weight: 700; color: #1E40AF; }
    .kpi-label { font-size: 0.8rem; color: #64748B; }
    .kpi-delta { font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────

COUNTRIES = {
    "Argentina": "AR",
    "Brasil":    "BR",
    "México":    "MX",
    "Colombia":  "CO",
    "Chile":     "CL",
    "Perú":      "PE",
    "Uruguay":   "UY",
}

INDICATORS = {
    "GDP per cápita (USD)":           "NY.GDP.PCAP.CD",
    "Crecimiento del GDP (%)":        "NY.GDP.MKTP.KD.ZG",
    "Inflación (%)":                  "FP.CPI.TOTL.ZG",
    "Desempleo (%)":                  "SL.UEM.TOTL.ZS",
    "Deuda pública (% del GDP)":      "GC.DOD.TOTL.GD.ZS",
    "Exportaciones (% del GDP)":      "NE.EXP.GNFS.ZS",
    "Inversión extranjera (% GDP)":   "BX.KLT.DINV.WD.GD.ZS",
    "Gasto en educación (% GDP)":     "SE.XPD.TOTL.GD.ZS",
}

COLORS = {
    "Argentina": "#2563EB",
    "Brasil":    "#16A34A",
    "México":    "#DC2626",
    "Colombia":  "#D97706",
    "Chile":     "#7C3AED",
    "Perú":      "#0891B2",
    "Uruguay":   "#DB2777",
}

# ──────────────────────────────────────────────
# CARGA DE DATOS
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_world_bank(indicator: str, countries: list, start: int = 2000, end: int = 2023) -> pd.DataFrame:
    """
    Obtiene datos del Banco Mundial via API REST.
    Cachea por 1 hora para no sobrecargar la API.
    """
    country_codes = ";".join(countries)
    url = (
        f"https://api.worldbank.org/v2/country/{country_codes}/indicator/{indicator}"
        f"?format=json&date={start}:{end}&per_page=1000"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if len(data) < 2 or not data[1]:
            return pd.DataFrame()
        records = []
        for item in data[1]:
            records.append({
                "country": item["country"]["value"],
                "year":    int(item["date"]),
                "value":   item["value"],
            })
        df = pd.DataFrame(records).dropna(subset=["value"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.sort_values(["country", "year"])
    except Exception:
        return pd.DataFrame()


@st.cache_data
def get_demo_data() -> dict:
    """
    Datos sintéticos como fallback si la API no está disponible.
    Basados en valores reales aproximados 2000-2023.
    """
    np.random.seed(42)
    years = list(range(2000, 2024))
    countries = list(COUNTRIES.keys())

    base_gdp = {"Argentina": 8000, "Brasil": 5000, "México": 9000,
                 "Colombia": 4000, "Chile": 12000, "Perú": 4500, "Uruguay": 10000}
    base_inf = {"Argentina": 25, "Brasil": 7, "México": 5,
                 "Colombia": 6, "Chile": 4, "Perú": 4, "Uruguay": 8}

    records_gdp, records_inf, records_unem = [], [], []
    for c in countries:
        gdp = base_gdp[c]
        inf = base_inf[c]
        for y in years:
            gdp *= (1 + np.random.uniform(0.01, 0.05))
            inf_val = inf + np.random.uniform(-3, 8)
            records_gdp.append({"country": c, "year": y, "value": round(gdp, 2)})
            records_inf.append({"country": c, "year": y, "value": round(max(inf_val, 0), 2)})
            records_unem.append({"country": c, "year": y, "value": round(np.random.uniform(4, 15), 2)})

    return {
        "NY.GDP.PCAP.CD":  pd.DataFrame(records_gdp),
        "FP.CPI.TOTL.ZG":  pd.DataFrame(records_inf),
        "SL.UEM.TOTL.ZS":  pd.DataFrame(records_unem),
    }


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────

with st.sidebar:
    st.header("🌎 Filtros")

    selected_countries = st.multiselect(
        "Países",
        options=list(COUNTRIES.keys()),
        default=["Argentina", "Brasil", "México", "Chile", "Colombia"]
    )

    year_range = st.slider("Período", 2000, 2023, (2005, 2023))

    selected_indicator = st.selectbox("Indicador principal", list(INDICATORS.keys()))

    st.divider()
    st.markdown("**Fuente de datos**")
    use_api = st.toggle("Usar API del Banco Mundial", value=True)
    if not use_api:
        st.caption("Usando datos de demo (sin conexión)")

    st.divider()
    st.markdown("**Acerca de**")
    st.caption("Datos: [World Bank Open Data](https://data.worldbank.org)")
    st.caption("Proyecto: [GitHub](https://github.com/DatabyFede/economic-viz-latam)")

if not selected_countries:
    st.warning("Seleccioná al menos un país en el sidebar.")
    st.stop()

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────

st.title("🌎 LATAM Macro Dashboard")
st.caption(f"Indicadores macroeconómicos de América Latina · {year_range[0]}–{year_range[1]} · Fuente: Banco Mundial")
st.divider()

# ──────────────────────────────────────────────
# CARGA
# ──────────────────────────────────────────────

country_codes = [COUNTRIES[c] for c in selected_countries]
indicator_code = INDICATORS[selected_indicator]

if use_api:
    with st.spinner("Cargando datos del Banco Mundial..."):
        df_main = fetch_world_bank(indicator_code, country_codes, year_range[0], year_range[1])
        df_gdp   = fetch_world_bank("NY.GDP.PCAP.CD",  country_codes, year_range[0], year_range[1])
        df_inf   = fetch_world_bank("FP.CPI.TOTL.ZG",  country_codes, year_range[0], year_range[1])
        df_unem  = fetch_world_bank("SL.UEM.TOTL.ZS",  country_codes, year_range[0], year_range[1])

    if df_main.empty:
        st.warning("No se pudo conectar a la API. Usando datos de demo.")
        use_api = False

if not use_api:
    demo = get_demo_data()
    df_gdp  = demo["NY.GDP.PCAP.CD"][demo["NY.GDP.PCAP.CD"]["country"].isin(selected_countries)]
    df_inf  = demo["FP.CPI.TOTL.ZG"][demo["FP.CPI.TOTL.ZG"]["country"].isin(selected_countries)]
    df_unem = demo["SL.UEM.TOTL.ZS"][demo["SL.UEM.TOTL.ZS"]["country"].isin(selected_countries)]
    df_main = demo.get(indicator_code, df_gdp)
    df_main = df_main[df_main["country"].isin(selected_countries)]

# Filtrar por años
for _df in [df_main, df_gdp, df_inf, df_unem]:
    if not _df.empty:
        mask = (_df["year"] >= year_range[0]) & (_df["year"] <= year_range[1])
        _df.drop(_df[~mask].index, inplace=True)

# ──────────────────────────────────────────────
# KPIs — último año disponible
# ──────────────────────────────────────────────

st.markdown("### 📊 Snapshot — último año disponible")

kpi_cols = st.columns(len(selected_countries))
for col, country in zip(kpi_cols, selected_countries):
    gdp_row  = df_gdp[df_gdp["country"] == country].sort_values("year")
    inf_row  = df_inf[df_inf["country"] == country].sort_values("year")
    unem_row = df_unem[df_unem["country"] == country].sort_values("year")

    gdp_val  = f"${gdp_row['value'].iloc[-1]:,.0f}"  if not gdp_row.empty  else "N/A"
    inf_val  = f"{inf_row['value'].iloc[-1]:.1f}%"   if not inf_row.empty  else "N/A"
    unem_val = f"{unem_row['value'].iloc[-1]:.1f}%"  if not unem_row.empty else "N/A"

    with col:
        flag = {"Argentina":"🇦🇷","Brasil":"🇧🇷","México":"🇲🇽",
                "Colombia":"🇨🇴","Chile":"🇨🇱","Perú":"🇵🇪","Uruguay":"🇺🇾"}.get(country, "🌎")
        st.markdown(f"""
        <div class='kpi-box'>
            <div class='kpi-label'>{flag} {country}</div>
            <div class='kpi-value'>{gdp_val}</div>
            <div class='kpi-delta'>GDP per cápita</div>
            <div class='kpi-delta'>📈 Inflación: {inf_val}</div>
            <div class='kpi-delta'>👷 Desempleo: {unem_val}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ──────────────────────────────────────────────
# GRÁFICO PRINCIPAL — Serie temporal
# ──────────────────────────────────────────────

st.markdown(f"### 📈 {selected_indicator} — evolución temporal")

if not df_main.empty:
    fig = px.line(
        df_main,
        x="year", y="value",
        color="country",
        color_discrete_map=COLORS,
        markers=True,
        labels={"year": "Año", "value": selected_indicator, "country": "País"},
    )
    fig.update_layout(
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#F1F5F9"),
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=5))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay datos disponibles para este indicador y selección.")

# ──────────────────────────────────────────────
# COMPARATIVA MULTIDIMENSIONAL
# ──────────────────────────────────────────────

st.divider()
st.markdown("### 🔄 Comparativa multidimensional — último año")

last_year_data = []
for country in selected_countries:
    row = {"País": country}
    for ind_name, ind_code in list(INDICATORS.items())[:4]:
        _df = fetch_world_bank(ind_code, [COUNTRIES[country]], year_range[1]-2, year_range[1]) if use_api else pd.DataFrame()
        if _df.empty:
            demo_key = ind_code
            if demo_key in get_demo_data():
                _df = get_demo_data()[demo_key]
                _df = _df[(_df["country"] == country) & (_df["year"] <= year_range[1])]
        if not _df.empty:
            row[ind_name] = round(_df.sort_values("year")["value"].iloc[-1], 2)
        else:
            row[ind_name] = None
    last_year_data.append(row)

df_compare = pd.DataFrame(last_year_data).set_index("País")
st.dataframe(
    df_compare.style.background_gradient(cmap="Blues", axis=0),
    use_container_width=True
)

# ──────────────────────────────────────────────
# GDP vs INFLACIÓN — Scatter
# ──────────────────────────────────────────────

st.divider()
st.markdown("### 💡 GDP per cápita vs Inflación")
st.caption("Cada punto es un país-año. El tamaño no tiene escala adicional — es para facilitar la lectura.")

if not df_gdp.empty and not df_inf.empty:
    merged = pd.merge(
        df_gdp.rename(columns={"value": "gdp"}),
        df_inf.rename(columns={"value": "inflation"}),
        on=["country", "year"]
    )
    fig_scatter = px.scatter(
        merged,
        x="gdp", y="inflation",
        color="country",
        animation_frame="year",
        color_discrete_map=COLORS,
        labels={"gdp": "GDP per cápita (USD)", "inflation": "Inflación (%)", "country": "País"},
        size_max=20,
        range_x=[merged["gdp"].min() * 0.8, merged["gdp"].max() * 1.1],
        range_y=[merged["inflation"].min() - 2, min(merged["inflation"].max() * 1.1, 100)],
    )
    fig_scatter.update_layout(height=450, plot_bgcolor="white",
                               yaxis=dict(gridcolor="#F1F5F9"),
                               xaxis=dict(gridcolor="#F1F5F9"))
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.caption("▶ Usá el slider de año para ver la evolución animada")

# ──────────────────────────────────────────────
# HEATMAP DE CORRELACIÓN
# ──────────────────────────────────────────────

st.divider()
st.markdown("### 🌡️ Inflación por país y año — Heatmap")

if not df_inf.empty:
    pivot = df_inf.pivot(index="country", columns="year", values="value")
    fig_heat = px.imshow(
        pivot.round(1),
        color_continuous_scale="RdYlGn_r",
        labels={"x": "Año", "y": "País", "color": "Inflación (%)"},
        aspect="auto",
    )
    fig_heat.update_layout(height=320)
    st.plotly_chart(fig_heat, use_container_width=True)
    st.caption("Verde = inflación baja · Rojo = inflación alta")

# ──────────────────────────────────────────────
# DESCARGA
# ──────────────────────────────────────────────

st.divider()
st.markdown("### 💾 Exportar datos")
col1, col2 = st.columns(2)
with col1:
    if not df_gdp.empty:
        csv = df_gdp.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar GDP per cápita", csv, "gdp_latam.csv", "text/csv")
with col2:
    if not df_inf.empty:
        csv = df_inf.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar Inflación", csv, "inflacion_latam.csv", "text/csv")
