item_events_hour_aggr_sql = """
INSERT INTO lwm2m_event_hour("countTime", "tenantID", "productID", "deviceID",
                             path, "objectItem",
                             "minValue", "maxValue", "avgValue", "sumValue",
                             "minCalc", "maxCalc", "avgCalc", "sumCalc")
SELECT time_bucket('1 hours', events."msgTime") AS "countTime",
       events."tenantID",
       events."productID",
       events."deviceID",
       json.path,
       json.name                                AS "objectItem",
       min(json.value::numeric)                 AS "minValue",
       max(json.value::numeric)                 AS "maxValue",
       avg(json.value::numeric)                 AS "avgValue",
       sum(json.value::numeric)                 AS "sumValue",
       min(json."calculateValue")               AS "minCalc",
       max(json."calculateValue")               AS "maxCalc",
       avg(json."calculateValue")               AS "avgCalc",
       sum(json."calculateValue")               AS "sumCal"
FROM device_events events
       CROSS JOIN LATERAL
  jsonb_to_recordset(events.payload_json) AS json(name text, path text,
                                                  value text,
                                                  "calculateValue" double precision,
                                                  type text)
       JOIN
     products ON products."productID" = events."productID"
WHERE events."msgTime" >=
      date_trunc('hour', current_timestamp) - INTERVAL '1 hour'
  AND events."msgTime" < date_trunc('hour', current_timestamp)
  AND products."cloudProtocol" = 3
  AND json.type = 'float'
GROUP BY "countTime", events."tenantID", events."productID",
         events."deviceID", json.path, "objectItem"
ON CONFLICT DO NOTHING
"""

item_events_day_aggr_sql = """
INSERT INTO data_point_event_day("countTime", "tenantID", "productID",
                                 "deviceID", topic, "dataPointID",
                                 "minValue", "maxValue", "avgValue", "sumValue",
                                 "minCalc", "maxCalc", "avgCalc", "sumCalc")
SELECT time_bucket('1 days', "countTime") AS "countDay",
       "tenantID",
       "productID",
       "deviceID",
       topic,
       "dataPointID",
       min("minValue")                    AS "minValue",
       max("maxValue")                    AS "maxValue",
       avg("sumValue")                    AS "avgValue",
       sum("sumValue")                    AS "sumValue",
       min("minCalc")                     AS "minCalc",
       max("maxCalc")                     AS "maxCalc",
       avg("sumCalc")                     AS "avgCalc",
       sum("sumCalc")                     AS "sumCalc"
FROM data_point_event_hour
WHERE "countTime" >= CURRENT_DATE - INTERVAL '1 days'
  AND "countTime" < CURRENT_DATE
GROUP BY "countDay", "tenantID", "productID", "deviceID", topic, "dataPointID"
ON CONFLICT DO NOTHING
"""

item_events_month_aggr_sql = """
INSERT INTO data_point_event_month("countTime", "tenantID", "productID",
                                   "deviceID", topic, "dataPointID",
                                   "minValue", "maxValue", "avgValue",
                                   "sumValue",
                                   "minCalc", "maxCalc", "avgCalc", "sumCalc")
SELECT date_trunc('month', "countTime") AS "countMonth",
       "tenantID",
       "productID",
       "deviceID",
       topic,
       "dataPointID",
       min("minValue")                  AS "minValue",
       max("maxValue")                  AS "maxValue",
       avg("sumValue")                  AS "avgValue",
       sum("sumValue")                  AS "sumValue",
       min("minCalc")                   AS "minCalc",
       max("maxCalc")                   AS "maxCalc",
       avg("sumCalc")                   AS "avgCalc",
       sum("sumCalc")                   AS "sumCalc"
FROM data_point_event_hour
WHERE "countTime" >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month'
  AND "countTime" < date_trunc('month', CURRENT_DATE)
GROUP BY "countMonth", "tenantID", "productID", "deviceID", topic, "dataPointID"
ON CONFLICT DO NOTHING
"""
