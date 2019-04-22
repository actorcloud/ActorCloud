<template>
  <div class="current-alerts-view">
    <emq-crud
      url="/current_alerts"
      :crudTitle="$t('alerts.currentAlerts')"
      :tableActions="tableActions"
      :valueOptions="valueOptions"
      :searchOptions="searchOptions"
      :searchTimeOptions="searchTimeOptions">
      <template slot="tableColumns">
        <el-table-column
          :label="$t('alerts.alertName')"
          prop="alertName">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/current_alerts/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.alertName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column :label="$t('alerts.rules')" prop="ruleName">
          <template v-slot="scope">
            <router-link
              v-if="scope.row.ruleIntID"
              :to="{ path: `/business_rules/${scope.row.ruleIntID}`, query: { oper: 'view' } }">
              {{ scope.row.ruleName }}
            </router-link>
            <router-link
              v-else-if="scope.row.scopeIntID"
              :to="{ path: `/scopes/scopes/${scope.row.scopeIntID}`, query: { oper: 'view' } }">
              {{ scope.row.ruleName }}
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
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'current-alerts-view',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['refresh', 'search', 'delete'],
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
.current-alerts-view {
  @import '../assets/tag.scss';
}
</style>
