<template>
  <div class="details-view gateway-details-control-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('gateways.gatewayControl') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>
    <gateway-control-table :url="url"></gateway-control-table>
  </div>
</template>


<script>
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import GatewayDetailTabs from '../components/GatewayDetailTabs'
import GatewayControlTable from '../components/GatewayControlTable'

export default {
  name: 'gateway-details-control-view',

  mixins: [currentDevicesMixin],

  components: {
    GatewayDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    GatewayControlTable,
  },

  data() {
    return {
      gatewayIntID: this.$route.params.id,
      loading: false,
      url: `/devices/gateways/${this.$route.params.id}/publish_logs`,
    }
  },
}
</script>
