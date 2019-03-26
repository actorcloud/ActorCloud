<template>
  <div class="login-logs-view">
    <emq-crud
      url="/login_logs"
      :crudTitle="$t('loginLogs.loginLogs')"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="tableColumns">
        <el-table-column
          :label="$t('loginLogs.username')"
          prop="username">
        </el-table-column>
        <el-table-column
          :label="$t('loginLogs.IP')"
          prop="IP">
        </el-table-column>
        <el-table-column
          :label="$t('loginLogs.isSuccess')"
          prop="isLoggedLabel">
        </el-table-column>
        <el-table-column
          prop="loginTime"
          sortable="custom"
          :label="$t('loginLogs.loginTime')">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'login-logs-view',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['search'],
      searchOptions: [
        {
          value: 'username',
          label: this.$t('loginLogs.username'),
        },
        {
          value: 'IP',
          label: this.$t('loginLogs.IP'),
        },
      ],
    }
  },
}
</script>
