select
    country_iso3,
    cast(observation_year as integer) as observation_year,
    indicator,
    cast(value as double) as value,
    unit,
    source_id
from read_csv_auto('data/processed/harmonized/fact_policy_indicator.csv', header = true)
