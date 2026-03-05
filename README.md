# Streamlit Dashboard Starter

NbS carbon and biodiversity KPI dashboard components for Streamlit applications.

## Domain Context

PUR Projet and similar NbS organizations track restoration projects across multiple countries.
This starter provides backend KPI logic for Streamlit dashboards: carbon credit issuance,
area planted, biodiversity score, and timeline progress — aligned with Verra VCS and Gold Standard.

## Features
- **NbS KPI summary**: total area, carbon credits, sequestration estimates, biodiversity
- **Carbon progress chart data**: cumulative time-series for Streamlit line charts
- **Multi-country support**: projects grouped by country and status
- **Sample data**: 8 NbS projects across Thailand, Indonesia, Vietnam, China

## Quick Start

```python
from src.main import StreamlitDashboardStarter

dash = StreamlitDashboardStarter(config={"emission_factor_t_ha": 8.5})
df = dash.load_data("sample_data/nbs_projects.csv")

kpis = dash.nbs_kpi_summary(df)
print(f"Total Area:       {kpis['total_area_ha']:,.1f} ha")
print(f"Carbon Credits:   {kpis['total_carbon_credits_tco2']:,.0f} tCO2")
print(f"Est. Annual Seq:  {kpis['estimated_annual_sequestration_tco2']:,.0f} tCO2/yr")
print(f"Projects by Country: {kpis['projects_by_country']}")

# For Streamlit chart
chart_data = dash.carbon_progress_chart_data(df, target_credits=150000)
# st.line_chart(chart_data.set_index("period")["cumulative_credits"])
```

## Running Tests
```bash
pytest tests/ -v
```

---

## [v1.3.0] Carbon Credit Projection & Biodiversity Scoring

```python
# 5-year carbon credit revenue projection
projection = dash.carbon_credit_projection(
    project_df, years=5, price_per_credit_usd=18.0, annual_growth_rate=0.07
)
print(projection[["year", "projected_area_ha", "estimated_credits_tco2", "revenue_usd"]])
# year  projected_area_ha  estimated_credits_tco2    revenue_usd
#    1             5800.0               49300.0     887400.0
#    5             7631.9               64871.0    1167678.0

# Biodiversity scoring per project
bio = dash.biodiversity_score(project_df)
print(bio[["project_id", "biodiversity_score", "classification"]])
# NBS-CN-01  100.0  Excellent
# NBS-VN-01   86.7  Excellent
# NBS-TH-01   75.0  Good
```
