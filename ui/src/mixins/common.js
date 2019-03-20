import io from 'socket.io-client'
import { socketClient } from '../utils/MQTTConnect'

export const deviceMixin = {
  methods: {
    handleDeviceLogin(record) {
      const { deviceConsoleIP, deviceConsoleUsername, deviceConsolePort, id } = record
      if (!deviceConsoleIP || !deviceConsoleUsername) {
        let info = ''
        if (!deviceConsoleIP && !deviceConsoleUsername) {
          info += '控制台 IP 地址与控制台用户名'
        } else if (!deviceConsoleUsername) {
          info += '控制台用户名'
        } else if (!deviceConsoleIP) {
          info += '控制台 IP 地址'
        }
        this.$confirm(`该设备暂无${info}信息`, '提示', {
          confirmButtonText: '前去完善',
          cancelButtonText: '取消',
          cancelButtonClass: 'cancel-button',
          type: 'warning',
        }).then(() => {
          this.$router.push(`/devices/devices/${id}?oper=edit`)
        }).catch(() => {})
      } else {
        window.open(`${window.location.origin}/terminal?host=${deviceConsoleIP}&username=${deviceConsoleUsername}&port=${deviceConsolePort}`)
      }
    },
  },
}

// TODO Keep the connection, Binding events are handled when destroy pages
export const socketClientMixin = {
  data() {
    return {
      client: {},
      socketTimer: 0,
      options: {
        query: {
          token: this.$store.state.accounts.user.token,
          deviceID: '',
        },
        path: '/realtime',
        timeout: 5000,
        reconnectionAttempts: 1,
      },
    }
  },
  methods: {
    socketConnect(url, options = {}) {
      // if (socketClient.client.connected) {
      //   this.client = socketClient.client
      //   this.handleSocketEvent()
      //   this.socketPing()
      // } else {
      //   this.client = io.connect(url, options)
      //   this.client.on('connect', () => {
      //     this.handleSocketEvent()
      //     this.socketPing()
      //   })
      // }
      this.client = io(url, options)
      this.client.on('connect', () => {
        this.socketPing()
      })
      this.handleSocketEvent()
    },
    // heartbeat packet
    socketPing() {
      clearInterval(this.socketTimer)
      this.socketTimer = setInterval(() => {
        if (!this.client.connected) {
          return
        }
        this.client.emit('ping')
      }, 30 * 1000)
    },
    // Initiate and register event operation after new connection
    handleSocketEvent() {},
    socketDisconnect() {
      clearInterval(this.socketTimer)
      socketClient.client = this.client
      if (this.client.disconnect) {
        this.client.disconnect()
      }
    },
  },
  beforeRouteLeave(to, from, next) {
    this.socketDisconnect()
    next()
  },
}

export default {}
