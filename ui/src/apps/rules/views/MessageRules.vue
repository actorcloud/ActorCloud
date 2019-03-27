<template>
  <div class="message-rules">
    <el-popover
      placement="top-start"
      width="320"
      trigger="hover">
      <span>
        消息规则能将某个产品/分组下的设备上报的数据转发至用户的 Webhook接口、数据库、消息队列。
        <br/>
        <br/>
        请阅读
        <a href="https://docs.actorcloud.io/rule_engine/message_rules.html" target="_blank">
          文档
        </a>，了解规则的创建与使用。
      </span>
      <i slot="reference" class="el-icon-question tips-icon" style="cursor: pointer;"></i>
    </el-popover>
    <emq-crud
      url="/message_rules"
      crudTitle="消息规则"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="tableColumns">
        <el-table-column prop="url" min-width="160px" label="URL">
          <template v-slot="scope">
            <router-link :to="`/message_rules/${scope.row.id}?oper=view`">
              {{ scope.row.config.url }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="接口状态">
          <template v-slot="props">
            <span v-if="props.row.status === 1" class="running-status not-point online">验证成功</span>
            <span v-else class="running-status not-point offline">验证失败</span>
          </template>
        </el-table-column>
        <el-table-column prop="productName" label="关联产品"></el-table-column>
        <el-table-column prop="groupName" label="关联分组"></el-table-column>
      </template>
      <template v-slot:customOper="props">
        <i
          class="iconfont oper-button custom-text"
          title="验证Webhook接口可用性"
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
        this.$message.success(response.data.status === 1 ? 'Webhook接口验证成功' : 'Webhook接口不可用')
      })
    },
  },
}
</script>


<style lang="scss">
.message-rules {
  position: relative;
  .tips-icon {
    z-index: 100;
    position: absolute;
    left: 80px;
    top: 18px;
  }
}
</style>
