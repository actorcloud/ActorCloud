<template>
  <div class="details-view gateway-details-events-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">网关</el-breadcrumb-item>
        <el-breadcrumb-item v-if="record">{{ record.gatewayName }}</el-breadcrumb-item>
        <el-breadcrumb-item>网关事件</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="record" class="emq-tag-group" slot="tag">
        <emq-tag>{{ record.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>
    <emq-crud
      class="emq-crud--details"
      ref="crud"
      :url="`/gateways/${this.$route.params.id}/events?dataType=${dataType}`"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :searchTimeOptions="searchTimeOptions">
      <template slot="customButton">
        <el-radio-group class="search-radio" v-model="dataType" @change="handleDataType">
          <el-radio-button label="realtime">实时数据</el-radio-button>
          <el-radio-button label="history">历史数据</el-radio-button>
        </el-radio-group>
      </template>
      <template slot="tableColumns">
        <el-table-column prop="topic" width="260px" :label="$t('devices.topic')">
        </el-table-column>
        <el-table-column prop="payload_string" :label="$t('devices.payload')">
          <template v-slot="{ row }">
            {{ row.payload_string }}
          </template>
        </el-table-column>
        <el-table-column prop="msgTime" width="170px" :label="$t('devices.createAtLog')">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import EmqCrud from '@/components/EmqCrud'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import GatewayDetailTabs from '../components/GatewayDetailTabs'

export default {
  name: 'gateway-details-events-view',

  components: {
    GatewayDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    EmqCrud,
  },

  data() {
    return {
      loading: false,
      dataType: 'realtime',
      tableActions: ['search', 'custom'],
      searchOptions: [
        {
          value: 'topic',
          label: '主题',
        },
      ],
      record: undefined,
    }
  },

  computed: {
    searchTimeOptions() {
      let timeData = []
      if (this.dataType === 'history') {
        timeData = [{
          value: 'msgTime',
          label: '发生时间',
          filter: ['hour', 'day', 'week'],
          limit: {
            time: 7 * 24 * 3600 * 1000,
            msg: '时间范围须小于一周',
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
      if (this.dataType === 'realtime') {
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

  created() {
    httpGet(`/gateways/${this.$route.params.id}`)
      .then((res) => {
        this.record = res.data
      })
  },

  mounted() {
    clearInterval(this.timer)
    this.setDataInterval()
  },

  beforeRouteLeave(to, form, next) {
    clearInterval(this.timer)
    next()
  },
}
</script>


<style lang="scss">
.gateway-details-events-view {
  .emq-crud--details {
    .el-card__body {
      padding: 30px;
    }
  }
}
</style>
