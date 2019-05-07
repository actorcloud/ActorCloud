<template>
  <div class="business-rules-view">
    <emq-crud
      url="/rules?ruleType=1"
      :crudTitle="$t('resource.business_rules')"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="tableColumns">
        <el-table-column
          prop="ruleName"
          :label="$t('rules.ruleName')">
          <template v-slot="scope">
            <router-link
              :to="{
                path: `/business_rules/${scope.row.id}`,
                query: { oper: 'view' }
              }">
              {{ scope.row.ruleName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column
          v-if="has('PUT,/rules/:id')"
          prop="enable"
          :label="$t('rules.enable')">
          <template v-slot="scope">
            <el-tooltip
              placement="left"
              :content="scope.row.enable === 1 ? $t('oper.enable') : $t('oper.disabled')">
              <el-switch
                v-model="scope.row.enable"
                active-color="#13ce66"
                inactive-color="#D0D3E0"
                :active-value="1"
                :inactive-value="0"
                @change="updateRules(scope.row)">
              </el-switch>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column
          prop="remark"
          :label="$t('rules.remark')">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import { httpPut } from '@/utils/api'
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'business-rules-view',

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
    updateRules(row) {
      httpPut(`/rules/${row.id}`, row).then(() => {
        this.$message.success(this.$t('oper.editSuccess'))
      }).catch(() => {
        row.enable = row.enable ? 0 : 1
        this.$message.error(this.$t('oper.updateFail'))
      })
    },
  },
}
</script>
