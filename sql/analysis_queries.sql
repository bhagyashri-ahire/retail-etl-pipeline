-- 1. Monthly revenue trend
SELECT SUBSTR(order_date, 1, 7) AS month, ROUND(SUM(total_amount), 2) AS revenue
FROM fact_sales GROUP BY month ORDER BY month;

-- 2. Revenue by category (JOIN + aggregation)
SELECT p.category, COUNT(*) AS line_items, ROUND(SUM(f.total_amount), 2) AS revenue
FROM fact_sales f JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category ORDER BY revenue DESC;

-- 3. Top 5 customers by spend
SELECT c.customer_name, c.city, ROUND(SUM(f.total_amount), 2) AS total_spend
FROM fact_sales f JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.city
ORDER BY total_spend DESC LIMIT 5;

-- 4. Reconciliation check from the audit log
SELECT run_id, rows_extracted, rows_loaded, rows_rejected, reconciled FROM etl_audit_log;

-- 5. Why rows were rejected
SELECT reject_reason, COUNT(*) AS n FROM rejected_rows GROUP BY reject_reason ORDER BY n DESC;
