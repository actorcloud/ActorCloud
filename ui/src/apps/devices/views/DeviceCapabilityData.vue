<template>
  <div class="details-view device-capability-data-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.capabilityData') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>

    <client-capability-data
      :url="`/devices/${currentDevice.deviceIntID}`"
      :currentClient="currentDevice">
    </client-capability-data>
  </div>
</template>


<script>
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import DeviceDetailTabs from '../components/DeviceDetailTabs'
import ClientCapabilityData from '../components/ClientCapabilityData'

export default {
  name: 'device-capability-data-view',

  mixins: [currentDevicesMixin],

  components: {
    EmqDetailsPageHead,
    EmqTag,
    DeviceDetailTabs,
    ClientCapabilityData,
  },
}
</script>
