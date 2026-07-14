{{ config(materialized='table') }}

select
    country,
    format_date('%Y-%m', order_date) as month,
    sum(amount) as net_revenue,
    countif(order_type = 'sale') as sales_orders,
    countif(order_type = 'return') as returns
from {{ ref('silver_sales_orders') }}
group by country, month
order by net_revenue desc