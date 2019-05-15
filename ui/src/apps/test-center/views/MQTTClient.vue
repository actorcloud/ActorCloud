<template>
  <div class="mqtt-client-view">
    <div class="emq-crud">
      <div class="crud-header">
        <el-row type="flex" justify="space-between" align="middle">
          <el-col :span="18">
            <span class="crud-title">{{ $t('testCenter.MQTTClient') }}</span>
          </el-col>
        </el-row>
      </div>

      <div class="connectPart">
        <el-select
          v-model="selectedDeviceID"
          remote
          filterable
          clearable
          size="mini"
          :placeholder="$t('testCenter.searchDeviceGateway')"
          :remote-method="search"
          :disabled="client.connected"
          :loading="selectLoading"
          @focus="search('', reload = true)">
          <el-option
            v-for="option in options"
            :key="option.id"
            :label="option.label"
            :value="option.value">
          </el-option>
        </el-select>
        <emq-button
          v-if="!client.connected"
          float="left"
          :loading="loading"
          @click.native="mqttConnect">
          {{ loading ? $t('testCenter.connecting') : $t('testCenter.connect') }}
        </emq-button>
        <emq-button
          v-if="client.connected"
          class="danger"
          float="left"
          :loading="loading"
          @click.native="mqttDisconnect">
          {{ loading ? $t('testCenter.disconnecting') : $t('testCenter.disconnect') }}
        </emq-button>
        <div class="connectInfo">
          <el-row>
            <el-col :span="12">
              <p>{{ $t('testCenter.host') }}{{ connect.host }}</p>
              <p>{{ $t('testCenter.username') }}{{ connect.username }}</p>
            </el-col>
            <el-col :span="12">
              <p>{{ $t('testCenter.clientId') }}{{ connect.clientId }}</p>
              <p>{{ $t('testCenter.password') }}{{ connect.password }}</p>
            </el-col>
          </el-row>
        </div>
      </div>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <el-tabs v-model="activeTabLeft">
              <el-tab-pane name="reportMessage" :label="$t('testCenter.reportData')">
                <el-form
                  class="publish-form"
                  label-position="top"
                  label-width="80px">
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
                  <emq-button float="left" @click="mqttPublish">
                    {{ $t('testCenter.reportData') }}</emq-button>
                </el-form>
              </el-tab-pane>
              <el-tab-pane
                name="subscribeTopic"
                class="subTopic"
                :label="$t('testCenter.subscribeTopic')">
                <div style="margin-top: 20px;">
                  <el-input
                    v-model="subscribe.topic"
                    clearable
                    :placeholder="$t('testCenter.topicPlaceholder')">
                  </el-input>
                  <emq-button
                    class="sub-btn"
                    @click="mqttSubscribe">{{ $t('testCenter.subscribe') }}</emq-button>
                </div>
                <el-table border style="width: 100%" :data="subscriptions">
                  <el-table-column prop="topic" :label="$t('events.topic')"></el-table-column>
                  <el-table-column prop="qos" label="Qos" width="60">
                  </el-table-column>
                  <el-table-column class-name="oper" width="60">
                    <template v-slot="props">
                      <a
                        style="float: none"
                        href="javascript:;"
                        class="border-button"
                        :title="$t('oper.delete')"
                        @click="showConfirmDialog(props.$index)">
                        <i class="iconfont icon icon-emq-delete"></i>
                      </a>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>

        <el-col class="messageCard" :span="12">
          <el-card>
            <el-tabs v-model="activeTabRight">
              <el-tab-pane name="publishedMessagesTab">
                <span slot="label">
                  <el-badge class="item" :is-dot="publishedMessagesChange">
                    {{ $t('testCenter.reportedData') }}</el-badge>
                </span>
                <div v-if="publishedMessages.length === 0" class="noData">{{ $t('oper.noData') }}</div>
                <el-card v-for="(messages, index) in publishedMessages" :key="index">
                  <p style="overflow:hidden; font-size:14px;">
                    <span style="color:var(--color-main-green);">[{{ messages.topic }}]</span>&nbsp;
                    <span style="color:var(--color-text-light);">{{ $t('testCenter.qos') }} : {{ messages.qos }}</span>
                    <span style="float:right; color:var(--color-text-light);">{{ messages.time }}</span>
                  </p>
                  <p style="font-size:18px; color:var(--color-text-lighter);">{{ messages.payload }}</p>
                </el-card>
              </el-tab-pane>
              <el-tab-pane name="receivedMessagesTab">
                <span slot="label">
                  <el-badge class="item" :is-dot="receivedMessagesChange">
                    {{ $t('testCenter.receivedData') }}</el-badge>
                </span>
                <div v-if="receivedMessages.length === 0" class="noData">{{ $t('oper.noData') }}</div>
                <el-card v-for="(messages, index) in receivedMessages" :key="index">
                  <p style="overflow:hidden; font-size:14px;">
                    <span style="color:var(--color-main-green);">[{{ messages.topic }}]</span>&nbsp;
                    <span style="color:var(--color-text-light);">{{ $t('testCenter.qos') }} : {{ messages.qos }}</span>
                    <span style="float:right;color:var(--color-text-light);">{{ messages.time }}</span>
                  </p>
                  <p style="font-size:18px;color:var(--color-text-lighter);">{{ messages.payload }}</p>
                </el-card>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <emq-dialog
      :title="$t('oper.warning')"
      :visible.sync="confirmDialogVisible"
      @confirm="deleteTopic">
      <span>{{ $t('testCenter.unsubscribe') }}</span>
    </emq-dialog>
  </div>
</template>


<script>
import mqtt from 'mqtt/lib/connect/index'
import dateformat from 'dateformat'
import { mapActions } from 'vuex'
import EmqDialog from '@/components/EmqDialog'
import EmqButton from '@/components/EmqButton'
import { httpGet } from '@/utils/api'
import { virtualDevice } from '@/utils/MQTTConnect'
import CodeEditor from '@/components/CodeEditor'

export default {
  name: 'mqtt-client-view',

  components: {
    CodeEditor,
    EmqButton,
    EmqDialog,
  },

  data() {
    return {
      activeTabLeft: 'reportMessage',
      activeTabRight: 'publishedMessagesTab',
      retryTimes: 0,
      loading: false,
      selectLoading: false,
      confirmDialogVisible: false,
      willDelectIds: '', // Optional device
      options: [], // Selected device
      selectedDeviceID: undefined,
      connect: {
        url: '',
        host: '',
        username: '',
        password: '',
        clientId: '',
        keepalive: 60,
        clean: true,
      },
      published: false,
      subscribe: {
        topic: '/temperature',
        qos: 1,
      },
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
      timer: 0,
      receivedMessages: [],
      publishedMessages: [],
      subscriptions: [],
      client: {},
      publishedMessagesChange: false, // True when a new message is published
      receivedMessagesChange: false, // True when a new message is received
      broker: {},
    }
  },

  watch: {
    selectedDeviceID: 'deployInfo',
    activeTabRight() {
      if (this.activeTabRight === 'publishedMessagesTab') {
        this.publishedMessagesChange = false
      } else if (this.activeTabRight === 'receivedMessagesTab') {
        this.receivedMessagesChange = false
      }
    },
  },

  methods: {
    ...mapActions(['LOADING_START', 'LOADING_END']),
    now() {
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
        httpGet('/emq_select/test_center/devices', { params }).then((response) => {
          response.data.forEach((record) => {
            const option = {
              label: record.label,
              value: record.value,
              clientId: record.attr.deviceID,
              username: record.attr.deviceUsername,
              password: record.attr.token,
              isGateway: record.attr.isGateway,
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

    // Configure startup information
    deployInfo() {
      if (!this.selectedDeviceID) {
        this.connect.clientId = ''
        this.connect.username = ''
        this.connect.password = ''
        this.connect.url = ''
        this.connect.host = ''
        return
      }
      const isSSL = window.location.protocol === 'https:'
      this.options.forEach((option) => {
        if (option.value === this.selectedDeviceID) {
          this.connect.clientId = option.clientId
          this.connect.username = option.username
          this.connect.password = option.password
          this.connect.url = isSSL ? `wss://${this.broker.wssBroker}/mqtt` : `ws://${this.broker.wsBroker}/mqtt`
          this.connect.host = isSSL ? this.broker.wssBroker : this.broker.wsBroker
        }
      })
    },

    mqttConnect() {
      if (!this.selectedDeviceID
        || !this.connect.username
        || !this.connect.password
        || !this.connect.clientId) {
        this.$message.error(this.$t('testCenter.selectDevice'))
        return
      }
      this.loading = true
      this.retryTimes = 0
      this.published = false
      const options = {
        keepalive: this.connect.keepalive,
        username: this.connect.username,
        password: this.connect.password,
        clientId: this.connect.clientId,
        clean: this.connect.clean,
        connectTimeout: 4000,
      }
      this.client = mqtt.connect(this.connect.url, options)
      this.client.on('connect', () => {
        if (this.published) {
          return
        }
        this.$message.success(this.$t('testCenter.connectSuccess'))
        this.loading = false
      })
      this.client.on('reconnect', () => {
        if (this.published) {
          this.$message.error(this.$t('testCenter.illegalError'))
          this.client.end()
          this.client = {}
          return
        }
        if (this.retryTimes >= 2) {
          this.retryTimes = 0
          this.client.end()
          this.client = {}
          this.loading = false
          this.$message.error(this.$t('testCenter.connectFail'))
          return
        }
        this.retryTimes += 1
      })
      this.client.on('error', () => {
        this.$message.error(this.$t('testCenter.connectFail'))
        this.retryTimes = 0
        this.loading = false
        this.client.end()
      })
      this.client.on('message', (topic, payload, packet) => {
        this.receivedMessages.unshift({
          topic,
          payload: payload.toString(),
          qos: packet.qos,
          time: this.now(),
        })
        if (this.activeTabRight !== 'receivedMessagesTab') {
          this.receivedMessagesChange = true
        }
      })
    },

    mqttDisconnect() {
      this.loading = true
      if (this.client.connected) {
        this.client.end()
        this.client.on('close', () => {
          this.client.connected = false
          this.$message.success(this.$t('testCenter.disconnected'))
          this.loading = false
        })
        this.receivedMessages = []
        this.publishedMessages = []
        this.subscriptions = []
        this.publishedMessagesChange = false
        this.receivedMessagesChange = false
      } else {
        this.$message.error(this.$t('testCenter.operFail'))
        this.loading = false
      }
    },

    mqttSubscribe() {
      if (!this.client.connected) {
        this.$message.warning(this.$t('testCenter.connectFirst'))
        return
      }
      const subscribedTopic = this.subscriptions.filter((sub) => {
        return this.subscribe.topic === sub.topic
      })
      if (subscribedTopic.length > 0) {
        this.$message.error(this.$t('testCenter.subscribeRepeat'))
        return
      }
      if (this.subscriptions.length >= 10) {
        this.$message.error(this.$t('testCenter.topicLimit'))
        return
      }
      this.client.subscribe(this.subscribe.topic, {
        qos: this.subscribe.qos,
      }, (error) => {
        if (error) {
          this.$message.error(`${this.$t('testCenter.subscribeError')}: ${error.toString()}`)
        } else {
          let coverIndex = -1
          this.subscriptions.forEach((element, index) => {
            if (element.topic === this.subscribe.topic) {
              coverIndex = index
            }
          })
          if (coverIndex === -1) {
            this.subscriptions.unshift({
              topic: this.subscribe.topic,
              qos: this.subscribe.qos,
              time: this.now(),
              news: false,
            })
          } else {
            this.subscriptions[coverIndex].qos = this.subscribe.qos
            this.subscriptions[coverIndex].time = this.now()
          }
          this.$message.success(this.$t('testCenter.subscribeSuccess'))
        }
      })
    },

    showConfirmDialog(id) {
      this.willDelectIds = id
      this.confirmDialogVisible = true
    },

    deleteTopic() {
      this.client.unsubscribe(this.subscriptions[this.willDelectIds].topic, (err) => {
        if (err) {
          this.$message.error(this.$t('testCenter.unsubscribeFail'))
          this.confirmDialogVisible = false
          return
        }
        this.subscriptions.splice(this.willDelectIds, 1)
        this.$message.success(this.$t('testCenter.unsubscribeSuccess'))
        this.confirmDialogVisible = false
      })
    },

    mqttPublish() {
      if (!this.client.connected) {
        this.$message.warning(this.$t('testCenter.connectFirst'))
        return
      }
      this.published = true
      const options = {
        qos: this.publish.qos,
        retain: this.publish.retain,
      }
      this.client.publish(this.publish.topic, this.publish.payload, options, (error) => {
        if (error) {
          this.$message.error(error.toString())
        } else {
          this.publishedMessages.unshift({
            payload: this.publish.payload,
            topic: this.publish.topic,
            qos: this.publish.qos,
            time: this.now(),
          })
          this.$message.success(this.$t('testCenter.publishSuccess'))
          if (this.activeTabRight !== 'publishedMessagesTab') {
            this.publishedMessagesChange = true
          }
        }
      })
    },

    loadConnect() {
      // Already connected: load
      if (virtualDevice.client && virtualDevice.client.connected) {
        this.client = virtualDevice.client
        Object.keys(virtualDevice.options).forEach((item) => {
          this[item] = virtualDevice.options[item]
        })
      } else {
        httpGet('/broker_info').then((response) => {
          this.broker = response.data
        })
      }
    },

    stashConnect() {
      virtualDevice.client = this.client
      Object.keys(virtualDevice.options).forEach((item) => {
        virtualDevice.options[item] = this[item]
      })
    },
  },

  created() {
    this.LOADING_START()
    this.loadConnect()
  },

  mounted() {
    setTimeout(() => { this.LOADING_END() }, 500)
  },

  beforeRouteLeave(to, from, next) {
    if (this.client.connected) {
      this.stashConnect()
    }
    next()
  },
}
</script>


<style lang="scss">
.mqtt-client-view {
  .connectPart {
    overflow: hidden;
    margin-bottom: -20px;
    .el-input--suffix .el-input__inner {
      padding-right: 15px;
      border-radius: 30px;
      background: transparent;
      height: 34px;
      border-color: var(--color-line-bg);
    }
    .el-select {
      width: 30%;
      float: left;
    }
    .emq-button {
      line-height: 20px;
      margin-left: 20px;
      padding: 6px 24px;
      border-radius: 30px;
      background-color: var(--color-bg-card);
      border-color: var(--color-line-card);
      box-shadow: 0 2px 12px 0 var(--color-shadow);
      &.danger {
        color: var(--color-main-pink);
        &:hover, &:active {
          color: var(--color-main-pink);
        }
      }
    }
    .connectInfo {
      clear: both;
      margin-left: 42%;
      position: relative;
      bottom: 38px;
      color: var(--color-text-light);
      p {
        margin: 0 0 0 40px;
        white-space: nowrap;
      }
    }
  }
  .el-tabs {
    background-color: var(--color-bg-card);
    border-radius: 4px;
    .el-tabs__nav-wrap::after {
      background-color: var(--color-line-card);
    }
    .el-tabs__nav {
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
      overflow-y: scroll;
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
    .subTopic {
      .el-input {
        width: 75%;
      }
    }
    .el-table {
      margin-top: 20px;
      .oper a {
        display: inline-block;
        img {
          width: 25px;
          margin-bottom: -8px;
        }
      }
      .el-table__header {
        padding-top: 0;
      }
      th, th.is-leaf, .el-table td {
        border-right: 1px solid var(--color-line-card);
      }
    }
    .el-table--group::after, .el-table--border::after, .el-table::before {
      background-color: var(--color-line-card)
    }
    .el-table--border {
      border: 1px solid var(--color-line-card);
      td {
        border-right: 1px solid var(--color-line-card);
      }
    }
  }
  .el-card {
    border-radius: 6px;
  }
  .messageCard {
    .el-card {
      border-color: var(--color-line-card);
      margin-bottom:10px;
    }
  }
  .noData {
    display: flex;
    height: 400px;
    justify-content: center;
    align-items: center;
    color: #979797;
  }
  .el-button--success {
    padding: 10px 24px;
    color: var(--color-main-green);
    border-radius: 30px;
    background-color: var(--color-bg-card);
    border-color: var(--color-bg-card);
    box-shadow: 0 1px 12px 0 var(--color-shadow);
    margin-left: 4px;
    &:hover {
      box-shadow: 0 1px 14px 1px var(--color-shadow);
      background: var(--color-bg-card);
    }
  }
  .sub-btn {
    margin-right: 4px;
  }
  .el-badge__content.is-fixed.is-dot {
    top: 5px;
  }
  @media screen and (min-width: 1366px) {
    .connectPart .el-input--suffix .el-input__inner {
      height: 38px;
    }
  }
}
</style>
