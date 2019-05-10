# 下拉选择

### 获取所有类型设备
> GET /emq_select/devices
##### Example response
```json
[
    {
        "attr": {
            "cloudProtocol": 3,
            "deviceIntID": 13,
            "deviceType": 1,
            "gatewayProtocol": null
        },
        "label": "end devices",
        "value": "123123124124124"
    },
    {
        "attr": {
            "cloudProtocol": 7,
            "deviceIntID": 10,
            "deviceType": 2,
            "gatewayProtocol": 7
        },
        "label": "gatways",
        "value": "2441aa371f1030d22ec18e8f1d1ff123"
    }
 ]
```

### 获取终端设备
> GET /emq_select/devices?deviceType=1
##### Example response
```json
[
    {
        "attr": {
            "cloudProtocol": 3,
            "deviceIntID": 13,
            "deviceType": 1,
            "gatewayProtocol": null
        },
        "label": "end devices",
        "value": "123123124124124"
    }
]
```

### 获取网关设备
> GET /emq_select/devices?deviceType=2
##### Example response
```json
[
    {
        "attr": {
            "cloudProtocol": 7,
            "deviceIntID": 10,
            "deviceType": 2,
            "gatewayProtocol": 7
        },
        "label": "gatways",
        "value": "2441aa371f1030d22ec18e8f1d1ff123"
    }
]
```

### 获取测试中心所有类型设备
> GET /emq_select/test_center/devices
##### Example response
```json
[
    {
        "attr": {
            "cloudProtocol": 3,
            "deviceID": "123123124124124",
            "deviceType": 1,
            "deviceUsername": "10001106d111d6014f1e1ee4020ec916",
            "gatewayProtocol": null,
            "token": "717d1f68ff4ac721cf8172211124ca1c"
        },
        "label": "devices",
        "value": 13
    },
    {
        "attr": {
            "cloudProtocol": 7,
            "deviceID": "2441aa371f1030d22ec18e8f1d1ff123",
            "deviceType": 2,
            "deviceUsername": "2441aa371f1030d22ec18e8f1d1ff123",
            "gatewayProtocol": 7,
            "token": "a3a0c1e8d114d42c1977124d0120de03"
        },
        "label": "gateways",
        "value": 10
    }
 ]
```

### 获取终端设备
> GET /emq_select/devices?deviceType=1
##### Example response
```json
[
    {
        "attr": {
            "cloudProtocol": 3,
            "deviceIntID": 13,
            "deviceType": 1,
            "gatewayProtocol": null
        },
        "label": "end devices",
        "value": "123123124124124"
    }
]
```

### 获取网关设备
> GET /emq_select/devices?deviceType=2
##### Example response
```json
[
    {
        "attr": {
            "cloudProtocol": 7,
            "deviceIntID": 10,
            "deviceType": 2,
            "gatewayProtocol": 7
        },
        "label": "gatways",
        "value": "2441aa371f1030d22ec18e8f1d1ff123"
    }
]
```

### 获取产品
> GET /emq_select/products
##### Example response
```json
[
    {
        "attr": {
            "cloudProtocol": 7,
            "gatewayProtocol": 7,
            "productIntID": 8,
            "productType": 2
        },
        "label": "网关设备产品",
        "value": "14ebb1"
    },
    {
        "attr": {
            "cloudProtocol": 7,
            "gatewayProtocol": null,
            "productIntID": 7,
            "productType": 1
        },
        "label": "终端设备产品",
        "value": "a061f9"
    }
]
```

### 获取分组
> GET /emq_select/groups
##### Example response
```json
[
    {
        "attr": {
            "groupIntID": 1
        },
        "label": "分组",
        "value": "q121qs"
    }
]
```

### 获取分组未加入的设备
> GET /emq_select/groups/<:id>/not_joined_devices
##### Example response
```json
[
    {
        "label": "device2",
        "value": 2
    }
]
```

### 获取证书列表
> GET /emq_select/certs
##### Example response
```json
[
    {
        "label": "cert",
        "value": 1
    }
]
```

### 获取证书未加入的设备
> GET /emq_select/certs/<:id>/not_joined_devices
* 只返回认证类型(authType)为证书(2)的设备
##### Example response
```json
[
    {
        "label": "cert device",
        "value": 6
    }
]
```
