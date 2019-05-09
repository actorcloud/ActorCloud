<template>
  <div class="details-view gateway-details-events-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="record">{{ record.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('gateways.gatewayEvent') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="record" class="emq-tag-group" slot="tag">
        <emq-tag>{{ record.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>

    <client-event
      v-if="record"
      :url="`/devices/${record.id}/events?deviceType=2`"
      :currentClient="record">
    </client-event>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import GatewayDetailTabs from '../components/GatewayDetailTabs'
import ClientEvent from '../components/ClientEvent'

export default {
  name: 'gateway-details-events-view',

  components: {
    GatewayDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    ClientEvent,
  },

  data() {
    return {
      record: undefined,
    }
  },

  created() {
    httpGet(`/devices/${this.$route.params.id}?deviceType=2`)
      .then((res) => {
        this.record = res.data
      })
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
