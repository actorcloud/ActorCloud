<template>
  <div class="business-rules-view">
    <emq-crud
      url="/business_rules"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.base.tabs.business_rules"></tabs-card-head>
      </template>
      <template slot="tableColumns">
        <el-table-column
          prop="ruleName"
          :label="$t('rules.ruleName')">
          <template v-slot="scope">
            <router-link
              :to="{
                path: `/business_rules/business_rules/${scope.row.id}`,
                query: { oper: 'view' }
              }">
              {{ scope.row.ruleName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column
          prop="productName"
          :label="$t('rules.product')">
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
        <el-table-column prop="frequency" :label="$t('rules.frequency')">
          <template v-slot="scope">
            {{ frequency(scope.row.frequency) }}
          </template>
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'
import TabsCardHead from '@/components/TabsCardHead'

export default {
  name: 'business-rules-view',

  components: {
    EmqCrud,
    TabsCardHead,
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
    frequency(item) {
      if (item.type === 1) {
        return this.$t('rules.everyTime')
      }
      if (item.type === 2 && item.period) {
        const unit = item.period.replace(/[^a-z]+/ig, '') === 'm'
          ? this.$t('rules.minute') : this.$t('rules.hour')
        return this.$t('rules.someTimeItem', {
          period: parseInt(item.period, 0),
          unitName: unit,
          times: item.times })
      }
      if (item.type === 3 && item.period) {
        const unit = item.period.replace(/[^a-z]+/ig, '') === 'm'
          ? this.$t('rules.minute') : this.$t('rules.hour')
        return this.$t('rules.continueTimeItem', {
          period: parseInt(item.period, 0),
          unitName: unit })
      }
    },
  },
}
</script>
