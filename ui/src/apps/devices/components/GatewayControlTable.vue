<template>
  <div class="details-view gateway-control-view">
    <div class="gateway-control-view-oper">
      <emq-button class="sync-btn" @click="add">
        更新网关配置
      </emq-button>
    </div>

    <!-- Gateway control table -->
    <el-card class="gateway-control-table table-wrapper">
      <el-table
        v-loading="loading"
        size="medium"
        :data="records"
        :empty-text="emptyText">
        <el-table-column
          prop="publishStatusLabel"
          min-width="100px"
          :label="$t('devices.publishStatusLabel')">
        </el-table-column>
        <el-table-column prop="topic" :label="$t('devices.publishTopic')">
        </el-table-column>
        <el-table-column min-width="100px" prop="createUser" :label="$t('devices.createUser')">
        </el-table-column>
        <el-table-column min-width="150px" prop="createAt" :label="$t('devices.publishCreateAt')">
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total >= 1"
        background
        layout="prev, pager, next"
        :current-page.sync="currentPage"
        :page-size="10"
        :total="total"
        @current-change="currentPageChanged">
      </el-pagination>
    </el-card>

    <emq-dialog
      title="提示"
      :visible.sync="confirmDialogVisible"
      :saveLoading="btnLoading"
      @confirm="syncGatewayInfo">
      <span>确认同步网关信息？</span>
    </emq-dialog>
  </div>
</template>


<script>
import { httpGet, httpPost } from '@/utils/api'
import EmqDialog from '@/components/EmqDialog'
import EmqButton from '@/components/EmqButton'

export default {
  name: 'gateway-control-view',

  components: {
    EmqDialog,
    EmqButton,
  },

  props: {
    url: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      btnLoading: false,
      dialogVisible: false,
      confirmDialogVisible: false,
      records: [],
      gatewayId: this.$route.params.id,
      currentPage: 1,
      pageSize: 10,
      total: 0,
      willDeleteId: 0,
      emptyText: ' ',
    }
  },
  methods: {
    loadRecords() {
      this.loading = true
      this.records = []
      const url = `/gateways/${this.$route.params.id}/control_logs`
      httpGet(url).then((response) => {
        if (response.data.meta) {
          this.total = response.data.meta.count || 0
        }
        this.loading = false
        this.records = response.data.items
        this.emptyText = this.records.length < 1 ? '暂无数据' : ' '
      }).catch(() => {
        this.loading = false
      })
    },

    loadData() {
      this.currentPageURL = this.$route.path
      this.loadRecords()
    },

    add() {
      this.confirmDialogVisible = true
    },

    currentPageChanged(page) {
      this.currentPage = page
      this.loadRecords()
    },

    syncGatewayInfo() {
      this.btnLoading = true
      const data = {
        gateway: parseInt(this.gatewayId, 10),
      }
      httpPost('/gateway_publish', data).then(() => {
        this.confirmDialogVisible = false
        this.$message.success('更新网关配置成功')
        this.loadData()
      }).catch(() => {
        this.btnLoading = false
      })
    },
  },

  created() {
    this.loadData()
  },
}
</script>


<style lang="scss">
.gateway-control-view {
  .gateway-control-view-oper {
    text-align: right;
    margin-top: 6px;
    margin-bottom: 22px;
    .sync-btn {
      float: none !important;
    }
  }
  .gateway-control-table {
    .el-table--fit {
      border: none !important;
    }
  }
  .el-pagination {
    margin: 20px 0px;
    float: right;
  }
}
</style>
