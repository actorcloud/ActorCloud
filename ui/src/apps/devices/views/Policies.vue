<template>
  <div class="policies-view">
    <emq-crud
      v-if="!isEmpty"
      url="/policies"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.base.tabs.security"></tabs-card-head>
      </template>
      <template slot="tableColumns">
        <el-table-column prop="name" min-width="160px" :label="$t('policies.name')">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/security/policies/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.name }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="topic" :label="$t('policies.topic')"></el-table-column>
        <el-table-column prop="accessLabel" min-width="100px" :label="$t('policies.accessLabel')"></el-table-column>
        <el-table-column prop="allowLabel"  :label="$t('policies.allowLabel')"></el-table-column>
        <el-table-column
          prop="createAt"
          :label="$t('policies.createAt')"
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
  name: 'policies-view',

  components: {
    EmqCrud,
    TabsCardHead,
  },

  data() {
    return {
      isEmpty: false,
      tableActions: ['view', 'search', 'create', 'edit', 'delete'],
      searchOptions: [
        {
          value: 'name',
          label: this.$t('policies.name'),
        },
      ],
    }
  },
}
</script>
