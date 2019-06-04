<template>
  <div class="details-view gateway-details-events-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('gateways.gatewayEvent') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>

    <client-event
      v-if="currentDevice"
      :url="`/devices/${currentDevice.deviceIntID}`"
      :currentClient="currentDevice">
    </client-event>
  </div>
</template>


<script>
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import GatewayDetailTabs from '../components/GatewayDetailTabs'
import ClientEvent from '../components/ClientEvent'

export default {
  name: 'gateway-details-events-view',

  mixins: [currentDevicesMixin],

  components: {
    GatewayDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    ClientEvent,
  },

  data() {
    return {
    }
  },
}
</script>


<style lang="scss">
.gateway-details-events-view {
  .emq-crud--details {
    .el-card__body {
      padding: 30px;
    }
  }
}
</style>
