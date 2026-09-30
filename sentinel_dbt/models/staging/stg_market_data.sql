SELECT
    symbol,
    CAST(date AS DATE) AS trade_date,
    CAST(open AS FLOAT64) AS open_price,
    CAST(high AS FLOAT64) AS high_price,
    CAST(low AS FLOAT64) AS low_price,
    CAST(close AS FLOAT64) AS close_price,
    CAST(volume AS INT64) AS volume
FROM {{ source('raw', 'raw_market_data') }}
WHERE close IS NOT NULL