<template>
  <div class="instruction-custom-view">
    <div class="form-item">
      <label>
        <span class="required">* </span>
        {{ `${$t('devices.publishStatusContent')}` }}
      </label>
      <div class="form-tips">
        <i class="el-icon-warning"></i>
        {{ $t('devices.instructWarning1') }}
      </div>
    </div>
    <code-editor
      ref="codeEditor"
      lang="application/json"
      theme="lesser-dark"
      v-model="jsonValue">
    </code-editor>

    <timer-publish-form
      ref="timerPublishForm"
      v-if="instructionType === 1">
    </timer-publish-form>

    <div class="form-item">
      <label>{{ `${$t('devices.publishTopic')}` }}</label>
      <div class="form-tips">
        <i class="el-icon-warning"></i>
        {{ $t('devices.instructWarning2') }}
      </div>
    </div>
    <el-input
      v-model="topic"
      placeholder="inbox"
      :disabled="this.currentDevice.cloudProtocol === $variable.cloudProtocol.LWM2M">
    </el-input>
  </div>
</template>


<script>
import { httpPost } from '@/utils/api'
import TimerPublishForm from './TimerPublishForm'
import CodeEditor from '@/components/CodeEditor'

export default {
  name: 'instruction-custom-view',

  components: {
    CodeEditor,
    TimerPublishForm,
  },

  props: {
    btnLoading: {
      type: Boolean,
      default: false,
    },
    postUrl: {
      type: String,
      required: true,
    },
    timerUrl: {
      type: String,
      required: true,
    },
    instructionType: {
      type: Number,
      required: true,
    },
    currentDevice: {
      type: Object,
      default: () => ({ cloudProtocol: 0 }),
    },
  },

  data() {
    return {
      jsonValue: JSON.stringify({ message: 'Hello' }, null, 2),
      topic: '',
      data: {},
      url: '',
    }
  },

  methods: {
    getID() {
      if (this.currentDevice.deviceID) {
        const { deviceID, cloudProtocol } = this.currentDevice
        this.data.deviceID = deviceID
        if (cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
          this.topic = '/19/1/0'
        }
      }
    },

    save() {
      if (!this.jsonValue) {
        this.$message.warning(this.$t('devices.payloadRequired'))
        return
      }
      try { // Format compressed JSON
        this.data.payload = JSON.stringify(JSON.parse(this.jsonValue))
      } catch (e) {
        this.data.payload = this.jsonValue
      }
      this.data.topic = this.topic
      if (this.instructionType === 0) {
        this.url = this.postUrl
        this.postData()
      } else {
        this.url = this.timerUrl
        this.$refs.timerPublishForm.getTimerDate()
          .then((res) => {
            Object.assign(this.data, res)
            this.postData()
          })
      }
    },

    postData() {
      this.$emit('update:btnLoading', true)
      httpPost(this.url, this.data).then((res) => {
        const [SUCCESS, FAILURE] = [3, 4]
        if (this.instructionType === 0) {
          if (res.data.status === SUCCESS) {
            this.$message.success(this.$t('devices.publishSuccess'))
          } else if (res.data.status === FAILURE) {
            this.$message.error(this.$t('devices.instructError'))
          }
        } else if (this.instructionType === 1) {
          this.$message.success(this.$t('devices.taskSuccess'))
        }
        this.$emit('update:btnLoading', false)
        this.$emit('close-form')
      }).catch(() => {
        this.$emit('update:btnLoading', false)
      })
    },

    initData() {
      this.topic = ''
      this.jsonValue = JSON.stringify({ message: 'Hello' }, null, 2)
      if (this.instructionType === 1) {
        this.data.taskName = undefined
        this.data.crontabTime = undefined
        this.data.minute = undefined
        this.data.hour = undefined
        this.data.weekday = undefined
        this.data.timerType = undefined
        this.$refs.timerPublishForm.initData()
      }
    },
  },

  created() {
    this.getID()
  },
}
</script>


<style lang="scss">
.instruction-custom-view {
  margin-top: 20px;
}
</style>
