select
    country_iso3,
    cast(observation_year as integer) as observation_year,
    metric,
    cast(value as double) as value,
    unit,
    observation_flag,
    source_id
from read_csv_auto('data/processed/harmonized/fact_gender_outcome.csv', header = true)
