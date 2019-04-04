<template>
  <div class="current-alerts-view">
    <emq-crud
      url="/current_alerts"
      crudTitle="当前告警"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :searchTimeOptions="searchTimeOptions">
      <template slot="tableColumns">
        <el-table-column
          label="告警名称"
          prop="alertName">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/current_alerts/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.alertName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="规则" prop="ruleName">
          <template v-slot="scope">
            <router-link
              v-if="scope.row.ruleIntID"
              :to="{ path: `/business_rules/business_rules/${scope.row.ruleIntID}`, query: { oper: 'view' } }">
              {{ scope.row.ruleName }}
            </router-link>
            <router-link
              v-else-if="scope.row.scopeIntID"
              :to="{ path: `/scopes/scopes/${scope.row.scopeIntID}`, query: { oper: 'view' } }">
              {{ scope.row.ruleName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="告警内容" prop="alertContent"></el-table-column>
        <el-table-column sortable label="告警次数" prop="alertTimes"></el-table-column>
        <el-table-column
          label="告警等级"
          prop="alertSeverityLabel"
          :filters="filtersData"
          :filter-method="filterTag">
          <template v-slot="scope">
            <el-tag v-if="scope.row.alertSeverityLabel==='紧急'" type="danger" size="mini">
              紧急
            </el-tag>
            <el-tag v-if="scope.row.alertSeverityLabel==='主要'" type="warning" size="mini">
              主要
            </el-tag>
            <el-tag v-if="scope.row.alertSeverityLabel==='次要'" type="info" size="mini">
              次要
            </el-tag>
            <el-tag v-if="scope.row.alertSeverityLabel==='警告'" type="success" size="mini">
              警告
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('devices.deviceName')" prop="deviceName"></el-table-column>
        <el-table-column sortable label="开始时间" prop="startTime" min-width="150px">
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
          label: '开始时间',
        },
      ],
      searchOptions: [
        {
          value: 'alertName',
          label: '告警名称',
        },
        {
          value: 'deviceName',
          label: this.$t('devices.deviceName'),
        },
      ],
      filtersData: [
        { text: '紧急', value: '紧急' },
        { text: '主要', value: '主要' },
        { text: '次要', value: '次要' },
        { text: '警告', value: '警告' },
      ],
    }
  },

  methods: {
    filterTag(value, row) {
      return row.alertSeverityLabel === value
    },
  },
}
</script>


<style lang="scss">
.current-alerts-view {
  @import '../assets/tag.scss';
  .el-table__column-filter-trigger {
    line-height: 25px;
  }
}
</style>
