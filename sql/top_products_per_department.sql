-- Top N products inside each department: CTE + ROW_NUMBER() window function.
-- Parameter: :n
WITH product_counts AS (
    SELECT
        d.department,
        p.product_name,
        COUNT(*) AS times_ordered
    FROM order_products__prior AS op
    JOIN products    AS p ON p.product_id    = op.product_id
    JOIN departments AS d ON d.department_id = p.department_id
    GROUP BY d.department, p.product_id, p.product_name
),
ranked AS (
    SELECT
        department,
        product_name,
        times_ordered,
        ROW_NUMBER() OVER (
            PARTITION BY department
            ORDER BY times_ordered DESC, product_name
        ) AS rank_in_department
    FROM product_counts
)
SELECT department, rank_in_department, product_name, times_ordered
FROM ranked
WHERE rank_in_department <= :n
ORDER BY department, rank_in_department;
