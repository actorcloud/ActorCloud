<template>
  <div class="scope-rules-view">
    <emq-crud
      url="/rules"
      :crudTitle="$t('resource.business_rules-scope_rules')"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="tableColumns">
        <el-table-column
          :label="$t('rules.ruleName')"
          prop="ruleName">
          <template v-slot="scope">
            <router-link
              :to="{
                path: `/scope_rules/${scope.row.id}`,
                query: { oper: 'view' }
              }">
              {{ scope.row.ruleName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column
          :label="$t('rules.product')"
          prop="productName">
          <template v-slot="scope">
            <router-link
              :to="{
                path: `/products/${scope.row.productIntID}`,
                query: { oper: 'view' }
              }">
              {{ scope.row.productName }}
            </router-link>
          </template>
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'scope-rules-view',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['search', 'edit', 'delete', 'create'],
      searchOptions: [
        {
          value: 'ruleName',
          label: this.$t('rules.ruleName'),
        }, {
          value: 'productName',
          label: this.$t('rules.product'),
        },
      ],
    }
  },

  methods: {
  },
}
</script>
