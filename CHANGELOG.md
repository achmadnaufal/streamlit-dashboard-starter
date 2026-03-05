# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.3.0] - 2026-03-05
### Added
- `carbon_credit_projection()`: multi-year carbon credit issuance and revenue projection with growth modeling
- `biodiversity_score()`: per-project biodiversity scoring and classification (Excellent/Good/Baseline/Below Baseline)
- 10 new unit tests covering carbon projection and biodiversity scoring
### Improved
- README updated with carbon projection table and biodiversity classification usage

## [1.2.0] - 2026-03-04
### Added
- `nbs_kpi_summary()`: portfolio-level KPIs (area, carbon credits, sequestration, biodiversity)
- `carbon_progress_chart_data()`: time-series cumulative credits for progress charts
- Multi-country NbS project sample data (Thailand, Indonesia, Vietnam, China)
- 13 unit tests covering KPI math, chart data preparation, and validation
### Fixed
- `validate()` checks for project_id and area_ha columns
- Missing numeric values filled with 0 (appropriate for credits/counts)
## [1.1.0] - 2026-03-02
### Added
- Add custom theme engine and real-time metric alerts
- Improved unit test coverage
- Enhanced documentation with realistic examples
