export const MQTTClient = {
  client: {},
  options: {
    host: '127.0.0.1',
    port: '8083',
    username: '',
    password: '',
    keepalive: 60,
    clean: true,
    clientId: `mqttjs_${Math.random().toString(16).substr(2, 10)}`,
    subTopic: '/World',
    subQos: 0,
    publishTopic: '/World',
    publishQos: 0,
    publishMessage: 'Hello world!',
    publishRetain: false,
    receivedMessages: [],
    publishedMessages: [],
    subscriptions: [],
    connectPartCtl: false,
    activeStatus: 'addtopic',
  },
}

export const virtualDevice = {
  options: {
    connect: {},
    published: false,
    subscribe: {},
    publish: {},
    receivedMessages: [],
    publishedMessages: [],
    subscriptions: [],
    options: [],
    selectedDeviceID: undefined,
    timer: 0,
    broker: {},
  },
  client: {},
}

export const socketClient = {
  client: {},
}
