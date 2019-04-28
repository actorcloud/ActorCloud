# LWM2M 协议设备下发


### 自定义指令下发
###### 请求示例
> POST /device_publish
```json
{
	"deviceID": "738692655169712",
	"topic": "/19/1/0",
	"payload": "{\"led\":true}"
}
```