select *
from {{ ref('fact_policy_indicator') }}
where value < 0 or value > 100
