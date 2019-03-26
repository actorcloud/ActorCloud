<template>
  <div class="messages-center-view">
    <emq-crud
      url="/messages"
      :crudTitle="$t('message.tab')"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions">
      <template slot="tableColumns">
        <el-table-column prop="msgTitle" label="消息标题">
        </el-table-column>
        <el-table-column prop="msgContent" :label="$t('message.content')">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/messages/${scope.row.id}`, query: { oper: 'view' } }"
              style="white-space: nowrap;">
              {{ scope.row.msgContent }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column min-width="150px" prop="createAt" :label="$t('message.createAt')">
        </el-table-column>
        <el-table-column prop="messageTypeLabel" :label="$t('message.type')">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'messages-center-view',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['search', 'deleteAll'],
      searchOptions: [
        {
          value: 'msgTitle',
          label: this.$t('message.title'),
        },
        {
          value: 'messageType',
          label: this.$t('message.type'),
        },
      ],
      valueOptions: {
        messageType: this.$store.state.base.dictCode.messageType,
      },
    }
  },
}
</script>
