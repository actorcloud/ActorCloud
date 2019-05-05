<template>
  <div class="details-view clients-details-events-view">
    <emq-crud
      class="emq-crud--details"
      ref="crud"
      :url="`${url}?timeType=${timeType}`"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :searchTimeOptions="searchTimeOptions"
      :valueOptions="valueOptions">
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
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'clients-details-events-view',

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
      timeType: 'realtime',
      tableActions: ['search', 'custom'],
      searchOptions: [
        {
          value: 'streamID',
          label: this.$t('dataStreams.streamID'),
        },
        {
          value: 'topic',
          label: this.$t('events.topic'),
        },
        {
          value: 'dataType',
          label: this.$t('events.dataTypeLabel'),
        },
      ],
      valueOptions: {
        dataType: this.$store.state.accounts.dictCode.dataType,
      },
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

  beforeDestroy() {
    clearInterval(this.timer)
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
.clients-details-events-view {

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
