-- Department summary using a CTE, plus a window function to rank departments.
WITH product_lines AS (
    SELECT
        d.department,
        op.product_id,
        op.reordered
    FROM order_products__prior AS op
    JOIN products    AS p ON p.product_id    = op.product_id
    JOIN departments AS d ON d.department_id = p.department_id
),
dept_stats AS (
    SELECT
        department,
        COUNT(*)                     AS total_lines,
        COUNT(DISTINCT product_id)   AS distinct_products,
        ROUND(AVG(reordered), 4)     AS reorder_rate
    FROM product_lines
    GROUP BY department
)
SELECT
    department,
    total_lines,
    distinct_products,
    reorder_rate,
    RANK() OVER (ORDER BY total_lines DESC) AS demand_rank,
    ROUND(100.0 * total_lines / SUM(total_lines) OVER (), 2) AS pct_of_all_lines
FROM dept_stats
ORDER BY demand_rank;
