"""Curated-data access and filtering helpers for the local dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PUBLISHED_DIR = ROOT / "data" / "published"
COUNTRY_NAMES = {"DEU": "Germany", "ESP": "Spain", "FRA": "France", "SWE": "Sweden"}
METRICS = {
    "Unadjusted gender pay gap (%)": {
        "value": "pay_gap_value",
        "flag": "pay_gap_flag",
        "unit": "percent",
        "source": "Eurostat sdg_05_20; annual, B-S_X_O, PC",
    },
    "Gender employment gap (percentage points)": {
        "value": "employment_gap_value",
        "flag": "employment_gap_flag",
        "unit": "percentage points",
        "source": "Eurostat sdg_05_30; annual, age Y20-64, wstatus EMP, PC_PNT",
    },
}


def required_paths() -> dict[str, Path]:
    return {
        "country_year": PUBLISHED_DIR / "mart_country_year.parquet",
        "cabinet": PUBLISHED_DIR / "mart_cabinet_transition.parquet",
        "policy": PUBLISHED_DIR / "fact_policy_indicator.parquet",
        "party_positions": PUBLISHED_DIR / "fact_ches_party_position.parquet",
        "cabinet_memberships": PUBLISHED_DIR / "bridge_cabinet_party_membership.parquet",
    }


def load_curated_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = required_paths()
    missing = [str(path.relative_to(ROOT)) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Curated dashboard inputs are missing. Run `python -m src.analytics.export_curated_data` first: "
            + ", ".join(missing)
        )
    country_year = pd.read_parquet(paths["country_year"])
    cabinets = pd.read_parquet(paths["cabinet"])
    policy = pd.read_parquet(paths["policy"])
    party_positions = pd.read_parquet(paths["party_positions"])
    cabinet_memberships = pd.read_parquet(paths["cabinet_memberships"])
    cabinets["start_date"] = pd.to_datetime(cabinets["start_date"])
    cabinets["end_date_exclusive"] = pd.to_datetime(cabinets["end_date_exclusive"])
    return country_year, cabinets, policy, party_positions, cabinet_memberships


def filter_years(frame: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    return frame.loc[frame["observation_year"].between(start_year, end_year)].copy()


def exclude_flagged_observations(frame: pd.DataFrame) -> pd.DataFrame:
    """Keep observations with no retained source-status flag.

    This is an inspection control, not a replacement for the full series: the
    dashboard always tells the reader when it has been applied.
    """
    return frame.loc[frame["observation_flag"].fillna("").eq("")].copy()


def metric_frame(frame: pd.DataFrame, metric_name: str) -> pd.DataFrame:
    specification = METRICS[metric_name]
    selected = frame[["country_iso3", "country_name", "observation_year", specification["value"], specification["flag"]]].copy()
    selected.columns = ["country_iso3", "country_name", "observation_year", "value", "observation_flag"]
    return selected
