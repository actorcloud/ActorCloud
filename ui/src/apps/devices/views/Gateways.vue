<template>
  <div class="gateways-view">
    <empty-page v-if="isEmpty" :emptyInfo="deviceEmptyInfo"></empty-page>
    <emq-crud
      v-if="!isEmpty"
      url="/gateways"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions">

      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.base.tabs.devices"></tabs-card-head>
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
        <el-table-column prop="authTypeLabel" label="认证方式">
          <template v-slot="props">
            {{ props.row.authTypeLabel || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="deviceStatusLabel" label="网关状态">
          <template v-slot="scope">
            <span
              :class="['running-status',
              (scope.row.deviceStatus === 0 || scope.row.deviceStatus === 3)
                ? 'offline' : scope.row.deviceStatus === 1 ? 'online' : 'sleep']">
              {{ scope.row.deviceStatusLabel }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="productName" label="所属产品"></el-table-column>
        <el-table-column
          v-if="has('PUT,/devices/gateways/:id')"
          prop="blocked"
          label="允许访问">
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
        <el-table-column v-else prop="blocked" label="允许访问">
          <template v-slot="scope">
            {{ scope.row.blocked === 0 ? '是' : '否' }}
          </template>
        </el-table-column>
        <el-table-column sortable prop="deviceCount" label="设备数量" min-width="110px"></el-table-column>
        <el-table-column sortable prop="createAt" label="创建日期" min-width="150px"></el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import TabsCardHead from '@/components/TabsCardHead'
import EmptyPage from '@/components/EmptyPage'
import EmqCrud from '@/components/EmqCrud'
import { httpPut } from '@/utils/api'

export default {
  name: 'gateways-view',

  components: {
    TabsCardHead,
    EmptyPage,
    EmqCrud,
  },

  data() {
    return {
      isEmpty: false,
      deviceEmptyInfo: {
        buttonText: '新建网关',
        title: '您还没有任何网关',
        subTitle: '',
      },
      tableActions: ['view', 'search', 'create', 'edit', 'delete'],
      searchOptions: [
        {
          value: 'deviceName',
          label: '网关名称',
        },
        {
          value: 'gatewayProtocol',
          label: '网关协议',
        },
        {
          value: 'mac',
          label: '网关MAC',
        },
        {
          value: 'deviceStatus',
          label: '网关状态',
        },
        {
          value: 'tagName',
          label: '标签',
        },
      ],
      valueOptions: {
        gatewayProtocol: this.$store.state.base.dictCode.gatewayProtocol,
        deviceStatus: this.$store.state.base.dictCode.deviceStatus,
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
