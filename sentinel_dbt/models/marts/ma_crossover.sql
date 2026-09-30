WITH moving_averages AS (
    SELECT
        symbol,
        trade_date,
        close_price,
        AVG(close_price) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS ma_7d,
        AVG(close_price) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS ma_30d
    FROM {{ ref('stg_market_data') }}
),

with_signal AS (
    SELECT
        *,
        CASE
            WHEN ma_7d > ma_30d THEN 'BULLISH'
            WHEN ma_7d < ma_30d THEN 'BEARISH'
            ELSE 'NEUTRAL'
        END AS trend_signal,
        LAG(CASE WHEN ma_7d > ma_30d THEN 'BULLISH' ELSE 'BEARISH' END)
            OVER (PARTITION BY symbol ORDER BY trade_date) AS prev_trend_signal
    FROM moving_averages
)

SELECT
    symbol,
    trade_date,
    close_price,
    ROUND(ma_7d, 4) AS ma_7d,
    ROUND(ma_30d, 4) AS ma_30d,
    trend_signal,
    CASE
        WHEN trend_signal != prev_trend_signal THEN TRUE
        ELSE FALSE
    END AS is_crossover_point
FROM with_signal