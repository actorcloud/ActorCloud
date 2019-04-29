<template>
  <div class="details-view instruction-lwm2m-view">
    <el-form
      ref="lwForm"
      label-width="80px"
      label-position="left"
      :model="lwForm"
      :rules="lwFormRules">
      <el-form-item :label="$t('products.item')" prop="path">
        <el-input
          v-model="lwForm.path"
          :placeholder="$t('publish.pathRequired')">
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('oper.oper')" prop="controlType">
        <el-radio-group v-model="lwForm.controlType">
          <el-radio
            :label="2">{{ $t('devices.R') }}</el-radio>
          <el-radio
            :label="3">{{ $t('devices.W') }}</el-radio>
          <el-radio
            :label="4">{{ $t('devices.E') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item
        v-if="lwForm.controlType !== operationDict.R"
        :label="$t('devices.value')"
        :prop="lwForm.controlType === operationDict.W ? 'payload' : ''">
        <el-input
          v-model="lwForm.payload"
          type="textarea"
          :placeholder="$t('devices.valueRequired')">
        </el-input>
      </el-form-item>
    </el-form>

    <timer-publish-form
      ref="timerPublishForm"
      v-if="instructionType === 1">
    </timer-publish-form>
  </div>
</template>


<script>
import { httpPost } from '@/utils/api'
import TimerPublishForm from './TimerPublishForm'

export default {
  name: 'instruction-lwm2m-view',

  components: {
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
      isDevice: true,
      currentControlType: null, // Operation on the current item
      url: '',
      data: {},
      lwForm: {
        controlType: 2, // Operation on the selected item
      },
      operationDict: {
        R: 2,
        W: 3,
        E: 4,
      },
      lwFormRules: {
        path: [
          { required: true, message: this.$t('publish.pathRequired') },
        ],
        controlType: [
          { required: true, message: this.$t('devices.operRequired') },
        ],
        payload: [
          { required: true, message: this.$t('devices.valueRequired') },
        ],
      },
    }
  },

  methods: {
    save() {
      this.$refs.lwForm.validate((valid) => {
        if (!valid) {
          return false
        }
        Object.assign(this.data, this.lwForm)
        this.data.deviceID = this.currentDevice.deviceID
        if (this.instructionType === 0) {
          this.url = this.postUrl
          this.postData()
        } else if (this.instructionType === 1) {
          this.url = this.timerUrl
          this.$refs.timerPublishForm.getTimerDate()
            .then((res) => {
              Object.assign(this.data, res)
              this.postData()
            })
        }
      })
    },

    postData() {
      this.$emit('update:btnLoading', true)
      httpPost(this.url, this.data).then((res) => {
        if (this.instructionType === 0) {
          const [SUCCESS, FAILURE] = [3, 4]
          const { status } = res.data
          if (status === SUCCESS) {
            this.$message.success(this.$t('devices.publishSuccess'))
          } else if (status === FAILURE) {
            this.message.error(this.$t('devices.instructError'))
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
}
</script>


<style lang="scss">
.instruction-lwm2m-view {
  margin-top: 20px;
  .el-cascader {
    width: 100%;
  }
}
</style>
