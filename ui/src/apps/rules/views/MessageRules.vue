<template>
  <div class="message-rules">
    <emq-crud
      url="/message_rules"
      :crudTitle="$t('rules.messageRule')"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="titleTips">
        <el-popover
          placement="top-start"
          width="320"
          trigger="hover">
          <span>{{ $t('rules.messageRuleTips') }}
            <br/>
            {{ $t('rules.read') }}
            <a href="https://docs.actorcloud.io/rule_engine/message_rules.html" target="_blank">
              {{ $t('rules.document') }}
            </a>{{ $t('rules.ruleUse') }}
          </span>
          <i slot="reference" class="el-icon-question tips-icon" style="cursor: pointer;"></i>
        </el-popover>
      </template>
      <template slot="tableColumns">
        <el-table-column prop="url" min-width="160px" label="URL">
          <template v-slot="scope">
            <router-link :to="`/message_rules/${scope.row.id}?oper=view`">
              {{ scope.row.config.url }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="$t('rules.interfaceStatus')">
          <template v-slot="props">
            <span v-if="props.row.status === 1" class="running-status not-point online">{{ $t('rules.verifySuccess') }}</span>
            <span v-else class="running-status not-point offline">{{ $t('rules.verifyFail') }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="productName" :label="$t('rules.product')"></el-table-column>
        <el-table-column prop="groupName" :label="$t('rules.group')"></el-table-column>
      </template>
      <template v-slot:customOper="props">
        <i
          class="iconfont oper-button custom-text"
          :title="$t('rules.Available')"
          @click="validateStatus(props.row)">
          检
        </i>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'
import { httpPost } from '@/utils/api'

export default {
  name: 'message-rules',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['view', 'create', 'edit', 'delete'],
      searchOptions: [],
    }
  },

  methods: {
    validateStatus(row) {
      httpPost('/validate_message_rule', { id: row.id }).then((response) => {
        row.status = response.data.status
        this.$message.success(response.data.status === 1
          ? this.$t('rules.AvailableSuccess') : this.$t('rules.AvailableFail'))
      })
    },
  },
}
</script>


<style lang="scss">
.message-rules {
  position: relative;
  .emq-crud .crud-header .crud-title {
    position: relative;
  }
  .tips-icon {
    z-index: 100;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    right: -26px;
    color: var(--color-text-default);
  }
}
</style>
