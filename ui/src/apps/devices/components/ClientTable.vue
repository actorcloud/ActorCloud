<template>
  <!-- It includes devices and gateways -->
  <div class="client-table-view">
    <emq-crud
      v-if="!isEmpty"
      ref="rows"
      selection
      :autocomplete="autocomplete"
      :class="isDetails ? 'emq-crud--details' : ''"
      :url="url"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :searchTimeOptions="searchTimeOptions"
      :valueOptions="valueOptions"
      @selection-change="handleSelectionChange">

      <!-- Custom button -->
      <template v-if="customButtonVisible" slot="customButton">
        <el-dropdown trigger="click" @command="handleCommand">
          <el-button class="operation-btn shadow-btn" size="small" round>
            {{ $t('oper.oper') }}
            <i class="el-icon-arrow-down el-icon--right"></i>
          </el-button>
          <el-dropdown-menu class="device-custom-dropdown" slot="dropdown">
            <el-dropdown-item
              v-if="has('GET,/devices_export')"
              command="export"
              :disabled="$refs.rows.selectedRecords.length !== 0">
              <i class="iconfont icon-emq-export"></i>
              <span>{{ $t('devices.devicesExport') }}</span>
            </el-dropdown-item>
            <el-dropdown-item
              v-if="has('POST,/devices_import')"
              command="import"
              :disabled="$refs.rows.selectedRecords.length !== 0">
              <i class="iconfont icon-emq-import"></i>
              <span>{{ $t('devices.devicesImport') }}</span>
            </el-dropdown-item>
            <el-dropdown-item
              command="deviceLogin"
              :disabled="$refs.rows.selectedRecords.length !== 1">
              <i class="iconfont icon-emq-console"></i>
              <span>{{ $t('devices.devicesLogin') }}</span>
            </el-dropdown-item>
            <el-dropdown-item
              v-if="has('POST,/device_publish')"
              command="deviceControl"
              :disabled="$refs.rows.selectedRecords.length !== 1">
              <i class="iconfont icon-emq-command"></i>
              <span>{{ $t('devices.instruct') }}</span>
            </el-dropdown-item>
            <el-dropdown-item
              v-if="has('POST,/timer_publish')"
              command="deviceTask"
              :disabled="$refs.rows.selectedRecords.length !== 1">
              <i class="iconfont icon-emq-task"></i>
              <span>{{ $t('devices.deviceTask') }}</span>
            </el-dropdown-item>
            <el-dropdown-item
              v-if="has('POST,/groups') && has('PUT,/groups/:id')"
              command="createGroup"
              :disabled="$refs.rows.selectedRecords.length === 0">
              <i class="iconfont icon-emq-group"></i>
              <span>{{ $t('devices.createGroup') }}</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </template>

      <template v-if="!isDetails" slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.accounts.tabs.devices"></tabs-card-head>
      </template>

      <emq-button
        v-if="tableActions.includes('create') && has(`POST,${url}`) && !isDetails"
        slot="createButton"
        class="create-btn"
        @click="createDevice">
        + {{ $t('oper.createBtn') }}
      </emq-button>

      <template slot="tableColumns">
        <el-table-column
          v-if="productType === $variable.productType.GATEWAY"
          min-width="160"
          class="word-limit"
          prop="gatewayName"
          :label="$t('gateways.gatewayName')">
          <template v-slot="scope">
            <a href="javascript:;" @click="showDetails(scope.row, 'view')">
              {{ scope.row.gatewayName }}
            </a>
          </template>
        </el-table-column>
        <el-table-column
          v-else
          min-width="160"
          class="word-limit"
          prop="deviceName"
          :label="$t('devices.deviceName')">
          <template v-slot="scope">
            <a href="javascript:;" @click="showDetails(scope.row, 'view')">
              {{ scope.row.deviceName }}
            </a>
          </template>
        </el-table-column>

        <el-table-column
          min-width="150"
          class="word-limit"
          prop="productName"
          :label="$t('devices.productName')">
        </el-table-column>

        <el-table-column prop="authTypeLabel" :label="$t('devices.authType')">
          <template v-slot="props">
            {{ props.row.authTypeLabel || '-' }}
          </template>
        </el-table-column>

        <el-table-column
          v-if="productType === $variable.productType.GATEWAY"
          prop="gatewayProtocolLabel"
          :label="$t('products.gatewayProtocol')">
        </el-table-column>
        <el-table-column
          v-else
          prop="cloudProtocolLabel"
          :label="$t('products.cloudProtocol')">
        </el-table-column>

        <el-table-column prop="deviceStatusLabel" :label="$t('devices.deviceStatus')">
          <template v-slot="scope">
            <span
              :class="['running-status',
              (scope.row.deviceStatus === 0 || scope.row.deviceStatus === 3)
                ? 'offline' : scope.row.deviceStatus === 1 ? 'online' : 'sleep']">
              {{ scope.row.deviceStatusLabel }}
            </span>
          </template>
        </el-table-column>

        <el-table-column
          v-if="has(`PUT,${url}/:id`)"
          prop="blocked"
          :label="$t('devices.blocked')">
          <template v-slot="scope">
            <el-tooltip
              placement="left"
              :content="scope.row.blocked === 0 ? $t('oper.allow') : $t('oper.reject')">
              <el-switch
                v-model="scope.row.blocked"
                active-color="#13ce66"
                inactive-color="#D0D3E0"
                :active-value="0"
                :inactive-value="1"
                @change="updateClient(scope.row)">
              </el-switch>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column v-else prop="blocked" :label="$t('devices.blocked')">
          <template v-slot="scope">
            {{ scope.row.blocked === 0 ? $t('devices.isTrue') : $t('devices.isFalse') }}
          </template>
        </el-table-column>

        <el-table-column
          v-if="productType === $variable.productType.GATEWAY"
          prop="deviceCount"
          :label="$t('groups.deviceNum')">
          <template v-slot="scope">
            <router-link
              :to="{ path: `/devices/gateways/${scope.row.id}/devices` }">
              {{ scope.row.deviceCount}}
            </router-link>
          </template>
        </el-table-column>

        <el-table-column
          prop="lastConnection"
          min-width="150"
          sortable="custom"
          :label="$t('devices.lastConnection')">
        </el-table-column>
      </template>

      <template v-slot:customOper="props">
        <i
          v-if="has(`PUT,${url}/:id`)"
          class="oper-button iconfont icon-emq-edit"
          @click="showDetails(props.row, 'edit')">
        </i>
      </template>
    </emq-crud>

    <!-- More operations depend on -->
    <emq-export-excel
      v-show="false"
      ref="exportButton"
      :url="url">
    </emq-export-excel>
    <emq-import-excel
      v-if="customButtonVisible"
      ref="importExcelComp"
      :url="url"
      :reloadData="$refs.rows.loadRecords">
    </emq-import-excel>

    <!-- Device control, task Config -->
    <instruction-dialog
      postUrl="/device_publish"
      :visible.sync="instruction.addVisible"
      :instructionType="instruction.instructionType"
      :currentDevice="instruction.device">
    </instruction-dialog>

    <!-- Create group -->
    <emq-dialog
      width="500px"
      :title="$t('devices.createGroup')"
      :visible.sync="groupDialogVisible"
      @confirm="initGroup"
      @close="resetForm">
      <el-form ref="record" :model="record" :rules="groupRules">
        <el-form-item prop="groupName" :label="$t('groups.groupName')">
          <el-input
            v-model="record.groupName"
            :placeholder="$t('groups.groupNameRequired')">
          </el-input>
        </el-form-item>
        <el-form-item prop="description" :label="$t('groups.description')">
          <el-input
            v-model="record.description"
            :placeholder="$t('groups.descriptionRequired')">
          </el-input>
        </el-form-item>
      </el-form>
    </emq-dialog>
  </div>
</template>


<script>
import { mapActions } from 'vuex'
import { httpGet, httpPost, httpPut } from '@/utils/api'
import TabsCardHead from '@/components/TabsCardHead'
import EmqCrud from '@/components/EmqCrud'
import EmqButton from '@/components/EmqButton'
import EmqExportExcel from '@/components/EmqExportExcel'
import EmqImportExcel from '@/components/EmqImportExcel'
import { deviceMixin } from '@/mixins/common'
import EmqDialog from '@/components/EmqDialog'
import InstructionDialog from './InstructionDialog'

export default {
  name: 'client-table-view',

  mixins: [deviceMixin],

  components: {
    TabsCardHead,
    EmqCrud,
    EmqButton,
    EmqExportExcel,
    EmqImportExcel,
    InstructionDialog,
    EmqDialog,
  },

  props: {
    url: {
      required: true,
      type: String,
    },
    isDetails: {
      type: Boolean,
      default: false,
    },
    tableActions: {
      type: Array,
      default: () => [],
    },
    searchTimeOptions: {
      type: Array,
      default: () => [],
    },
    searchOptions: {
      type: Array,
      default: () => [],
    },
    valueOptions: {
      type: Object,
      default: () => {},
    },
    autocomplete: {
      type: Object,
      default: () => ({}),
    },
    productType: {
      type: Number,
      default: 1,
    },
  },

  data() {
    return {
      isEmpty: false,
      customButtonVisible: false,
      groupDialogVisible: false,
      instruction: {
        addVisible: false,
        instructionType: 0, // Control: 0, Timer: 1
        device: {},
      },
      records: [],
      record: {},
      groupRules: {
        groupName: [
          { required: true, message: this.$t('groups.groupNameRequired'), trigger: 'blur' },
        ],
        description: [
          { required: true, message: this.$t('groups.descriptionRequired'), trigger: 'blur' },
        ],
      },
    }
  },

  computed: {
    currentDevices() {
      return this.$store.state.devices.currentDevices
    },
  },

  methods: {
    ...mapActions(['STORE_DEVICES']),

    // Route to the create device page
    createDevice() {
      this.$router.push({
        path: '/devices/devices/0/create_device',
      })
    },

    // Whether the update allows access
    updateClient(row) {
      httpPut(`${this.url}/${row.id}`, row).then(() => {
        this.$message.success(this.$t('users.editSuccess'))
      }).catch((error) => {
        // Failed to restore the original state
        row.blocked = row.blocked ? 0 : 1
        this.$message.error(error.response.data.message)
      })
    },

    // More operations
    handleCommand(command) {
      const records = this.$refs.rows.selectedRecords
      switch (command) {
        case 'export':
          this.$refs.exportButton.exportExcel()
          break
        case 'import':
          this.$refs.importExcelComp.showDialog()
          break
        default:
          // deviceLogin, deviceControl, deviceTask, createGroup
          this[command](records)
          break
      }
    },

    // Load device/gateway details
    showDetails(record, accessType) {
      let type = ''
      if (this.productType === this.$variable.productType.GATEWAY) {
        type = 'gateways'
      } else {
        type = 'devices'
        this.localCache(record)
      }
      this.$router.push({ path: `/devices/${type}/${record.id}`, query: { oper: accessType } })
    },

    deviceLogin(records) {
      httpGet(`${this.url}/${records[0].id}`).then((response) => {
        this.handleDeviceLogin(response.data)
      })
    },

    deviceControl(records, type = 0) {
      const selected = records[0]
      this.instruction.device = {
        deviceIntID: selected.id,
        deviceID: selected.deviceID,
        cloudProtocol: selected.cloudProtocol,
        productIntID: selected.productIntID,
        productID: selected.productID,
      }
      this.instruction.addVisible = true
      this.instruction.instructionType = type
    },

    deviceTask(records) {
      this.deviceControl(records, 1)
    },

    // Device that requires the same product
    createGroup(records) {
      const ids = records.map($ => $.productID)
      if ([...new Set(ids)].length > 1) {
        this.$message.error(this.$t('groups.notCrossProduct'))
        return
      }
      this.records = records
      this.record.productID = records[0].productID
      this.groupDialogVisible = true
    },

    initGroup() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return
        }
        httpPost('/groups', this.record).then((response) => {
          const { id } = response.data
          const ids = this.records.map($ => $.id)
          // Add clients to groups
          httpPost(`/groups/${id}/devices`, { ids }).then(() => {
            this.$message.success(this.$t('oper.createSuccess'))
            this.groupDialogVisible = false
          })
        })
      })
    },

    resetForm() {
      this.$refs.record.resetFields()
    },

    // Toggle the refresh/delete button
    handleSelectionChange(selectedRecords) {
      const tempTableActions = []
      if (selectedRecords.length > 0) {
        this.tableActions.forEach((item) => {
          if (item !== 'refresh') {
            tempTableActions.push(item)
          }
        })
        tempTableActions.push('deleteAll')
        this.$emit('update:tableActions', tempTableActions)
      } else {
        this.tableActions.forEach((item) => {
          if (item !== 'deleteAll') {
            tempTableActions.push(item)
          }
        })
        tempTableActions.push('refresh')
        this.$emit('update:tableActions', tempTableActions)
      }
    },

    // Cache device information locall
    localCache(cache) {
      const currentDevices = this.currentDevices.slice()
      const currentDevice = {
        deviceID: cache.deviceID,
        deviceName: cache.deviceName,
        deviceIntID: cache.id,
        cloudProtocol: cache.cloudProtocol,
        cloudProtocolLabel: cache.cloudProtocolLabel,
        productIntID: cache.productIntID,
        productID: cache.productID,
        token: cache.token,
        deviceUsername: cache.deviceUsername,
        upLinkSystem: cache.upLinkSystem,
      }
      const hasExist = this.currentDevices.find(
        item => item.deviceIntID === cache.id,
      )
      // Cache is added only when it is not in the cache
      if (!hasExist) {
        currentDevices.push(currentDevice)
      }
      this.STORE_DEVICES({ currentDevices })
    },
  },

  mounted() {
    this.customButtonVisible = this.productType === this.$variable.productType.DEVICE
  },
}
</script>


<style lang="scss">
  .client-table-view .emq-crud {
    .el-card .el-table .cell {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
  .device-custom-dropdown {
    width: 120px;
    transform: translateX(-5px) !important;
    .iconfont {
      font-size: 18px;
    }
    .el-dropdown-menu__item {
      color: var(--color-text-lighter);
      &.is-disabled, &.is-disabled:hover {
        color: var(--color-text-default);
        cursor: not-allowed;
      }
    }
  }
  @media screen and (max-width: 1366px) {
    .client-table-view .emq-crud {
      .module-left {
        width: 40%;
      }
      .module-right {
        width: 60%;
      }
    }
  }
</style>
