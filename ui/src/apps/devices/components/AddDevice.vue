<template>
  <div class="add-device">
    <el-card class="device-list">
      <div slot="header">
        <span>包含设备</span>
        <emq-button
          v-if="has(`PUT,${url}/:id`)"
          @click="addDeviceDialog">
          添加设备
        </emq-button>
      </div>
      <el-table class="device-include-table" v-loading="loading" size="medium" :data="deviceData">
        <el-table-column
          :label="$t('devices.deviceName')"
          prop="deviceName">
          <template v-slot="scope">
            <router-link
              style="float: left"
              :to="{ path: `/devices/devices/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.deviceName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="设备类型" prop="deviceTypeLabel"></el-table-column>
        <el-table-column label="设备编号" prop="deviceID"></el-table-column>
        <el-table-column v-if="has(`PUT,${url}/:id`)" width="60px">
          <template v-slot="props">
            <a
              style="float: none"
              href="javascript:;"
              title="删除"
              @click="showConfirmDialog(props.row.id)">
              <img src="@/assets/images/delete.png"/>
            </a>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="total >= 1"
        background
        layout="prev, pager, next"
        :current-page.sync="currentPage"
        :page-size="pageSize"
        :total="total"
        @current-change="handlePageChange">
      </el-pagination>
    </el-card>

    <!-- Add device -->
    <emq-dialog title="添加设备" :visible.sync="dialogVisible" @confirm="addDevice">
      <el-popover
        ref="addDevicePopover"
        placement="top-start"
        trigger="hover"
        content="一个分组最多能绑定1000个设备">
      </el-popover>
      <i class="el-icon-question tips-icon" style="cursor: pointer;" v-popover:addDevicePopover></i>
      <el-select
        v-model="selectedDevice"
        remote
        filterable
        multiple
        placeholder="输入设备名称搜索"
        :loading="selectLoading"
        :remote-method="search">
        <!--@focus="search('', reload = true)">-->
        <el-option
          v-for="option in options"
          :key="option.id"
          :label="option.label"
          :value="option.value">
        </el-option>
      </el-select>
    </emq-dialog>

    <!-- Delete Confirm -->
    <emq-dialog title="警告" :visible.sync="confirmDialogVisible" @confirm="deleteRecords">
      <span>确认删除？</span>
    </emq-dialog>
  </div>
</template>


<script>
import { httpGet, httpPost, httpDelete } from '@/utils/api'
import EmqButton from '@/components/EmqButton'
import EmqDialog from '@/components/EmqDialog'

export default {
  name: 'add-device',

  components: {
    EmqButton,
    EmqDialog,
  },

  props: {
    // The REST api to add device
    url: {
      type: String,
      required: true,
    },
    // Device intID
    detailsID: {
      type: Number,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      dialogVisible: false,
      selectLoading: false,
      confirmDialogVisible: false,
      willDeleteId: undefined,
      page: 1, // The pages number the device to added
      currentPage: 1, // The pages number the device has been added
      pageSize: 10,
      count: 0,
      total: 0,
      searchValue: '',
      deviceData: [], // Contains the device
      options: [],
      selectedDevice: [], // Selected device
    }
  },

  methods: {
    // Load the group detail data
    loadData() {
      if (!this.detailsID) {
        return false
      }
      this.loading = true
      httpGet(`${this.url}/${this.detailsID}/devices?_page=${this.currentPage}&_limit=${this.pageSize}`)
        .then((response) => {
          this.deviceData = response.data.items
          this.total = response.data.meta.count
          this.loading = false
        }).catch((error) => {
          this.loading = false
          this.$message.error(error.response.data.message)
        })
    },

    addDeviceDialog() {
      if (!this.detailsID) {
        return false
      }
      this.dialogVisible = true
      this.selectedDevice = []
      this.search('', true)
    },

    // Remote search device
    search(query, reload = false) {
      const params = {}
      // When the device is not selected, click to load the device
      if (reload && this.selectedDevice.length) {
        return
      }
      if (!reload && !query) {
        return
      }
      this.selectLoading = true
      setTimeout(() => {
        this.options = []
        params.deviceName_like = query
        httpGet(`/emq_select${this.url}/${this.detailsID}/not_joined_devices`, { params })
          .then((res) => {
            this.options = res.data
            this.selectLoading = false
          })
      }, 200)
    },

    showConfirmDialog(deleteID = undefined) {
      this.willDeleteId = deleteID
      this.confirmDialogVisible = true
    },

    // Add the device to the group
    addDevice() {
      if (!this.selectedDevice.length) {
        this.$message.error('所选设备不能为空')
        return
      }
      httpPost(`${this.url}/${this.detailsID}/devices`, { ids: this.selectedDevice })
        .then(() => {
          this.$message.success('添加成功')
          this.loadData()
          this.dialogVisible = false
        })
    },

    deleteRecords() {
      this.confirmDialogVisible = false
      if (!this.willDeleteId) {
        return
      }
      httpDelete(`${this.url}/${this.detailsID}/devices?ids=${this.willDeleteId}`)
        .then(() => {
          this.$message.success('删除成功')
          this.currentPage = 1
          this.loadData()
        })
        .catch((error) => {
          this.$message.error(error.response.data.message || '删除失败')
        })
    },

    handlePageChange(page) {
      this.currentPage = page
      this.loadData()
    },
  },

  created() {
    this.loadData()
  },
}
</script>


<style lang="scss">
.add-device {
  .device-list {
    .el-pagination {
      margin: 20px 0px;
      float: right;
    }
  }
  .device-include-table {
    a {
      float: none;
    }
  }
  .emq-dialog {
    .el-select {
      width: 100%;
      .el-input {
        height: auto;
      }
    }
    p {
      margin: 0 0 10px 0;
    }
    .tips-icon {
      position: absolute;
      top: 20px;
      left: 100px;
    }
  }
}
</style>
