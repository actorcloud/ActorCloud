<template>
  <div class="details-view client-capability-data-view">
    <el-row ref="capabilityForm" class="capability-search-form" :gutter="20">
      <el-form ref="form" class="custom-search__form" :model="record">
        <el-col :span="6">
          <el-radio-group class="search-radio" v-model="timeType" @change="handleTypeChange">
            <el-radio-button label="realtime">{{ $t('devices.realtime') }}</el-radio-button>
            <el-radio-button label="history">{{ $t('devices.historyTime') }}</el-radio-button>
          </el-radio-group>
        </el-col>
        <el-col v-if="searchTimeValue" :span="9">
          <el-form-item>
            <div class="form-label__disabeld">{{ $t('devices.msgTime') }}</div>
             <el-date-picker
              ref="timePicker"
              size="small"
              v-model="searchTimeValue"
              prefix-icon="el-icon-date"
              class="search-value"
              popper-class="emq-search-form--date-picker"
              type="datetimerange"
              range-separator="-"
              :start-placeholder="$t('oper.startDate')"
              :end-placeholder="$t('oper.endDate')"
              :picker-options="pickerOptions"
              @change="refreshData(false)">
            </el-date-picker>
          </el-form-item>
        </el-col>

        <el-col :span="9" :offset="!searchTimeValue ? 9 : 0">
          <el-form-item>
            <div class="form-label__disabeld">{{ $t('devices.dataPoint') }}</div>
            <el-cascader
              clearable
              size="small"
              class="search-value"
              expand-trigger="hover"
              :options="dataPointOptions"
              @change="handleDataPoint">
            </el-cascader>
          </el-form-item>
        </el-col>
      </el-form>
    </el-row>

    <emq-crud
      class="emq-crud--details"
      ref="crud"
      :url="url"
      :autoLoad="false">
      <template
        slot="tableColumns">
        <el-table-column
          v-if="currentClient.cloudProtocol !== $variable.cloudProtocol.MODBUS"
          prop="streamName"
          :label="$t('products.dataStreams')">
        </el-table-column>
        <el-table-column prop="dataPointName" :label="$t('products.dataPoints')"></el-table-column>
        <el-table-column prop="value" :label="$t('devices.reportedValue')"></el-table-column>
        <el-table-column prop="msgTime" :label="$t('devices.msgTime')"></el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'client-capability-data-view',

  components: {
    EmqCrud,
  },

  props: {
    url: {
      type: String,
      required: true,
    },
    currentClient: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      record: {},
      timeType: 'realtime',
      dataPointOptions: [],
      tempTimeValue: null,
      pickerOptions: {
        disabledDate(time) {
          return time.getTime() > Date.now()
        },
        shortcuts: [{
          text: this.$t('oper.lastHour'),
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 1)
            picker.$emit('pick', [start, end])
          },
        }, {
          text: this.$t('oper.lastDay'),
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 1)
            picker.$emit('pick', [start, end])
          },
        }, {
          text: this.$t('oper.lastWeek'),
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
            picker.$emit('pick', [start, end])
          },
        }],
      },
    }
  },

  computed: {
    searchTimeValue: {
      get() {
        if (!this.tempTimeValue && this.timeType === 'history') {
          const end = new Date()
          const start = new Date()
          start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
          return [start, end]
        }
        return this.tempTimeValue
      },
      set(newVal) {
        this.tempTimeValue = newVal
      },
    },
  },

  methods: {
    refreshData(disableLoading) {
      const params = {
        timeType: this.timeType,
      }
      Object.assign(params, this.record)
      delete params.dataPoints
      if (this.searchTimeValue) {
        if ((this.searchTimeValue[1] - this.searchTimeValue[0]) > 3600 * 1000 * 24 * 7) {
          this.$message.error(this.$t('devices.timeLimit'))
          return
        }
      }
      const { _data } = this.$refs.crud
      _data.httpConfig = { disableLoading }
      // Prevent bad parameters when paging
      if (disableLoading) {
        this.$refs.crud.loadRecords({}, '', '', params, 'msgTime', this.searchTimeValue)
      } else {
        this.$refs.crud.search('', '', params, 'msgTime', this.searchTimeValue)
      }
    },
    handleTypeChange() {
      clearInterval(this.timer)
      if (this.timeType === 'realtime') {
        this.searchTimeValue = null
        this.setDataInterval()
      }
      this.refreshData()
    },
    handleDataPoint(selectItem) {
      const { cloudProtocol } = this.currentClient
      if (cloudProtocol === this.$variable.cloudProtocol.MODBUS) {
        this.record.dataPointID = selectItem[0]
      } else {
        this.record.streamID = selectItem[0]
        this.record.dataPointID = selectItem[1]
      }
      this.refreshData()
    },
    setDataInterval() {
      this.timer = setInterval(() => {
        this.refreshData(true)
      }, 5000)
    },
    loadDataPoint() {
      httpGet(`/emq_select/stream_datapoints?productID=${this.currentClient.productID}`)
        .then((res) => {
          this.dataPointOptions = res.data
        })
    },
  },

  mounted() {
    clearInterval(this.timer)
    this.refreshData()
    this.setDataInterval()
  },

  created() {
    this.loadDataPoint()
  },

  beforeDestroy() {
    clearInterval(this.timer)
  },
}
</script>


<style lang="scss">
.client-capability-data-view {
  .capability-search-form {
    position: relative;
    top: 3px;
    height: 35px;
    margin-top: 21px;
    .el-form-item {
      margin-top: -3px;
    }
    .custom-search__form .el-input__inner {
      border-color: var(--color-bg-hover);
    }
  }

  @media screen and (min-width: 1366px) {
    .capability-search-form {
      height: 41px;
      .el-form-item {
        margin-top: 0px;
      }
    }
  }
}
</style>
