insert_publish_logs_sql = """
INSERT INTO "publish_logs"
    ("topic", "streamID", "payload", "publishStatus", 
    "taskID", "deviceID", "tenantID")
VALUES ('{topic}', '{streamID}', '{payload}', '1', '{taskID}',
         '{deviceID}', '{tenantID}')
"""

update_publish_logs_sql = """
UPDATE client_publish_logs
SET "publishStatus"={taskStatus}
WHERE client_publish_logs."taskID"='{taskID}'
"""
