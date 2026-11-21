select
    outcomes.country_iso3,
    country.country_name,
    outcomes.observation_year,
    outcomes.pay_gap_value,
    outcomes.pay_gap_flag,
    outcomes.employment_gap_value,
    outcomes.employment_gap_flag,
    policy.value as enrolment_0_2_registered_ecec_pct,
    policy.source_id as policy_source_id
from {{ ref('stg_country_year_outcomes') }} as outcomes
inner join {{ ref('stg_country') }} as country using (country_iso3)
left join {{ ref('fact_policy_indicator') }} as policy
    on outcomes.country_iso3 = policy.country_iso3
    and outcomes.observation_year = policy.observation_year
    and policy.indicator = 'enrolment_0_2_registered_ecec_pct'
