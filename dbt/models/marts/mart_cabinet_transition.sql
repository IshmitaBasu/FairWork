with periods as (
    select
        *,
        lag(parlgov_cabinet_id) over ( partition by country_iso3 order by start_date, parlgov_cabinet_id) as previous_parlgov_cabinet_id,
        lag(cabinet_name) over (partition by country_iso3order by start_date, parlgov_cabinet_id) as previous_cabinet_name
    from {{ ref('stg_cabinet_period') }})
select
    country_iso3,
    parlgov_cabinet_id,
    cabinet_name,
    start_date,
    end_date_exclusive,
    caretaker,
    date_rule,
    previous_parlgov_cabinet_id,
    previous_cabinet_name,
    case when previous_parlgov_cabinet_id is null then 'first_observed_period' else 'cabinet_change' end as transition_type
from periods
