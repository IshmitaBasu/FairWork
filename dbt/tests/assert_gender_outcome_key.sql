select country_iso3, observation_year, metric, count(*) as row_count
from {{ ref('fact_gender_outcome') }}
group by 1, 2, 3
having count(*) != 1
