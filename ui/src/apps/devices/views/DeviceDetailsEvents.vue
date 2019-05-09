<template>
  <div class="details-view device-details-events-view">
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

    <client-event
      :url="`/devices/${currentDevice.deviceIntID}/events?deviceType=1`"
      :currentClient="currentDevice">
    </client-event>
  </div>
</template>


<script>
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import DeviceDetailTabs from '../components/DeviceDetailTabs'
import ClientEvent from '../components/ClientEvent'

export default {
  name: 'device-details-events-view',

  mixins: [currentDevicesMixin],

  components: {
    DeviceDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    ClientEvent,
  },
}
</script>
