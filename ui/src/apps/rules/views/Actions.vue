<template>
  <div class="actions-view">
    <emq-crud
      url="/actions"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.accounts.tabs.business_rules"></tabs-card-head>
      </template>
      <template slot="tableColumns">
        <el-table-column prop="actionName" :label="$t('actions.actionName')">
          <template v-slot="props">
            <router-link :to="`/business_rules/actions/${props.row.id}?oper=view`">
              {{ props.row.actionName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="actionTypeLabel" :label="$t('actions.actionType')"></el-table-column>
        <el-table-column prop="createUser" :label="$t('actions.createUser')"></el-table-column>
        <el-table-column prop="createAt" min-width="150px" :label="$t('actions.createAt')"></el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'actions-view',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['search', 'create', 'edit', 'delete'],
      searchOptions: [
        {
          value: 'actionName',
          label: this.$t('actions.actionName'),
        },
      ],
    }
  },
}
</script>
