select *
from {{ ref('fact_gender_outcome') }}
where value < -100 or value > 100
