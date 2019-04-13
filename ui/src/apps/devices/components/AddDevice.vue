<template>
  <div class="add-device">
    <el-card class="device-list">
      <div slot="header">
        <span>{{$t('devices.includeDevices')}}</span>
        <emq-button
          v-if="has(`PUT,${url}/:id`)"
          @click="addDeviceDialog">
          {{ $t('devices.addDevices') }}
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
        <el-table-column :label="$t('devices.deviceType')" prop="deviceTypeLabel"></el-table-column>
        <el-table-column :label="$t('devices.deviceID')" prop="deviceID"></el-table-column>
        <el-table-column v-if="has(`PUT,${url}/:id`)" width="60px">
          <template v-slot="props">
            <a
              :title="$t('oper.delete')"
              style="float: none"
              href="javascript:;"
              class="border-button"
              @click="showConfirmDialog(props.row.id)">
              <i class="iconfont icon icon-emq-delete"></i>
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
    <emq-dialog :title="$t('devices.addDevices')" :visible.sync="dialogVisible" @confirm="addDevice">
      <el-popover
        ref="addDevicePopover"
        placement="top-start"
        trigger="hover"
        :content="$t('groups.groupDeviceLimit')">
      </el-popover>
      <i class="el-icon-question tips-icon" style="cursor: pointer;" v-popover:addDevicePopover></i>
      <el-select
        v-model="selectedDevice"
        remote
        filterable
        multiple
        :placeholder="$t('oper.devicesSearch')"
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
    <emq-dialog :title="$t('oper.warning')" :visible.sync="confirmDialogVisible" @confirm="deleteRecords">
      <span>{{ $t('oper.confirmDelete') }}</span>
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
        this.$message.error(this.$t('groups.notNull'))
        return
      }
      httpPost(`${this.url}/${this.detailsID}/devices`, { ids: this.selectedDevice })
        .then(() => {
          this.$message.success(this.$t('oper.addSuccess'))
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
          this.$message.success(this.$t('oper.deleteSuccess'))
          this.currentPage = 1
          this.loadData()
        })
        .catch((error) => {
          this.$message.error(error.response.data.message || this.$t('oper.deleteSuccess'))
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
