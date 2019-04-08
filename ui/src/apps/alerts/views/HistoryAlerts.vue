<template>
  <div class="history-alerts-view">
    <emq-crud
      url="/history_alerts"
      :crudTitle="$t('alerts.historyAlerts')"
      :tableActions="tableActions"
      :valueOptions="valueOptions"
      :timeSearch="true"
      :searchTimeOptions="searchTimeOptions"
      :searchOptions="searchOptions">
      <template slot="tableColumns">
        <el-table-column
          :label="$t('alerts.alertName')"
          prop="alertName">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/history_alerts/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.alertName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column :label="$t('alerts.alertContent')" prop="alertContent"></el-table-column>
        <el-table-column sortable :label="$t('alerts.alertTimes')" prop="alertTimes"></el-table-column>
        <el-table-column
          :label="$t('alerts.alertSeverity')"
          prop="alertSeverityLabel">
          <template v-slot="scope">
            <el-tag
              :type="scope.row.alertSeverity === 1
                ? 'danger'
                : scope.row.alertSeverity === 2
                ? 'warning'
                : scope.row.alertSeverity === 3
                ? 'info'
                : 'success'"
              size="mini">
              {{ scope.row.alertSeverityLabel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('devices.deviceName')" prop="deviceName"></el-table-column>
        <el-table-column sortable :label="$t('alerts.startTime')" prop="startTime" min-width="150px">
        </el-table-column>
        <el-table-column sortable :label="$t('alerts.endTime')" prop="endTime" min-width="150px">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'history-alerts-view',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['search', 'timeSearch', 'delete'],
      searchTimeOptions: [
        {
          value: 'startTime',
          label: this.$t('alerts.startTime'),
        },
      ],
      searchOptions: [
        {
          value: 'alertName',
          label: this.$t('alerts.alertName'),
        },
        {
          value: 'deviceName',
          label: this.$t('devices.deviceName'),
        },
        {
          value: 'alertSeverity',
          label: this.$t('alerts.alertSeverity'),
        },
      ],
      valueOptions: {
        alertSeverity: [
          { label: this.$t('alerts.emergency'), value: 1 },
          { label: this.$t('alerts.main'), value: 2 },
          { label: this.$t('alerts.secondary'), value: 3 },
          { label: this.$t('alerts.warning'), value: 4 },
        ],
      },
    }
  },
}
</script>


<style lang="scss">
.history-alerts-view {
  @import '../assets/tag.scss';
}
</style>
