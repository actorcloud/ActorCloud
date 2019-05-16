devices_count_sql = """
INSERT INTO {TABLE}("createAt", "countTime", "tenantID",
                    "deviceCount", "deviceOnlineCount",
                    "deviceOfflineCount", "deviceSleepCount")
SELECT current_timestamp                                        AS "createAt",
       date_trunc('{time_unit}',
                  current_timestamp - INTERVAL '1 {time_unit}') AS "countTime",
       devices."tenantID",
       COUNT(*)                                                 AS "deviceCount",
       COUNT(
           CASE WHEN "deviceStatus" = 0 THEN 1 ELSE NULL END)   AS "deviceOfflineCount",
       COUNT(
           CASE WHEN "deviceStatus" = 1 THEN 1 ELSE NULL END)   AS "deviceOnlineCount",
       COUNT(
           CASE WHEN "deviceStatus" = 2 THEN 1 ELSE NULL END)   AS "deviceSleepCount"
FROM devices
GROUP BY devices."tenantID"
"""
