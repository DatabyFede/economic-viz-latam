# LATAM Macro Dashboard

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red?logo=streamlit)
![World Bank API](https://img.shields.io/badge/Datos-Banco%20Mundial-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Cuando volví a estudiar datos me di cuenta de que la mayoría de los proyectos de portfolio usan datasets de Kaggle que todo el mundo ya vio. Quería hacer algo con datos reales y relevantes para la región. Este dashboard consume la API pública del Banco Mundial en tiempo real y visualiza indicadores macroeconómicos de 7 países de LATAM.

**[→ Probalo en vivo acá](https://economic-viz-latam-eubizz88pctu7nrsu3o9jc.streamlit.app/)**

---

## Qué muestra

- **GDP per cápita** en USD — evolución histórica por país
- **Inflación** — heatmap por país y año, fácil de leer de un vistazo
- **Desempleo** — serie temporal comparativa
- **Scatter animado** — GDP vs Inflación con slider de año para ver la evolución
- **Tabla comparativa** — múltiples indicadores en el último año disponible
- **Descarga de datos** — exportás los datasets directamente como CSV

Países incluidos: Argentina, Brasil, México, Colombia, Chile, Perú, Uruguay.

---

## Instalación local

```bash
git clone https://github.com/DatabyFede/economic-viz-latam.git
cd economic-viz-latam
pip install -r requirements.txt
streamlit run app.py
```

No necesita API key — el Banco Mundial tiene su API abierta y gratuita.

---

## Fuente de datos

[World Bank Open Data](https://data.worldbank.org) — base de datos pública con más de 1.600 indicadores de desarrollo mundial. La app consume la API REST directamente, con caché de 1 hora para no sobrecargar el servidor.

Si la API no está disponible (sin internet o rate limit), la app cae automáticamente a datos sintéticos de demo para que igual se pueda explorar.

---

## Lo que aprendí

Trabajar con APIs REST que devuelven JSON anidado tiene su complejidad — el Banco Mundial devuelve los datos en un formato donde el primer elemento del array es metadata y el segundo son los datos reales. Ese tipo de detalles no aparecen en los tutoriales.

El scatter animado con Plotly Express fue lo más divertido de implementar — con `animation_frame` en una línea tenés una animación completa que comunica la evolución histórica de dos variables a la vez.

---

## Próximos pasos

- [ ] Agregar datos del INDEC para Argentina con mayor granularidad
- [ ] Comparativa con países fuera de LATAM (España, Portugal)
- [ ] Predicción de inflación con modelo simple de series temporales

---

## Otros proyectos

- [SQL Analytics Toolkit](https://github.com/DatabyFede/sql-analytics-toolkit) — cohortes, RFM, funnels y simulador de impacto en revenue
- [ML Explainer](https://github.com/DatabyFede/streamlit-ml-explainer) — entrenamiento de modelos y explicaciones SHAP interactivas

---

## Autor

**DatabyFede** · [LinkedIn](https://www.linkedin.com/in/federico-matyjaszczyk/) · [GitHub](https://github.com/DatabyFede)

> Parte de mi portfolio de proyectos de Data & IA — armado para volver al ruedo después de un tiempo fuera del mundo de los datos.
