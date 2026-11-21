select
    country_iso3,
    country_name,
    eurostat_geo,
    cast(ches_country_code as integer) as ches_country_code,
    cast(parlgov_country_id as integer) as parlgov_country_id,
    parlgov_country_short
from read_csv_auto('data/metadata/country_crosswalk.csv', header = true)
