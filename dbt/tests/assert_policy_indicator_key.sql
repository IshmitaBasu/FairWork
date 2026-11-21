select country_iso3, observation_year, indicator, count(*) as row_count
from {{ ref('fact_policy_indicator') }}
group by 1, 2, 3
having count(*) != 1
