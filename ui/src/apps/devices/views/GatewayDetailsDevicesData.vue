<template>
  <div class="details-view gateway-details-devices-data-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="record">{{ record.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('gateways.deviceData') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="record" class="emq-tag-group" slot="tag">
        <emq-tag>{{ record.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>

    <div class="detail-tabs">
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>

    <device-data-table
      :url="url"
      :record="record">
    </device-data-table>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import GatewayDetailTabs from '../components/GatewayDetailTabs'
import DeviceDataTable from '../components/DeviceDataTable'

export default {
  name: 'gateway-details-devices-data-view',

  components: {
    GatewayDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    DeviceDataTable,
  },

  data() {
    return {
      gatewayIntID: this.$route.params.id,
      url: '',
      record: {},
    }
  },

  created() {
    this.url = `/device_capability_data?gatewayIntID=${this.gatewayIntID}`
    httpGet(`/devices/${this.gatewayIntID}`).then((res) => {
      this.record = res.data
    })
  },
}
</script>
