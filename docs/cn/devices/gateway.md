# 网关

### 查看网关列表
> GET /devices?deviceType=2
```json
{
    "items": [
        {
            "authType": 1,
            "authTypeLabel": "Token",
            "blocked": 0,
            "createAt": "2019-05-08 11:39:04",
            "description": null,
            "deviceConsoleIP": null,
            "deviceConsolePort": 22,
            "deviceConsoleUsername": null,
            "deviceID": "2441aa371f1030d22ec18e8f1d1ff123",
            "deviceName": "gatways",
            "deviceStatus": 0,
            "deviceStatusLabel": "离线",
            "deviceType": 2,
            "deviceUsername": "2441aa371f1030d22ec18e8f1d1ff123",
            "hardwareVersion": null,
            "id": 10,
            "lastConnection": null,
            "latitude": null,
            "location": null,
            "longitude": null,
            "mac": null,
            "manufacturer": null,
            "metaData": null,
            "productID": "14ebb1",
            "serialNumber": null,
            "softVersion": null,
            "token": "a3a0c1e8d114d42c1977124d0120de03",
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

### 获取网关详情
> GET /devices/<:id>?deviceType=2
```json
{
    "authType": 1,
    "authTypeLabel": "Token",
    "blocked": 0,
    "cloudProtocol": 7,
    "cloudProtocolLabel": "Modbus",
    "createAt": "2019-05-08 11:39:04",
    "createUser": "actorcloud",
    "description": null,
    "deviceConsoleIP": null,
    "deviceConsolePort": 22,
    "deviceConsoleUsername": null,
    "deviceID": "2441aa371f1030d22ec18e8f1d1ff123",
    "deviceName": "gatways",
    "deviceStatus": 0,
    "deviceStatusLabel": "离线",
    "deviceType": 2,
    "deviceUsername": "2441aa371f1030d22ec18e8f1d1ff123",
    "gatewayProtocol": 7,
    "gatewayProtocolLabel": "Modbus",
    "hardwareVersion": null,
    "id": 10,
    "lastConnection": null,
    "latitude": null,
    "location": null,
    "longitude": null,
    "mac": null,
    "manufacturer": null,
    "metaData": null,
    "productID": "14ebb1",
    "productIntID": 8,
    "productName": "modbus网关",
    "serialNumber": null,
    "softVersion": null,
    "token": "a3a0c1e8d114d42c1977124d0120de03",
    "upLinkNetwork": 3,
    "updateAt": null
}
```

### 新建网关
> POST /devices
##### Example request
```json
{
	"deviceName": "gatways",
	"productID": "14ebb1",
	"deviceType": 2,
	"authType": 1,
	"upLinkNetwork": 3,
	"autoCreateCert":1,
	"upLinkSystem": 1
}
```

### 更新网关
> POST /devices
##### Example request
```json

```

### 删除网关
> POST /devices?deviceType=2&ids=11