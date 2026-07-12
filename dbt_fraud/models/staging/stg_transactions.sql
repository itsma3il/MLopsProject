with source as (
    select * from {{ source('raw', 'creditcard_transactions') }}
),

deduplicated as (
    select distinct
        cast(Time as double) as transaction_time,
        {% for i in range(1, 29) -%}
        cast(V{{ i }} as double) as v{{ i }},
        {% endfor -%}
        cast(Amount as double) as amount,
        cast(Class as integer) as class
    from source
    where Time is not null
      and Amount is not null
      and Class in (0, 1)
      and Amount >= 0
)

select * from deduplicated
