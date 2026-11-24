-- Product-level demand stats: JOINs across 4 tables + aggregation.
-- Optional filter: :department (NULL = all departments)
SELECT
    p.product_id,
    p.product_name,
    a.aisle,
    d.department,
    COUNT(*)                          AS times_ordered,
    SUM(op.reordered)                 AS times_reordered,
    ROUND(AVG(op.reordered), 4)       AS reorder_rate,
    ROUND(AVG(op.add_to_cart_order), 2) AS avg_cart_position
FROM order_products__prior AS op
JOIN products    AS p ON p.product_id    = op.product_id
JOIN aisles      AS a ON a.aisle_id      = p.aisle_id
JOIN departments AS d ON d.department_id = p.department_id
WHERE :department IS NULL OR d.department = :department
GROUP BY p.product_id, p.product_name, a.aisle, d.department
ORDER BY times_ordered DESC, p.product_id;
