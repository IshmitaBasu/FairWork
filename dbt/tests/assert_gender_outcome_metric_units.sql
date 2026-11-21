select *
from {{ ref('fact_gender_outcome') }}
where (metric = 'unadjusted_gender_pay_gap_pct' and unit != 'PC')
   or (metric = 'gender_employment_gap_pp' and unit != 'PC_PNT')
