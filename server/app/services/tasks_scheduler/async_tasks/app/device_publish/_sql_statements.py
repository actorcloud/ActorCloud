query_id_device_sql = """
SELECT devices.id AS device_id
FROM devices
WHERE devices.blocked = 0
  AND devices.id ={deviceIntID}
"""

insert_device_publish_logs_sql = """
INSERT INTO "client_publish_logs"
("createAt", "payload", "topic", "path", "taskID", "publishStatus",
 "userIntID", "deviceIntID", "controlType")
VALUES ('{createAt}', '{payload}', '{topic}', '{path}', '{taskID}',
         {publishStatus}, {userIntID}, {deviceIntID}, {controlType})
"""

query_path_lwm2m_sql = """
SELECT lwm2m_items."itemOperations", lwm2m_items."itemType"
FROM lwm2m_items
       JOIN lwm2m_instance_items
            ON lwm2m_instance_items."itemIntID" = lwm2m_items.id
WHERE lwm2m_instance_items.path = '{path}'
  AND lwm2m_instance_items."deviceIntID" = '{deviceIntID}'
  AND lwm2m_instance_items."tenantID" = '{tenantID}'
"""

update_device_publish_logs_sql = """
UPDATE client_publish_logs
SET "publishStatus"={taskStatus}
WHERE client_publish_logs."taskID"='{taskID}'
"""
