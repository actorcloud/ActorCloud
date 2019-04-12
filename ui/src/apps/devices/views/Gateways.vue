<template>
  <div class="gateways-view">
    <emq-crud
      url="/gateways"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions">

      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.accounts.tabs.devices"></tabs-card-head>
      </template>

      <template slot="tableColumns">
        <el-table-column :label="$t('gateways.gatewayName')" prop="gatewayName">
          <template v-slot="scope">
            <router-link :to="{ path: `/devices/gateways/${scope.row.id}`, query: { oper: 'view' } }">
              {{ scope.row.gatewayName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="gatewayProtocolLabel" :label="$t('products.gatewayProtocol')"></el-table-column>
        <el-table-column prop="authTypeLabel" :label="$t('devices.authType')">
          <template v-slot="props">
            {{ props.row.authTypeLabel || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="deviceStatusLabel" :label="$t('gateways.gatewayStatus')">
          <template v-slot="scope">
            <span
              :class="['running-status',
              (scope.row.deviceStatus === 0 || scope.row.deviceStatus === 3)
                ? 'offline' : scope.row.deviceStatus === 1 ? 'online' : 'sleep']">
              {{ scope.row.deviceStatusLabel }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="productName" :label="$t('devices.productName')"></el-table-column>
        <el-table-column
          v-if="has('PUT,/devices/gateways/:id')"
          prop="blocked"
          :label="$t('devices.blocked')">
          <template v-slot="scope">
            <el-tooltip placement="left" :content="scope.row.blocked === 0 ? $t('oper.allow') : $t('oper.reject')">
              <el-switch
                v-model="scope.row.blocked"
                active-color="#13ce66"
                inactive-color="#d0d3e0"
                :active-value="0"
                :inactive-value="1"
                @change="updateGateway(scope.row)">
              </el-switch>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column v-else prop="blocked" :label="$t('devices.blocked')">
          <template v-slot="scope">
            {{ scope.row.blocked === 0 ? $t('devices.isTrue') : $t('devices.isFalse') }}
          </template>
        </el-table-column>
        <el-table-column sortable prop="deviceCount" :label="$t('groups.deviceNum')"  min-width="110px"></el-table-column>
        <el-table-column sortable prop="createAt" :label="$t('devices.createAt')" min-width="150px"></el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import TabsCardHead from '@/components/TabsCardHead'
import EmqCrud from '@/components/EmqCrud'
import { httpPut } from '@/utils/api'

export default {
  name: 'gateways-view',

  components: {
    TabsCardHead,
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['view', 'search', 'create', 'edit', 'delete'],
      searchOptions: [
        {
          value: 'deviceName',
          label: this.$t('gateways.gatewayName'),
        },
        {
          value: 'gatewayProtocol',
          label: this.$t('products.gatewayProtocol'),
        },
        {
          value: 'mac',
          label: this.$t('gateways.gatewayMac'),
        },
        {
          value: 'deviceStatus',
          label: this.$t('gateways.gatewayStatus'),
        },
        {
          value: 'tagName',
          label: this.$t('tags.tag'),
        },
      ],
      valueOptions: {
        gatewayProtocol: this.$store.state.accounts.dictCode.gatewayProtocol,
        deviceStatus: this.$store.state.accounts.dictCode.deviceStatus,
      },
    }
  },

  methods: {
    // Whether the update allows access
    updateGateway(row) {
      httpPut(`/devices/gateways/${row.id}`, row).then(() => {
        this.$message.success(this.$t('users.editSuccess'))
      }).catch((error) => {
        // Failed to restore the original state
        row.blocked = row.blocked ? 0 : 1
        this.$message.error(error.response.data.message)
      })
    },
  },
}
</script>
