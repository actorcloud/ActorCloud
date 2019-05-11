<template>
  <div class="gateway-devices-view details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="record">{{ record.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('gateways.devices') }}</el-breadcrumb-item>
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
          query: { upLinkSystem: 3, gateway: gatewayIntID, gatewayName: record.deviceName } })">
        + {{ $t('oper.createBtn') }}
      </emq-button>
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>
    <client-table
      :autocomplete="autocomplete"
      :isDetails="true"
      :url="`/devices?gateway=${gatewayIntID}`"
      :tableActions.sync="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions"
      :searchTimeOptions="searchTimeOptions">
    </client-table>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'

import EmqButton from '@/components/EmqButton'
import EmqTag from '@/components/EmqTag'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import GatewayDetailTabs from '@/apps/devices/components/GatewayDetailTabs'
import ClientTable from '@/apps/devices/components/ClientTable'

export default {
  name: 'gateway-devices-view',

  components: {
    EmqButton,
    EmqTag,
    EmqDetailsPageHead,
    GatewayDetailTabs,
    ClientTable,
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
        authType: this.$store.state.accounts.dictCode.authType,
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
    httpGet(`/devices/${this.gatewayIntID}?deviceType=2`).then((res) => {
      this.record = res.data
    })
  },
}
</script>
