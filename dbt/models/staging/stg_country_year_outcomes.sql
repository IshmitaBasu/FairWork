select
    country_iso3,
    cast(observation_year as integer) as observation_year,
    cast(pay_gap_value as double) as pay_gap_value,
    pay_gap_flag,
    cast(employment_gap_value as double) as employment_gap_value,
    employment_gap_flag
from read_csv_auto('data/processed/harmonized/country_year_outcomes.csv', header = true)
