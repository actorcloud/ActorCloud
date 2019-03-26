<template>
	<div class="message-center-detail">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/messages' }">消息中心
        </el-breadcrumb-item>
        <el-breadcrumb-item>详情</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>
    <el-card>
      <el-row>
        <el-col :span="18">
          <h3>{{ record.msgTitle }}</h3>
        </el-col>
        <el-col :span="6" style="text-align: right; line-height: 56px;">
          <el-tag size="small">{{ record.messageTypeLabel }}</el-tag>
          <span>{{ record.createAt }}</span>
        </el-col>
      </el-row>
      <div class="article">{{ record.msgContent }}</div>
    </el-card>
  </div>
</template>


<script>
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'

export default {
  name: 'app-role-detail',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
  },

  data() {
    return {
      url: '/messages',
    }
  },
}
</script>

<style lang="scss">
.message-center-detail {
  h3 {
    color: var(--color-text-lighter);
  }
  .article {
    color: var(--color-text-light);
  }
  .el-tag {
    margin-right: 10px;
  }
}
</style>
