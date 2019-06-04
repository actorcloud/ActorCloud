<template>
  <div class="details-view gateway-details-connect-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceConnect') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>

    <!-- Connect logs -->
    <connect-logs
      :url="`/devices/${$route.params.id}/connect_logs`">
    </connect-logs>
  </div>
</template>


<script>
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import GatewayDetailTabs from '../components/GatewayDetailTabs'
import ConnectLogs from '../components/ConnectLogs'

export default {
  name: 'gateway-details-connect-view',

  mixins: [currentDevicesMixin],

  components: {
    GatewayDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    ConnectLogs,
  },

  data() {
    return {
    }
  },

  computed: {
  },

  methods: {
  },
}
</script>
