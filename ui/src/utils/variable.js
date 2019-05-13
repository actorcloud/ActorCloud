const dict = {
  access: [
    {
      label: 'Publish',
      value: 1,
      key: 'PUBLISH',
    },
    {
      label: 'Subscribe',
      value: 2,
      key: 'SUBSCRIBE',
    },
    {
      label: 'Publish or subscribe',
      value: 3,
      key: 'PUBLISH_OR_SUBSCRIBE',
    },
  ],
  actionType: [
    {
      label: 'Alert',
      value: 1,
      key: 'ALERT',
    },
    {
      label: 'Email',
      value: 2,
      key: 'EMAIL',
    },
    {
      label: 'Webhook',
      value: 3,
      key: 'WEBHOOK',
    },
    {
      label: 'Command',
      value: 4,
      key: 'COMMAND',
    },
    {
      label: 'Mqtt',
      value: 5,
      key: 'MQTT',
    },
  ],
  aggregateType: [
    {
      label: 'Maximun',
      value: 1,
      key: 'MAXIMUM',
    },
    {
      label: 'Minimun',
      value: 2,
      key: 'MINIMUM',
    },
    {
      label: 'Average',
      value: 3,
      key: 'AVERAGE',
    },
    {
      label: 'Cumulative',
      value: 4,
      key: 'CUMULATIVE',
    },
  ],
  alertSeverity: [
    {
      label: 'Urgent',
      value: 1,
      key: 'URGENT',
    },
    {
      label: 'Main',
      value: 2,
      key: 'MAIN',
    },
    {
      label: 'Secondary',
      value: 3,
      key: 'SECONDARY',
    },
    {
      label: 'Warning',
      value: 4,
      key: 'WARNING',
    },
  ],
  allow: [
    {
      label: 'Deny',
      value: 0,
      key: 'DENY',
    },
    {
      label: 'Allowed',
      value: 1,
      key: 'ALLOWED',
    },
  ],
  appStatus: [
    {
      label: 'Disabled',
      value: 0,
      key: 'DISABLED',
    },
    {
      label: 'Available',
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
      label: 'Certificate',
      value: 2,
      key: 'CERTIFICATE',
    },
  ],
  autoCreateCert: [
    {
      label: 'False',
      value: 0,
      key: 'FALSE',
    },
    {
      label: 'True',
      value: 1,
      key: 'TRUE',
    },
  ],
  cardChartType: [
    {
      label: 'Line',
      value: 1,
      key: 'LINE',
    },
    {
      label: 'Histogram',
      value: 2,
      key: 'HISTOGRAM',
    },
    {
      label: 'Pie',
      value: 3,
      key: 'PIE',
    },
    {
      label: 'Instrument',
      value: 4,
      key: 'INSTRUMENT',
    },
    {
      label: 'Numerical',
      value: 5,
      key: 'NUMERICAL',
    },
    {
      label: 'Map',
      value: 6,
      key: 'MAP',
    },
  ],
  cardDataSource: [
    {
      label: 'Device',
      value: 1,
      key: 'DEVICE',
    },
    {
      label: 'Product',
      value: 2,
      key: 'PRODUCT',
    },
    {
      label: 'Group',
      value: 3,
      key: 'GROUP',
    },
    {
      label: 'Paltform',
      value: 4,
      key: 'PLATFORM',
    },
  ],
  cardDeviceStatistic: [
    {
      label: 'Indicators',
      value: 101,
      key: 'INDICATORS',
    },
    {
      label: 'DataPoint',
      value: 102,
      key: 'FUNCTION_POINT',
    },
  ],
  cardGroupStatistic: [
    {
      label: 'Number of devices',
      value: 301,
      key: 'NUMBER_OF_DEVICES',
    },
    {
      label: 'Number of online devices',
      value: 302,
      key: 'NUMBER_OF_ONLINE_DEVICES',
    },
    {
      label: 'Number if offline devices',
      value: 303,
      key: 'NUMBER_OF_OFFLINE_DEVICES',
    },
    {
      label: 'Number of device alert',
      value: 304,
      key: 'NUMBER_OF_DEVICE_ALARMS',
    },
    {
      label: 'Number of online offline',
      value: 305,
      key: 'NUMBER_OF_ONLINE_OFFLINE',
    },
  ],
  cardPlatformStatistic: [
    {
      label: 'Number of devices',
      value: 401,
      key: 'NUMBER_OF_DEVICES',
    },
    {
      label: 'Number of online devices',
      value: 402,
      key: 'NUMBER_OF_ONLINE_DEVICES',
    },
    {
      label: 'Number of offline devices',
      value: 403,
      key: 'NUMBER_OF_OFFLINE_DEVICES',
    },
    {
      label: 'Number of device alert',
      value: 404,
      key: 'NUMBER_OF_DEVICE_ALARMS',
    },
    {
      label: 'Number of online offline',
      value: 405,
      key: 'NUMBER_OF_ONLINE_OFFLINE',
    },
    {
      label: 'Number of product',
      value: 406,
      key: 'NUMBER_OF_PRODUCT',
    },
    {
      label: 'Number of group',
      value: 407,
      key: 'GROUP_NUMBER',
    },
    {
      label: 'API calls',
      value: 408,
      key: 'API_CALLS',
    },
    {
      label: 'Message number',
      value: 409,
      key: 'MESSAGE_NUMBER',
    },
    {
      label: 'Traffic',
      value: 410,
      key: 'TRAFFIC',
    },
  ],
  cardProductStatistic: [
    {
      label: 'Number of devices',
      value: 201,
      key: 'NUMBER_OF_DEVICES',
    },
    {
      label: 'Number of online devices',
      value: 202,
      key: 'NUMBER_OF_ONLINE_DEVICES',
    },
    {
      label: 'Number of offline devices',
      value: 203,
      key: 'NUMBER_OF_OFFLINE_DEVICES',
    },
    {
      label: 'Number of device alerts',
      value: 204,
      key: 'NUMBER_OF_DEVICE_ALARMS',
    },
    {
      label: 'Number of online offline',
      value: 205,
      key: 'NUMBER_OF_ONLINE_OFFLINE',
    },
  ],
  carrier: [
    {
      label: 'CTCC',
      value: 1,
      key: 'CTCC',
    },
    {
      label: 'CMCC',
      value: 2,
      key: 'CMCC',
    },
    {
      label: 'CUCC',
      value: 3,
      key: 'CUCC',
    },
    {
      label: 'Other',
      value: 4,
      key: 'OTHER',
    },
  ],
  certEnable: [
    {
      label: 'Disabeld',
      value: 0,
      key: 'DISABLE',
    },
    {
      label: 'Enable',
      value: 1,
      key: 'ENABLE',
    },
  ],
  chargeType: [
    {
      label: 'Free',
      value: 1,
      key: 'FREE',
    },
    {
      label: 'Duration',
      value: 2,
      key: 'DURATION',
    },
    {
      label: 'Times',
      value: 3,
      key: 'TIMES',
    },
    {
      label: 'Numbers',
      value: 4,
      key: 'NUMBERS',
    },
  ],
  chartType: [
    {
      label: 'Line',
      value: 1,
      key: 'LINE',
    },
    {
      label: 'Histogram',
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
      label: 'offline',
      value: 0,
      key: 'OFFLINE',
    },
    {
      label: 'online',
      value: 1,
      key: 'ONLINE',
    },
    {
      label: 'Authentication failure',
      value: 2,
      key: 'AUTHENTICATION_FAILED',
    },
  ],
  dataTransType: [
    {
      label: 'Up',
      value: 1,
      key: 'UP',
    },
    {
      label: 'Down',
      value: 2,
      key: 'DOWN',
    },
    {
      label: 'Up down',
      value: 3,
      key: 'UP_DOWN',
    },
  ],
  deviceBlocked: [
    {
      label: 'Allowed',
      value: 0,
      key: 'ALLOWED',
    },
    {
      label: 'No allowed',
      value: 1,
      key: 'NO_ALLOWED',
    },
  ],
  deviceStatus: [
    {
      label: 'Offline',
      value: 0,
      key: 'OFFLINE',
    },
    {
      label: 'Online',
      value: 1,
      key: 'ONLINE',
    },
    {
      label: 'Dormancy',
      value: 2,
      key: 'DORMANCY',
    },
  ],
  enable: [
    {
      label: 'Enable',
      value: 0,
      key: 'ENABLE',
    },
    {
      label: 'Disabe',
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
      label: 'Top up',
      value: 1,
      key: 'TOP_UP',
    },
    {
      label: 'Consumption',
      value: 2,
      key: 'CONSUMPTION',
    },
  ],
  inviteStatus: [
    {
      label: 'Not join',
      value: 0,
      key: 'NOT_JOIN',
    },
    {
      label: 'Joined',
      value: 1,
      key: 'JOINED',
    },
  ],
  invoiceStatus: [
    {
      label: 'In review',
      value: 0,
      key: 'IN_REVIEW',
    },
    {
      label: 'Cancelled',
      value: 1,
      key: 'CANCELLED',
    },
    {
      label: 'Mailed',
      value: 2,
      key: 'MAILED',
    },
    {
      label: 'Not careful',
      value: 3,
      key: 'NOT_CAREFUL',
    },
  ],
  invoiceType: [
    {
      label: 'Personal vat invoice',
      value: 1,
      key: 'PERSONAL_VAT_INVOICE',
    },
    {
      label: 'Enterprise vat invoice',
      value: 2,
      key: 'ENTERPRISE_VAT_INVOICE',
    },
  ],
  isLogged: [
    {
      label: 'Failure',
      value: 0,
      key: 'FAILURE',
    },
    {
      label: 'Successful',
      value: 1,
      key: 'SUCCESSFUL',
    },
  ],
  locationType: [
    {
      label: 'Longitude',
      value: 1,
      key: 'LONGITUDE',
    },
    {
      label: 'Latitude',
      value: 2,
      key: 'LATITUDE',
    },
    {
      label: 'Altitude',
      value: 3,
      key: 'ALTITUDE',
    },
  ],
  messageType: [
    {
      label: 'Financial messages',
      value: 1,
      key: 'FINANCIAL_MESSAGES',
    },
    {
      label: 'Product messages',
      value: 2,
      key: 'PRODUCT_MESSAGES',
    },
    {
      label: 'Safety messages',
      value: 3,
      key: 'SAFETY_MESSAGES',
    },
    {
      label: 'Other messages',
      value: 4,
      key: 'OTHER_MESSAGES',
    },
    {
      label: 'Announcement',
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
      label: 'Numerical',
      value: 1,
      key: 'NUMERICAL',
    },
    {
      label: 'String',
      value: 3,
      key: 'STRING',
    },
    {
      label: 'Fault',
      value: 4,
      key: 'FAULT',
    },
    {
      label: 'Boolean',
      value: 5,
      key: 'BOOLEAN',
    },
    {
      label: 'Fiexd string',
      value: 11,
      key: 'FIXED_STRING',
    },
    {
      label: 'Strings',
      value: 12,
      key: 'STRINGS',
    },
    {
      label: 'Fixed binary',
      value: 13,
      key: 'FIXED_BINARY',
    },
    {
      label: 'binarys',
      value: 14,
      key: 'BINARYS',
    },
    {
      label: 'Signed integer',
      value: 15,
      key: 'SIGNED_INTEGER',
    },
    {
      label: 'Unsigned integer',
      value: 16,
      key: 'UNSIGNED_INTEGER',
    },
    {
      label: 'Single floating',
      value: 17,
      key: 'SINGLE_FLOATING',
    },
    {
      label: 'Double floating',
      value: 18,
      key: 'DOUBLE_FLOATING',
    },
    {
      label: 'Bit type',
      value: 19,
      key: 'BIT_TYPE',
    },
  ],
  productType: [
    {
      label: 'Device',
      value: 1,
      key: 'DEVICE',
    },
    {
      label: 'Gateway',
      value: 2,
      key: 'GATEWAY',
    },
  ],
  productResource: [
    {
      label: 'Hardware version',
      value: 'hardwareVersion',
      key: 'HARDWARE_VERSION',
    },
    {
      label: 'Manufacturer',
      value: 'manufacturer',
      key: 'MANUFACTURERS',
    },
    {
      label: 'Serial number',
      value: 'serialNumber',
      key: 'SERIAL_NUMBER',
    },
    {
      label: 'Soft version',
      value: 'softVersion',
      key: 'SOFTWARE_VERSION',
    },
  ],
  publishStatus: [
    {
      label: 'Failure',
      value: 0,
      key: 'FAILURE',
    },
    {
      label: 'Success',
      value: 1,
      key: 'SUCCESS',
    },
    {
      label: 'Reached',
      value: 2,
      key: 'REACHED',
    },
    {
      label: 'Timing',
      value: 3,
      key: 'TIMING',
    },
  ],
  publishType: [
    {
      label: 'Device',
      value: 0,
      key: 'DEVICE',
    },
    {
      label: 'Group',
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
      label: 'Not repeat',
      value: 0,
      key: 'NOT_REPEAT',
    },
    {
      label: 'Repeat',
      value: 1,
      key: 'REPEAT',
    },
    {
      label: 'Completed',
      value: 2,
      key: 'COMPLETED',
    },
  ],
  scopeType: [
    {
      label: 'Active area',
      value: 1,
      key: 'ACTIVE_AREA',
    },
    {
      label: 'Forbidden area',
      value: 2,
      key: 'FORBIDDEN_AREA',
    },
  ],
  sdkType: [
    {
      label: 'Application',
      value: 1,
      key: 'APPLICATION',
    },
    {
      label: 'Firmware',
      value: 2,
      key: 'FIRMWARE',
    },
    {
      label: 'Kernel',
      value: 3,
      key: 'KERNEL',
    },
  ],
  serviceGroup: [
    {
      label: 'Basic services',
      value: 1,
      key: 'BASIC_SERVICES',
    },
    {
      label: 'Device manage platform',
      value: 2,
      key: 'DMP',
    },
    {
      label: 'Application enablement platform',
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
      label: 'Binary',
      value: 2,
      key: 'BINARY',
    },
  ],
  streamType: [
    {
      label: 'Up',
      value: 1,
      key: 'UP',
    },
    {
      label: 'Down',
      value: 2,
      key: 'DOWN',
    },
  ],
  templateType: [
    {
      label: 'Switch',
      value: 1,
      key: 'SWITCH',
    },
    {
      label: 'Enumeration',
      value: 2,
      key: 'ENUMERATION',
    },
    {
      label: 'Numerical',
      value: 3,
      key: 'NUMERICAL',
    },
    {
      label: 'String',
      value: 4,
      key: 'STRING',
    },
    {
      label: 'Boolean',
      value: 5,
      key: 'BOOLEAN',
    },
    {
      label: 'Time',
      value: 6,
      key: 'TIME',
    },
  ],
  tenantType: [
    {
      label: 'Personal',
      value: 1,
      key: 'PERSONAL',
    },
    {
      label: 'Enterprise',
      value: 2,
      key: 'ENTERPRISE',
    },
  ],
  topUpStatus: [
    {
      label: 'Failure',
      value: 0,
      key: 'FAILURE',
    },
    {
      label: 'Waiting',
      value: 1,
      key: 'WAITING',
    },
    {
      label: 'Complete',
      value: 2,
      key: 'COMPLETE',
    },
  ],
  topUpType: [
    {
      label: 'Ali pay',
      value: 1,
      key: 'ALI_PAY',
    },
    {
      label: 'WeChat pay',
      value: 2,
      key: 'WEICHAT_PAY',
    },
  ],
  upLinkSystem: [
    {
      label: 'Cloud',
      value: 1,
      key: 'CLOUD',
    },
    {
      label: 'Device',
      value: 2,
      key: 'DEVICE',
    },
    {
      label: 'Gateway',
      value: 3,
      key: 'GATEWAY',
    },
  ],
  webhookType: [
    {
      label: 'Private',
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
