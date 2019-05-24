dict_code_sql = """
SELECT code,
       array_agg("codeValue") AS values,
       array_agg("{language}Label") AS labels
FROM dict_code
GROUP BY code
"""

query_devices_sql = """
SELECT devices.*,
       "lwm2mData"->>'IMEI' AS "IMEI",
       "lwm2mData"->>'IMSI' AS "IMSI",
       users.username AS "createUser",
       products."productName",
       products."cloudProtocol"
FROM devices
       JOIN end_devices ON end_devices.id = devices.id
       JOIN users ON users.id = devices."userIntID"
       JOIN products ON products."productID" = devices."productID"
"""

device_import_sql = """
WITH devices AS (
    INSERT INTO devices(
        "createAt", "deviceName", "deviceType", "productID",
        "authType", "upLinkNetwork", "deviceID", "deviceUsername", "token",
        "location", "latitude", "longitude",
        "manufacturer", "serialNumber", "softVersion", "hardwareVersion",
        "deviceConsoleIP", "deviceConsoleUsername", "deviceConsolePort",
        "mac", "userIntID", "tenantID"
        )
    VALUES (
        '{createAt}', '{deviceName}', '{deviceType}', '{productID}',
        '{authType}', '{upLinkNetwork}', '{deviceID}', '{deviceUsername}', '{token}',
        '{location}', '{latitude}', '{longitude}',
        '{manufacturer}', '{serialNumber}', '{softVersion}', '{hardwareVersion}',
        '{deviceConsoleIP}', '{deviceConsoleUsername}', '{deviceConsolePort}',
        '{mac}', '{userIntID}', '{tenantID}'
        )
    RETURNING id
)
INSERT INTO end_devices(
        id, "upLinkSystem", gateway,
        "loraData", "lwm2mData", "modbusData", "parentDevice"
    )
SELECT id, 
      '{upLinkSystem}', '{gateway}', '{parentDevice}',
      '{loraData}', '{lwm2mData}', '{modbusData}'
FROM devices;
"""


query_devices_name_sql = """
SELECT "deviceName"
FROM devices
WHERE "deviceName" = ANY ('{{{devicesName}}}'::varchar[])
    AND "tenantID"='{tenantID}';
"""

query_product_sql = """
SELECT "productName", "productID", "cloudProtocol"
FROM products
    JOIN users ON products."userIntID" = users.id
WHERE "productName" = ANY ('{{{productsName}}}'::varchar[])
    AND users."tenantID" = '{tenantID}';
"""

query_device_uid_sql = """
SELECT "deviceID"
FROM devices
WHERE "deviceID" = ANY ('{{{devicesID}}}'::varchar[])
"""

query_gateway_sql = """
SELECT devices."deviceName", devices.id
FROM devices
    JOIN gateways ON devices.id = gateways.id
WHERE devices."deviceName" = ANY ('{{{gatewaysName}}}'::varchar[])
    AND devices."tenantID" = '{tenantID}';
"""

query_tenant_devices_limit_sql = """
SELECT COUNT(devices.id), tenants."deviceCount"
FROM devices
    JOIN tenants on tenants."tenantID" = devices."tenantID"
WHERE tenants."tenantID" = '{tenantID}'
GROUP BY tenants."deviceCount"
"""
