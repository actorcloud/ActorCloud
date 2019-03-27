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
          label="规则名称"
          prop="ruleName">
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
          label="关联产品"
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
        <el-table-column prop="frequency" label="频率">
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
          label: '规则名称',
        }, {
          value: 'productName',
          label: '关联产品',
        },
      ],
    }
  },

  methods: {
    frequency(item) {
      if (item.type === 1) {
        return '每次满足条件都触发'
      }
      if (item.type === 2 && item.period) {
        const unit = item.period.replace(/[^a-z]+/ig, '') === 'm' ? '分钟' : '小时'
        return `${parseInt(item.period, 0)}${unit}内满足${item.times}次时触发`
      }
      if (item.type === 3 && item.period) {
        const unit = item.period.replace(/[^a-z]+/ig, '') === 'm' ? '分钟' : '小时'
        return `持续满足${parseInt(item.period, 0)}${unit}时触发`
      }
    },
  },
}
</script>
