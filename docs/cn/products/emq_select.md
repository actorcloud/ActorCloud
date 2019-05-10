# 下拉选择

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

### 获取数据流
> GET /emq_select/data_streams
##### request args:
* productID:  产品ID, type=string
```json
[
    {
        "attr": {
            "productID": "342f2f",
            "streamID": "hum_temp",
            "streamType": 1
        },
        "label": "温湿度数据流",
        "value": 1
    }
]
```

### 获取功能点
> GET /emq_select/data_points
##### request args:
* productID:  产品ID, type=string
* dataStreamIntID: 数据流id, type=integer
##### Example response:
```json
[
    {
        "attr": {
            "dataPointID": "hum",
            "dataTransType": 1,
            "pointDataType": 1,
            "productID": "342f2f"
        },
        "label": "湿度",
        "value": 2
    },
    {
        "attr": {
            "dataPointID": "temp",
            "dataTransType": 1,
            "pointDataType": 1,
            "productID": "342f2f"
        },
        "label": "温度",
        "value": 1
    }
]
```

### 获取数据流功能点
> GET /emq_select/data_points
##### request args:
* productID:  产品ID, type=string
```json
[
    {
        "children": [
            {
                "label": "温度",
                "value": "temp"
            },
            {
                "label": "湿度",
                "value": "hum"
            }
        ],
        "label": "温湿度数据流",
        "value": "hum_temp"
    },
    {
        "children": [
            {
                "label": "电量",
                "value": "battery"
            }
        ],
        "label": "网关信息",
        "value": "gateway_info"
    }
]
```

