dict_code_sql = """
SELECT code,
       array_agg("codeValue") AS values,
       array_agg("{language}Label") AS labels
FROM dict_code
WHERE code IN ('authType', 'upLinkSystem')
GROUP BY code
"""

query_device_count_sql = """
SELECT "deviceCount"
FROM tenants
WHERE "tenantID" = '{tenantID}';
"""

query_device_sum_sql = """
SELECT COUNT(*)
FROM devices
WHERE "tenantID" = '{tenantID}';
"""

query_devices_name_sql = """
SELECT "deviceName"
FROM devices
WHERE "deviceName" = ANY ('{{{devices_name}}}'::varchar[])
    AND "tenantID"='{tenantID}';
"""

query_product_sql = """
SELECT "productName", "productID", "cloudProtocol"
FROM products
    JOIN users ON products."userIntID" = users.id
WHERE "productName" = ANY ('{{{products_name}}}'::varchar[])
    AND users."tenantID" = '{tenantID}';
"""

query_device_by_uid_sql = """
SELECT "deviceID"
FROM devices
WHERE "deviceID" = ANY ('{{{devices_uid}}}'::varchar[])
    AND "tenantID"='{tenantID}';
"""

query_device_by_username_sql = """
SELECT "deviceID", "deviceUsername"
FROM devices
WHERE ("deviceID","deviceUsername") IN ({devices})
"""

query_gateway_sql = """
SELECT devices."deviceName", devices.id
FROM devices
    JOIN gateways ON devices.id = gateways.id
WHERE devices."deviceName" = ANY ('{{{devices_name}}}'::varchar[])
    AND devices."tenantID" = '{tenantID}';
"""

insert_device_sql = """
WITH {client} AS (
    INSERT INTO devices("createAt", "updateAt", "deviceID", "deviceName", "softVersion",
        "hardwareVersion", manufacturer, "serialNumber", "location", longitude, latitude,
        "deviceUsername", token, "authType", "deviceStatus", "deviceConsoleIP",
        "deviceConsoleUsername", "deviceConsolePort", "upLinkNetwork", carrier,
        blocked, description, mac, "deviceType", "productID",
        "userIntID", "tenantID")
    VALUES ('{createAt}', '{updateAt}', '{deviceID}', '{deviceName}', '{softVersion}',
        '{hardwareVersion}', '{manufacturer}', '{serialNumber}', '{location}', {longitude},
        {latitude}, '{deviceUsername}', '{token}', {authType}, {deviceStatus},
        '{deviceConsoleIP}', '{deviceConsoleUsername}',{deviceConsolePort},
        {upLinkNetwork}, {carrier}, {blocked},'{description}', '{mac}', {deviceType}, '{productID}',
         {userIntID}, '{tenantID}')
    RETURNING id
)
INSERT INTO end_devices(id, "upLinkSystem", gateway, "loraData", "lwm2mData", "modbusData", "parentDevice")
    SELECT id, {upLinkSystem}, {gateway}, '{loraData}', '{lwm2mData}', '{modbusData}', {parentDevice}
    FROM {client};
"""

query_column_default = """
SELECT column_name, column_default
FROM INFORMATION_SCHEMA.COLUMNS
WHERE table_name = 'devices'
   OR table_name = 'end_devices';
"""

query_device_by_product_sql = """
SELECT id, "productID", CONCAT_WS(':',"tenantID","productID", "deviceID") AS client_id
FROM devices
WHERE "productID" = ANY ('{{{products_uid}}}'::varchar[]);
"""

query_device_by_imei_sql = """
SELECT end_devices."lwm2mData"::jsonb ->>'IMEI' as "IMEI"
FROM end_devices
    JOIN devices ON devices.id=end_devices.id
WHERE  end_devices."lwm2mData"::jsonb ->>'IMEI' = ANY ('{{{devices_imei}}}'::varchar[])
    AND "tenantID"='{tenantID}';
"""
