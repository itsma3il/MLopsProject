with base as (
    select * from {{ ref('stg_transactions') }}
),

features as (
    select
        transaction_time as Time,
        {% for i in range(1, 29) -%}
        v{{ i }} as V{{ i }},
        {% endfor -%}
        amount as Amount,
        cast(floor(transaction_time / 3600) % 24 as integer) as transaction_hour,
        case
            when cast(floor(transaction_time / 3600) % 24 as integer) <= 6 then 0
            when cast(floor(transaction_time / 3600) % 24 as integer) <= 12 then 1
            when cast(floor(transaction_time / 3600) % 24 as integer) <= 18 then 2
            else 3
        end as day_period,
        ln(1 + amount) as amount_log,
        case
            when amount < 50 then 0
            when amount < 200 then 1
            when amount < 1000 then 2
            else 3
        end as amount_bin,
        (
            {% for i in range(1, 29) -%}
            v{{ i }}{% if not loop.last %} + {% endif %}
            {% endfor -%}
        ) / 28.0 as v_mean,
        (
            select stddev_pop(x)
            from (
                values
                {% for i in range(1, 29) -%}
                (v{{ i }}){% if not loop.last %},{% endif %}
                {% endfor -%}
            ) as t(x)
        ) as v_std,
        (v4 + v11 + v2 + v19) - (v14 + v12 + v10 + v17) as risk_score,
        amount * abs(v14) as amount_x_v14,
        amount * abs(v17) as amount_x_v17,
        class as Class
    from base
)

select * from features
