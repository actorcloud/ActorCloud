# 设备图表

### 设备历史图表数据
> GET /devices/<:id>/charts
##### Request args
* timeUnit(string): 5m, 1h, 6h, 1d, 1w
 
##### Example response
```json
[
    {
        "chartData": {
            "time": [
                "2019-05-07 14:04:30"
            ],
            "value": [
                80
            ]
        },
        "chartName": "温湿度数据流/湿度",
        "dataPointID": "hum",
        "streamID": "hum_temp"
    },
    {
        "chartData": {
            "time": [
                "2019-05-07 14:04:30"
            ],
            "value": [
                20
            ]
        },
        "chartName": "温湿度数据流/温度",
        "dataPointID": "temp",
        "streamID": "hum_temp"
    }
]
```

### 设备最新数据
> GET /last_data_charts

##### Example response
```json
[
    {
        "chartData": {
            "time": "2019-05-07 14:04:30",
            "value": 80
        },
        "chartName": "温湿度数据流/湿度",
        "dataPointID": "hum",
        "streamID": "hum_temp"
    },
    {
        "chartData": {
            "time": "2019-05-07 14:04:30",
            "value": 20
        },
        "chartName": "温湿度数据流/温度",
        "dataPointID": "temp",
        "streamID": "hum_temp"
    }
]
```