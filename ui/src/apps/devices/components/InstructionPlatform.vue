<template>
  <div class="details-view instruction-platform-view">
    <el-form
      ref="streamPointForm"
      label-width="80px"
      label-position="left"
      :rules="streamPointFormRules"
      :model="streamPointForm">
      <el-form-item class="data-stream-item" label="数据流" prop="dataStream">
        <emq-select
          v-model="streamPointForm.dataStream"
          placeholder="请选择"
          class="data-stream-select"
          :field="{
            url: `emq_select/data_streams?deviceIntID=${currentDevice.deviceIntID}&streamType=2`
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
      <el-table-column prop="dataPointName" width="140px" label="功能点名称">
      </el-table-column>
      <el-table-column label="设置值">
        <template v-slot="scope">
          <!-- Select the enum value -->
          <div v-if="scope.row.enum.length">
            <el-radio-group v-model="scope.row.value">
              <el-radio-button
                v-for="(item, index) in scope.row.enum"
                :key="index"
                :label="item[1]">
                {{ item[0] }}
              </el-radio-button>
            </el-radio-group>
          </div>
          <div v-else>
            <div v-if="scope.row.pointDataType === 5">
              <el-radio v-model="scope.row.value"  :label="JSON.stringify(true)">true
              </el-radio>
              <el-radio v-model="scope.row.value" :label="JSON.stringify(false)">false
              </el-radio>
            </div>
            <div v-else>
              <el-input
                v-model="scope.row.value"
                :type="stringTypes.includes(scope.row.pointDataType) ? 'string' : 'number'"
                :placeholder="`请填写${scope.row.pointDataTypeLabel}`">
              </el-input>
            </div>
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
      data: {
        controlType: 1,
      },
      emptyText: '暂无数据',
      streamPointForm: {},
      stringTypes: [3, 11, 12], // dataPointType, String
      streamPointFormRules: {
        dataStream: [
          { required: true, message: '请选择数据流' },
        ],
      },
      dataPointRecords: [],
      url: '',
    }
  },

  methods: {
    // Get device ID
    getID() {
      this.data.deviceID = this.currentDevice.deviceID
      this.data.deviceIntID = this.currentDevice.deviceIntID
      if (this.currentDevice.cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
        this.data.controlType = 3
        this.data.path = '/19/1/0'
      }
    },

    handleStreamSelect(id, selectItem) {
      if (!id) {
        return
      }
      this.data.streamID = selectItem.attr.streamID
      this.loadDataPoints(id)
    },

    loadDataPoints(streamIntID) {
      if (!streamIntID) {
        return
      }
      httpGet(`/devices/${this.currentDevice.deviceIntID}/stream_points?dataStreamIntID=${streamIntID}`)
        .then((res) => {
          // Search the label by dictcode
          const { pointDataType } = this.$store.state.base.dictCode
          this.dataPointRecords = res.data.dataPoints
          this.topic = res.data.topic
          this.dataPointRecords.forEach((record) => {
            const dataPoint = pointDataType.find(
              item => item.value === record.pointDataType,
            )
            record.pointDataTypeLabel = dataPoint.label
          })
        })
    },

    save() {
      this.$refs.streamPointForm.validate((valid) => {
        if (!valid) {
          return false
        }
        this.getID()
        const dataPointValid = this.dataPointRecords.find(item => !item.value)
        if (dataPointValid) {
          this.$message.error('请填写所有的功能点的值')
          return false
        }
        const dataPointPayload = {}
        this.dataPointRecords.forEach((item) => {
          // The numeric type is converted to Number
          if (!this.stringTypes.includes(item.pointDataType)
            && item.pointDataType !== 5) {
            item.value = parseInt(item.value, 10)
          }
          // Deserialize Boolean
          if (item.pointDataType === 5) {
            item.value = JSON.parse(item.value)
          }
          dataPointPayload[item.dataPointID] = item.value
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
              this.data.publishType = 1
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
            this.$message.error('指令下发失败')
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
