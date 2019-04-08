<template>
  <div class="details-view device-code-view">
    <input
      v-model="clipboardContent"
      type="text"
      id="clipboard">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="device-code-card" v-loading="loading">
          <span class="card-title">{{ $t('devices.deviceCode') }}</span>
          <el-popover placement="left" width="290" trigger="hover">
            <p>{{ $t('devices.mqttWarning') }}</p>
            <i slot="reference" class="el-icon-question"></i>
          </el-popover>
          <el-scrollbar>
            <el-form label-position="left" class="details-code">
              <el-form-item :label="`${$t('devices.deviceID')}：`">
                <template>
                  <el-tooltip effect="dark" :content="clipboardStatus" placement="top">
                    <i
                      v-show="record.deviceID"
                      class="material-icons copy-icon"
                      @click="copyText(record.deviceID)">
                      check
                    </i>
                  </el-tooltip>
                  <span>{{ record.deviceID }}</span>
                </template>
              </el-form-item>
              <el-form-item :label="`${$t('devices.token')}：`">
                <template v-if="currentDevice.upLinkSystem !== Gateway">
                  <el-tooltip effect="dark" :content="clipboardStatus" placement="top">
                    <i
                      v-show="record.token"
                      class="material-icons copy-icon"
                      @click="copyText(record.token)">
                      check
                    </i>
                  </el-tooltip>
                  <span>{{ record.token }}</span>
                </template>
                <template v-else>
                  <span style="right: 0px"> — </span>
                </template>
              </el-form-item>
              <el-form-item :label="`${$t('devices.username')}：`">
                <template v-if="currentDevice.upLinkSystem !== Gateway">
                  <el-tooltip effect="dark" :content="clipboardStatus" placement="top">
                    <i
                      v-show="record.deviceUsername"
                      class="material-icons copy-icon"
                      @click="copyText(record.deviceUsername)">
                      check
                    </i>
                  </el-tooltip>
                  <span>{{ record.deviceUsername }}</span>
                </template>
                <template v-else>
                  <span style="right: 0px"> — </span>
                </template>
              </el-form-item>
            </el-form>
          </el-scrollbar>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="device-code-card" v-loading="loading">
          <span class="card-title">{{ $t('devices.mqtt') }}</span>
          <el-form label-position="left" class="details-code code">
            <el-form-item label="TCP：">
              <template>
                <span>{{ broker.mqttBroker }}</span>
              </template>
            </el-form-item>
            <el-form-item label="TLS：">
              <template>
                <span>{{ broker.mqttsBroker }}</span>
              </template>
            </el-form-item>
            <el-form-item :label="`${$t('devices.mqttssBroker')}：`">
              <template>
                <span>{{ broker.mqttssBroker }}</span>
              </template>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="device-code-card" v-loading="loading">
          <span class="card-title">{{ $t('devices.CoAP') }}</span>
          <el-form label-position="left" class="details-code">
            <el-form-item label="UDP：">
              <template>
                <span>{{ broker.coapBroker }}</span>
              </template>
            </el-form-item>
            <el-form-item label="DTLS：">
              <template>
                <span>{{ broker.coapsBroker }}</span>
              </template>
            </el-form-item>
            <el-form-item :label="`${$t('devices.coapssBroker')}：`">
              <template>
                <span>{{ broker.coapssBroker }}</span>
              </template>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import { currentDevicesMixin } from '@/mixins/currentDevices'

export default {
  name: 'device-code-view',

  mixins: [currentDevicesMixin],

  data() {
    return {
      url: '/devices',
      record: {},
      broker: {},
      loading: false,
      clipboardContent: '',
      clipboardStatus: this.$t('oper.copy'),
      Gateway: 2,
    }
  },

  methods: {
    loadData() {
      this.loading = true
      this.record = this.currentDevice
      httpGet('/broker_info').then((response) => {
        this.broker = response.data
        this.loading = false
      })
    },
    copyText(content) {
      this.clipboardContent = content
      this.clipboardStatus = this.$t('oper.copySuccess')
      setTimeout(() => {
        document.querySelector('#clipboard').select()
        document.execCommand('Copy')
        setTimeout(() => {
          this.clipboardStatus = this.$t('oper.copy')
        }, 500)
      }, 500)
    },
  },

  created() {
    this.loadData()
  },
}
</script>


<style lang="scss">
@import '~@/assets/scss/detailsPage.scss';

.device-code-view {
  #clipboard {
    position: absolute;
    z-index: -1;
  }
  .device-code-card {
    white-space: nowrap;
    overflow-x: scroll;
    font-size: 14px;
    .el-card__body {
      .card-title {
        color: var(--color-text-lighter);
      }
      .el-icon-question {
        color: var(--color-text-light);
        cursor: pointer;
        margin-left: 4px;
      }
      .details-code {
        margin-top: 20px;
        margin-bottom: 10px;
        .el-form-item {
          margin-bottom: 5px;
          .el-form-item__content {
            line-height: 40px;
            span {
              color: var(--color-text-default);
              position: relative;
              right: 17px;
            }
          }
          .copy-icon {
            display: inline-block;
            position: relative;
            top: 5px;
            right: 17px;
            margin-right: 4px;
            color: var(--color-main-green);
            font-size: 24px;
            cursor: pointer;
          }
        }
      }
      padding: 20px 20px 0px 20px !important;
    }
  }
}
</style>
