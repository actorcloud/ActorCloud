const dict = {
  access: [
    {
      label: '发布',
      value: 1,
      key: 'PUBLISH',
    },
    {
      label: '订阅',
      value: 2,
      key: 'SUBSCRIBE',
    },
    {
      label: '发布或订阅',
      value: 3,
      key: 'PUBLISH_OR_SUBSCRIBE',
    },
  ],
  actionType: [
    {
      label: '告警',
      value: 1,
      key: 'ALERT',
    },
    {
      label: '邮件',
      value: 2,
      key: 'EMAIL',
    },
    {
      label: 'Webhook',
      value: 3,
      key: 'WEBHOOK',
    },
    {
      label: '指令下发',
      value: 4,
      key: 'COMMAND',
    },
  ],
  aggregateType: [
    {
      label: '最大值',
      value: 1,
      key: 'MAXIMUM',
    },
    {
      label: '最小值',
      value: 2,
      key: 'MINIMUM',
    },
    {
      label: '平均值',
      value: 3,
      key: 'AVERAGE',
    },
    {
      label: '累计值',
      value: 4,
      key: 'CUMULATIVE',
    },
  ],
  alertSeverity: [
    {
      label: '紧急',
      value: 1,
      key: 'URGENT',
    },
    {
      label: '主要',
      value: 2,
      key: 'MAIN',
    },
    {
      label: '次要',
      value: 3,
      key: 'SECONDARY',
    },
    {
      label: '警告',
      value: 4,
      key: 'WARNING',
    },
  ],
  allow: [
    {
      label: '拒绝',
      value: 0,
      key: 'DENY',
    },
    {
      label: '允许',
      value: 1,
      key: 'ALLOWED',
    },
  ],
  appStatus: [
    {
      label: '不可用',
      value: 0,
      key: 'DISABLED',
    },
    {
      label: '可用',
      value: 1,
      key: 'AVAILABLE',
    },
  ],
  authType: [
    {
      label: 'Token',
      value: 1,
      key: 'TOKEN',
    },
    {
      label: '证书',
      value: 2,
      key: 'CERTIFICATE',
    },
  ],
  autoCreateCert: [
    {
      label: '否',
      value: 0,
      key: 'FALSE',
    },
    {
      label: '是',
      value: 1,
      key: 'TRUE',
    },
  ],
  cardChartType: [
    {
      label: '折线图',
      value: 1,
      key: 'LINE',
    },
    {
      label: '柱状图',
      value: 2,
      key: 'HISTOGRAM',
    },
    {
      label: '饼图',
      value: 3,
      key: 'PIE',
    },
    {
      label: '仪表图',
      value: 4,
      key: 'INSTRUMENT',
    },
    {
      label: '数值',
      value: 5,
      key: 'NUMERICAL',
    },
    {
      label: '地图',
      value: 6,
      key: 'MAP',
    },
  ],
  cardDataSource: [
    {
      label: '设备',
      value: 1,
      key: 'DEVICE',
    },
    {
      label: '产品',
      value: 2,
      key: 'PRODUCT',
    },
    {
      label: '分组',
      value: 3,
      key: 'GROUP',
    },
    {
      label: '平台',
      value: 4,
      key: 'PLATFORM',
    },
  ],
  cardDeviceStatistic: [
    {
      label: '指标',
      value: 101,
      key: 'INDICATORS',
    },
    {
      label: '功能点',
      value: 102,
      key: 'FUNCTION_POINT',
    },
  ],
  cardGroupStatistic: [
    {
      label: '设备数量',
      value: 301,
      key: 'NUMBER_OF_DEVICES',
    },
    {
      label: '在线设备数量',
      value: 302,
      key: 'NUMBER_OF_ONLINE_DEVICES',
    },
    {
      label: '离线设备数量',
      value: 303,
      key: 'NUMBER_OF_OFFLINE_DEVICES',
    },
    {
      label: '设备告警次数',
      value: 304,
      key: 'NUMBER_OF_DEVICE_ALARMS',
    },
    {
      label: '设备在线/离线情况',
      value: 305,
      key: 'NUMBER_OF_ONLINE_OFFLINE',
    },
  ],
  cardPlatformStatistic: [
    {
      label: '设备数量',
      value: 401,
      key: 'NUMBER_OF_DEVICES',
    },
    {
      label: '在线设备数量',
      value: 402,
      key: 'NUMBER_OF_ONLINE_DEVICES',
    },
    {
      label: '离线设备数量',
      value: 403,
      key: 'NUMBER_OF_OFFLINE_DEVICES',
    },
    {
      label: '设备告警次数',
      value: 404,
      key: 'NUMBER_OF_DEVICE_ALARMS',
    },
    {
      label: '设备在线/离线情况',
      value: 405,
      key: 'NUMBER_OF_ONLINE_OFFLINE',
    },
    {
      label: '产品数量',
      value: 406,
      key: 'NUMBER_OF_PRODUCT',
    },
    {
      label: '分组数量',
      value: 407,
      key: 'GROUP_NUMBER',
    },
    {
      label: 'API调用次数',
      value: 408,
      key: 'API_CALLS',
    },
    {
      label: '消息数',
      value: 409,
      key: 'MESSAGE_NUMBER',
    },
    {
      label: '流量',
      value: 410,
      key: 'TRAFFIC',
    },
  ],
  cardProductStatistic: [
    {
      label: '设备数量',
      value: 201,
      key: 'NUMBER_OF_DEVICES',
    },
    {
      label: '在线设备数量',
      value: 202,
      key: 'NUMBER_OF_ONLINE_DEVICES',
    },
    {
      label: '离线设备数量',
      value: 203,
      key: 'NUMBER_OF_OFFLINE_DEVICES',
    },
    {
      label: '设备告警次数',
      value: 204,
      key: 'NUMBER_OF_DEVICE_ALARMS',
    },
    {
      label: '设备在线/离线情况',
      value: 205,
      key: 'NUMBER_OF_ONLINE_OFFLINE',
    },
  ],
  carrier: [
    {
      label: '中国电信',
      value: 1,
      key: 'CTCC',
    },
    {
      label: '中国移动',
      value: 2,
      key: 'CMCC',
    },
    {
      label: '中国联通',
      value: 3,
      key: 'CUCC',
    },
    {
      label: '其他',
      value: 4,
      key: 'OTHER',
    },
  ],
  certEnable: [
    {
      label: '不可用',
      value: 0,
      key: 'DISABLE',
    },
    {
      label: '可用',
      value: 1,
      key: 'ENABLE',
    },
  ],
  chargeType: [
    {
      label: '免费',
      value: 1,
      key: 'FREE',
    },
    {
      label: '时长',
      value: 2,
      key: 'DURATION',
    },
    {
      label: '次数',
      value: 3,
      key: 'TIMES',
    },
    {
      label: '条数',
      value: 4,
      key: 'NUMBERS',
    },
  ],
  chartType: [
    {
      label: '折线图',
      value: 1,
      key: 'LINE',
    },
    {
      label: '柱状图',
      value: 2,
      key: 'HISTOGRAM',
    },
  ],
  cloudProtocol: [
    {
      label: 'MQTT',
      value: 1,
      key: 'MQTT',
    },
    {
      label: 'CoAP',
      value: 2,
      key: 'COAP',
    },
    {
      label: 'LwM2M',
      value: 3,
      key: 'LWM2M',
    },
    {
      label: 'LoRa',
      value: 4,
      key: 'LORA',
    },
    {
      label: 'HTTP',
      value: 5,
      key: 'HTTP',
    },
    {
      label: 'WebSocket',
      value: 6,
      key: 'WEBSOCKET',
    },
    {
      label: 'Modbus',
      value: 7,
      key: 'MODBUS',
    },
  ],
  connectStatus: [
    {
      label: '下线',
      value: 0,
      key: 'OFFLINE',
    },
    {
      label: '上线',
      value: 1,
      key: 'ONLINE',
    },
    {
      label: '认证失败',
      value: 2,
      key: 'AUTHENTICATION_FAILED',
    },
  ],
  dataTransType: [
    {
      label: '只上报',
      value: 1,
      key: 'UP',
    },
    {
      label: '只下发',
      value: 2,
      key: 'DOWN',
    },
    {
      label: '可上报可下发',
      value: 3,
      key: 'UP_DOWN',
    },
  ],
  deviceBlocked: [
    {
      label: '允许访问',
      value: 0,
      key: 'ALLOWED',
    },
    {
      label: '不允许访问',
      value: 1,
      key: 'NO_ALLOWED',
    },
  ],
  deviceStatus: [
    {
      label: '离线',
      value: 0,
      key: 'OFFLINE',
    },
    {
      label: '在线',
      value: 1,
      key: 'ONLINE',
    },
    {
      label: '休眠',
      value: 2,
      key: 'DORMANCY',
    },
  ],
  deviceType: [
    {
      label: '终端',
      value: 1,
      key: 'TERMINAL',
    },
    {
      label: '网关',
      value: 2,
      key: 'GATEWAY',
    },
    {
      label: '智能手机',
      value: 3,
      key: 'SMART_PHONE',
    },
  ],
  enable: [
    {
      label: '不允许',
      value: 0,
      key: 'ENABLE',
    },
    {
      label: '允许',
      value: 1,
      key: 'DISABLE',
    },
  ],
  fcntCheck: [
    {
      label: 'Strict 16-bit',
      value: 0,
      key: 'STRICT_16_BIT',
    },
    {
      label: 'Strict 32-bit',
      value: 1,
      key: 'STRICT_32_BIT',
    },
    {
      label: 'Reset on zero',
      value: 2,
      key: 'RESET_ON_ZERO',
    },
    {
      label: 'Disabled',
      value: 3,
      key: 'DISABLED',
    },
  ],
  feeType: [
    {
      label: '充值',
      value: 1,
      key: 'TOP_UP',
    },
    {
      label: '消费',
      value: 2,
      key: 'CONSUMPTION',
    },
  ],
  inviteStatus: [
    {
      label: '未加入',
      value: 0,
      key: 'NOT_JOIN',
    },
    {
      label: '已加入',
      value: 1,
      key: 'JOINED',
    },
  ],
  invoiceStatus: [
    {
      label: '审核中',
      value: 0,
      key: 'IN_REVIEW',
    },
    {
      label: '已取消',
      value: 1,
      key: 'CANCELLED',
    },
    {
      label: '已邮寄',
      value: 2,
      key: 'MAILED',
    },
    {
      label: '未过审',
      value: 3,
      key: 'NOT_CAREFUL',
    },
  ],
  invoiceType: [
    {
      label: '个人增值税普通发票',
      value: 1,
      key: 'PERSONAL_VAT_INVOICE',
    },
    {
      label: '企业增值税普通发票',
      value: 2,
      key: 'ENTERPRISE_VAT_INVOICE',
    },
  ],
  isLogged: [
    {
      label: '失败',
      value: 0,
      key: 'FAILURE',
    },
    {
      label: '成功',
      value: 1,
      key: 'SUCCESSFUL',
    },
  ],
  locationType: [
    {
      label: '经度',
      value: 1,
      key: 'LONGITUDE',
    },
    {
      label: '纬度',
      value: 2,
      key: 'LATITUDE',
    },
    {
      label: '海拔',
      value: 3,
      key: 'ALTITUDE',
    },
  ],
  messageType: [
    {
      label: '财务消息',
      value: 1,
      key: 'FINANCIAL_MESSAGES',
    },
    {
      label: '产品消息',
      value: 2,
      key: 'PRODUCT_MESSAGES',
    },
    {
      label: '安全消息',
      value: 3,
      key: 'SAFETY_MESSAGES',
    },
    {
      label: '其它消息',
      value: 4,
      key: 'OTHER_MESSAGES',
    },
    {
      label: '公告',
      value: 5,
      key: 'ANNOUNCEMENT',
    },
  ],
  msgType: [
    {
      label: 'login',
      value: 1,
      key: 'LOGIN',
    },
    {
      label: 'subscribe',
      value: 2,
      key: 'SUBSCRIBE',
    },
    {
      label: 'unsubscribe',
      value: 3,
      key: 'UNSUBSCRIBE',
    },
    {
      label: 'publish',
      value: 4,
      key: 'PUBLISH',
    },
    {
      label: 'receive',
      value: 5,
      key: 'RECEIVE',
    },
  ],
  physicalNetwork: [
    {
      label: 'WIFI',
      value: 1,
      key: 'WIFI',
    },
    {
      label: '2G',
      value: 2,
      key: 'GSM',
    },
    {
      label: '3G',
      value: 3,
      key: 'WCDMA',
    },
    {
      label: '4G',
      value: 4,
      key: 'LTE',
    },
    {
      label: 'NB-IOT',
      value: 5,
      key: 'NB_IOT',
    },
    {
      label: 'BlueTooth',
      value: 6,
      key: 'BLUETOOTH',
    },
  ],
  pointDataType: [
    {
      label: '数值',
      value: 1,
      key: 'NUMERICAL',
    },
    {
      label: '字符串',
      value: 3,
      key: 'STRING',
    },
    {
      label: '故障',
      value: 4,
      key: 'FAULT',
    },
    {
      label: '布尔',
      value: 5,
      key: 'BOOLEAN',
    },
    {
      label: '定长字符串',
      value: 11,
      key: 'FIXED_STRING',
    },
    {
      label: '变长字符串',
      value: 12,
      key: 'STRINGS',
    },
    {
      label: '定长binary',
      value: 13,
      key: 'FIXED_BINARY',
    },
    {
      label: '变长binary',
      value: 14,
      key: 'BINARYS',
    },
    {
      label: '有符号整型',
      value: 15,
      key: 'SIGNED_INTEGER',
    },
    {
      label: '无符号整型',
      value: 16,
      key: 'UNSIGNED_INTEGER',
    },
    {
      label: '单精度浮点型',
      value: 17,
      key: 'SINGLE_FLOATING',
    },
    {
      label: '双精度浮点型',
      value: 18,
      key: 'DOUBLE_FLOATING',
    },
    {
      label: 'bit类型',
      value: 19,
      key: 'BIT_TYPE',
    },
  ],
  productResource: [
    {
      label: '硬件版本',
      value: 'hardwareVersion',
      key: 'HARDWARE_VERSION',
    },
    {
      label: '制造商',
      value: 'manufacturer',
      key: 'MANUFACTURERS',
    },
    {
      label: '序列号',
      value: 'serialNumber',
      key: 'SERIAL_NUMBER',
    },
    {
      label: '软件版本',
      value: 'softVersion',
      key: 'SOFTWARE_VERSION',
    },
  ],
  publishStatus: [
    {
      label: '下发失败',
      value: 0,
      key: 'FAILURE',
    },
    {
      label: '已下发',
      value: 1,
      key: 'SUCCESS',
    },
    {
      label: '已到达',
      value: 2,
      key: 'REACHED',
    },
    {
      label: '定时下发',
      value: 3,
      key: 'TIMING',
    },
  ],
  publishType: [
    {
      label: '设备下发',
      value: 0,
      key: 'DEVICE',
    },
    {
      label: '分组下发',
      value: 1,
      key: 'GROUP',
    },
  ],
  region: [
    {
      label: 'Australia 915-928MHz',
      value: 'AU915-928',
      key: 'AUSTRALIA_915_928MHZ',
    },
    {
      label: 'China 470-510MHz',
      value: 'CN470-510',
      key: 'CHINA_470_510MHZ',
    },
    {
      label: 'China 779-787MHz',
      value: 'CN779-787',
      key: 'CHINA_779_787MHZ',
    },
    {
      label: 'EU 433MHz',
      value: 'EU433',
      key: 'I_433MHZ',
    },
    {
      label: 'EU 863-870MHz',
      value: 'EU863-870',
      key: 'EU_863_870MHZ',
    },
    {
      label: 'South Korea 920-923MHz',
      value: 'KR920-923',
      key: 'SOUTH_KOREA_920_923MHZ',
    },
    {
      label: 'US 902-928MHz',
      value: 'US902-928',
      key: 'US_902_928MHZ',
    },
    {
      label: 'US 902-928MHz (Private)',
      value: 'US902-928-PR',
      key: 'US_902_928MHZ_(PRIVATE)',
    },
  ],
  ruleType: [
    {
      label: 'Webhook',
      value: 1,
      key: 'WEBHOOK',
    },
  ],
  scheduleType: [
    {
      label: '定时不重复',
      value: 0,
      key: 'NOT_REPEAT',
    },
    {
      label: '定时重复',
      value: 1,
      key: 'REPEAT',
    },
    {
      label: '已完成',
      value: 2,
      key: 'COMPLETED',
    },
  ],
  scopeType: [
    {
      label: '活动区域',
      value: 1,
      key: 'ACTIVE_AREA',
    },
    {
      label: '禁止区域',
      value: 2,
      key: 'FORBIDDEN_AREA',
    },
  ],
  sdkType: [
    {
      label: '应用程序',
      value: 1,
      key: 'APPLICATION',
    },
    {
      label: '固件',
      value: 2,
      key: 'FIRMWARE',
    },
    {
      label: '内核',
      value: 3,
      key: 'KERNEL',
    },
  ],
  serviceGroup: [
    {
      label: '基础服务',
      value: 1,
      key: 'BASIC_SERVICES',
    },
    {
      label: '设备管理平台 DMP',
      value: 2,
      key: 'DMP',
    },
    {
      label: '应用使能平台 AEP',
      value: 3,
      key: 'AEP',
    },
  ],
  streamDataType: [
    {
      label: 'JSON',
      value: 1,
      key: 'JSON',
    },
    {
      label: '二进制',
      value: 2,
      key: 'BINARY',
    },
  ],
  streamType: [
    {
      label: '终端上报',
      value: 1,
      key: 'UP',
    },
    {
      label: '数据下发',
      value: 2,
      key: 'DOWN',
    },
  ],
  templateType: [
    {
      label: '开关',
      value: 1,
      key: 'SWITCH',
    },
    {
      label: '枚举',
      value: 2,
      key: 'ENUMERATION',
    },
    {
      label: '数值',
      value: 3,
      key: 'NUMERICAL',
    },
    {
      label: '字符串',
      value: 4,
      key: 'STRING',
    },
    {
      label: '布尔',
      value: 5,
      key: 'BOOLEAN',
    },
    {
      label: '时间',
      value: 6,
      key: 'TIME',
    },
  ],
  tenantType: [
    {
      label: '个人用户',
      value: 1,
      key: 'PERSONAL',
    },
    {
      label: '企业用户',
      value: 2,
      key: 'ENTERPRISE',
    },
  ],
  topUpStatus: [
    {
      label: '充值失败',
      value: 0,
      key: 'FAILURE',
    },
    {
      label: '充值等待',
      value: 1,
      key: 'WAITING',
    },
    {
      label: '充值完成',
      value: 2,
      key: 'COMPLETE',
    },
  ],
  topUpType: [
    {
      label: '支付宝充值',
      value: 1,
      key: 'ALI_PAY',
    },
    {
      label: '微信充值',
      value: 2,
      key: 'WEICHAT_PAY',
    },
  ],
  upLinkSystem: [
    {
      label: '云',
      value: 1,
      key: 'CLOUD',
    },
    {
      label: '网关',
      value: 2,
      key: 'GATEWAY',
    },
  ],
  webhookType: [
    {
      label: '私有',
      value: 1,
      key: 'PRIVATE',
    },
    {
      label: 'APICloud',
      value: 2,
      key: 'APICLOUD',
    },
    {
      label: 'LeanCloud',
      value: 3,
      key: 'LEANCLOUD',
    },
  ],
}

const variable = {}

Object.keys(dict).forEach((key) => {
  variable[key] = {}
  dict[key].forEach((item) => {
    variable[key][item.key] = item.value
  })
})

export default variable
