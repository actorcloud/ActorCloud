dict_code_sql = """
SELECT code,
       array_agg("codeValue") AS values,
       array_agg("{language}Label") AS labels
FROM dict_code
WHERE code IN ('deviceStatus', 'authType', 'deviceType', 'deviceBlocked',
               'cloudProtocol')
GROUP BY code
"""

devices_query_sql = """
SELECT clients.*,
       devices."deviceType",
       users.username AS "createUser",
       products."productName",
       products."cloudProtocol"
FROM clients
       JOIN devices ON devices.id = clients.id
       JOIN users ON users.id = clients."userIntID"
       JOIN products ON products."productID" = clients."productID"
"""
