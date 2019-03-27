query_device_count_sql = """
SELECT "deviceCount" 
FROM tenants
WHERE "tenantID" = '{tenantID}';
"""

query_device_sum_sql = """
SELECT COUNT(*) 
FROM clients
WHERE "tenantID" = '{tenantID}';
"""

query_devices_name_sql = """
SELECT "deviceName" 
FROM clients
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
FROM clients
WHERE "deviceID" = ANY ('{{{devices_uid}}}'::varchar[])
    AND "tenantID"='{tenantID}';
"""

query_device_by_username_sql = """
SELECT "deviceID", "deviceUsername"
FROM clients
WHERE ("deviceID","deviceUsername") IN {devices}
"""

query_gateway_sql = """
SELECT clients."deviceName", clients.id
FROM clients
    JOIN gateways ON clients.id = gateways.id
WHERE clients."deviceName" = ANY ('{{{devices_name}}}'::varchar[])
    AND clients."tenantID" = '{tenantID}';
"""

query_sub_sql = """
SELECT "productID", product_group_sub.topic, product_group_sub.qos
FROM products
       JOIN product_group_sub ON product_group_sub."productIntID" = products.id
WHERE products."productID" = ANY ('{{{products_uid}}}'::varchar[]);
"""

insert_device_sql = """
WITH {client} AS (
    INSERT INTO clients("createAt", "updateAt", "deviceID", "deviceName", "softVersion",
        "hardwareVersion", manufacturer, "serialNumber", "location", longitude, latitude,
        "deviceUsername", token, "authType", "deviceStatus", "deviceConsoleIP",
        "deviceConsoleUsername", "deviceConsolePort", "upLinkSystem", "IMEI", "IMSI", carrier,
        "physicalNetwork", blocked, "autoSub", description, mac, type, "productID", "userIntID", 
        "tenantID")
    VALUES ('{createAt}', '{updateAt}', '{deviceID}', '{deviceName}', '{softVersion}', 
        '{hardwareVersion}', '{manufacturer}', '{serialNumber}', '{location}', {longitude},
        {latitude}, '{deviceUsername}', '{token}', {authType}, {deviceStatus}, '{deviceConsoleIP}', 
        '{deviceConsoleUsername}',{deviceConsolePort}, {upLinkSystem}, '{IMEI}', '{IMSI}',{carrier},
        {physicalNetwork}, {blocked}, {autoSub}, '{description}', '{mac}', '{type}', '{productID}',
        {userIntID}, '{tenantID}')
    RETURNING id
)
INSERT INTO devices(id, "deviceType", gateway, lora, "modBusIndex", "metaData", "parentDevice")
    SELECT id, {deviceType}, {gateway}, {lora}, {modBusIndex}, {metaData}, {parentDevice}
    FROM {client};
"""

query_column_default = """
SELECT column_name, column_default
FROM INFORMATION_SCHEMA.COLUMNS
WHERE table_name = 'clients'
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
FROM clients
WHERE "productID" = ANY ('{{{products_uid}}}'::varchar[]);
"""

query_device_by_imei_sql = """
SELECT "IMEI" 
FROM clients
WHERE "IMEI" = ANY ('{{{devices_imei}}}'::varchar[])
    AND "tenantID"='{tenantID}';
"""