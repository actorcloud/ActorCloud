query_id_device_sql = """
SELECT clients.id AS device_id
FROM clients
WHERE clients.blocked = 0
  AND clients.id ={deviceIntID}
"""

insert_device_control_logs_sql = """
INSERT INTO "device_control_logs"
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

update_device_control_logs_sql = """
UPDATE device_control_logs
SET "publishStatus"={taskStatus}
WHERE device_control_logs."taskID"='{taskID}'
"""
