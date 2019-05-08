device_events_hour_aggr_sql = """
create or replace function cast_to_numeric(jsonb) returns numeric as $$
begin
    return Coalesce($1->>'value', $1::text)::numeric;
exception when invalid_text_representation then
    return NULL;
end;
$$ language plpgsql immutable;


INSERT INTO device_events_hour("countTime", "tenantID", "deviceID", "streamID", "dataPointID",
                               "minValue", "maxValue", "avgValue", "sumValue")
SELECT
    time_bucket('1 hours',
                Coalesce(to_timestamp((value->>'time')::float)::timestamp without time zone,
                         device_events."msgTime")
    ) AS "countTime",
    device_events."tenantID", device_events."deviceID",
    device_events."streamID", key AS "dataPointID",
    min(cast_to_numeric(value)) AS "minValue",
    max(cast_to_numeric(value)) AS "maxValue",
    avg(cast_to_numeric(value)) AS "avgValue",
    sum(cast_to_numeric(value)) AS "sumValue"
FROM
    device_events, jsonb_each(device_events.data)
WHERE
    device_events."dataType" = 1
GROUP BY
    "countTime", "tenantID", "deviceID", "streamID", "dataPointID"
ON CONFLICT DO NOTHING
"""

device_events_day_aggr_sql = """
INSERT INTO device_events_day("countTime", "tenantID", "deviceID", "streamID", "dataPointID",
                              "minValue", "maxValue", "avgValue", "sumValue")
SELECT
    time_bucket('1 days', "countTime") AS "countDay",
    "tenantID", "deviceID", "streamID", "dataPointID",
    min("minValue") AS "minValue",
    max("maxValue") AS "maxValue",
    avg("avgValue") AS "avgValue",
    sum("sumValue") AS "sumValue"
FROM
    device_events_hour
WHERE
    "countTime" >= CURRENT_DATE - INTERVAL '1 days'
    AND "countTime" < CURRENT_DATE
GROUP BY
    "countDay", "tenantID", "deviceID", "streamID", "dataPointID"
ON CONFLICT DO NOTHING
"""

device_events_month_aggr_sql = """
INSERT INTO device_events_month("countTime", "tenantID", "deviceID", "streamID", "dataPointID",
                                "minValue", "maxValue", "avgValue", "sumValue")
SELECT
    date_trunc('month', "countTime") AS "countMonth",
    "tenantID", "deviceID", "streamID", "dataPointID",
    min("minValue") AS "minValue",
    max("maxValue") AS "maxValue",
    avg("avgValue") AS "avgValue",
    sum("sumValue") AS "sumValue"
FROM
    device_events_hour
WHERE
    "countTime" >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month'
    AND "countTime" < date_trunc('month', CURRENT_DATE)
GROUP BY
    "countMonth", "tenantID", "deviceID", "streamID", "dataPointID"
ON CONFLICT DO NOTHING
"""
