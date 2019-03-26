<template>
  <div class="groups-view">
    <empty-page v-if="isEmpty" :emptyInfo="deviceEmptyInfo"></empty-page>
    <emq-crud
      v-if="!isEmpty"
      url="/groups"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.base.tabs.devices"></tabs-card-head>
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
          prop="deviceCount">
          <template v-slot="scope">
            <router-link
              :to="{ path: '/devices/devices', query: { groupID: scope.row.groupID } }">
              {{ scope.row.deviceCount}}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column
          :label="$t('groups.productName')"
          prop="productName">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import TabsCardHead from '@/components/TabsCardHead'
import EmptyPage from '@/components/EmptyPage'
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'groups-view',

  components: {
    TabsCardHead,
    EmptyPage,
    EmqCrud,
  },

  data() {
    return {
      isEmpty: false,
      deviceEmptyInfo: {
        buttonText: '新建分组',
        title: '您还没有任何分组',
        subTitle: '创建设备前，请先创建产品',
        url: '/',
      },
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
