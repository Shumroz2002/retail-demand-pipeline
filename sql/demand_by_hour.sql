-- When does demand happen? Item lines by day of week and hour.
-- (Instacart order_dow is 0-6; the dataset does not say which day is 0.)
SELECT
    o.order_dow,
    o.order_hour_of_day,
    COUNT(DISTINCT o.order_id) AS orders,
    COUNT(*)                   AS item_lines
FROM orders AS o
JOIN order_products__prior AS op ON op.order_id = o.order_id
GROUP BY o.order_dow, o.order_hour_of_day
ORDER BY o.order_dow, o.order_hour_of_day;
