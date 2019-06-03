<template>
  <div class="details-view instruction-platform-view">
    <el-form
      ref="streamPointForm"
      label-position="left"
      :label-width="lang === 'en' ? '110px': '80px'"
      :rules="streamPointFormRules"
      :model="streamPointForm">
      <el-form-item class="data-stream-item" :label="$t('products.dataStreams')" prop="dataStream">
        <emq-select
          v-model="streamPointForm.dataStream"
          class="data-stream-select"
          :placeholder="$t('oper.select')"
          :field="{
            url: `select_options/data_streams?productID=${currentDevice.productID}&streamType=2`
          }"
          :record="streamPointForm"
          :disabled="false"
          @input="handleStreamSelect">
        </emq-select>
      </el-form-item>
    </el-form>

    <el-table
      v-if="dataPointRecords.length"
      class="my-table"
      size="medium"
      :data="dataPointRecords"
      :empty-text="emptyText">
      <el-table-column prop="label" width="140px" :label="$t('products.dataPointName')">
      </el-table-column>
      <el-table-column :label="$t('devices.setValue')">
        <template v-slot="scope">
          <div v-if="scope.row.attr.pointDataType === $variable.pointDataType.BOOLEAN">
            <el-radio v-model="scope.row.payload"  :label="JSON.stringify(true)">true
            </el-radio>
            <el-radio v-model="scope.row.payload" :label="JSON.stringify(false)">false
            </el-radio>
          </div>
          <div v-else>
            <el-input
              v-model="scope.row.payload"
              :type="scope.row.attr.pointDataType !== $variable.pointDataType.NUMBER ? 'string' : 'number'"
              :placeholder="`${$t('oper.required')}${scope.row.pointDataTypeLabel}`">
            </el-input>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <timer-publish-form
      ref="timerPublishForm"
      v-if="instructionType === 1">
    </timer-publish-form>
  </div>
</template>


<script>
import { httpGet, httpPost } from '@/utils/api'
import EmqSelect from '@/components/EmqSelect'
import TimerPublishForm from './TimerPublishForm'

export default {
  name: 'instruction-platform-view',

  components: {
    EmqSelect,
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
      data: {},
      emptyText: this.$t('oper.noData'),
      streamPointForm: {},
      streamPointFormRules: {
        dataStream: [
          { required: true, message: this.$t('products.dataStreamRequired') },
        ],
      },
      dataPointRecords: [],
      url: '',
    }
  },

  computed: {
    lang() {
      return this.$store.state.accounts.lang
    },
  },

  methods: {
    // Get device ID
    getID() {
      this.data.deviceID = this.currentDevice.deviceID
      this.data.deviceIntID = this.currentDevice.deviceIntID
      if (this.currentDevice.cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
        this.data.path = '/19/1/0'
      }
    },

    handleStreamSelect(id, selectItem) {
      if (!id) {
        return
      }
      this.data.topic = selectItem.attr.topic
      this.data.streamID = selectItem.attr.streamID
      this.loadDataPoints(id)
    },

    loadDataPoints(streamIntID) {
      if (!streamIntID) {
        return
      }
      httpGet(`/select_options/data_points?productID=${this.currentDevice.productID}&dataStreamIntID=${streamIntID}`)
        .then((res) => {
          // Search the label by dictcode
          const { pointDataType } = this.$store.state.accounts.dictCode
          this.dataPointRecords = res.data
          this.dataPointRecords.forEach((record) => {
            const dataPoint = pointDataType.find(
              item => item.value === record.attr.pointDataType,
            )
            record.pointDataTypeLabel = this.lang === 'zh' ? dataPoint.zhLabel : dataPoint.enLabel
          })
        })
    },

    save() {
      this.$refs.streamPointForm.validate((valid) => {
        if (!valid) {
          return false
        }
        this.getID()
        const dataPointValid = this.dataPointRecords.find(item => !item.payload)
        if (dataPointValid) {
          this.$message.error(this.$t('devices.dataPointsAll'))
          return false
        }
        const dataPointPayload = {}
        this.dataPointRecords.forEach((item) => {
          // The numeric type is converted to Number
          if (item.pointDataType === this.$variable.pointDataType.NUMBER) {
            item.payload = parseInt(item.payload, 10)
          }
          // Deserialize Boolean
          if (item.pointDataType === this.$variable.pointDataType.BOOLEAN) {
            item.payload = JSON.parse(item.payload)
          }
          dataPointPayload[item.attr.dataPointID] = item.payload
        })
        this.data.payload = JSON.stringify(dataPointPayload)
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
        const [SUCCESS, FAILURE] = [3, 4]
        const { status } = res.data
        if (this.instructionType === 0) {
          if (status === SUCCESS) {
            this.$message.success(this.$t('devices.publishSuccess'))
          } else if (status === FAILURE) {
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
}
</script>


<style lang="scss">
.instruction-platform-view {
  margin-top: 20px;
  .el-table.el-table--fit {
    border: 1px solid var(--color-line-card);
    border-bottom: 0;
  }
}
</style>
