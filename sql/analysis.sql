-- SQLite. Import data from CSV into users, orders, marketing tables.
-- Net GMV excludes refunded orders; refunded orders incur a 45 RUB handling cost.
-- Unit economics parameters mirror src/analysis.py.
WITH per_order AS (
  SELECT u.channel, o.user_id, o.order_id, o.status,
         CASE WHEN o.status = 'fulfilled' THEN o.gmv_rub ELSE 0 END AS net_gmv,
         CASE WHEN o.status = 'fulfilled' THEN 0.15 * o.gmv_rub + 35 ELSE 0 END AS revenue,
         CASE WHEN o.status = 'fulfilled' THEN 0.022 * o.gmv_rub + 65 + 12 ELSE 45 END AS variable_cost
  FROM orders o JOIN users u ON u.user_id = o.user_id
),
users_by_channel AS (
  SELECT channel, COUNT(DISTINCT user_id) AS acquired_users FROM users GROUP BY channel
),
orders_by_channel AS (
  SELECT channel, COUNT(*) AS orders,
         COUNT(DISTINCT CASE WHEN status = 'fulfilled' THEN user_id END) AS buyers,
         SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) AS refunds,
         SUM(net_gmv) AS net_gmv,
         SUM(revenue) AS revenue,
         SUM(revenue - variable_cost) AS contribution_90d
  FROM per_order GROUP BY channel
)
SELECT u.channel, u.acquired_users, o.orders, o.buyers,
       ROUND(1.0 * o.buyers / u.acquired_users, 4) AS purchase_conversion,
       ROUND(1.0 * o.refunds / o.orders, 4) AS refund_rate,
       ROUND(1.0 * m.marketing_spend_rub / u.acquired_users, 2) AS cac_rub,
       ROUND(o.contribution_90d / u.acquired_users, 2) AS ltv90_contribution_rub,
       ROUND(o.contribution_90d / m.marketing_spend_rub, 3) AS ltv90_to_cac,
       ROUND(o.contribution_90d - m.marketing_spend_rub, 2) AS net_after_marketing_90d_rub
FROM users_by_channel u
JOIN orders_by_channel o ON o.channel = u.channel
JOIN marketing m ON m.channel = u.channel
ORDER BY u.channel;
