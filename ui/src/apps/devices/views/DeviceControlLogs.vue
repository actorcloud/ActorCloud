<template>
  <div class="device-control-logs-view">
    <emq-crud
      url="/device_control_logs"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :searchTimeOptions="searchTimeOptions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.base.tabs.device_logs"></tabs-card-head>
      </template>
      <template slot="tableColumns">
        <el-table-column :label="$t('deviceLogs.deviceName')" prop="deviceName"></el-table-column>
        <el-table-column :label="$t('deviceLogs.instruct')" prop="payload">
          <template v-slot="scope">
            {{ JSON.parse(scope.row.payload) }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('deviceLogs.publishStatusLabel')" prop="publishStatusLabel"></el-table-column>
        <el-table-column
          :label="$t('deviceLogs.controlCreateAt')"
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
  name: 'device-control-logs-view',

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
      ],
      searchTimeOptions: [
        {
          value: 'createAt',
          label: '创建时间',
        },
      ],
    }
  },
}
</script>
