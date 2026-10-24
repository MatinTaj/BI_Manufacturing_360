SELECT
    p.product_name,
    SUM(pr.attempted_units) AS total_production,
    SUM(pr.defective_units) AS total_defects,
    ROUND(
        100.0 * SUM(pr.defective_units)
        / SUM(pr.attempted_units),
        2
    ) AS defect_rate_pct
FROM production pr
JOIN products p
    ON pr.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY defect_rate_pct DESC;