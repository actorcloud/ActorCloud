<template>
  <div class="details-view device-details-charts-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceEvent') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>

    <clients-charts
      :url="`/devices/${currentDevice.deviceIntID}/charts`">
    </clients-charts>
  </div>
</template>


<script>
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import DeviceDetailTabs from '../components/DeviceDetailTabs'
import ClientsCharts from '../components/ClientsCharts'

export default {
  name: 'device-details-charts-view',

  mixins: [currentDevicesMixin],

  components: {
    DeviceDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    ClientsCharts,
  },

  data() {
    return {
    }
  },
}
</script>
