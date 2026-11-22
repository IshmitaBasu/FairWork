"""Local FairWork Streamlit dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from src.dashboard.data import (
    COUNTRY_NAMES,
    METRICS,
    exclude_flagged_observations,
    filter_years,
    load_curated_data,
    metric_frame,
)


st.set_page_config(page_title="FairWork | European equality explorer", page_icon="⚖️", layout="wide")


@st.cache_data(show_spinner=False)
def get_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return load_curated_data()


def inject_styles() -> None:
    st.markdown(
        """
        <style>
          .stApp { background: #f6f8fc; }
          [data-testid="stSidebar"] { background: linear-gradient(180deg, #11233f 0%, #1f4674 100%); }
          [data-testid="stSidebar"] * { color: #f8fbff; }
          [data-testid="stSidebar"] [data-baseweb="select"] * { color: #172033; }
          [data-testid="stSidebar"] .selection-summary { background: #e7f3fb; border: 1px solid #8dc6e3; border-radius: 12px; padding: .7rem .8rem; margin: .2rem 0 .8rem; }
          [data-testid="stSidebar"] .selection-summary, [data-testid="stSidebar"] .selection-summary * { color: #10233f; }
          .fairwork-hero { background: linear-gradient(115deg, #10233f 0%, #235b89 58%, #4b8f8c 100%); border-radius: 22px; padding: 2rem 2.2rem 1.7rem; color: white; margin: .2rem 0 1.25rem; box-shadow: 0 12px 32px rgba(27, 61, 102, .20); }
          .fairwork-hero h1 { font-size: 2.45rem; margin: 0; color: white; }
          .fairwork-hero p { font-size: 1.05rem; max-width: 52rem; margin: .45rem 0 0; color: #e5f2fa; }
          .section-kicker { color: #2f6f95; font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
          .spectrum-labels { display: flex; justify-content: space-between; font-weight: 700; margin: .2rem .4rem 1rem; }
          .spectrum-left { color: #2563eb; } .spectrum-centre { color: #7c3aed; } .spectrum-right { color: #dc2626; }
          [data-testid="stMetric"] { background: white; border-radius: 14px; padding: .85rem 1rem; border: 1px solid #e0e8f0; }
          .stTabs [data-baseweb="tab-list"] { gap: .35rem; }
          .stTabs [data-baseweb="tab"] { background: #e9eff5; border-radius: 999px; padding: .5rem 1rem; }
          .stTabs [aria-selected="true"] { background: #1f628d !important; color: white !important; }
          :focus-visible { outline: 3px solid #f18f01 !important; outline-offset: 3px; }
          @media (max-width: 700px) { .fairwork-hero { padding: 1.35rem; border-radius: 16px; } .fairwork-hero h1 { font-size: 1.8rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def decimal_year(timestamp: pd.Timestamp) -> float:
    return timestamp.year + (timestamp.day_of_year - 1) / 365.25


def add_cabinet_markers(figure: go.Figure, cabinets: pd.DataFrame, country: str, start_year: int, end_year: int) -> None:
    starts = cabinets.loc[
        (cabinets["country_iso3"] == country)
        & (cabinets["start_date"].dt.year.between(start_year, end_year))
    ].sort_values("start_date")
    for cabinet in starts.itertuples():
        start = decimal_year(cabinet.start_date)
        figure.add_vline(x=start, line_dash="dot", line_color="#4b5563", opacity=0.58)
        figure.add_annotation(x=start, y=1, yref="paper", text=cabinet.cabinet_name, showarrow=False, textangle=-90, yanchor="bottom", font={"size": 10, "color": "#475467"})


def observed_change(values: pd.DataFrame) -> tuple[str, str]:
    ordered = values.sort_values("observation_year")
    if len(ordered) < 2:
        return "—", "Fewer than two observations"
    first, last = ordered.iloc[0], ordered.iloc[-1]
    return f"{last.value - first.value:+.1f}", f"{int(first.observation_year)}–{int(last.observation_year)} observed change"


def outcome_chart(values: pd.DataFrame, cabinets: pd.DataFrame, country: str, start_year: int, end_year: int, metadata: dict[str, str], show_markers: bool) -> go.Figure:
    figure = px.area(values, x="observation_year", y="value", markers=True, labels={"observation_year": "Observation year", "value": metadata["unit"]}, template="plotly_white", color_discrete_sequence=["#2E86AB"])
    figure.update_traces(fillcolor="rgba(46, 134, 171, .16)", line={"width": 3}, marker={"size": 8})
    if show_markers:
        add_cabinet_markers(figure, cabinets, country, start_year, end_year)
    figure.update_layout(height=420, margin={"l": 8, "r": 8, "t": 22, "b": 8}, hovermode="x unified")
    return figure


def political_spectrum_chart(parties: pd.DataFrame) -> go.Figure:
    ordered = parties.sort_values("lrgen")
    for field in ("parlgov_party_name", "vote_share_pct", "seat_share_pct", "womens_rights_position"):
        if field not in ordered:
            ordered[field] = None
    vote_size = ordered.vote_share_pct.fillna(4).clip(lower=2)
    figure = go.Figure()
    figure.add_vrect(x0=0, x1=3.33, fillcolor="#dbeafe", opacity=0.72, line_width=0)
    figure.add_vrect(x0=3.33, x1=6.67, fillcolor="#ede9fe", opacity=0.72, line_width=0)
    figure.add_vrect(x0=6.67, x1=10, fillcolor="#fee2e2", opacity=0.72, line_width=0)
    figure.add_trace(go.Scatter(
        x=ordered.lrgen, y=ordered.party_name, mode="markers+text", text=ordered.party_name, textposition="middle right",
        marker={"size": vote_size * 1.25 + 8, "color": ordered.lrgen, "colorscale": [[0, "#2563eb"], [0.5, "#7c3aed"], [1, "#dc2626"]], "cmin": 0, "cmax": 10, "line": {"color": "white", "width": 1.5}, "showscale": True, "colorbar": {"title": "CHES left-right", "tickvals": [0, 5, 10], "ticktext": ["0 Left", "5", "10 Right"]}},
        customdata=ordered[["parlgov_party_name", "vote_share_pct", "seat_share_pct", "womens_rights_position"]],
        hovertemplate="<b>%{y}</b><br>CHES general left-right: %{x:.1f} / 10<br>ParlGov match: %{customdata[0]}<br>Vote share: %{customdata[1]:.1f}%<br>Seat share: %{customdata[2]:.1f}%<br>CHES women's-rights position: %{customdata[3]:.1f}<extra></extra>",
    ))
    figure.update_layout(xaxis={"range": [-0.2, 10.8], "dtick": 1, "title": "CHES general left-right position (0 = left, 10 = right)"}, yaxis={"title": "", "automargin": True}, height=max(420, len(ordered) * 57), margin={"l": 8, "r": 55, "t": 22, "b": 10}, template="plotly_white", showlegend=False)
    return figure


def chart_png(figure: go.Figure) -> bytes | None:
    """Return a PNG download when the local Plotly renderer is available."""
    try:
        return pio.to_image(figure, format="png", scale=2)
    except Exception:
        return None


def show_chart_download(figure: go.Figure, filename: str, key: str) -> None:
    state_key = f"{key}_image"
    if st.button("Prepare PNG download", key=f"{key}_prepare"):
        with st.spinner("Preparing PNG…"):
            image = chart_png(figure)
        if image is None:
            st.warning("PNG export could not start in this local setup. Try the interactive chart in the browser or install a supported local Chrome runtime.")
        else:
            st.session_state[state_key] = image
    if image := st.session_state.get(state_key):
        st.download_button("Download chart as PNG", image, file_name=filename, mime="image/png", key=key)


def quality_summary(values: pd.DataFrame, metric_name: str) -> str:
    flags = int(values.observation_flag.fillna("").ne("").sum())
    if values.empty:
        return "No observations are available for this selection."
    first_year = int(values.observation_year.min())
    last_year = int(values.observation_year.max())
    return f"{len(values)} annual observations, {first_year}–{last_year}; {flags} retained Eurostat flag(s)."


def political_band(position: float) -> str:
    if position <= 3.33:
        return "Left (0–3.3)"
    if position < 6.67:
        return "Centre (3.4–6.6)"
    return "Right (6.7–10)"


def cabinet_event_chart(values: pd.DataFrame, cabinet: pd.Series, metric_name: str) -> go.Figure:
    figure = px.line(
        values,
        x="observation_year",
        y="value",
        markers=True,
        labels={"observation_year": "Observation year", "value": METRICS[metric_name]["unit"]},
        template="plotly_white",
        color_discrete_sequence=["#7851A9"],
    )
    figure.update_traces(line={"width": 3}, marker={"size": 9})
    start = decimal_year(cabinet.start_date)
    figure.add_vline(x=start, line_dash="dash", line_color="#202938", line_width=2)
    figure.add_annotation(x=start, y=1, yref="paper", text=f"{cabinet.cabinet_name} starts", showarrow=False, yanchor="bottom")
    figure.update_layout(height=390, margin={"l": 8, "r": 8, "t": 25, "b": 8}, hovermode="x unified")
    return figure


def main() -> None:
    inject_styles()
    try:
        country_year, cabinets, policy, party_positions, cabinet_memberships = get_data()
    except FileNotFoundError as error:
        st.error(str(error))
        st.stop()

    st.title("FairWork")
    st.markdown("""<div class="fairwork-hero"><h1>Explore equality outcomes with political context.</h1><p>Trace country trends, inspect documented cabinet changes, and explore party positions without turning association into causation.</p></div>""", unsafe_allow_html=True)

    with st.sidebar:
        st.header("Explore the evidence")
        country = st.selectbox(
            "Country context",
            options=list(COUNTRY_NAMES),
            format_func=COUNTRY_NAMES.get,
            help="This single country controls the overview, explorer, cabinet and political-landscape pages.",
        )
        st.markdown(
            f"<div class='selection-summary'><strong>Selected country</strong><br>{COUNTRY_NAMES[country]} ({country})</div>",
            unsafe_allow_html=True,
        )
        metric_name = st.radio("Outcome measure", options=list(METRICS), index=0)
        start_year, end_year = st.slider("Observation years", min_value=2010, max_value=2022, value=(2010, 2022))
        hide_flagged = st.toggle("Hide observations with Eurostat flags", value=False)
        show_markers = st.toggle("Show cabinet starts", value=True)
        show_guide = st.toggle("Show guided reading tips", value=False)
        with st.expander("Sources and methodology"):
            st.markdown(
                "**Outcomes:** Eurostat annual series.  \n"
                "**Policy context:** OECD PF3.2.  \n"
                "**Cabinets:** ParlGov dated periods.  \n"
                "**Party positions:** CHES expert-survey waves (2010, 2014, 2019)."
            )
            st.caption("Only approved, curated records are read. Political context is descriptive and does not establish causation.")
        st.divider()
        st.caption("Dashed cabinet markers are factual context. They do not establish an immediate government effect on annual outcomes.")

    metadata = METRICS[metric_name]
    selected_country = filter_years(country_year.loc[country_year.country_iso3 == country].copy(), start_year, end_year)
    all_selected_metric = metric_frame(selected_country, metric_name).sort_values("observation_year")
    selected_metric = exclude_flagged_observations(all_selected_metric) if hide_flagged else all_selected_metric
    selected_policy = filter_years(policy.loc[policy.country_iso3 == country].copy(), start_year, end_year)
    flagged = int(all_selected_metric.observation_flag.fillna("").ne("").sum())
    change_value, change_label = observed_change(selected_metric)
    current_value = selected_metric.sort_values("observation_year").iloc[-1].value if not selected_metric.empty else None

    overview, explorer, coalition, politics, compare, methods = st.tabs(
        ["Overview", "Country explorer", "Cabinets & events", "Political landscape", "Compare countries", "Methods & sources"]
    )

    with overview:
        st.markdown("<p class='section-kicker'>At a glance</p>", unsafe_allow_html=True)
        first, second, third, fourth = st.columns(4)
        first.metric(f"Latest {COUNTRY_NAMES[country]} value", f"{current_value:.1f}" if current_value is not None else "—", metadata["unit"])
        second.metric("Observed change", change_value, change_label)
        third.metric("Cabinet periods", int((cabinets.country_iso3 == country).sum()), "Dated periods, not annual labels")
        fourth.metric("Flagged observations", flagged, "Inspect before comparing" if flagged else "No retained flags")
        st.markdown("<p class='section-kicker'>Selected outcome</p>", unsafe_allow_html=True)
        if selected_metric.empty:
            st.warning("No observations remain after applying the current data-quality filter. Turn it off to inspect the retained source flags.")
        else:
            overview_figure = outcome_chart(selected_metric, cabinets, country, start_year, end_year, metadata, show_markers)
            st.plotly_chart(overview_figure, width="stretch", key="overview_outcome")
            show_chart_download(overview_figure, f"fairwork_{country.lower()}_{metadata['value']}.png", "overview_png")
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown("<p class='section-kicker'>Policy context</p>", unsafe_allow_html=True)
            if selected_policy.empty:
                st.info("OECD PF3.2 observations begin in 2015 for this local pilot.")
            else:
                policy_chart = px.area(selected_policy, x="observation_year", y="value", markers=True, labels={"observation_year": "Year", "value": "ECEC enrolment (%)"}, template="plotly_white", color_discrete_sequence=["#4b8f8c"])
                policy_chart.update_traces(fillcolor="rgba(75,143,140,.15)", line={"width": 3})
                policy_chart.update_layout(height=310, margin={"l": 8, "r": 8, "t": 12, "b": 8})
                st.plotly_chart(policy_chart, width="stretch", key="overview_policy")
        with right:
            st.markdown("<p class='section-kicker'>How to read this</p>", unsafe_allow_html=True)
            st.info("FairWork compares consistently defined outcomes and preserves data-quality flags. Political context, party positions, policy context and outcomes are shown together for exploration—not causal attribution.")
            st.markdown(f"**Source configuration:** {metadata['source']}")
        st.markdown("<p class='section-kicker'>What can this selection support?</p>", unsafe_allow_html=True)
        st.success(
            f"For {COUNTRY_NAMES[country]}, this view supports a descriptive statement about the observed {metric_name.lower()} between {start_year} and {end_year}. It does not show that a cabinet, left-right position or policy caused the change. Use the event-window view to inspect timing and the data-quality note before drawing conclusions."
        )
        if show_guide:
            st.success("Start with the selected outcome trend, inspect source flags, then use the Cabinet & events and Political landscape pages for separately dated political context. These views do not establish cause and effect.")

    with explorer:
        st.subheader(f"{COUNTRY_NAMES[country]}: {metric_name}")
        if selected_metric.empty:
            st.warning("No observations remain after applying the current data-quality filter.")
        else:
            explorer_figure = outcome_chart(selected_metric, cabinets, country, start_year, end_year, metadata, show_markers)
            st.plotly_chart(explorer_figure, width="stretch", key="explorer_outcome")
        quality_left, quality_right = st.columns([1.2, 0.8])
        quality_left.info(f"Data quality: {quality_summary(all_selected_metric, metric_name)}")
        quality_right.caption("Flag filter is " + ("on; flagged rows are hidden." if hide_flagged else "off; all retained source rows are shown.") + " Blank flags do not make causal conclusions safe.")
        if not selected_metric.empty:
            show_chart_download(explorer_figure, f"fairwork_{country.lower()}_explorer.png", "explorer_png")
        content, context = st.columns([1.15, 0.85])
        with content:
            st.subheader("Observed values and flags")
            st.dataframe(selected_metric, hide_index=True, width="stretch")
            st.download_button("Download displayed outcome data (CSV)", data=selected_metric.to_csv(index=False).encode("utf-8"), file_name=f"fairwork_{country.lower()}_{metadata['value']}_{start_year}_{end_year}.csv", mime="text/csv")
        with context:
            st.subheader("Cabinet context")
            country_cabinets = cabinets.loc[cabinets.country_iso3 == country].copy()
            country_cabinets["start_date"] = country_cabinets.start_date.dt.strftime("%Y-%m-%d")
            country_cabinets["end_date_exclusive"] = country_cabinets.end_date_exclusive.dt.strftime("%Y-%m-%d").fillna("Open in release")
            st.dataframe(country_cabinets[["cabinet_name", "start_date", "end_date_exclusive", "caretaker"]], column_config={"cabinet_name": "Cabinet", "start_date": "Start", "end_date_exclusive": "End", "caretaker": "Caretaker"}, hide_index=True, width="stretch")
        if flagged:
            st.warning("Selected observations carry Eurostat status flags. The codes are retained from the source and should be considered before interpreting changes.")

    with coalition:
        st.subheader(f"Cabinets and descriptive event windows: {COUNTRY_NAMES[country]}")
        country_cabinets = cabinets.loc[cabinets.country_iso3 == country].sort_values("start_date").copy()
        selected_cabinet_id = st.selectbox(
            "Select a documented cabinet period",
            options=country_cabinets.parlgov_cabinet_id.tolist(),
            format_func=lambda cabinet_id: (
                f"{country_cabinets.loc[country_cabinets.parlgov_cabinet_id == cabinet_id, 'start_date'].iloc[0].date()} — "
                f"{country_cabinets.loc[country_cabinets.parlgov_cabinet_id == cabinet_id, 'cabinet_name'].iloc[0]}"
            ),
            key="cabinet_event_selector",
        )
        selected_cabinet = country_cabinets.loc[country_cabinets.parlgov_cabinet_id == selected_cabinet_id].iloc[0]
        event_window = st.slider("Years shown before and after the cabinet start", 1, 4, 3, key="event_window")
        all_country_metric = metric_frame(country_year.loc[country_year.country_iso3 == country].copy(), metric_name)
        if hide_flagged:
            all_country_metric = exclude_flagged_observations(all_country_metric)
        start_event_year = int(selected_cabinet.start_date.year)
        event_values = all_country_metric.loc[
            all_country_metric.observation_year.between(start_event_year - event_window, start_event_year + event_window)
        ].copy()
        event_figure = cabinet_event_chart(event_values, selected_cabinet, metric_name)
        st.plotly_chart(event_figure, width="stretch", key="cabinet_event_chart")
        show_chart_download(event_figure, f"fairwork_{country.lower()}_cabinet_event.png", "event_png")
        before_count = int((event_values.observation_year < start_event_year).sum())
        after_count = int((event_values.observation_year >= start_event_year).sum())
        before, after, context_card = st.columns(3)
        before.metric("Pre-start observations", before_count)
        after.metric("Start-year and later observations", after_count)
        context_card.metric("Retained flags in window", int(event_values.observation_flag.fillna("").ne("").sum()))
        st.info("This is a descriptive timing window. It does not estimate a cabinet effect, account for lags or control for economic and social conditions.")

        st.subheader("Recorded coalition membership and separate CHES context")
        membership = cabinet_memberships.loc[cabinet_memberships.parlgov_cabinet_id == selected_cabinet_id].copy()
        country_party_positions = party_positions.loc[party_positions.country_iso3 == country].copy()
        source_waves = sorted(country_party_positions.ches_wave.unique())
        selected_source_wave = st.select_slider(
            "CHES source wave shown beside this cabinet",
            options=source_waves,
            value=min(source_waves, key=lambda wave: abs(wave - start_event_year)),
            key="coalition_source_wave",
        )
        source_positions = country_party_positions.loc[
            country_party_positions.ches_wave == selected_source_wave,
            ["ches_party_id", "party_name", "lrgen", "vote_share_pct", "seat_share_pct", "womens_rights_position"],
        ]
        membership["ches_party_id"] = pd.to_numeric(membership.ches_party_id, errors="coerce").astype("Int64")
        coalition_positions = membership.merge(source_positions, on="ches_party_id", how="left")
        accepted_positions = coalition_positions.loc[coalition_positions.lrgen.notna()].copy()
        if accepted_positions.empty:
            st.warning("No accepted party positions are available at this selected CHES wave for the parties in this cabinet.")
        else:
            accepted_positions["political_band"] = accepted_positions.lrgen.map(political_band)
            summary_left, summary_middle, summary_right = st.columns(3)
            summary_left.metric("Recorded cabinet parties", len(membership))
            summary_middle.metric("Accepted CHES positions", len(accepted_positions), f"Wave {selected_source_wave}")
            summary_right.metric("Position span", f"{accepted_positions.lrgen.min():.1f}–{accepted_positions.lrgen.max():.1f} / 10", "Not a coalition ideology score")
            composition = (
                accepted_positions.groupby("political_band", observed=True)
                .size()
                .reindex(["Left (0–3.3)", "Centre (3.4–6.6)", "Right (6.7–10)"], fill_value=0)
                .rename_axis("CHES band")
                .reset_index(name="Parties")
            )
            composition_chart = px.bar(
                composition,
                x="CHES band",
                y="Parties",
                color="CHES band",
                text="Parties",
                category_orders={"CHES band": ["Left (0–3.3)", "Centre (3.4–6.6)", "Right (6.7–10)"]},
                color_discrete_map={"Left (0–3.3)": "#2563eb", "Centre (3.4–6.6)": "#7c3aed", "Right (6.7–10)": "#dc2626"},
                template="plotly_white",
            )
            composition_chart.update_layout(height=270, margin={"l": 8, "r": 8, "t": 20, "b": 8}, showlegend=False, yaxis_title="Recorded parties with accepted positions")
            st.plotly_chart(composition_chart, width="stretch", key="coalition_composition")
            st.caption("The three bands make the cabinet's documented party composition easier to scan. They are counts at the selected survey wave, not a coalition or national ideology score.")
            st.plotly_chart(political_spectrum_chart(accepted_positions), width="stretch", key="coalition_spectrum")
        st.dataframe(
            coalition_positions[["parlgov_party_name", "mapping_status", "review_action", "lrgen", "womens_rights_position"]],
            column_config={
                "parlgov_party_name": "Cabinet party", "mapping_status": "Crosswalk status", "review_action": "Review action",
                "lrgen": f"CHES left-right ({selected_source_wave})", "womens_rights_position": "CHES women's-rights position",
            },
            hide_index=True,
            width="stretch",
        )
        st.caption("Cabinet membership and CHES positions are intentionally displayed as separate dated evidence. Selecting a nearby survey wave does not create an annual ideology score or show that the cabinet adopted that position.")

    with politics:
        st.subheader(f"Political landscape: {COUNTRY_NAMES[country]}")
        country_parties = party_positions.loc[party_positions.country_iso3 == country].copy()
        waves = sorted(country_parties.ches_wave.unique())
        selected_wave = st.select_slider("CHES survey wave", options=waves, value=waves[-1])
        wave_parties = country_parties.loc[country_parties.ches_wave == selected_wave].copy()
        st.markdown("<div class='spectrum-labels'><span class='spectrum-left'>0 — LEFT</span><span class='spectrum-centre'>5 — CENTRE</span><span class='spectrum-right'>10 — RIGHT</span></div>", unsafe_allow_html=True)
        spectrum_selection = st.plotly_chart(
            political_spectrum_chart(wave_parties),
            width="stretch",
            key="political_spectrum",
            on_select="rerun",
            selection_mode="points",
        )
        left, right = st.columns(2)
        left.metric("Accepted party mappings shown", len(wave_parties), f"CHES wave {selected_wave}")
        right.metric("Mean position in shown parties", f"{wave_parties.lrgen.mean():.1f} / 10", "Not a government or national ideology score")
        st.caption("Dots represent parties with accepted ParlGov-to-CHES links. Position is CHES lrgen, its original 0–10 general left–right expert-survey scale. Dot size reflects the CHES-reported vote share where available. This is a survey-wave measure, not an annual party score or an endorsement.")
        selected_from_chart = None
        points = spectrum_selection.get("selection", {}).get("points", [])
        if points:
            selected_from_chart = points[0].get("y")
        party_options = wave_parties.party_name.tolist()
        selected_party = st.selectbox(
            "Inspect a party",
            options=party_options,
            index=party_options.index(selected_from_chart) if selected_from_chart in party_options else 0,
            key=f"party_detail_{country}_{selected_wave}",
        )
        party_detail = wave_parties.loc[wave_parties.party_name == selected_party].iloc[0]
        detail_left, detail_right, detail_third = st.columns(3)
        detail_left.metric("Left-right position", f"{party_detail.lrgen:.1f} / 10", "0 left; 10 right")
        detail_right.metric("Vote share", f"{party_detail.vote_share_pct:.1f}%" if pd.notna(party_detail.vote_share_pct) else "Not available")
        detail_third.metric("Women's-rights position", f"{party_detail.womens_rights_position:.1f}" if pd.notna(party_detail.womens_rights_position) else "Not available")
        st.caption(f"{party_detail.party_name} is shown through the accepted match to ParlGov party {party_detail.parlgov_party_name}. Click a dot or choose a party to update this card.")
        st.dataframe(wave_parties[["party_name", "lrgen", "vote_share_pct", "seat_share_pct", "womens_rights_position"]].sort_values("lrgen"), column_config={"party_name": "Party", "lrgen": "Left-right (0–10)", "vote_share_pct": "Vote share (%)", "seat_share_pct": "Seat share (%)", "womens_rights_position": "Women's-rights position"}, hide_index=True, width="stretch")

    with compare:
        st.subheader(f"Compare countries: {metric_name}")
        comparison_countries = st.multiselect(
            "Countries shown in this comparison",
            options=list(COUNTRY_NAMES),
            default=[country],
            format_func=COUNTRY_NAMES.get,
            key=f"comparison_countries_{country}",
        )
        comparison_country_names = ", ".join(COUNTRY_NAMES[item] for item in comparison_countries) or "None"
        st.caption(f"Primary dashboard country: **{COUNTRY_NAMES[country]}**. Comparison countries selected: **{comparison_country_names}**.")
        comparison = metric_frame(filter_years(country_year, start_year, end_year), metric_name)
        if hide_flagged:
            comparison = exclude_flagged_observations(comparison)
        comparison = comparison.loc[comparison.country_iso3.isin(comparison_countries)].copy()
        if comparison.empty:
            st.info("Select at least one country to show a comparison.")
        else:
            comparison_chart = px.line(comparison, x="observation_year", y="value", color="country_name", markers=True, labels={"observation_year": "Observation year", "value": metadata["unit"], "country_name": "Country"}, template="plotly_white", color_discrete_sequence=["#2E86AB", "#F18F01", "#4B8F8C", "#B34A5A"])
            comparison_chart.update_layout(height=480, legend_title_text="Country", hovermode="x unified")
            st.plotly_chart(comparison_chart, width="stretch", key="country_comparison")
            compare_left, compare_right = st.columns([1.1, 0.9])
            with compare_left:
                st.dataframe(comparison.sort_values(["country_name", "observation_year"]), hide_index=True, width="stretch")
            with compare_right:
                st.info("Countries share the approved metric configuration. Cabinet markers appear only in the country view, so a national political event is never visually implied to apply across all countries.")

    with methods:
        st.subheader("Evidence, definitions and limits")
        methods_left, methods_right = st.columns(2)
        with methods_left:
            st.markdown("### What is included")
            st.markdown("- 52 approved country-year outcome rows (2010–2022)\n- 32 OECD PF3.2 policy-context observations (2015–2022)\n- 34 dated ParlGov cabinet periods\n- 54 reviewed CHES party-wave positions (2010, 2014, 2019)")
        with methods_right:
            st.markdown("### What is not claimed")
            st.markdown("- No causal effect of governments or parties\n- No annual interpolation of party ideology\n- No party ranking or political endorsement\n- No replacement of missing values with zero")
        st.markdown("### Metric definitions")
        st.markdown("**Unadjusted gender pay gap:** Eurostat sdg_05_20, annual percentage, economic activity B-S_X_O.  \n**Gender employment gap:** Eurostat sdg_05_30, annual percentage points, ages 20–64, employed population.  \n**Policy indicator:** OECD PF3.2 registered ECEC enrolment for children aged 0–2, percentage.  \n**Political spectrum:** CHES lrgen, original general left–right expert-survey scale from 0 (left) to 10 (right).")
        with st.expander("Source and methodology details"):
            st.markdown(
                "The app reads curated Parquet files built locally from approved source snapshots. Eurostat status flags remain attached to outcome records; the filter only helps inspect their influence and never overwrites data. Cabinet memberships, survey-wave party positions, policies and annual outcomes retain their own dates and are not converted into a causal model."
            )


if __name__ == "__main__":
    main()
