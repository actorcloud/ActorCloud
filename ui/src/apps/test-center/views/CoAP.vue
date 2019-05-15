<template>
  <div class="coap-view">
    <div class="emq-crud">
      <div class="crud-header">
        <el-row type="flex" justify="space-between" align="middle">
          <el-col :span="18">
            <span class="crud-title">{{ $t('testCenter.CoAPClient') }}</span>
          </el-col>
        </el-row>
      </div>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-select
            v-model="selectedDevice"
            filterable
            remote
            clearable
            reserve-keyword
            style="width: 100%;"
            size="mini"
            :placeholder="$t('testCenter.searchDevice')"
            :loading="selectLoading"
            :remote-method="search"
            @focus="search('', reload = true)">
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-col>
      </el-row>

      <el-row style="margin-top: 20px;" :gutter="20">
        <el-col :span="12">
          <el-card>
            <el-tabs v-model="activeTabLeft">
              <el-tab-pane name="reportMessage" :label="$t('testCenter.reportData')">
                <el-form
                  class="publish-form"
                  label-position="top"
                  label-width="80px"
                  :model="publish">
                  <el-form-item :label="$t('events.topic')">
                    <el-input v-model="publish.topic"></el-input>
                  </el-form-item>
                  <el-form-item class="code-json" :label="$t('testCenter.message')">
                    <code-editor
                      class="code-json__editor code-editor__reset"
                      height="190px"
                      v-model="publish.payload"
                      lang="application/json"
                      :disabled="false">
                    </code-editor>
                  </el-form-item>
                  <el-button class="publish-btn" type="success" @click="publishMsg">{{ $t('testCenter.reportData') }}</el-button>
                </el-form>
              </el-tab-pane>
              <el-tab-pane name="subscribeTopic" :label="$t('testCenter.subscribeTopic')">
                <el-input
                  style="margin-top: 20px;"
                  v-model="subscribe.topic"
                  :placeholder="$t('testCenter.topicPlaceholder')">
                  <el-button slot="append" icon="el-icon-zoom-in" @click="subscribeTopic">{{ $t('testCenter.subscribe') }}
                  </el-button>
                </el-input>
                <el-table style="margin-top: 20px;" :data="subscribedData">
                  <el-table-column prop="topic" :label="$t('events.topic')">
                  </el-table-column>
                  <el-table-column prop="qos" label="Qos">
                  </el-table-column>
                </el-table>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <el-tabs v-model="activeTab">
              <el-tab-pane class="msg-card" name="sendedDataTab">
                <span slot="label">
                  <el-badge :is-dot="sendedDataDot">{{ $t('testCenter.reportedData') }}</el-badge>
                </span>
                <div v-if="sendedData.length === 0" class="noData">{{ $t('oper.noData') }}</div>
                <template v-if="sendedData.length > 0">
                  <el-card
                    v-for="(item, index) in sendedData"
                    class="message-card" :key="index">
                    <el-col class="item-url"><a>{{ item.url }}</a></el-col>
                    <el-col class="item-msg">{{ item.payload }}</el-col>
                    <el-col class="item-date-time">{{ item.dateTime }}</el-col>
                  </el-card>
                </template>
              </el-tab-pane>
              <el-tab-pane class="msg-card" name="receivedDataTab">
                <span slot="label">
                  <el-badge :is-dot="receivedDataDot">{{ $t('testCenter.receivedData') }}</el-badge>
                </span>
                <div v-if="receivedData.length === 0" class="noData">{{ $t('oper.noData') }}</div>
                <template v-if="receivedData.length > 0">
                  <el-card
                    v-for="(item, index) in receivedData"
                    class="message-card" :key="index">
                    <el-col class="item-url"><a>{{ item.url }}</a></el-col>
                    <el-col class="item-msg">{{ item.payload }}</el-col>
                    <el-col class="item-date-time">{{ item.dateTime }}</el-col>
                  </el-card>
                </template>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import { mapActions } from 'vuex'
import mqtt from 'mqtt'
import dateformat from 'dateformat'
import CodeEditor from '@/components/CodeEditor'

export default {
  name: 'coap-view',

  components: {
    CodeEditor,
  },

  data() {
    return {
      activeTabLeft: 'reportMessage',
      activeTabRight: 'publishedMessagesTab',
      options: [],
      selectedDevice: [],
      selectLoading: false,
      brokerInfo: {},
      connectOptions: {
        url: '',
        username: '',
        password: '',
        clientId: '',
        keepalive: 60,
        clean: true,
        connectTimeout: 3000,
        coapBroker: '',
      },
      client: {},
      reconnectedTime: 0,
      publish: {
        topic: '/temperature',
        qos: 1,
        payload: JSON.stringify({
          data_type: 'event',
          stream_id: 'temperature',
          data: {
            temperature: { time: 1547661822, value: 100 },
          },
        }, null, 2),
        retain: false,
      },
      subscribe: {
        topic: '/temperature',
        qos: 1,
      },
      subscribedData: [],
      activeTab: 'sendedDataTab',
      sendedDataDot: false,
      receivedDataDot: false,
      sendedData: [],
      receivedData: [],
    }
  },

  watch: {
    selectedDevice: 'connect',
    activeTab() {
      if (this.activeTab === 'sendedDataTab') {
        this.sendedDataDot = false
      } else if (this.activeTab === 'receivedDataTab') {
        this.receivedDataDot = false
      }
    },
  },

  methods: {
    ...mapActions(['LOADING_START', 'LOADING_END']),
    datetimeNow() {
      return dateformat(new Date(), 'yyyy-mm-dd HH:MM:ss')
    },

    // Remote search device
    search(query, reload = false) {
      const params = {}
      // Click to load the device when no device is selected
      if (reload && this.selectedDeviceID) {
        return
      }
      if (!reload && !query) {
        return
      }
      this.selectLoading = true
      // Search delay
      clearTimeout(this.timer)
      this.timer = setTimeout(() => {
        this.options = []
        params.deviceName_like = query
        httpGet('/emq_select/test_center/devices?cloudProtocol=CoAP', { params }).then((response) => {
          response.data.forEach((record) => {
            const option = {
              label: record.label,
              value: record.value,
            }
            const existOption = this.options.filter((row) => {
              return row.value === option.value
            })
            if (existOption.length === 0) {
              this.options.push(option)
            }
          })
          this.selectLoading = false
        })
      }, 200)
    },

    connect() {
      this.disconnect()
      this.sendedData = []
      this.receivedData = []
      if (this.selectedDevice) {
        const isSSL = window.location.protocol === 'https:'
        const protocol = isSSL ? 'wss:' : 'ws:'
        this.connectOptions.url = isSSL ? this.brokerInfo.wssBroker : this.brokerInfo.wsBroker
        this.connectOptions.coapBroker = this.brokerInfo.coapBroker
        httpGet(`/devices/${this.selectedDevice}`).then((res) => {
          this.connectOptions.clientId = res.data.deviceID
          this.connectOptions.username = res.data.deviceUsername
          this.connectOptions.password = res.data.token
          // Start connecting
          this.client = mqtt.connect(`${protocol}//${this.connectOptions.url}/mqtt`, this.connectOptions)
          // Reconnect more than 3 times, close the connection
          this.client.on('reconnect', () => {
            if (this.reconnectedTime >= 2) {
              this.reconnectedTime = 0
              this.client.end()
              this.client = {}
              this.$message.error(this.$t('testCenter.connectFail'))
              return
            }
            this.reconnectedTime += 1
          })
          // Connection error, close connection
          this.client.on('error', () => {
            this.$message.error(this.$t('testCenter.connectError'))
            this.reconnectedTime = 0
            this.client.end()
          })
          // Receive subscribed topic messages
          this.client.on('message', (topic, payload) => {
            this.receivedData.unshift({
              url: `coap://${this.connectOptions.coapBroker}/mqtt/${topic.replace(/\//, '')}
              ?c=${this.connectOptions.clientId}
              &u=${this.connectOptions.username}
              &p=${this.connectOptions.password}`.replace(/\s+/g, ''),
              payload: payload.toString(),
              dateTime: this.datetimeNow(),
            })
            if (this.activeTab !== 'receivedDataTab') {
              this.receivedDataDot = true
            }
          })
        })
      }
    },

    disconnect() {
      if (this.client.connected) {
        this.client.end()
        this.client.on('close', () => {
          this.client.connected = false
        })
      }
    },

    publishMsg() {
      if (this.client.connected) {
        const options = {
          qos: this.publish.qos,
          retain: this.publish.retain,
        }
        this.client.publish(this.publish.topic, this.publish.payload, options, (error) => {
          if (error) {
            this.$message.error(error)
          } else {
            this.sendedData.unshift({
              url: `coap://${this.connectOptions.coapBroker}/mqtt/${this.publish.topic.replace(/\//, '')}
              ?c=${this.connectOptions.clientId}
              &u=${this.connectOptions.username}
              &p=${this.connectOptions.password}`.replace(/\s+/g, ''),
              payload: this.publish.payload,
              dateTime: this.datetimeNow(),
            })
            this.$message({
              message: this.$t('testCenter.reportSuccess'),
              type: 'success',
            })
            if (this.activeTab !== 'sendedDataTab') {
              this.sendedDataDot = true
            }
          }
        })
      } else if (this.selectedDevice) {
        this.$message.error(this.$t('testCenter.reportFail'))
      } else {
        this.$message({
          message: this.$t('testCenter.selectDevice'),
          type: 'warning',
        })
      }
    },

    subscribeTopic() {
      if (this.client.connected) {
        if (this.subscribedData.length >= 10) {
          this.$message({
            message: this.$t('testCenter.topicLimit'),
            type: 'error',
          })
          return
        }
        this.client.subscribe(this.subscribe.topic, {
          qos: this.subscribe.qos,
        }, (error) => {
          if (error) {
            this.$message.error(`${this.$t('testCenter.subscribeError')}: ${error.toString()}`)
          } else {
            this.subscribedData.unshift({
              topic: this.subscribe.topic,
              qos: this.subscribe.qos,
            })
            this.$message({
              message: this.$t('testCenter.subscribeSuccess'),
              type: 'success',
            })
          }
        })
      } else if (this.selectedDevice) {
        this.$message.error(this.$t('testCenter.subscribeFail'))
      } else {
        this.$message({
          message: this.$t('testCenter.selectDevice'),
          type: 'warning',
        })
      }
    },
  },

  created() {
    this.LOADING_START()
    httpGet('/broker_info').then((res) => {
      this.brokerInfo = res.data
    })
  },

  mounted() {
    setTimeout(() => { this.LOADING_END() }, 500)
  },

  beforeRouteLeave(to, from, next) {
    this.disconnect()
    next()
  },
}
</script>


<style lang="scss">
.coap-view {
  .el-input--suffix .el-input__inner {
    padding-right: 15px;
    border-radius: 30px;
    background: transparent;
    height: 34px;
    border-color: var(--color-line-bg);
  }
  @media screen and (min-width: 1366px) {
    .el-input--suffix .el-input__inner {
      height: 38px;
    }
  }
  .el-card {
    border-radius: 6px;
  }
  .message-card {
    margin-top: 20px;
    overflow-x: scroll;
    box-shadow: 3px 3px 1px var(--color-shadow);
    .el-col-24 {
      padding-bottom: 20px;
    }
    .item-url {
      white-space: nowrap;
    }
    .item-msg {
      font-size: 18px;
    }
    .item-date-time {
      color: var(--color-text-light);
    }
  }
  .noData {
    display: flex;
    height: 400px;
    justify-content: center;
    align-items: center;
    color: var(--color-text-light);
  }
  .el-table__header {
    padding-top: 0;
  }
  .el-tabs__nav {
    .el-tabs__nav-wrap::after {
      background-color: var(--color-line-bg);
    }
    .el-tabs__item {
      color: var(--color-text-default);
      font-weight: normal;
    }
    .el-tabs__item.is-active {
      color: var(--color-main-green);
    }
  }
  .el-tabs__content {
    height: 420px;
    overflow: scroll;
    .publish-form {
      .el-form-item__label {
        padding: 0;
        color: var(--color-text-light);
      }
      .code-json {
        .el-form-item__content {
          line-height: 18px;
          .code-json__editor {
            border: 1px solid var(--color-line-card);
            border-radius: 6px;
            .CodeMirror {
              border-radius: 6px;
            }
          }
        }
      }
    }
  }
  .publish-btn.el-button--success {
    padding: 10px 24px;
    color: var(--color-main-green);
    border-radius: 30px;
    background-color: var(--color-bg-card);
    border-color: var(--color-line-card);
    box-shadow: 0 2px 12px 0 var(--color-shadow);
    margin-left: 4px;

    &:hover {
      box-shadow: 0 2px 12px 2px var(--color-shadow);
    }
  }
  .el-badge__content.is-fixed.is-dot {
    top: 5px;
  }
}
</style>
