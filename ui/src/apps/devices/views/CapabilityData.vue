<template>
  <div class="details-view capability-data-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.capabilityData') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>

    <el-row ref="capabilityForm" class="capability-search-form" :gutter="20">
      <el-form ref="form" class="custom-search__form" :model="record">
        <el-col :span="6">
          <el-radio-group class="search-radio" v-model="dataType" @change="handleTypeChange">
            <el-radio-button label="realtime">{{ $t('devices.realTime') }}</el-radio-button>
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
            <div
              v-if="currentDevice.cloudProtocol !== $variable.cloudProtocol.LWM2M"
              class="form-label__disabeld">{{ $t('devices.dataPoint') }}</div>
            <emq-select
              v-else
              class="form-label__select"
              v-model="lwm2mType"
              size="small"
              :field="{
                options: [
                  { value: 'data_point', label: $t('devices.dataPoint') },
                  { value: 'path', label: $t('devices.lwm2mPath') },
                ],
              }"
              @input="handleTypeChange">
            </emq-select>
            <emq-search-select
              v-if="currentDevice.cloudProtocol === $variable.cloudProtocol.LWM2M
                && lwm2mType === 'path'"
              ref="productItem"
              v-model="record.productItemIntID"
              clearable
              size="small"
              :record="record"
              :disabled="false"
              :placeholder="$t('devices.itemSearch')"
              :field="{
                url: '/emq_select/product_items',
                params: { productID: currentDevice.productID },
                searchKey: 'itemName',
              }"
              @input="handleItemPath">
            </emq-search-select>
            <el-cascader
              v-if="currentDevice.cloudProtocol !== $variable.cloudProtocol.LWM2M
                || (currentDevice.cloudProtocol === $variable.cloudProtocol.LWM2M
                  && lwm2mType === 'data_point')"
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
      :url="`/capability_data?deviceID=${currentDevice.deviceID}`"
      :autoLoad="false">
      <template
        v-if="currentDevice.cloudProtocol === $variable.cloudProtocol.LWM2M
          && lwm2mType === 'path'"
        slot="tableColumns">
        <el-table-column prop="path" label="PATH"></el-table-column>
        <el-table-column prop="itemName" :label="$t('devices.itemName')"></el-table-column>
        <el-table-column prop="value" :label="$t('devices.reportedValue')"></el-table-column>
        <el-table-column prop="msgTime" :label="$t('devices.msgTime')"></el-table-column>
      </template>
      <template
        v-if="currentDevice.cloudProtocol !== $variable.cloudProtocol.LWM2M
          || (currentDevice.cloudProtocol === $variable.cloudProtocol.LWM2M
            && lwm2mType === 'data_point')"
        slot="tableColumns">
        <el-table-column
          v-if="currentDevice.cloudProtocol !== $variable.cloudProtocol.MODBUS"
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
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqCrud from '@/components/EmqCrud'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import EmqSearchSelect from '@/components/EmqSearchSelect'
import DeviceDetailTabs from '../components/DeviceDetailTabs'

export default {
  name: 'capability-data-view',

  mixins: [currentDevicesMixin],

  components: {
    EmqDetailsPageHead,
    EmqTag,
    DeviceDetailTabs,
    EmqCrud,
    EmqSearchSelect,
  },

  data() {
    return {
      record: {},
      dataType: 'realtime',
      lwm2mType: 'data_point',
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
        if (!this.tempTimeValue && this.dataType === 'history') {
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
      const { cloudProtocol } = this.currentDevice
      const params = {
        dataType: this.dataType,
      }
      Object.assign(params, this.record)
      if (cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
        params.lwm2mType = this.lwm2mType
        delete params.productItemIntID
      } else {
        delete params.dataPoints
      }
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
      if (this.dataType === 'realtime') {
        this.searchTimeValue = null
        this.setDataInterval()
      }
      this.refreshData()
    },
    handleDataPoint(selectItem) {
      const { cloudProtocol } = this.currentDevice
      if (cloudProtocol === this.$variable.cloudProtocol.MODBUS) {
        this.record.dataPointID = selectItem[0]
      } else {
        this.record.dataStreamIntID = selectItem[0]
        this.record.dataPointID = selectItem[1]
      }
      this.refreshData()
    },
    handleItemPath(id, selectItem) {
      if (selectItem) {
        this.record.path = `/${selectItem.attr.objectID}/${selectItem.attr.itemID}`
      } else {
        delete this.record.path
      }
      this.refreshData()
    },
    setDataInterval() {
      this.timer = setInterval(() => {
        this.refreshData(true)
      }, 5000)
    },
    loadDataPoint() {
      httpGet(`/emq_select/stream_datapoints?productID=${this.currentDevice.productID}`)
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

  beforeRouteLeave(to, form, next) {
    clearInterval(this.timer)
    next()
  },
}
</script>


<style lang="scss">
.capability-data-view {
  .capability-search-form {
    position: relative;
    top: 3px;
    height: 35px;
    margin-top: 21px;
    .el-form-item {
      margin-top: -3px;
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
