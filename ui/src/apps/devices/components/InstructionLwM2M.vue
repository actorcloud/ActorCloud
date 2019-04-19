<template>
  <div class="details-view instruction-lwm2m-view">
    <el-form
      ref="lwForm"
      label-width="80px"
      label-position="left"
      :model="lwForm"
      :rules="lwFormRules">
      <el-form-item :label="$t('products.item')" prop="$instanceItems">
        <el-cascader
          :options="itemOptions"
          v-model="lwForm.$instanceItems"
          @change="handleItemChange">
        </el-cascader>
      </el-form-item>
      <el-form-item v-if="!isDevice" :label="$t('devices.instance')" prop="instanceID">
        <el-input
          type="number"
          v-model.number="lwForm.instanceID">
        </el-input>
      </el-form-item>
      <el-form-item :label="$t('oper.oper')" prop="controlType">
        <el-radio-group v-model="lwForm.controlType">
          <el-radio
            :disabled="currentControlType === 'E' || currentControlType === 'W'"
            :label="2">{{ $t('devices.R') }}</el-radio>
          <el-radio
            :disabled="currentControlType === 'E' || currentControlType === 'R'"
            :label="3">{{ $t('devices.W') }}</el-radio>
          <el-radio
            :disabled="currentControlType && currentControlType !== 'E'"
            :label="4">{{ $t('devices.E') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item
        v-if="currentControlType
          && lwForm.controlType === operationDict.W"
        :label="$t('devices.value')"
        prop="payload">
        <el-input
          v-model="lwForm.payload"
          type="textarea"
          :placeholder="$t('devices.valueRequired')">
        </el-input>
      </el-form-item>
      <el-form-item
        v-if="currentControlType
          && lwForm.controlType === operationDict.E"
          :label="$t('devices.value')">
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
import { httpGet, httpPost } from '@/utils/api'
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
    currentGroup: {
      type: Object,
      default: () => ({}),
    },
  },

  data() {
    return {
      isDevice: true,
      currentControlType: null, // Operation on the current item
      url: '',
      data: {},
      lwForm: {
        controlType: null, // Operation on the selected item
      },
      operationDict: {
        R: 2,
        W: 3,
        E: 4,
      },
      itemOptions: [],
      lwFormRules: {
        $instanceItems: [
          { required: true, message: this.$t('devices.itemRequired') },
        ],
        instanceID: [
          { required: true, message: this.$t('devices.instanceRequired') },
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
    // Load cascade items
    loadItems() {
      let getUrl = ''
      if (this.currentGroup.groupID) {
        this.isDevice = false
        getUrl = `/emq_select/group/product_items?productID=${this.currentGroup.productID}`
      } else if (this.currentDevice.deviceID) {
        this.isDevice = true
        getUrl = `/emq_select/lwm2m_items?deviceIntID=${this.currentDevice.deviceIntID}`
      }
      httpGet(getUrl).then((res) => {
        this.itemOptions = res.data
      })
    },

    save() {
      this.$refs.lwForm.validate((valid) => {
        if (!valid) {
          return false
        }
        Object.assign(this.data, this.lwForm)
        if (!this.isDevice) { // Is group
          this.url = '/group_publish'
          this.data.groupID = this.currentGroup.groupID
          const payload = {
            operation: this.switchOper(this.lwForm.controlType),
            itemName: this.lwForm.itemName,
            itemID: this.lwForm.itemID,
            instanceID: this.lwForm.instanceID,
            objectID: this.lwForm.objectID,
          }
          if (this.lwForm.payload && this.lwForm.controlType === this.operationDict.E) {
            payload.args = this.lwForm.payload
          } else if (this.lwForm.payload && this.lwForm.controlType === this.operationDict.W) {
            payload.value = this.lwForm.payload
          }
          this.data.payload = JSON.stringify(payload)
          this.postData()
          return
        }
        this.data.deviceID = this.currentDevice.deviceID
        delete this.data.$instanceItems
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

    // Gets the operation of the current selected item
    handleItemChange(values) {
      if (!values) {
        return
      }
      this.lwForm.path = `/${values.join('/')}`
      if (!this.isDevice) {
        this.lwForm.objectID = values[0]
        this.lwForm.itemID = values[1]
        const currentObject = this.itemOptions.find(item => item.value === values[0])
        const currentItem = currentObject.children.find(item => item.value === values[1])
        this.currentControlType = currentItem.itemOperations
        this.lwForm.itemName = currentItem.label
      } else {
        const currentObject = this.itemOptions.find(item => item.value === values[0])
        const currentInstance = currentObject.children.find(item => item.value === values[1])
        const currentItem = currentInstance.children.find(item => item.value === values[2])
        this.currentControlType = currentItem.itemOperations
        if (this.currentControlType === 'RW') {
          this.lwForm.controlType = this.operationDict.R
        } else {
          this.lwForm.controlType = this.operationDict[this.currentControlType]
        }
      }
    },

    switchOper(oper) {
      switch (oper) {
        case 'read':
          return 'R'
        case 'write':
          return 'W'
        case 'execute':
          return 'E'
        default:
          return ''
      }
    },
  },

  created() {
    this.loadItems()
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
