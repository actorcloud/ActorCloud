<template>
  <div class="details-view">
    <div class="emq-crud">
      <div class="crud-header">
        <el-row type="flex" justify="space-between" align="middle">
          <el-col :span="18">
            <span class="crud-title">{{ $t('systems.systemInfo') }}</span>
          </el-col>
        </el-row>
      </div>
    </div>

    <div>
      <el-card v-loading="pageLoading">
        <el-row :gutter="20">
          <el-form
            ref="record"
            label-width="82px"
            label-position="top"
            :model="record"
            :rules="rules">
            <el-col :span="12">
              <el-form-item :label="$t('systems.mqttTCP')" prop="mqttBroker">
                <el-input type="text" v-model="record.mqttBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('systems.CoAPUDP')" prop="coapBroker">
                <el-input type="text" v-model="record.coapBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('systems.mqttTLS')" prop="mqttsBroker">
                <el-input type="text" v-model="record.mqttsBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('systems.CoAPDTLS')" prop="coapsBroker">
                <el-input type="text" v-model="record.coapsBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('systems.mqttCert')" prop="mqttssBroker">
                <el-input type="text" v-model="record.mqttssBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('systems.CoAPCert')" prop="coapssBroker">
                <el-input type="text" v-model="record.coapssBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('systems.webSocketTCP')" prop="wsBroker">
                <el-input type="text" v-model="record.wsBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('systems.webSocketCert')" prop="wssBroker">
                <el-input type="text" v-model="record.wssBroker"></el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <emq-button icon="save" :loading="btnLoading" @click="save">完成</emq-button>
      </el-card>
    </div>
  </div>
</template>


<script>
import { httpGet, httpPut } from '@/utils/api'
import EmqButton from '@/components/EmqButton'

export default {
  name: 'system-setting-view',

  components: {
    EmqButton,
  },

  data() {
    return {
      pageLoading: false,
      btnLoading: false,
      record: {},
      rules: {
        mqttBroker: [
          { required: true, message: this.$t('systems.mqttTCPRequired'), trigger: 'blur' },
        ],
        mqttsBroker: [
          { required: true, message: this.$t('systems.mqttTLSRequired'), trigger: 'blur' },
        ],
        mqttssBroker: [
          { required: true, message: this.$t('systems.mqttCertRequired'), trigger: 'blur' },
        ],
        coapBroker: [
          { required: true, message: this.$t('systems.CoAPUDPRequired'), trigger: 'blur' },
        ],
        coapsBroker: [
          { required: true, message: this.$t('systems.CoAPDTLSRequired'), trigger: 'blur' },
        ],
        coapssBroker: [
          { required: true, message: this.$t('systems.CoAPCertRequired'), trigger: 'blur' },
        ],
        wsBroker: [
          { required: true, message: this.$t('systems.webSocketTCPRequired'), trigger: 'blur' },
        ],
        wssBroker: [
          { required: true, message: this.$t('systems.webSocketCertRequired'), trigger: 'blur' },
        ],
      },
    }
  },

  methods: {
    loadData() {
      this.pageLoading = true
      httpGet('/system_info').then((response) => {
        this.record = response.data
        this.pageLoading = false
      }).catch(() => {
        this.pageLoading = false
      })
    },
    // Setting
    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        this.btnLoading = true
        httpPut('/system_info', this.record).then(() => {
          this.$message.success(this.$t('oper.setSuccess'))
          this.btnLoading = false
        }).catch(() => {
          this.btnLoading = false
        })
      })
    },
  },

  created() {
    this.loadData()
  },
}
</script>
