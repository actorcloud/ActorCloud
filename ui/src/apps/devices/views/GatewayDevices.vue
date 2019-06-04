<template>
  <div class="gateway-devices-view details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('gateways.devices') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <emq-button
        v-if="has('POST,/devices')"
        class="custom-button"
        @click="$router.push({
          path: '/devices/devices/0/create_device',
          query: { upLinkSystem: 3, gateway: gatewayIntID, gatewayName: currentDevice.deviceName } })">
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
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqButton from '@/components/EmqButton'
import EmqTag from '@/components/EmqTag'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import GatewayDetailTabs from '@/apps/devices/components/GatewayDetailTabs'
import ClientTable from '@/apps/devices/components/ClientTable'

export default {
  name: 'gateway-devices-view',

  mixins: [currentDevicesMixin],

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
}
</script>
