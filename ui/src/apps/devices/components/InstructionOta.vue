<template>
  <div class="instruction-ota-view">
    <el-form
      ref="otaForm"
      label-width="80px"
      label-position="left"
      :model="otaForm"
      :rules="otaFormRules">
      <el-form-item prop="url" :label="$t('devices.softwarePackage')">
        <emq-search-select
          v-model="otaForm.url"
          :placeholder="$t('devices.softwarePackageRequired')"
          :field="sdkSelectFiled"
          :record="otaForm"
          :disabled="false"
          @input="handleSDKSelect">
        </emq-search-select>
      </el-form-item>
    </el-form>

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
      <el-input v-model="topic" placeholder="inbox"></el-input>
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
import EmqSearchSelect from '@/components/EmqSearchSelect'
import TimerPublishForm from './TimerPublishForm'
import CodeEditor from '@/components/CodeEditor'

export default {
  name: 'instruction-ota-view',

  components: {
    EmqSearchSelect,
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
      otaForm: {},
      topic: '',
      progress: 0,
      data: {
        controlType: 1,
      },
      url: '',
      otaFormRules: {
        url: [
          { required: true, message: this.$t('devices.softwarePackageRequired') },
        ],
      },
      sdkSelectFiled: {
        url: '/emq_select/sdk_packages',
        searchKey: 'sdkName',
      },
    }
  },

  methods: {
    // Selected sdk packages
    handleSDKSelect() {
      const url = `${window.location.origin}${this.otaForm.url}`
      this.$refs.codeEditor.codeEditor.setValue(JSON.stringify({ url }, null, 2))
    },

    // Get device or group ID
    getID() {
      if (this.currentDevice.deviceID) {
        const { deviceID, deviceIntID } = this.currentDevice
        this.isDevice = true
        this.sdkSelectFiled.params = { deviceIntID }
        this.data.deviceID = deviceID
        this.data.deviceIntID = deviceIntID
      } else if (this.currentGroup.groupID) {
        const { id, groupID } = this.currentGroup
        this.isDevice = false
        this.sdkSelectFiled.params = { groupID }
        this.data.groupID = groupID
        this.data.groupIntID = id
      }
    },

    save() {
      this.$refs.otaForm.validate((valid) => {
        if (!valid) {
          return false
        }
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
              this.data.publishType = this.isDevice ? 1 : 2
              this.postData()
            })
        }
      })
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
  },

  created() {
    this.getID()
  },
}
</script>


<style lang="scss">
.instruction-ota-view {
  margin-top: 20px;
}
</style>
