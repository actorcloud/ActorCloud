query_base_devices_sql = """
SELECT
       devices.id, devices."authType", devices."deviceID", 
       devices."deviceUsername", devices.token,
       devices."productID", devices."tenantID",
       lower(dict_code."enLabel") AS protocol
FROM devices
JOIN products  ON devices."productID" = products."productID"
JOIN dict_code ON dict_code."codeValue" = products."cloudProtocol"
WHERE
      devices."deviceID" = '{deviceID}'
  AND devices.blocked = 0
  AND dict_code.code = 'cloudProtocol'
"""

device_cert_auth_sql = """
SELECT
       devices.id, devices."authType", devices."deviceID", 
       devices."deviceUsername", devices.token,
       lower(dict_code."enLabel") AS protocol
FROM devices
JOIN certs_devices ON certs_devices."deviceIntID" = devices.id
JOIN certs ON certs.id = certs_devices."certIntID"
JOIN products  ON devices."productID" = products."productID"
JOIN dict_code ON dict_code."codeValue" = products."cloudProtocol"
WHERE
      devices."deviceID" = '{deviceID}'
  AND devices.blocked = 0
  AND certs."CN" = '{CN}'
  AND certs.enable = 1
  AND dict_code.code = 'cloudProtocol'
"""

insert_connect_logs_sql = """
INSERT INTO "connect_logs"
    ("IP", "connectStatus", "msgTime", "deviceID", "tenantID") 
VALUES('{IP}', {connectStatus}, '{msgTime}', '{deviceID}', '{tenantID}') 
"""

update_device_sql = """
UPDATE "devices" 
SET 
    "lastConnection"='{lastConnection}', 
    "deviceStatus"={deviceStatus} 
WHERE 
     devices."deviceID" = '{deviceID}'
"""

insert_publish_logs_sql = """
INSERT INTO "publish_logs"
    ("topic", "streamID", "payload", "publishStatus", 
    "taskID", "deviceID", "tenantID")
VALUES ('{topic}', '{streamID}', '{payload}', '1', '{taskID}',
         '{deviceID}', '{tenantID}')
"""

update_device_status_sql = """
UPDATE devices SET "deviceStatus"={deviceStatus} WHERE "id"={id}
"""

update_publish_logs_sql = """
UPDATE publish_logs
SET "publishStatus"={publishStatus}
WHERE publish_logs."taskID"='{taskID}'
"""
