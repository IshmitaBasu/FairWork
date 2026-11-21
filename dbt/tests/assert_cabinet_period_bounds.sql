select *
from {{ ref('mart_cabinet_transition') }}
where start_date >= coalesce(end_date_exclusive, date '9999-12-31')
