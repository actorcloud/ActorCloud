<template>
  <div class="details-view gateway-details-connect-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="record">{{ record.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceConnect') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="record" class="emq-tag-group" slot="tag">
        <emq-tag>{{ record.gatewayProtocolLabel }}</emq-tag>
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
import { httpGet } from '@/utils/api'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import GatewayDetailTabs from '../components/GatewayDetailTabs'
import ConnectLogs from '../components/ConnectLogs'

export default {
  name: 'gateway-details-connect-view',

  components: {
    GatewayDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    ConnectLogs,
  },

  data() {
    return {
      record: {},
    }
  },

  computed: {
  },

  methods: {
  },

  created() {
    httpGet(`/devices/${this.$route.params.id}?deviceType=2`)
      .then((res) => {
        this.record = res.data
      })
  },
}
</script>
