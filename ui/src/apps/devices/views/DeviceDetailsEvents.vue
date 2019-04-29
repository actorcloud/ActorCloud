<template>
  <div class="details-view device-details-events-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceEvent') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>
    <emq-crud
      class="emq-crud--details"
      ref="crud"
      :url="`/devices/${$route.params.id}/events?timeType=${timeType}`"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :searchTimeOptions="searchTimeOptions">
      <template slot="customButton">
        <el-radio-group class="search-radio" v-model="timeType" @change="handleDataType">
          <el-radio-button label="realtime">{{ $t('devices.realTime') }}</el-radio-button>
          <el-radio-button label="history">{{ $t('devices.historyTime') }}</el-radio-button>
        </el-radio-group>
      </template>
      <template slot="tableColumns">
        <el-table-column
          prop="dataTypeLabel"
          width="90px"
          :label="$t('events.dataTypeLabel')">
        </el-table-column>
        <el-table-column prop="streamID" width="120px" :label="$t('dataStreams.streamID')">
        </el-table-column>
        <el-table-column prop="topic" width="150px" :label="$t('events.topic')">
        </el-table-column>
        <el-table-column prop="data" :label="$t('events.data')">
          <template v-slot="{ row }">
            <el-popover
              v-if="row.data && row.data.length >= 200"
              popper-class="payload-pop"
              trigger="hover"
              placement="top"
              :width="900">
              <p>{{ row.data }}</p>
              <div slot="reference" class="name-wrapper">
                <div class="payload-content">{{ row.data | truncate }}</div>
              </div>
            </el-popover>
            <div v-else class="payload-content">{{ row.data | truncate }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="responseResult" width="120px" :label="$t('events.responseResult')">
        </el-table-column>
        <el-table-column prop="msgTime" width="160px" :label="$t('events.createAtLog')">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqCrud from '@/components/EmqCrud'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import DeviceDetailTabs from '../components/DeviceDetailTabs'

export default {
  name: 'device-details-events-view',

  mixins: [currentDevicesMixin],

  components: {
    DeviceDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    EmqCrud,
  },

  data() {
    return {
      loading: false,
      timeType: 'realtime',
      tableActions: ['search', 'custom'],
      searchOptions: [
        {
          value: 'topic',
          label: this.$t('events.topic'),
        },
      ],
    }
  },

  computed: {
    searchTimeOptions() {
      let timeData = []
      if (this.timeType === 'history') {
        timeData = [{
          value: 'msgTime',
          label: this.$t('events.createAtLog'),
          filter: ['hour', 'day', 'week'],
          limit: {
            time: 7 * 24 * 3600 * 1000,
            msg: this.$t('devices.timeLimit'),
          },
          defaultValue: 7 * 24 * 3600 * 1000,
          disabledDate(time) {
            return time.getTime() > Date.now()
          },
        }]
      }
      return timeData
    },
  },

  methods: {
    loadData(disableLoading) {
      const { _data } = this.$refs.crud
      _data.httpConfig = { disableLoading }
      this.$refs.crud.loadRecords({}, _data.searchKeywordName, _data.searchKeywordValue, '', '', '')
    },
    handleDataType() {
      clearInterval(this.timer)
      if (this.timeType === 'realtime') {
        this.loadData(false)
        this.setDataInterval()
      }
    },
    setDataInterval() {
      this.timer = setInterval(() => {
        this.loadData(true)
      }, 5000)
    },
  },

  mounted() {
    clearInterval(this.timer)
    this.setDataInterval()
  },

  beforeRouteLeave(to, form, next) {
    clearInterval(this.timer)
    next()
  },

  // FireFox does not support line-clamp CSS properties
  filters: {
    // Superfluous content shows ellipsis (...)
    truncate(value) {
      return value && value.length >= 200 ? `${value.slice(0, 199)}...` : value
    },
  },
}
</script>


<style lang="scss">
.device-details-events-view {

  .payload-content {
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

}

.payload-pop {
  background: var(--color-bg-card);
  color: var(--color-text-light);
  line-height: 25px;
  word-break: break-all;
  box-shadow: 2px 10px 20px 0px var(--color-bg-gray);
  border: 1px solid var(--color-line-card);
}
</style>
