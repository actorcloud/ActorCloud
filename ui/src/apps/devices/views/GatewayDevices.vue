<template>
  <div class="gateway-devices-view details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">网关</el-breadcrumb-item>
        <el-breadcrumb-item v-if="record">{{ record.gatewayName }}</el-breadcrumb-item>
        <el-breadcrumb-item>设备列表</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="record" class="emq-tag-group" slot="tag">
        <emq-tag>{{ record.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <emq-button
        v-if="has('POST,/devices')"
        class="custom-button"
        @click="$router.push({
          path: '/devices/devices/0/create_device',
          query: { upLinkSystem: 2, gateway: gatewayIntID, gatewayName: record.gatewayName } })">
        + {{ $t('oper.createBtn') }}
      </emq-button>
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>
    <device-table
      :autocomplete="autocomplete"
      :isDetails="true"
      :url="`/devices?gateway=${gatewayIntID}`"
      :tableActions.sync="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions"
      :searchTimeOptions="searchTimeOptions">
    </device-table>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'

import EmqButton from '@/components/EmqButton'
import EmqTag from '@/components/EmqTag'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import GatewayDetailTabs from '@/apps/devices/components/GatewayDetailTabs'
import DeviceTable from '@/apps/devices/components/DeviceTable'

export default {
  name: 'gateway-devices-view',

  components: {
    EmqButton,
    EmqTag,
    EmqDetailsPageHead,
    GatewayDetailTabs,
    DeviceTable,
  },

  data() {
    return {
      gatewayIntID: this.$route.params.id,
      record: undefined,
      tableActions: ['search', 'delete', 'refresh'],
      searchOptions: [
        {
          value: 'deviceName',
          label: this.$t('devices.deviceName'),
        },
        {
          value: 'deviceID',
          label: this.$t('devices.deviceID'),
        },
        {
          value: 'authType',
          label: this.$t('devices.authType'),
        },
      ],
      valueOptions: { // Select of search value option
        deviceType: this.$store.state.base.dictCode.deviceType,
        authType: this.$store.state.base.dictCode.authType,
      },
      searchTimeOptions: [],
      autocomplete: {
        deviceName: {
          params: {
            gatewayIntID: this.$route.params.id,
          },
        },
        deviceID: {
          params: {
            gatewayIntID: this.$route.params.id,
          },
        },
      },
    }
  },

  created() {
    httpGet(`/gateways/${this.gatewayIntID}`).then((res) => {
      this.record = res.data
    })
  },
}
</script>
