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
WHERE ("deviceID","deviceUsername") IN {devices}
"""

query_gateway_sql = """
SELECT devices."deviceName", devices.id
FROM devices
    JOIN gateways ON devices.id = gateways.id
WHERE devices."deviceName" = ANY ('{{{devices_name}}}'::varchar[])
    AND devices."tenantID" = '{tenantID}';
"""

query_sub_sql = """
SELECT "productID", product_sub.topic, product_sub.qos
FROM products
       JOIN product_sub ON product_sub."productIntID" = products.id
WHERE products."productID" = ANY ('{{{products_uid}}}'::varchar[]);
"""

insert_device_sql = """
WITH {client} AS (
    INSERT INTO devices("createAt", "updateAt", "deviceID", "deviceName", "softVersion",
        "hardwareVersion", manufacturer, "serialNumber", "location", longitude, latitude,
        "deviceUsername", token, "authType", "deviceStatus", "deviceConsoleIP",
        "deviceConsoleUsername", "deviceConsolePort", "upLinkSystem", "IMEI", "IMSI", carrier,
        "physicalNetwork", blocked, "autoSub", description, mac, type, "productID",
        "userIntID", "tenantID")
    VALUES ('{createAt}', '{updateAt}', '{deviceID}', '{deviceName}', '{softVersion}',
        '{hardwareVersion}', '{manufacturer}', '{serialNumber}', '{location}', {longitude},
        {latitude}, '{deviceUsername}', '{token}', {authType}, {deviceStatus},
        '{deviceConsoleIP}', '{deviceConsoleUsername}',{deviceConsolePort},
        {upLinkSystem}, '{IMEI}', '{IMSI}',{carrier}, {physicalNetwork}, {blocked},
        {autoSub}, '{description}', '{mac}', '{type}', '{productID}', {userIntID},
        '{tenantID}')
    RETURNING id
)
INSERT INTO devices(id, gateway, lora, "modBusIndex", "metaData", "parentDevice")
    SELECT id, {gateway}, {lora}, {modBusIndex}, {metaData}, {parentDevice}
    FROM {client};
"""

query_column_default = """
SELECT column_name, column_default
FROM INFORMATION_SCHEMA.COLUMNS
WHERE table_name = 'devices'
   OR table_name = 'devices';
"""

insert_sub_sql = """
INSERT INTO mqtt_sub("createAt", topic, qos, "clientID","deviceIntID")
SELECT '{createAt}', '{topic}', {qos}, '{clientID}', {deviceIntID}
WHERE NOT EXISTS (
    SELECT 1
    FROM mqtt_sub
    WHERE "clientID"='{clientID}'
        AND "deviceIntID"={deviceIntID}
);
"""
query_device_by_product_sql = """
SELECT id, "productID", CONCAT_WS(':',"tenantID","productID", "deviceID") AS client_id
FROM devices
WHERE "productID" = ANY ('{{{products_uid}}}'::varchar[]);
"""

query_device_by_imei_sql = """
SELECT "IMEI"
FROM devices
WHERE "IMEI" = ANY ('{{{devices_imei}}}'::varchar[])
    AND "tenantID"='{tenantID}';
"""
