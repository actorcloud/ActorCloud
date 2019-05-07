dict_code_sql = """
SELECT code,
       array_agg("codeValue") AS values,
       array_agg("{language}Label") AS labels
FROM dict_code
WHERE code IN ('deviceStatus', 'authType', 'deviceBlocked', 'cloudProtocol')
GROUP BY code
"""

devices_query_sql = """
SELECT devices.*,
       users.username AS "createUser",
       products."productName",
       products."cloudProtocol"
FROM devices
       JOIN devices ON devices.id = devices.id
       JOIN users ON users.id = devices."userIntID"
       JOIN products ON products."productID" = devices."productID"
"""
