<template>
  <div class="device-connect-logs-view">
    <emq-crud
      url="/device_connect_logs"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :searchTimeOptions="searchTimeOptions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.base.tabs.device_logs"></tabs-card-head>
      </template>
      <template slot="tableColumns">
        <el-table-column
          :label="$t('deviceLogs.deviceName')"
          prop="deviceName">
        </el-table-column>
        <el-table-column
          :label="$t('deviceLogs.deviceID')"
          prop="deviceID">
        </el-table-column>
        <el-table-column
          :label="$t('deviceLogs.IP')"
          prop="IP">
        </el-table-column>
        <el-table-column
          :label="$t('deviceLogs.connectStatusLabel')"
          prop="connectStatusLabel">
        </el-table-column>
        <el-table-column
          :label="$t('deviceLogs.createAt')"
          prop="createAt"
          width="150px"
          sortable="custom">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'
import TabsCardHead from '@/components/TabsCardHead'

export default {
  name: 'device-connect-logs-view',

  components: {
    EmqCrud,
    TabsCardHead,
  },

  data() {
    return {
      tableActions: ['search'],
      searchOptions: [
        {
          value: 'deviceName',
          label: this.$t('deviceLogs.deviceName'),
        },
        {
          value: 'deviceID',
          label: this.$t('deviceLogs.deviceID'),
        },
        {
          value: 'IP',
          label: this.$t('deviceLogs.IP'),
        },
      ],
      searchTimeOptions: [
        {
          value: 'createAt',
          label: '创建时间',
          filter: ['hour', 'day', 'week'],
          limit: {
            time: 7 * 24 * 3600 * 1000,
            msg: '时间范围须小于一周',
          },
          disabledDate(time) {
            return time.getTime() > Date.now()
          },
        },
      ],
    }
  },
}
</script>
