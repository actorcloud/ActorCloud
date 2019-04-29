<template>
  <div class="connect-logs-view">
    <emq-crud
      :url="url"
      class="emq-crud--details"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions"
      :searchTimeOptions="searchTimeOptions">
      <template slot="tableColumns">
        <el-table-column
          :label="$t('deviceLogs.connectStatusLabel')"
          prop="connectStatusLabel">
        </el-table-column>
        <el-table-column
          :label="$t('deviceLogs.IP')"
          prop="IP">
        </el-table-column>
        <el-table-column
          :label="$t('deviceLogs.createAt')"
          prop="msgTime"
          sortable="custom">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'connect-logs-view',

  components: {
    EmqCrud,
  },

  props: {
    url: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      tableActions: ['search'],
      searchOptions: [
        {
          value: 'connectStatus',
          label: this.$t('deviceLogs.connectStatusLabel'),
        },
      ],
      valueOptions: {
        connectStatus: this.$store.state.accounts.dictCode.connectStatus,
      },
      searchTimeOptions: [
        {
          value: 'msgTime',
          label: this.$t('devices.createAtLog'),
          filter: ['hour', 'day', 'week'],
          disabledDate(time) {
            return time.getTime() > Date.now()
          },
        },
      ],
    }
  },
}
</script>
