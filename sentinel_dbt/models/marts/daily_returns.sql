SELECT
    symbol,
    trade_date,
    close_price,
    LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date) AS prev_close_price,
    ROUND(
        (close_price - LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date))
        / LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date) * 100,
        4
    ) AS daily_return_pct
FROM {{ ref('stg_market_data') }}