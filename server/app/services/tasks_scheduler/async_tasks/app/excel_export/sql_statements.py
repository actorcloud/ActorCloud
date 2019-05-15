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
       lwm2m.*,
       users.username AS "createUser",
       products."productName",
       products."cloudProtocol"
FROM devices
       JOIN end_devices ON end_devices.id = devices.id
       CROSS JOIN LATERAL jsonb_to_record(end_devices."lwm2mData") AS lwm2m("IMEI" text, "IMSI" text)
       JOIN users ON users.id = devices."userIntID"
       JOIN products ON products."productID" = devices."productID"
"""
