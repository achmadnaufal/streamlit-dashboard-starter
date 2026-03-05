"""Unit tests for StreamlitDashboardStarter."""
import pytest
import pandas as pd
import sys
sys.path.insert(0, "/Users/johndoe/projects/streamlit-dashboard-starter")
from src.main import StreamlitDashboardStarter


@pytest.fixture
def project_df():
    return pd.DataFrame({
        "project_id": ["NBS-TH-01", "NBS-ID-01", "NBS-VN-01", "NBS-CN-01", "NBS-TH-02"],
        "country": ["Thailand", "Indonesia", "Vietnam", "China", "Thailand"],
        "area_ha": [1250.0, 850.0, 620.0, 2100.0, 980.0],
        "species_count": [45, 38, 52, 60, 42],
        "carbon_credits_issued": [18750, 12750, 9300, 31500, 14700],
        "period": ["2025-Q1", "2025-Q1", "2025-Q1", "2025-Q2", "2025-Q2"],
        "status": ["Active", "Active", "Pending", "Active", "Active"],
    })


@pytest.fixture
def dash():
    return StreamlitDashboardStarter(config={"emission_factor_t_ha": 8.5})


class TestValidation:
    def test_empty_raises(self, dash):
        with pytest.raises(ValueError, match="empty"):
            dash.validate(pd.DataFrame())

    def test_missing_columns_raises(self, dash):
        df = pd.DataFrame({"project_id": ["X"], "country": ["Thailand"]})
        with pytest.raises(ValueError, match="Missing required columns"):
            dash.validate(df)

    def test_valid_passes(self, dash, project_df):
        assert dash.validate(project_df) is True


class TestNbsKpiSummary:
    def test_returns_expected_keys(self, dash, project_df):
        result = dash.nbs_kpi_summary(project_df)
        assert "total_projects" in result
        assert "total_area_ha" in result
        assert "total_carbon_credits_tco2" in result
        assert "estimated_annual_sequestration_tco2" in result

    def test_total_area_correct(self, dash, project_df):
        result = dash.nbs_kpi_summary(project_df)
        expected = project_df["area_ha"].sum()
        assert abs(result["total_area_ha"] - expected) < 0.1

    def test_sequestration_uses_emission_factor(self, dash, project_df):
        result = dash.nbs_kpi_summary(project_df)
        expected_seq = project_df["area_ha"].sum() * 8.5
        assert abs(result["estimated_annual_sequestration_tco2"] - expected_seq) < 1.0

    def test_projects_by_country(self, dash, project_df):
        result = dash.nbs_kpi_summary(project_df)
        assert "Thailand" in result["projects_by_country"]
        assert result["projects_by_country"]["Thailand"] == 2

    def test_avg_biodiversity_present(self, dash, project_df):
        result = dash.nbs_kpi_summary(project_df)
        assert result["avg_biodiversity_score"] is not None

    def test_total_carbon_credits(self, dash, project_df):
        result = dash.nbs_kpi_summary(project_df)
        expected = project_df["carbon_credits_issued"].sum()
        assert abs(result["total_carbon_credits_tco2"] - expected) < 1.0


class TestCarbonProgressChartData:
    def test_returns_dataframe(self, dash, project_df):
        result = dash.carbon_progress_chart_data(project_df, target_credits=100000)
        assert isinstance(result, pd.DataFrame)

    def test_cumulative_increasing(self, dash, project_df):
        result = dash.carbon_progress_chart_data(project_df)
        assert (result["cumulative_credits"].diff().dropna() >= 0).all()

    def test_progress_pct_with_target(self, dash, project_df):
        result = dash.carbon_progress_chart_data(project_df, target_credits=100000)
        assert "progress_pct" in result.columns

    def test_missing_period_raises(self, dash):
        df = pd.DataFrame({"project_id": ["X"], "area_ha": [100], "carbon_credits_issued": [1000]})
        with pytest.raises(ValueError, match="period"):
            dash.carbon_progress_chart_data(df)


class TestCarbonCreditProjection:
    def test_returns_dataframe(self, dash, project_df):
        result = dash.carbon_credit_projection(project_df)
        assert isinstance(result, pd.DataFrame)

    def test_default_5_years(self, dash, project_df):
        result = dash.carbon_credit_projection(project_df)
        assert len(result) == 5

    def test_cumulative_credits_increasing(self, dash, project_df):
        result = dash.carbon_credit_projection(project_df)
        cum = result["cumulative_credits_tco2"].tolist()
        assert cum == sorted(cum)

    def test_negative_price_raises(self, dash, project_df):
        with pytest.raises(ValueError, match="positive"):
            dash.carbon_credit_projection(project_df, price_per_credit_usd=-5.0)

    def test_missing_area_ha_raises(self, dash):
        df = pd.DataFrame({"project_id": ["P1"], "species_count": [30]})
        with pytest.raises(ValueError, match="area_ha"):
            dash.carbon_credit_projection(df)

    def test_custom_years(self, dash, project_df):
        result = dash.carbon_credit_projection(project_df, years=10)
        assert len(result) == 10


class TestBiodiversityScore:
    def test_returns_dataframe(self, dash, project_df):
        result = dash.biodiversity_score(project_df)
        assert isinstance(result, pd.DataFrame)

    def test_score_in_range(self, dash, project_df):
        result = dash.biodiversity_score(project_df)
        assert (result["biodiversity_score"] >= 0).all()
        assert (result["biodiversity_score"] <= 100).all()

    def test_classification_column(self, dash, project_df):
        result = dash.biodiversity_score(project_df)
        valid_classes = {"Excellent", "Good", "Baseline", "Below Baseline"}
        assert set(result["classification"]).issubset(valid_classes)

    def test_missing_species_raises(self, dash):
        df = pd.DataFrame({"project_id": ["P1"], "area_ha": [100.0]})
        with pytest.raises(ValueError, match="Missing columns"):
            dash.biodiversity_score(df)
