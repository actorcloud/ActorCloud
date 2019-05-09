<template>
  <div class="groups-view">
    <emq-crud
      url="/groups"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.accounts.tabs.devices"></tabs-card-head>
      </template>
      <template slot="tableColumns">
        <el-table-column
          :label="$t('groups.groupName')"
          prop="groupName">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/devices/groups/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.groupName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column
          :label="$t('groups.groupID')"
          prop="groupID">
        </el-table-column>
        <el-table-column
          :label="$t('groups.deviceNum')"
          prop="endDeviceCount">
          <template v-slot="scope">
            <router-link
              :to="{ path: '/devices/devices', query: { groupID: scope.row.groupID } }">
              {{ scope.row.endDeviceCount}}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column
          :label="$t('groups.gatewayNum')"
          prop="gatewayCount">
          <template v-slot="scope">
            <router-link
              :to="{ path: '/devices/gateways', query: { groupID: scope.row.groupID } }">
              {{ scope.row.gatewayCount}}
            </router-link>
          </template>
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import TabsCardHead from '@/components/TabsCardHead'
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'groups-view',

  components: {
    TabsCardHead,
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['view', 'search', 'create', 'edit', 'delete'],
      searchOptions: [
        {
          value: 'groupName',
          label: this.$t('groups.groupName'),
        },
        {
          value: 'groupID',
          label: this.$t('groups.groupID'),
        },
      ],
    }
  },
}
</script>
