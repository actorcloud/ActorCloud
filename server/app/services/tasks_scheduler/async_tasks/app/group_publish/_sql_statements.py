query_group_of_uid_sql = """
SELECT groups."groupID"
FROM groups
WHERE groups."groupID" = '{group_uid}'
"""

query_group_devices_sql = """
SELECT group_devices."deviceIntID",
       group_devices."deviceID"
FROM group_devices
WHERE group_devices."groupID" = '{group_uid}'
"""

insert_group_control_log_sql = """
INSERT INTO "group_publish_logs"("createAt", "payload", "taskID",
                                 "publishStatus", "groupID", "userIntID",
                                 "topic")
VALUES ('{createAt}', '{payload}', '{taskID}',
         {publishStatus}, '{groupID}', {userIntID}, '{topic}') RETURNING "id";
"""

update_devices_control_log_sql = """
UPDATE device_publish_logs
SET "publishStatus"=0
WHERE device_publish_logs."taskID" = ANY ('{{{task_uids}}}'::varchar[])
"""

update_group_control_log_sql = """
UPDATE group_publish_logs
SET "publishStatus"=0
WHERE group_publish_logs.id = {group_control_id}
"""
