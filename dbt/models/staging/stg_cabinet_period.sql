select
    country_iso3,
    cast(parlgov_cabinet_id as integer) as parlgov_cabinet_id,
    cabinet_name,
    cast(start_date as date) as start_date,
    nullif(cast(end_date_exclusive as varchar), '')::date as end_date_exclusive,
    cast(caretaker as boolean) as caretaker,
    date_rule
from read_csv_auto('data/processed/political_context/cabinet_periods.csv', header = true)
