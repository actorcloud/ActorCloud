# 证书管理

### 获取证书下拉列表
> GET /emq_select/certs
##### Example response
```json
[
    {
        "label": "test2",
        "value": 1
    }
]
```

### 获取证书列表
> GET /certs
##### Example response
```json
{
    "items": [
        {
            "certName": "test",
            "createAt": "2019-05-05 14:20:04",
            "enable": 1,
            "id": 1
        }
    ],
    "meta": {
        "count": 1,
        "limit": 10,
        "page": 1
    }
}
```

### 查看证书详情
> GET /certs/<id:>
##### Example response
```json
{
    "CN": "CI6EZkvoN:50ad5ddd1e05da5d61566d8818",
    "cert": "-----BEGIN CERTIFICATE-----xxxxx==-----END CERTIFICATE-----\n",
    "certName": "test",
    "createAt": "2019-05-05 14:20:04",
    "createUser": "actorcloud",
    "enable": 1,
    "id": 1,
    "key": "-----BEGIN PRIVATE KEY-----xxxxx==-----END PRIVATE KEY-----\n",
    "root": "-----BEGIN CERTIFICATE-----xxxxx==-----END CERTIFICATE-----\n",
    "updateAt": null
}
```

### 新建证书
> POST /certs
##### Example request
```json
{
	"certName": "test",
	"enable": 1
}
```
##### Example response
```json
{
    "CN": "CI6EZkvoN:50ad5ddd1e05da5d61566d8818",
    "cert": "-----BEGIN CERTIFICATE-----xxxxx==-----END CERTIFICATE-----\n",
    "certName": "test",
    "createAt": "2019-05-05 14:20:04",
    "enable": 1,
    "id": 1,
    "key": "-----BEGIN PRIVATE KEY-----xxxxx==-----END PRIVATE KEY-----\n",
    "root": "-----BEGIN CERTIFICATE-----xxxxx==-----END CERTIFICATE-----\n",
    "updateAt": null
}
```
### 更新证书信息
> PUT /certs/<id:>
##### Example request
```json
{
	"certName": "test",
	"enable": 0
}
```
##### Example response
```json
{
    "CN": "CI6EZkvoN:50ad5ddd1e05da5d61566d8818",
    "cert": "-----BEGIN CERTIFICATE-----xxxxx==-----END CERTIFICATE-----\n",
    "certName": "test",
    "createAt": "2019-05-05 14:20:04",
    "createUser": "actorcloud",
    "enable": 0,
    "id": 1,
    "key": "-----BEGIN PRIVATE KEY-----xxxxx==-----END PRIVATE KEY-----\n",
    "root": "-----BEGIN CERTIFICATE-----xxxxx==-----END CERTIFICATE-----\n",
    "updateAt": "2019-05-05 14:34:43"
}
```

### 删除证书
> DELETE /certs?ids=<id:>
##### 错误提示
```json

```

### 获取证书未绑定的clients
> GET /emq_select/certs/<id:>/not_joined_devices
```json
[
    {
        "label": "cert_test2",
        "value": 22
    }
]
```

### 获取证书绑定的设备
> GET /certs/<id:>/devices
##### Example response
```json
{
    "items": [
        {
            "authType": 2,
            "deviceID": "c111828ea1f1a8168aed08a270124fa2",
            "deviceName": "cert_test",
            "deviceUsername": "c111828ea1f1a8168aed08a270124fa2",
            "hardwareVersion": null,
            "id": 20
        }
    ],
    "meta": {
        "count": 1,
        "limit": 10,
        "page": 1
    }
}
```
### 证书绑定设备
> POST /certs/<id:>/devices
##### Example request
```json
{
	"devices": [21]
}
```
##### Example response
```json
{
    "devices": [21]
}
```
### 证书解绑devices
> DELETE /certs/<id:>/devices?ids=21
##### Example error
```json

```
