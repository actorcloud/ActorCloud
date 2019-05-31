insert_publish_logs_sql = """
INSERT INTO "publish_logs"
    ("topic", "streamID", "payload", "publishStatus", 
    "taskID", "deviceID", "tenantID")
VALUES ('{topic}', '{streamID}', '{payload}', '1', '{taskID}',
         '{deviceID}', '{tenantID}')
"""

update_publish_logs_sql = """
UPDATE publish_logs
SET "publishStatus"={publishStatus}
WHERE publish_logs."taskID"='{taskID}'
"""
