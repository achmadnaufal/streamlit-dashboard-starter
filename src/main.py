"""
Streamlit dashboard starter kit for NbS carbon and biodiversity KPI tracking.

Provides reusable components for building NbS project dashboards: carbon credit
calculations, biodiversity scoring, area progress tracking, and reporting
metrics aligned with Verra VCS and Gold Standard frameworks.

Author: github.com/achmadnaufal
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List


class StreamlitDashboardStarter:
    """
    NbS project KPI dashboard components.

    Computes and structures KPI data for Streamlit NbS dashboards:
    carbon credit issuance, area planted progress, biodiversity scores,
    and project timeline tracking.

    Args:
        config: Optional dict with keys:
            - emission_factor_t_ha: Default tCO2/ha/year for carbon calc (default 8.5)
            - biodiversity_baseline: Minimum biodiversity score (default 50)

    Example:
        >>> dash = StreamlitDashboardStarter(config={"emission_factor_t_ha": 8.5})
        >>> df = dash.load_data("data/project_data.csv")
        >>> kpis = dash.nbs_kpi_summary(df)
        >>> print(kpis)
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.emission_factor = self.config.get("emission_factor_t_ha", 8.5)
        self.biodiversity_baseline = self.config.get("biodiversity_baseline", 50)

    def load_data(self, filepath: str) -> pd.DataFrame:
        """
        Load NbS project data from CSV or Excel.

        Args:
            filepath: Path to file. Expected columns: project_id, country,
                      area_ha, species_count, carbon_credits_issued, period.

        Returns:
            DataFrame with project data.

        Raises:
            FileNotFoundError: If file does not exist.
        """
        p = Path(filepath)
        if not p.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        if p.suffix in (".xlsx", ".xls"):
            return pd.read_excel(filepath)
        return pd.read_csv(filepath)

    def validate(self, df: pd.DataFrame) -> bool:
        """
        Validate NbS project data.

        Args:
            df: DataFrame to validate.

        Returns:
            True if valid.

        Raises:
            ValueError: If empty or missing required columns.
        """
        if df.empty:
            raise ValueError("Input DataFrame is empty")
        df_cols = [c.lower().strip().replace(" ", "_") for c in df.columns]
        required = ["project_id", "area_ha"]
        missing = [c for c in required if c not in df_cols]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return True

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names and fill missing values."""
        df = df.copy()
        df.dropna(how="all", inplace=True)
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
        num_cols = df.select_dtypes(include="number").columns
        for col in num_cols:
            if df[col].isnull().any():
                df[col].fillna(0, inplace=True)
        return df

    def nbs_kpi_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate NbS portfolio KPI summary for dashboard header metrics.

        Computes total area, carbon credits, biodiversity status, and
        project count across the portfolio.

        Args:
            df: NbS project DataFrame with area_ha and optional columns:
                carbon_credits_issued, species_count, status.

        Returns:
            Dict with:
                - total_projects: Number of active projects
                - total_area_ha: Total restoration area (hectares)
                - total_carbon_credits_tco2: Issued carbon credits
                - estimated_annual_sequestration_tco2: Area × emission factor
                - avg_biodiversity_score: Mean species count / diversity score
                - projects_by_country: Dict of {country: project_count}
                - projects_by_status: Dict of {status: count}
        """
        df = self.preprocess(df)

        total_area = float(df["area_ha"].sum())
        total_credits = float(df["carbon_credits_issued"].sum()) if "carbon_credits_issued" in df.columns else 0.0
        annual_seq = total_area * self.emission_factor

        avg_biodiversity = None
        if "species_count" in df.columns:
            avg_biodiversity = round(float(df["species_count"].mean()), 1)
        elif "biodiversity_score" in df.columns:
            avg_biodiversity = round(float(df["biodiversity_score"].mean()), 1)

        countries = {}
        if "country" in df.columns:
            countries = df.groupby("country").size().to_dict()

        statuses = {}
        if "status" in df.columns:
            statuses = df.groupby("status").size().to_dict()

        return {
            "total_projects": int(df["project_id"].nunique()),
            "total_area_ha": round(total_area, 1),
            "total_carbon_credits_tco2": round(total_credits, 1),
            "estimated_annual_sequestration_tco2": round(annual_seq, 1),
            "avg_biodiversity_score": avg_biodiversity,
            "projects_by_country": countries,
            "projects_by_status": statuses,
        }

    def carbon_progress_chart_data(
        self, df: pd.DataFrame, target_credits: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Prepare time-series data for carbon credit issuance progress chart.

        Args:
            df: Project DataFrame with period and carbon_credits_issued columns.
            target_credits: Annual target for progress % calculation.

        Returns:
            DataFrame with period, cumulative_credits, period_credits,
            and progress_pct (if target provided).
        """
        df = self.preprocess(df)
        if "carbon_credits_issued" not in df.columns:
            raise ValueError("Column 'carbon_credits_issued' required")
        if "period" not in df.columns:
            raise ValueError("Column 'period' required for time-series chart")

        period_totals = df.groupby("period")["carbon_credits_issued"].sum().sort_index()
        result = pd.DataFrame({
            "period": period_totals.index,
            "period_credits": period_totals.values,
        })
        result["cumulative_credits"] = result["period_credits"].cumsum()
        if target_credits and target_credits > 0:
            result["progress_pct"] = (result["cumulative_credits"] / target_credits * 100).round(2)
        return result

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run descriptive analysis and return summary metrics."""
        df = self.preprocess(df)
        result = {
            "total_records": len(df),
            "columns": list(df.columns),
            "missing_pct": (df.isnull().sum() / len(df) * 100).round(1).to_dict(),
        }
        numeric_df = df.select_dtypes(include="number")
        if not numeric_df.empty:
            result["summary_stats"] = numeric_df.describe().round(3).to_dict()
            result["totals"] = numeric_df.sum().round(2).to_dict()
            result["means"] = numeric_df.mean().round(3).to_dict()
        return result

    def run(self, filepath: str) -> Dict[str, Any]:
        """Full pipeline: load → validate → analyze."""
        df = self.load_data(filepath)
        self.validate(df)
        return self.analyze(df)

    def to_dataframe(self, result: Dict) -> pd.DataFrame:
        """Convert result dict to flat DataFrame for export."""
        rows = []
        for k, v in result.items():
            if isinstance(v, dict):
                for kk, vv in v.items():
                    rows.append({"metric": f"{k}.{kk}", "value": vv})
            else:
                rows.append({"metric": k, "value": v})
        return pd.DataFrame(rows)
