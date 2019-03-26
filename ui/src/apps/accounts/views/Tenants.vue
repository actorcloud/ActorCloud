<template>
  <div class="tenants-view">
    <emq-crud
      url="/tenants"
      :crudTitle="$t('tenants.tenants')"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="tableColumns">
        <el-table-column :label="$t('tenants.name')" prop="tenantName">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/tenants/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.tenantName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column :label="$t('tenants.type')" prop="tenantTypeLabel"></el-table-column>
        <el-table-column :label="$t('tenants.email')" prop="contactEmail"></el-table-column>
        <el-table-column :label="$t('tenants.tel')" prop="contactPhone"></el-table-column>
        <el-table-column :label="$t('tenants.enable')" prop="enable">
          <template v-slot="scope">
            <el-tooltip
              :content="scope.row.enable === 1 ? $t('tenants.allowed') : $t('tenants.notAllowed')"
              placement="left">
              <el-switch
                v-model="scope.row.enable"
                active-color="#13ce66"
                inactive-color="#d0d3e0"
                :disabled="!has('PUT,/tenants/:id')"
                :active-value="1"
                :inactive-value="0"
                @change="updateUser(scope.row)">
              </el-switch>
            </el-tooltip>
          </template>
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import { httpPut } from '@/utils/api'
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'tenants-view',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['view', 'search'],
      searchOptions: [
        {
          value: 'company',
          label: this.$t('tenants.name'),
        },
        {
          value: 'contactEmail',
          label: this.$t('tenants.email'),
        },
      ],
    }
  },

  methods: {
    // Whether the update allows access
    updateUser(row) {
      httpPut(`/tenants/${row.id}`, row).then(() => {
        this.$message.success(this.$t('tenants.editSuccess'))
      }).catch((error) => {
        // Failed to restore the original state
        row.enable = row.enable ? 0 : 1
        this.$message.error(error.response.data.message)
      })
    },
  },
}
</script>
