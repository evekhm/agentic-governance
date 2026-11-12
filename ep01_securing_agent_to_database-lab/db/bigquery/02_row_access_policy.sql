-- Episode 01 Lab: BigQuery Row Access Policies & k-Anonymity Aggregate View
-- Mirrors Snippet 11 in ep01_securing_agent_to_database.html.

-- 1. Per-User Row Access Policy (ONE policy covers all workforce/customer users via SESSION_USER())
CREATE OR REPLACE ROW ACCESS POLICY customer_own_orders
ON `${DATA_PROJECT_ID}.sales.orders`
GRANT TO ("domain:example.com", "group:customers@example.com")
FILTER USING (customer_email = SESSION_USER());

-- 2. Explicit Pipeline SA Policy (once any policy exists, unmatched SAs see 0 rows!)
CREATE OR REPLACE ROW ACCESS POLICY etl_pipeline_full_read
ON `${DATA_PROJECT_ID}.sales.orders`
GRANT TO ("serviceAccount:analytics-etl@${DATA_PROJECT_ID}.iam.gserviceaccount.com")
FILTER USING (TRUE);

-- 3. Aggregate View with k-Anonymity Floor (k >= 5 blocks difference attacks)
CREATE OR REPLACE VIEW `${DATA_PROJECT_ID}.agent_views.regional_order_stats_v` AS
SELECT
    region,
    status,
    COUNT(*) AS order_count,
    ROUND(AVG(total), 2) AS avg_total
FROM `${DATA_PROJECT_ID}.sales.orders`
GROUP BY region, status
HAVING COUNT(DISTINCT customer_email) >= 5;
