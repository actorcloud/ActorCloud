query_ids_device_sql = """
SELECT clients.id                   AS "deviceIntID",
       clients."deviceID",
       clients."productID",
       lower(dict_code."codeLabel") AS protocol
FROM clients
       JOIN products ON products."productID" = clients."productID"
       JOIN dict_code ON dict_code."codeValue" = products."cloudProtocol"
WHERE dict_code.code = 'cloudProtocol'
  AND clients.blocked = 0
  AND clients.id = ANY ('{{{client_ids}}}'::int[])
"""

query_uids_group_sql = """
SELECT groups.id                    AS "groupIntID",
       groups."groupID",
       groups."productID",
       lower(dict_code."codeLabel") AS protocol
FROM groups
       JOIN products ON products."productID" = groups."productID"
       JOIN dict_code ON dict_code."codeValue" = products."productType"
WHERE dict_code.code = 'cloudProtocol'
  AND groups."groupID" = ANY ('{{{group_uids}}}'::varchar[])
"""

update_crontab_task_sql = """
UPDATE "timer_publish"
SET "taskStatus"=3
WHERE timer_publish.id = ANY ('{{{crontab_ids}}}'::int[])
"""
