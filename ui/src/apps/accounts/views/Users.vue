<template>
  <div class="users-view">
    <emq-crud
      url="/users"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.accounts.tabs.users"></tabs-card-head>
      </template>
      <template slot="tableColumns">
        <el-table-column :label="$t('users.username')" prop="username">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/users/users/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.username }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column :label="$t('users.email')" prop="email"></el-table-column>
        <el-table-column :label="$t('users.roleName')" prop="roleName">
          <template v-slot="scope">
            {{ scope.row.roleName | convertRoleName }}
          </template>
        </el-table-column>
        <el-table-column v-if="has('PUT,/users/:id')" :label="$t('users.enable')" prop="enable">
          <template v-slot="scope">
            <el-tooltip :content="scope.row.enable === 1 ? $t('users.allowed') : $t('users.notAllowed')" placement="left">
              <el-switch
                v-model="scope.row.enable"
                active-color="#13ce66"
                inactive-color="#d0d3e0"
                :active-value="1"
                :inactive-value="0"
                @change="updateUser(scope.row)">
              </el-switch>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column
          v-else
          :label="$t('users.enable')"
          prop="enable">
          <template v-slot="scope">
            {{ scope.row.enable === 1 ? $t('users.isTrue') : $t('users.isFalse') }}
          </template>
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import { httpPut } from '@/utils/api'
import EmqCrud from '@/components/EmqCrud'
import TabsCardHead from '@/components/TabsCardHead'

export default {
  name: 'users-view',

  components: {
    EmqCrud,
    TabsCardHead,
  },

  data() {
    return {
      tableActions: ['view', 'search', 'create', 'edit', 'delete'],
      searchOptions: [
        {
          value: 'username',
          label: this.$t('users.username'),
        },
        {
          value: 'email',
          label: this.$t('users.email'),
        },
      ],
    }
  },

  methods: {
    // Whether the update allows access
    updateUser(row) {
      httpPut(`/users/${row.id}`, row).then(() => {
        this.$message.success(this.$t('users.editSuccess'))
      }).catch((error) => {
        // Failed to restore the original state
        row.enable = row.enable ? 0 : 1
        this.$message.error(error.response.data.message)
      })
    },
  },
}
</script>
