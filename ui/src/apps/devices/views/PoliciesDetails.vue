<template>
  <div class="policies-details-view details-view">
   <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/security/policies' }">{{ $t('policies.policie') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <div class="policies-card-details-body">
      <el-card :class="disabled ? 'is-details-form' : ''">
        <edit-toggle-button
          :url="url"
          :disabled="disabled"
          :accessType="accessType"
          @toggleStatus="toggleStatus">
        </edit-toggle-button>
        <el-row :gutter="50">
          <el-form
            ref="record"
            label-width="82px"
            label-position="left"
            :model="record"
            :rules="accessType !== 'view' ? rules : {}">
            <el-col :span="12">
              <el-form-item :label="$t('policies.name')" prop="name">
                <el-input
                  v-model="record.name"
                  :placeholder="disabled ? '' : $t('policies.nameRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('policies.topic')" prop="topic">
                <el-input
                  v-model="record.topic"
                  :placeholder="disabled ? '' : $t('policies.topicRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('policies.accessLabel')" prop="access">
                <emq-select
                  v-model="record.access"
                  :placeholder="$t('oper.select')"
                  :field="{ key: 'access' }"
                  :record="record"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('policies.allowLabel')" prop="allow">
                <emq-select
                  v-model="record.allow"
                  :placeholder="$t('oper.select')"
                  :field="{ key: 'allow' }"
                  :record="record"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'view'" :span="12">
              <el-form-item :label="$t('policies.createUser')" prop="createUser">
                <el-input
                  v-model="record.createUser"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('policies.description')" prop="description">
                <el-input
                  v-model="record.description"
                  :placeholder="accessType !== 'view' ? $t('policies.descriptionRequired') : ''"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <emq-button v-if="!disabled" icon="save" @click="save">
          {{ $t('oper.finish') }}
        </emq-button>
      </el-card>

      <!-- Contains the device -->
      <el-card v-if="accessType !== 'create'" class="device-list">
        <div slot="header">
          <span>{{ $t('policies.includeDevices') }}</span>
          <emq-button
            v-if="has('PUT,/policies/:id')"
            class="create-btn"
            @click="loadDevice(reload=true)">
            {{ $t('policies.addDevices') }}
          </emq-button>
        </div>
        <el-table
          v-loading="loading"
          size="medium"
          :data="deviceData">
          <el-table-column :label="$t('policies.deviceName')" prop="deviceName"></el-table-column>
          <el-table-column :label="$t('policies.deviceType')" prop="deviceTypeLabel"></el-table-column>
          <el-table-column :label="$t('policies.deviceID')" prop="deviceID"></el-table-column>
          <el-table-column v-if="has('PUT,/policies/:id')" width="60px">
            <template v-slot="props">
              <a
                style="float: none"
                href="javascript:;"
                :title="$t('oper.delete')"
                @click="showConfirmDialog(props.row.id)">
                <img src="../../../assets/images/delete.png"/>
              </a>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-if="total>=10"
          background
          layout="sizes, prev, pager, next"
          :current-page.sync="currentPage"
          :page-sizes="[10, 100, 200, 500]"
          :page-size="pageSize"
          :total="total"
          @current-change="currentPageChanged(false)"
          @size-change="currentPageChanged">
        </el-pagination>
      </el-card>

      <!-- Bind the device -->
      <emq-dialog
        width="660px"
        :title="$t('policies.addDevices')"
        :visible.sync="dialogVisible"
        @confirm="addDevice">
        <emq-search-form
          :searchOptions="searchOptions"
          :timeSearch="false"
          :valueOptions="valueOptions"
          :loading="searchLoading"
          @search="remoteSearch">
        </emq-search-form>
        <el-table
          v-loading="selectLoading"
          ref="multipleTable"
          tooltip-effect="dark"
          style="width: 100%"
          :data="deviceList.currentPageList"
          @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column prop="deviceName" :label="$t('policies.deviceName')"></el-table-column>
          <el-table-column prop="productName" :label="$t('policies.productName')"></el-table-column>
          <el-table-column prop="groupName" :label="$t('policies.groupName')"></el-table-column>
        </el-table>
        <el-pagination
          v-if="count>=5"
          background
          layout="total, prev, pager, next"
          :page-size="5"
          :current-page.sync="params._page"
          :total="count"
          @current-change="loadDevice(reload = false)">
        </el-pagination>
      </emq-dialog>

      <!-- Delete Confirm -->
      <emq-dialog
        :title="$t('oper.warning')"
        :visible.sync="confirmDialogVisible"
        @confirm="deleteRecords">
        <span>{{ $t('oper.confirmDelete') }}?</span>
      </emq-dialog>
    </div>
  </div>
</template>


<script>
import { httpGet, httpPost, httpDelete } from '@/utils/api'
import detailsPage from '@/mixins/detailsPage'
import EmqButton from '@/components/EmqButton'
import EmqSelect from '@/components/EmqSelect'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqSearchForm from '@/components/EmqSearchForm'
import EmqDialog from '@/components/EmqDialog'

export default {
  name: 'policies-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqSelect,
    EmqDialog,
    EmqSearchForm,
  },

  data() {
    return {
      url: '/policies',
      loading: false,
      dialogVisible: false,
      selectLoading: false,
      searchLoading: false,
      confirmDialogVisible: false,
      willDeleteId: undefined,
      // Bound devices list page
      params: {
        _page: 1,
        _limit: 5,
      },
      count: 0,
      // Contains the device list page
      currentPage: 1,
      pageSize: 10,
      total: 0,
      deviceData: [], // Contains the device
      deviceList: {
        currentPageList: [], // Current page device
        currentPageActiveList: [], // Device selected on current page
        selectedDevice: {}, // Device selected on current operition
      },
      rules: {
        name: [
          { required: true, message: this.$t('policies.nameRequired') },
        ],
        topic: [
          { required: true, message: this.$t('policies.topicRequired') },
        ],
        access: [
          { required: true, message: this.$t('policies.accessRequired') },
        ],
        allow: [
          { required: true, message: this.$t('policies.allowRequired') },
        ],
      },
      searchOptions: [
        {
          value: 'deviceName',
          label: this.$t('policies.deviceName'),
        },
        {
          value: 'productName',
          label: this.$t('policies.productName'),
        },
        {
          value: 'groupName',
          label: this.$t('policies.groupName'),
        },
        {
          value: 'authType',
          label: this.$t('devices.authType'),
        },
      ],
      valueOptions: {
        authType: this.$store.state.base.dictCode.authType,
      },
    }
  },

  methods: {
    // Load the device that contains the polices
    loadPoliciesDevice() {
      if (this.accessType === 'create') {
        return false
      }
      this.loading = true
      httpGet(`/policies/${this.detailsID}/devices?_page=${this.currentPage}&_limit=${this.pageSize}`)
        .then((response) => {
          this.loading = false
          this.deviceData = response.data.items
          this.total = response.data.meta.count || 0
        }).catch((error) => {
          this.loading = false
          this.$message.error(error.response.data.message)
        })
    },
    // Load and search for optional devices
    loadDevice(reload = false) {
      if (!this.detailsID) {
        return false
      }
      this.selectLoading = true
      this.dialogVisible = true
      // Clear the selected and reset page number
      if (reload) {
        this.$set(this.params, '_page', 1)
        this.deviceList.selectedDevice = {}
      }
      this.deviceList.currentPageActiveList = []
      httpGet(`/emq_select/policies/${this.detailsID}/not_joined_devices`, { params: this.params })
        .then((response) => {
          this.searchLoading = false
          this.selectLoading = false
          this.deviceList.currentPageList = response.data.items
          // highlighted
          this.handleActiveSelection()
          this.count = response.data.meta.count || 0
        }).catch(() => {
          this.searchLoading = false
          this.selectLoading = false
        })
    },
    // Optional device search
    remoteSearch(searchName, searchValue) {
      this.searchLoading = true
      this.params = { _page: 1, _limit: 5 }
      if (!searchValue) {
        this.loadDevice()
      } else {
        const filterKey = typeof searchValue === 'number' ? '' : '_like'
        this.params[`${searchName}${filterKey}`] = searchValue
        this.loadDevice()
      }
    },
    // Add device to policy
    addDevice() {
      const devicesIntID = [...new Set(Object.values(this.deviceList.selectedDevice))]
      if (devicesIntID.length === 0) {
        this.$message.error(this.$t('policies.notNull'))
        return
      }
      httpPost(`/policies/${this.detailsID}/devices`, { devicesIntID })
        .then(() => {
          this.$message.success(this.$t('oper.addSuccess'))
          this.currentPage = 1
          this.loadPoliciesDevice()
          this.dialogVisible = false
        })
    },

    showConfirmDialog(deleteID = undefined) {
      this.willDeleteId = deleteID
      this.confirmDialogVisible = true
    },

    deleteRecords() {
      this.confirmDialogVisible = false
      if (!this.willDeleteId) {
        return
      }
      httpDelete(`/policies/${this.detailsID}/devices?ids=${this.willDeleteId}`)
        .then(() => {
          this.$message.success(this.$t('oper.deleteSuccess'))
          this.loadPoliciesDevice()
        })
        .catch((error) => {
          this.$message.error(error.response.data.message || this.$t('oper.deleteFail'))
        })
    },
    currentPageChanged(pageSize) {
      if (pageSize) {
        this.pageSize = pageSize
      }
      this.loadPoliciesDevice()
    },
    handleSelectionChange(row) {
      const ids = row.map(device => device.id)
      row.forEach((device) => {
        // Add
        this.deviceList.selectedDevice[device.id] = device.id
      })
      this.deviceList.currentPageActiveList.forEach((id) => {
        // Remove
        if (!ids.includes(id)) {
          delete this.deviceList.selectedDevice[id]
        }
      })
    },
    // Highlight and record the selected column of the current page
    handleActiveSelection() {
      setTimeout(() => {
        this.deviceList.currentPageList.forEach((device) => {
          this.deviceList.currentPageActiveList.push(device.id)
          if (this.deviceList.selectedDevice[device.id]) {
            this.$refs.multipleTable.toggleRowSelection(device)
          }
        })
      }, 10)
    },
  },

  created() {
    this.loadPoliciesDevice()
  },
}
</script>


<style lang="scss">
@import '~@/assets/scss/detailsPage.scss';

.policies-details-view {
  .device-list {
    .el-card__body {
      padding-top: 30px;
    }
    .el-pagination {
      margin: 20px auto;
      float: right;
    }
  }
  .emq-dialog {
    .el-select {
      .el-input {
        height: auto;
      }
    }
    p {
      margin: 0 0 10px 0;
    }
    .emq-search-form {
      .el-col.el-col-9 {
        width: 100%;
      }
    }
    .el-table.el-table--fit {
      border: 1px solid var(--color-line-card);
      border-bottom: 0;
    }
    .el-pagination {
      margin: 20px 0 10px 0;
      text-align: right;
    }
  }
}
</style>
