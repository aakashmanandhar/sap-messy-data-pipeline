{{ config(materialized='table') }}

with deduped as (

    select
        *,
        row_number() over (partition by vbeln order by erdat) as row_num
    from {{ source('bronze', 'sales_orders') }}

),

typed as (

    select
        vbeln as order_id,
        kunnr as customer_id,
        coalesce(name1, 'Unknown') as customer_name,

        case
            when land1 in ('DE', 'Germany', 'Deutschland') then 'DE'
            when land1 in ('FR', 'France')                 then 'FR'
            when land1 in ('IT', 'Italy')                  then 'IT'
            when land1 in ('ES', 'Spain', 'Espana')         then 'ES'
            when land1 in ('NL', 'Netherlands')            then 'NL'
            when land1 in ('PL', 'Poland')                 then 'PL'
            when land1 in ('AT', 'Austria')                then 'AT'
            when land1 in ('BE', 'Belgium')                then 'BE'
            when land1 in ('CH', 'Switzerland')            then 'CH'
            when land1 in ('SE', 'Sweden')                 then 'SE'
            else land1
        end as country,

        cast(netwr as numeric) as amount,
        waerk as currency,
        parse_date('%Y%m%d', erdat) as order_date

    from deduped
    where row_num = 1

)

select
    *,
    case when amount < 0 then 'return' else 'sale' end as order_type
from typed