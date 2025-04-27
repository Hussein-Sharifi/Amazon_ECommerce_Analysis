CREATE TABLE amazon_orders (
    index_id            SERIAL PRIMARY KEY,
    order_id            TEXT NOT NULL,
    date                TIMESTAMP NOT NULL,
    status              TEXT NOT NULL,
    fulfillment         TEXT NOT NULL,
    sales_channel       TEXT NOT NULL,
    ship_service_level  TEXT NOT NULL,
    style               TEXT,
    sku                 TEXT NOT NULL,
    category            TEXT NOT NULL,
    size                TEXT NOT NULL,
    asin                TEXT NOT NULL,
    quantity            INT NOT NULL,
    currency            TEXT,
    amount              FLOAT,
    ship_city           TEXT NOT NULL,
    ship_state          TEXT NOT NULL,
    ship_postal_code    FLOAT,
    ship_country        TEXT NOT NULL,
    b2b                 BOOLEAN NOT NULL,
    abnormal            BOOLEAN NOT NULL
);

\copy amazon_orders FROM 'data\amazon_sales_cleaned.csv' DELIMITER ',' CSV HEADER;


-- to fill in missing payment info, I'll create a spread sheet with most common unit price. First, let's determine
-- whether quantity is factored into amount
SELECT t1.asin, t1.quantity, t1.amount , t2.asin, t2.quantity, t2.amount
   FROM amazon_orders t1 JOIN amazon_orders t2
   ON t1.asin = t2.asin
   WHERE t1.quantity >=1 AND t2.quantity > t1.quantity
   LIMIT 10;


-- quantity does factor into amount. next, if we have either quantity or amount, we can recover payment info. 
-- let's check if any entries are missing both
SELECT * FROM amazon_orders WHERE (quantity = 0 AND amount = 0);
SELECT * FROM amazon_orders WHERE (quantity = 0 AND amount IS NULL);


-- no entries are missing both. create unit price spreadsheet to recover payment info
CREATE TABLE unit_price AS
SELECT asin,
       mode() WITHIN GROUP (ORDER BY amount/quantity) as mode
FROM amazon_orders
WHERE quantity >= 1 AND amount > 0
GROUP BY asin
ORDER BY asin;

-- Make sure unit price statistics are coherent
SELECT 
    width_bucket(mode, 
        (SELECT MIN(mode) FROM unit_price),
        (SELECT MAX(mode) FROM unit_price),
        10) as bucket,
    COUNT(*) as count,
    MIN(mode) as min_price,
    MAX(mode) as max_price
FROM unit_price
GROUP BY bucket
ORDER BY bucket;


-- fill in payment info
UPDATE amazon_orders ao
    SET 
        quantity = CASE
            WHEN (ao.quantity = 0 AND ao.amount IS NOT NULL) THEN ROUND(ao.amount/up.mode)
            WHEN (ao.quantity = 0 AND ao.amount IS NULL) THEN 1
            ELSE ao.quantity
    END
    FROM unit_price up
    WHERE ao.asin = up.asin

UPDATE amazon_orders ao
    SET 
        amount = CASE
            WHEN (ao.amount = 0 OR ao.amount IS NULL) THEN (up.mode * ao.quantity)
            ELSE ao.amount
    END
    FROM unit_price up
    WHERE ao.asin = up.asin
    RETURNING 
        ao.asin,
        ao.order_id,
        ao.amount as new_amount,
        ao.quantity as new_quantity,
        ao.amount/NULLIF(ao.quantity,0) as calculated_unit_price,
        up.most_common_unit_price;