emqx_bills_hour_aggr_sql = """
INSERT INTO emqx_bills_hour("countTime",
                            "msgType", "msgCount", "msgSize", "tenantID")
SELECT date_trunc('hour', current_timestamp - INTERVAL '1 hour') AS "countTime",
       emqx_bills."msgType"                                      AS "msgType",
       COUNT(*)                                                  AS "msgCount",
       SUM(emqx_bills."msgSize")                                 AS "msgSize",
       emqx_bills."tenantID"
FROM emqx_bills
       JOIN tenants ON tenants."tenantID" = emqx_bills."tenantID"
WHERE "msgTime" >= date_trunc('hour', current_timestamp - INTERVAL '1 hour')
  AND "msgTime" < date_trunc('hour', current_timestamp)
  AND tenants.enable = 1
GROUP BY emqx_bills."tenantID", emqx_bills."msgType"
"""

emqx_bills_day_aggr_sql = """
INSERT INTO emqx_bills_day("createAt", "countTime",
                           "msgType", "msgCount", "msgSize", "tenantID")
SELECT current_timestamp                                       AS "createAt",
       date_trunc('day', current_timestamp - INTERVAL '1 day') AS "countTime",
       emqx_bills_hour."msgType"                               AS "msgType",
       SUM(emqx_bills_hour."msgCount")                         AS "msgCount",
       SUM(emqx_bills_hour."msgSize")                          AS "msgSize",
       emqx_bills_hour."tenantID"
FROM emqx_bills_hour
WHERE "countTime" >= date_trunc('day', current_timestamp - INTERVAL '1 day')
  AND "countTime" < date_trunc('day', current_timestamp)
GROUP BY emqx_bills_hour."tenantID", emqx_bills_hour."msgType"
"""

emqx_bills_month_aggr_sql = """
INSERT INTO emqx_bills_month("createAt", "countTime",
                             "msgType", "msgCount", "msgSize", "tenantID")
SELECT current_timestamp                                       AS "createAt",
       date_trunc('day', current_timestamp - INTERVAL '1 day') AS "countTime",
       emqx_bills_day."msgType"                                AS "msgType",
       SUM(emqx_bills_day."msgCount")                          AS "msgCount",
       SUM(emqx_bills_day."msgSize")                           AS "msgSize",
       emqx_bills_day."tenantID"
FROM emqx_bills_day
WHERE "countTime" >= date_trunc('day', current_timestamp - INTERVAL '1 day')
  AND "countTime" < date_trunc('day', current_timestamp)
GROUP BY emqx_bills_day."tenantID", emqx_bills_day."msgType"
"""
