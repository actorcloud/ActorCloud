<template>
  <div class="tenants-view">
    <emq-crud
      url="/operate_detail"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.base.tabs.operate_reporting"></tabs-card-head>
      </template>
      <template slot="tableColumns">
        <el-table-column
          :label="$t('operations.companyName')"
          prop="tenantName">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/operate_reporting/operate_detail/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.tenantName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column
          :label="$t('tenants.type')"
          prop="tenantTypeLabel">
        </el-table-column>
        <el-table-column
          :label="$t('operations.adminEmail')"
          prop="contactEmail">
        </el-table-column>
        <el-table-column
          :label="$t('operations.deviceTotal')"
          prop="deviceCount"
          sortable="custom">
        </el-table-column>
        <el-table-column
          :label="$t('operations.createAt')"
          prop="createAt"
          min-width="150px"
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
  name: 'tenants-view',

  components: {
    EmqCrud,
    TabsCardHead,
  },

  data() {
    return {
      tableActions: ['search', 'view'],
      searchOptions: [
        {
          value: 'tenantType',
          label: this.$t('tenants.type'),
        },
        {
          value: 'tenantName',
          label: this.$t('operations.companyName'),
        },
        {
          value: 'contactEmail',
          label: this.$t('operations.adminEmail'),
        },
      ],
      valueOptions: {
        tenantType: this.$store.state.base.dictCode.tenantType,
      },
    }
  },
}
</script>
