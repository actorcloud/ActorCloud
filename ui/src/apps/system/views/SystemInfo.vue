<template>
  <div class="details-view">
    <div class="emq-crud">
      <div class="crud-header">
        <el-row type="flex" justify="space-between" align="middle">
          <el-col :span="18">
            <span class="crud-title">系统信息</span>
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
              <el-form-item label="MQTT 服务器地址（TCP）" prop="mqttBroker">
                <el-input type="text" v-model="record.mqttBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="CoAP 服务器地址（UDP）" prop="coapBroker">
                <el-input type="text" v-model="record.coapBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="MQTT 服务器地址（TLS）" prop="mqttsBroker">
                <el-input type="text" v-model="record.mqttsBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="CoAP 服务器地址（DTLS）" prop="coapsBroker">
                <el-input type="text" v-model="record.coapsBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="MQTT 服务器地址（证书）" prop="mqttssBroker">
                <el-input type="text" v-model="record.mqttssBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="CoAP 服务器地址（证书）" prop="coapssBroker">
                <el-input type="text" v-model="record.coapssBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="WebSocket 服务器地址（TCP）" prop="wsBroker">
                <el-input type="text" v-model="record.wsBroker"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="WebSocket 服务器地址（证书）" prop="wssBroker">
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
import { httpGet, httpPut } from '@/functions/api'
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
          { required: true, message: '请输入MQTT服务器地址（TCP）', trigger: 'blur' },
        ],
        mqttsBroker: [
          { required: true, message: '请输入MQTT服务器地址（DTLS）', trigger: 'blur' },
        ],
        mqttssBroker: [
          { required: true, message: '请输入MQTT服务器地址（证书）', trigger: 'blur' },
        ],
        coapBroker: [
          { required: true, message: '请输入CoAP服务器地址（UDP）', trigger: 'blur' },
        ],
        coapsBroker: [
          { required: true, message: '请输入CoAP服务器地址（DTLS）', trigger: 'blur' },
        ],
        coapssBroker: [
          { required: true, message: '请输入CoAP服务器地址（证书）', trigger: 'blur' },
        ],
        wsBroker: [
          { required: true, message: '请输入WebSocket服务器地址（TCP）', trigger: 'blur' },
        ],
        wssBroker: [
          { required: true, message: '请输入WebSocket服务器地址（证书）', trigger: 'blur' },
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
          this.$message.success('设置成功!')
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
