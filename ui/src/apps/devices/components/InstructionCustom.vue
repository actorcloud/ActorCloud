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

    <template v-if="isDevice">
      <div class="form-item">
        <label>{{ `${$t('devices.publishTopic')}` }}</label>
        <div class="form-tips">
          <i class="el-icon-warning"></i>
          {{ $t('devices.instructWarning2') }}
        </div>
      </div>
      <el-input
        v-if="this.currentDevice.cloudProtocol === $variable.cloudProtocol.LWM2M"
        v-model="data.path"
        :disabled="true">
      </el-input>
      <el-input
        v-else
        v-model="topic"
        placeholder="inbox">
      </el-input>
    </template>

    <el-progress
      v-if="instructionType === 0 && !isDevice"
      style="top: 18px; margin-bottom: 23px;"
      :text-inside="true"
      :stroke-width="18"
      :percentage="progress || 0">
    </el-progress>
  </div>
</template>


<script>
import { httpGet, httpPost } from '@/utils/api'
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
    currentGroup: {
      type: Object,
      default: () => ({}),
    },
  },

  data() {
    return {
      isDevice: true, // Is device or group
      jsonValue: JSON.stringify({ message: 'Hello' }, null, 2),
      topic: '',
      progress: 0,
      data: {
        controlType: 1,
      },
      url: '',
    }
  },

  methods: {
    // Get device or group ID
    getID() {
      if (this.currentDevice.deviceID) {
        const { deviceID, deviceIntID, cloudProtocol } = this.currentDevice
        this.isDevice = true
        this.data.deviceID = deviceID
        this.data.deviceIntID = deviceIntID
        if (cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
          this.data.controlType = 3
          this.data.path = '/19/1/0'
        }
      } else if (this.currentGroup.groupID) {
        const { id, groupID } = this.currentGroup
        this.isDevice = false
        this.data.groupID = groupID
        this.data.groupIntID = id
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
      if (this.isDevice) {
        this.data.topic = this.topic
      }
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
        const [PENDING, PROGRESS, SUCCESS, FAILURE] = [1, 2, 3, 4]
        // If not timed and grouped, poll the progress and prompt for results
        if (!this.instructionType && !this.isDevice) {
          if (res.data.status === SUCCESS) {
            const { statusUrl } = res.data.result
            let time = 0
            const poll = setInterval(() => {
              httpGet(statusUrl).then((res) => {
                const { failed, success } = res.data.result
                this.progress = res.data.progress
                if (res.data.status === SUCCESS) {
                  clearInterval(poll)
                  this.$message.success(`
                    ${this.$t('groups.publishSuccess')} ${success} ${this.$t('oper.item')}，
                    ${this.$t('groups.publishFailure')} ${failed} ${this.$t('oper.item')}`)
                  this.$emit('update:btnLoading', false)
                  this.$emit('close-form')
                } else if (res.data.status === FAILURE) {
                  clearInterval(poll)
                  this.$message.error(this.$t('groups.publishFailure'))
                  this.progress = 0
                  this.$emit('update:btnLoading', false)
                  this.$emit('close-form')
                } else if (
                  (res.data.status === PENDING || res.data.status === PROGRESS) && time >= 300) {
                  clearInterval(poll)
                  this.$message.error(this.$t('groups.publishTimeout'))
                  this.progress = 0
                  this.$emit('update:btnLoading', false)
                  this.$emit('close-form')
                }
              })
              time += 1
            }, 1000)
          } else if (res.data.status === FAILURE) {
            this.$message.error(this.$t('groups.groupPublishFailure'))
            this.progress = 0
            this.$emit('update:btnLoading', false)
          }
          return
        }

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
      this.progress = 0
      this.topic = ''
      this.jsonValue = JSON.stringify({ message: 'Hello' }, null, 2)
      if (this.instructionType) {
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
