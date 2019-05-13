api_hour_count_sql = """
INSERT INTO app_api_logs_hour("createAt", "countTime", "apiCount", "tenantID")
SELECT current_timestamp                                         AS "createAt",
       date_trunc('hour', current_timestamp - INTERVAL '1 hour') AS "countTime",
       COUNT(*)                                                  AS "apiCount",
       app_api_logs."tenantID"
FROM app_api_logs
WHERE "createAt" >= date_trunc('hour', current_timestamp - INTERVAL '1 hour')
  AND "createAt" < date_trunc('hour', current_timestamp)
GROUP BY app_api_logs."tenantID"
"""

# Daily aggregation based on hourly aggregation
api_day_count_sql = """
INSERT INTO app_api_logs_day(
    "createAt", "countTime", "apiCount", "tenantID"
)
SELECT 
    current_timestamp AS "createAt",
    date_trunc('day', current_timestamp - INTERVAL '1 day') AS "countTime",
    SUM(app_api_logs_hour."apiCount") AS "apiCount",
    app_api_logs_hour."tenantID"
FROM app_api_logs_hour
WHERE 
   "countTime" >= date_trunc('day', current_timestamp - INTERVAL '1 day')
   AND "countTime" < date_trunc('day', current_timestamp)
GROUP BY app_api_logs_hour."tenantID"
"""

# Monthly aggregation based on daily aggregation
api_month_count_sql = """
INSERT INTO app_api_logs_month("createAt", "countTime", "apiCount", "tenantID")
SELECT current_timestamp                                           AS "createAt",
       date_trunc('month',
                  current_timestamp - INTERVAL '1 month')          AS "countTime",
       SUM(app_api_logs_day."apiCount")                            AS "apiCount",
       app_api_logs_day."tenantID"
FROM app_api_logs_day
WHERE "countTime" >= date_trunc('month', current_timestamp - INTERVAL '1 month')
  AND "countTime" < date_trunc('month', current_timestamp)
GROUP BY app_api_logs_day."tenantID"
"""
