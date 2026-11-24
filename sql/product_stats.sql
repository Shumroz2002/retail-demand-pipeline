-- Product-level demand stats. Aggregates the 32M-row table by product_id FIRST,
-- then joins the small lookup tables (much faster than joining before grouping).
-- Optional filter: :department (NULL = all departments)
WITH product_agg AS (
    SELECT product_id,
           COUNT(*)               AS times_ordered,
           SUM(reordered)         AS times_reordered,
           AVG(add_to_cart_order) AS avg_cart_position
    FROM order_products__prior
    GROUP BY product_id
)
SELECT p.product_id, p.product_name, a.aisle, d.department,
       pa.times_ordered,
       pa.times_reordered,
       ROUND(1.0 * pa.times_reordered / pa.times_ordered, 4) AS reorder_rate,
       ROUND(pa.avg_cart_position, 2)                        AS avg_cart_position
FROM product_agg AS pa
JOIN products    AS p ON p.product_id    = pa.product_id
JOIN aisles      AS a ON a.aisle_id      = p.aisle_id
JOIN departments AS d ON d.department_id = p.department_id
WHERE :department IS NULL OR d.department = :department
ORDER BY pa.times_ordered DESC, p.product_id;
