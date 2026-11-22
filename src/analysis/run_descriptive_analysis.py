"""Produce descriptive FairWork research outputs from the curated DuckDB marts.

This is intentionally a descriptive workflow. It does not estimate effects,
assign annual outcomes to cabinets, or infer causality from coincident trends.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = ROOT / "data" / "processed" / "fairwork.duckdb"
ANALYSIS_DIR = ROOT / "data" / "processed" / "analysis"
FIGURE_DIR = ROOT / "reports" / "figures"
REPORT_PATH = ROOT / "reports" / "phase_5_descriptive_results.md"
COUNTRIES = ("DEU", "ESP", "FRA", "SWE")
COUNTRY_LABELS = {"DEU": "Germany", "ESP": "Spain", "FRA": "France", "SWE": "Sweden"}
METRICS = (
    ("pay_gap_value", "pay_gap_flag", "Unadjusted gender pay gap (%)"),
    ("employment_gap_value", "employment_gap_flag", "Gender employment gap (percentage points)"),
)


def query_rows(connection: duckdb.DuckDBPyConnection, statement: str) -> list[dict[str, Any]]:
    cursor = connection.execute(statement)
    fields = [column[0] for column in cursor.description]
    return [dict(zip(fields, row, strict=True)) for row in cursor.fetchall()]


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def first_last_summary(rows: list[dict[str, Any]], value_field: str, flag_field: str, metric_label: str) -> list[dict[str, Any]]:
    """Summarize first-to-last observed values without imputing missing years."""
    summaries: list[dict[str, Any]] = []
    for country in COUNTRIES:
        observations = sorted(
            (row for row in rows if row["country_iso3"] == country and row[value_field] is not None),
            key=lambda row: row["observation_year"],
        )
        if not observations:
            continue
        first, last = observations[0], observations[-1]
        summaries.append(
            {
                "country_iso3": country,
                "country_name": COUNTRY_LABELS[country],
                "metric": metric_label,
                "observations": len(observations),
                "first_year": first["observation_year"],
                "first_value": first[value_field],
                "last_year": last["observation_year"],
                "last_value": last[value_field],
                "net_change": last[value_field] - first[value_field],
                "minimum_value": min(row[value_field] for row in observations),
                "maximum_value": max(row[value_field] for row in observations),
                "flagged_observations": sum(bool(row[flag_field]) for row in observations),
            }
        )
    return summaries


def flag_sensitivity(rows: list[dict[str, Any]], value_field: str, flag_field: str, metric_label: str) -> list[dict[str, Any]]:
    """Compare full first-to-last change with a flag-excluded descriptive view."""
    results: list[dict[str, Any]] = []
    for country in COUNTRIES:
        observations = sorted(
            (row for row in rows if row["country_iso3"] == country and row[value_field] is not None),
            key=lambda row: row["observation_year"],
        )
        unflagged = [row for row in observations if not row[flag_field]]
        full_change = observations[-1][value_field] - observations[0][value_field]
        unflagged_change = unflagged[-1][value_field] - unflagged[0][value_field] if len(unflagged) >= 2 else None
        results.append(
            {
                "country_iso3": country,
                "country_name": COUNTRY_LABELS[country],
                "metric": metric_label,
                "all_observations": len(observations),
                "flagged_observations": len(observations) - len(unflagged),
                "full_window_change": full_change,
                "unflagged_observations": len(unflagged),
                "unflagged_window_change": unflagged_change,
                "change_difference": unflagged_change - full_change if unflagged_change is not None else None,
            }
        )
    return results


def plot_outcomes(rows: list[dict[str, Any]], cabinet_rows: list[dict[str, Any]]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(4, 2, figsize=(11, 10), sharex=True, constrained_layout=True)
    colors = {"DEU": "#4c78a8", "ESP": "#f58518", "FRA": "#54a24b", "SWE": "#e45756"}
    for row_index, country in enumerate(COUNTRIES):
        transition_years = sorted(
            cabinet["start_date"].year + (cabinet["start_date"].timetuple().tm_yday - 1) / 365.25
            for cabinet in cabinet_rows
            if cabinet["country_iso3"] == country and date(2010, 1, 1) <= cabinet["start_date"] < date(2023, 1, 1)
        )
        for column_index, (value_field, _flag_field, title) in enumerate(METRICS):
            axis = axes[row_index][column_index]
            observations = sorted(
                (row for row in rows if row["country_iso3"] == country and row[value_field] is not None),
                key=lambda row: row["observation_year"],
            )
            axis.plot(
                [row["observation_year"] for row in observations],
                [row[value_field] for row in observations],
                marker="o",
                linewidth=1.8,
                color=colors[country],
            )
            for year in transition_years:
                axis.axvline(year, color="#777777", linewidth=0.7, linestyle="--", alpha=0.5, zorder=0)
            axis.set_title(f"{COUNTRY_LABELS[country]} — {title}", fontsize=10)
            axis.set_ylabel("Percent" if value_field == "pay_gap_value" else "Percentage points")
            axis.grid(axis="y", alpha=0.25)
            if row_index == len(COUNTRIES) - 1:
                axis.set_xlabel("Observation year")
    figure.suptitle("FairWork descriptive outcome trends (not causal estimates)", fontsize=13)
    figure.savefig(FIGURE_DIR / "outcome_trends_with_cabinet_markers.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def plot_policy(policy_rows: list[dict[str, Any]]) -> None:
    figure, axis = plt.subplots(figsize=(10, 4.8), constrained_layout=True)
    for country in COUNTRIES:
        observations = sorted(
            (row for row in policy_rows if row["country_iso3"] == country),
            key=lambda row: row["observation_year"],
        )
        axis.plot(
            [row["observation_year"] for row in observations],
            [row["value"] for row in observations],
            marker="o",
            linewidth=1.8,
            label=COUNTRY_LABELS[country],
        )
    axis.set_title("Registered ECEC enrolment, children aged 0–2 (OECD PF3.2)")
    axis.set_xlabel("Observation year")
    axis.set_ylabel("Percent")
    axis.grid(axis="y", alpha=0.25)
    axis.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    figure.savefig(FIGURE_DIR / "policy_context_trends.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def plot_cabinet_timeline(cabinet_rows: list[dict[str, Any]]) -> None:
    figure, axis = plt.subplots(figsize=(10, 4.8), constrained_layout=True)
    colors = {"DEU": "#4c78a8", "ESP": "#f58518", "FRA": "#54a24b", "SWE": "#e45756"}
    start_bound = date(2010, 1, 1)
    end_bound = date(2023, 1, 1)
    for index, country in enumerate(COUNTRIES):
        for cabinet in (row for row in cabinet_rows if row["country_iso3"] == country):
            start = max(cabinet["start_date"], start_bound)
            end = min(cabinet["end_date_exclusive"] or end_bound, end_bound)
            if end <= start:
                continue
            axis.barh(
                index,
                mdates.date2num(end) - mdates.date2num(start),
                left=mdates.date2num(start),
                height=0.55,
                color=colors[country],
                edgecolor="white",
            )
    axis.set_yticks(range(len(COUNTRIES)), [COUNTRY_LABELS[country] for country in COUNTRIES])
    axis.xaxis_date()
    axis.xaxis.set_major_locator(mdates.YearLocator(2))
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axis.set_xlim(start_bound, end_bound)
    axis.set_title("Documented cabinet periods (ParlGov); periods are not annualised")
    axis.set_xlabel("Date")
    figure.savefig(FIGURE_DIR / "cabinet_period_timeline.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def markdown_table(rows: list[dict[str, Any]], fields: list[str]) -> list[str]:
    header = "| " + " | ".join(field.replace("_", " ") for field in fields) + " |"
    divider = "| " + " | ".join("---" for _ in fields) + " |"
    formatted = [header, divider]
    for row in rows:
        values = []
        for field in fields:
            value = row[field]
            values.append(f"{value:.2f}" if isinstance(value, float) else str(value if value is not None else "—"))
        formatted.append("| " + " | ".join(values) + " |")
    return formatted


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Run the Phase 4 warehouse build before descriptive analysis.")
    connection = duckdb.connect(str(DATABASE_PATH), read_only=True)
    try:
        country_year_rows = query_rows(
            connection,
            """
            select country_iso3, observation_year, pay_gap_value, pay_gap_flag,
                   employment_gap_value, employment_gap_flag,
                   enrolment_0_2_registered_ecec_pct
            from analytics.mart_country_year
            order by country_iso3, observation_year
            """,
        )
        policy_rows = query_rows(
            connection,
            """
            select country_iso3, observation_year, indicator, value, unit, source_id
            from analytics.fact_policy_indicator
            order by country_iso3, observation_year
            """,
        )
        cabinet_rows = query_rows(
            connection,
            """
            select country_iso3, parlgov_cabinet_id, cabinet_name, start_date,
                   end_date_exclusive, caretaker, transition_type
            from analytics.mart_cabinet_transition
            order by country_iso3, start_date
            """,
        )
    finally:
        connection.close()

    outcome_summaries = [
        summary
        for value_field, flag_field, label in METRICS
        for summary in first_last_summary(country_year_rows, value_field, flag_field, label)
    ]
    sensitivity_rows = [
        summary
        for value_field, flag_field, label in METRICS
        for summary in flag_sensitivity(country_year_rows, value_field, flag_field, label)
    ]
    flag_counts: Counter[tuple[str, str]] = Counter()
    for value_field, flag_field, label in METRICS:
        for row in country_year_rows:
            flag_counts[(label, row[flag_field] or "none")] += 1
    coverage_rows = [
        {
            "asset": "Gender outcome facts",
            "expected_rows": 104,
            "observed_rows": len(country_year_rows) * 2,
            "coverage_window": "2010-2022",
        },
        {
            "asset": "Country-year mart",
            "expected_rows": 52,
            "observed_rows": len(country_year_rows),
            "coverage_window": "2010-2022",
        },
        {
            "asset": "OECD policy facts",
            "expected_rows": 32,
            "observed_rows": len(policy_rows),
            "coverage_window": "2015-2022",
        },
        {
            "asset": "Cabinet periods",
            "expected_rows": 34,
            "observed_rows": len(cabinet_rows),
            "coverage_window": "2010-2022",
        },
    ]
    cabinet_summary = [
        {
            "country_iso3": country,
            "country_name": COUNTRY_LABELS[country],
            "cabinet_periods": sum(row["country_iso3"] == country for row in cabinet_rows),
            "cabinet_changes_after_first": sum(
                row["country_iso3"] == country and row["transition_type"] == "cabinet_change" for row in cabinet_rows
            ),
        }
        for country in COUNTRIES
    ]
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(ANALYSIS_DIR / "coverage_summary.csv", coverage_rows, list(coverage_rows[0]))
    write_csv(ANALYSIS_DIR / "country_metric_summary.csv", outcome_summaries, list(outcome_summaries[0]))
    write_csv(ANALYSIS_DIR / "flag_sensitivity_summary.csv", sensitivity_rows, list(sensitivity_rows[0]))
    write_csv(ANALYSIS_DIR / "cabinet_transition_summary.csv", cabinet_summary, list(cabinet_summary[0]))
    write_csv(
        ANALYSIS_DIR / "outcome_flag_summary.csv",
        [
            {"metric": metric, "observation_flag": flag, "observations": count}
            for (metric, flag), count in sorted(flag_counts.items())
        ],
        ["metric", "observation_flag", "observations"],
    )
    plot_outcomes(country_year_rows, cabinet_rows)
    plot_policy(policy_rows)
    plot_cabinet_timeline(cabinet_rows)

    report_lines = [
        "# Phase 5 descriptive results",
        "",
        "**Status:** Descriptive baseline complete; no causal analysis has been performed.  ",
        "**Scope:** Germany, Spain, France and Sweden; outcomes 2010–2022; OECD policy context 2015–2022.",
        "",
        "## Coverage and data quality",
        "",
        *markdown_table(coverage_rows, ["asset", "expected_rows", "observed_rows", "coverage_window"]),
        "",
        "Eurostat status flags remain attached to the outcome facts. The accompanying `outcome_flag_summary.csv` lists their distribution; they are not silently removed or recoded.",
        "",
        "## First-to-last descriptive changes",
        "",
        "The figures below compare the first and last available observation within each country. They describe observed movement only; they are not estimates of a government or policy effect.",
        "",
        *markdown_table(
            outcome_summaries,
            ["country_name", "metric", "first_year", "first_value", "last_year", "last_value", "net_change", "flagged_observations"],
        ),
        "",
        "![Outcome trends with cabinet markers](figures/outcome_trends_with_cabinet_markers.png)",
        "",
        "Dashed lines show pilot-country cabinet starts. They are visual context only: one annual outcome must not be attributed to a cabinet solely because its date overlaps a calendar year.",
        "",
        "![Policy context trends](figures/policy_context_trends.png)",
        "",
        "![Cabinet-period timeline](figures/cabinet_period_timeline.png)",
        "",
        "## Flag sensitivity and cabinet coverage",
        "",
        "The sensitivity table compares the full first-to-last window to a view excluding observations carrying a Eurostat status flag. A changed window can change the comparison even when the underlying series is valid, so this is a transparency check rather than a correction.",
        "",
        *markdown_table(
            sensitivity_rows,
            ["country_name", "metric", "flagged_observations", "full_window_change", "unflagged_window_change", "change_difference"],
        ),
        "",
        *markdown_table(cabinet_summary, ["country_name", "cabinet_periods", "cabinet_changes_after_first"]),
        "",
        "## Interpretation limits",
        "",
        "- This four-country panel is too small and too confounded to support causal conclusions from these descriptive comparisons.",
        "- CHES party positions remain survey-wave measures and are not used here as annual government ideology values.",
        "- The OECD ECEC indicator is policy context, not evidence that a named government enacted or caused a policy outcome.",
        "- Future analysis must report the Eurostat flags, missingness and the political crosswalk review queue alongside any charts or model outputs.",
        "",
        "## Reproduction",
        "",
        "```powershell",
        "python -m src.analytics.build_warehouse",
        "python -m src.analysis.run_descriptive_analysis",
        "```",
    ]
    REPORT_PATH.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"Wrote descriptive tables to {ANALYSIS_DIR.relative_to(ROOT)}")
    print(f"Wrote figures to {FIGURE_DIR.relative_to(ROOT)}")
    print(f"Wrote report to {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
