# 终端设备

### 查看终端设备列表
> GET /devices?deviceType=1
```json
{
    "items": [
        {
            "authType": 1,
            "authTypeLabel": "Token",
            "blocked": 0,
            "createAt": "2019-05-07 15:45:25",
            "description": null,
            "deviceConsoleIP": null,
            "deviceConsolePort": 22,
            "deviceConsoleUsername": null,
            "deviceID": "191c2b2d112122e0227588182cc1a8c9",
            "deviceName": "end device modbus",
            "deviceStatus": 0,
            "deviceStatusLabel": "离线",
            "deviceType": 1,
            "deviceUsername": "191c2b2d112122e0227588182cc1a8c9",
            "hardwareVersion": null,
            "id": 8,
            "lastConnection": null,
            "latitude": null,
            "location": null,
            "longitude": null,
            "mac": null,
            "manufacturer": null,
            "metaData": null,
            "productID": "a061f9",
            "serialNumber": null,
            "softVersion": null,
            "token": "e938c98a17a1790441a32e3133d2bdd9",
            "upLinkNetwork": 3,
            "updateAt": null
        }
    ],
    "meta": {
        "count": 1,
        "limit": 10,
        "page": 1
    }
}
```

### 获取终端设备详情
> GET /devices/<:id>?deviceType=1
```json
{
    "authType": 1,
    "authTypeLabel": "Token",
    "blocked": 0,
    "cloudProtocol": 1,
    "cloudProtocolLabel": "MQTT",
    "createAt": "2019-05-07 15:17:47",
    "createUser": "actorcloud",
    "description": null,
    "deviceConsoleIP": null,
    "deviceConsolePort": 22,
    "deviceConsoleUsername": null,
    "deviceID": "40901d0112437880c0319697cf0ee1e9",
    "deviceName": "end device",
    "deviceStatus": 0,
    "deviceStatusLabel": "离线",
    "deviceType": 1,
    "deviceUsername": "40901d0112437880c0319697cf0ee1e9",
    "gateway": null,
    "gatewayProtocol": null,
    "hardwareVersion": null,
    "id": 3,
    "lastConnection": null,
    "latitude": null,
    "location": null,
    "longitude": null,
    "lora": null,
    "lwm2m": null,
    "mac": null,
    "manufacturer": null,
    "metaData": null,
    "modbus": null,
    "parentDevice": null,
    "productID": "342f2f",
    "productIntID": 1,
    "productName": "MQTT 设备产品",
    "serialNumber": null,
    "softVersion": null,
    "token": "29010c08101e03e9fe04d122dd00d009",
    "upLinkNetwork": 3,
    "upLinkSystem": 1,
    "updateAt": null
}
```

### 新建终端设备
> POST /devices
##### Example request
```json
# mqtt
{
	"deviceName": "end device mqtt",
	"productID": "342f2f",
	"authType": 1,
	"upLinkNetwork": 3,
	"autoCreateCert":1,
	"upLinkSystem": 1,
	"deviceType": 1
}
# lwm2m
{
	"deviceName": "end device lwm2m",
	"productID": "201392",
	"authType": 1,
	"upLinkNetwork": 3,
	"autoCreateCert":1,
	"upLinkSystem": 1,
	"deviceType": 1,
	"lwm2m": {"autoSub": 1, "IMEI": "123456789asdqwe", "IMSI": "123456789asdqwe"}
}
# lora
{
	"deviceName": "end device lora",
	"productID": "112471",
	"authType": 1,
	"upLinkNetwork": 3,
	"autoCreateCert":1,
	"upLinkSystem": 1,
	"deviceType": 1,
	"lora": {
	            "type": "otaa", 
	            "region": "EU863-870", 
	            "appEUI": "123456789asdqwe", 
	            "appKey": "123456789asdqwe",
	             "fcntCheck": 1, 
	             "canJoin": true
	        }
}
# modbus
{
	"deviceName": "end device modbus",
	"productID": "a061f9",
	"authType": 1,
	"upLinkNetwork": 3,
	"autoCreateCert":1,
	"upLinkSystem": 1,
	"deviceType": 1,
	"modbusData": {"modBusIndex": 1}
}
```

### 更新终端设备
> POST /devices
##### Example request
```json

```