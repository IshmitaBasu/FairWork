select
    country_iso3,
    cast(parlgov_party_id as integer) as parlgov_party_id,
    parlgov_party_short,
    parlgov_party_name,
    ches_party_id,
    mapping_method,
    mapping_status,
    cast(ches_wave_observation as boolean) as ches_wave_observation,
    review_action
from read_csv_auto('data/processed/political_context/party_crosswalk_review.csv', header = true)
