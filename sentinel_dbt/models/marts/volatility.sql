SELECT
    symbol,
    trade_date,
    daily_return_pct,
    ROUND(
        STDDEV(daily_return_pct) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 4
    ) AS volatility_7d,
    ROUND(
        STDDEV(daily_return_pct) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ), 4
    ) AS volatility_30d
FROM {{ ref('daily_returns') }}
WHERE daily_return_pct IS NOT NULL