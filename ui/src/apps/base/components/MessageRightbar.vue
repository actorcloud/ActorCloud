<template>
  <rightbar-pop>
    <el-card :v-loading="loading" v-if="messageVisible" class="message-rightbar-view">
      <div slot="header" class="clearfix">
        <span class="message-header">{{ $t('message.tab') }}</span>
        <a href="javascript:;" @click="closeMessage" class="message-close">
          <i class="el-icon-close"></i>
        </a>
      </div>
      <div v-if="!records.length" class="message-null">
        {{ $t('message.noMessage') }}
      </div>
      <div>
        <div
          v-for="(record, index) in records"
          :key="index"
          class="message-body text item">
          <div class="message-body-title">{{ record.msgTitle }}</div>
          <el-row>
            <el-col :span="12">
              <div class="message-body-content">{{ record.messageTypeLabel }}</div>
            </el-col>
            <el-col :span="12">
              <div class="message-body-time">{{ record.createAt }}</div>
            </el-col>
          </el-row>
        </div>
      </div>
      <div class="message-bottom clearfix">
        <a href="javascript:;" @click="viewMessageCenter">{{ $t('message.messageCenter') }}</a>
      </div>
    </el-card>
  </rightbar-pop>
</template>


<script>
import { httpGet } from '@/utils/api'
import RightbarPop from '@/components/RightbarPop'

export default {
  name: 'message-rightbar-view',

  components: {
    RightbarPop,
  },

  props: {
    messageVisible: {
      type: Boolean,
      required: true,
    },
  },

  data() {
    return {
      records: [],
      loading: false,
    }
  },

  watch: {
    messageVisible() {
      if (this.messageVisible) {
        this.loadData()
      }
    },
  },

  methods: {
    loadData() {
      this.loading = true
      httpGet('/messages?_page=1&_limit=10').then((response) => {
        this.records = response.data.items
      }).catch(() => {
        this.loading = false
      })
    },
    closeMessage() {
      this.$emit('update:messageVisible', false)
    },
    viewMessageCenter() {
      this.$emit('update:messageVisible', false)
      this.$router.push('/messages')
    },
  },

  created() {
  },
}
</script>


<style lang="scss">
.message-rightbar-view {
  position: fixed;
  right: 0;
  z-index: 1002;
  width: 314px;
  height: 100%;
  background: var(--color-bg-card);
  border-radius: 0;
  box-shadow: -5px 0px 12px rgba(0, 0, 0, 0.1);
  .message-header {
    font-size: 16px;
    color: var(--color-text-light);
    line-height: 28px;
  }
  .message-close {
    float: right;
    color: var(--color-text-light);
    padding: 5px 0;
  }
  .el-card__header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--color-line-card);
    height: 56px;
  }
  .el-card__body {
    padding: 0px;
    .message-null {
      margin: 20px;
      text-align: center;
      color: var(--color-text-default);
      font-size: 14px;
    }
    .message-body {
      margin: 20px;
      padding-bottom: 20px;
      border-bottom: 1px solid #DADBE0;
      font-size: 14px;
      .message-body-title {
        color: var(--color-text-light);
      }
      .message-body-content {
        margin-top: 10px;
        color: var(--color-text-default);
      }
      .message-body-time {
        margin-top: 11px;
        color: var(--color-text-default);
      }
    }
    .message-body:last-child {
      border: none;
    }
    .message-bottom {
      position: absolute;
      bottom: 56px;
      width: 314px;
      height: 56px;
      line-height: 56px;
      background: var(--color-bg-card);
      border-top: 1px solid var(--color-line-card);
      text-align: center;
      a {
        font-size: 14px;
      }
    }
  }
}
@media screen and (min-width: 1366px) {
  .message-rightbar-view {
   .el-card__body .message-bottom {
     bottom: 82px;
   }
  }
}
</style>
