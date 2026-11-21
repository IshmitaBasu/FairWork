select country_iso3, observation_year, count(*) as row_count
from {{ ref('mart_country_year') }}
group by 1, 2
having count(*) != 1
