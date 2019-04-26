<template>
  <div class="connect-logs-view">
    <emq-crud
      url="/"
      class="emq-crud--details"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
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

export default {
  name: 'connect-logs-view',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['search'],
      searchOptions: [
        {
          value: 'IP',
          label: this.$t('deviceLogs.connectStatusLabel'),
        },
      ],
      searchTimeOptions: [
        {
          value: 'createAt',
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
