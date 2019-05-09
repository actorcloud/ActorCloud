<template>
  <div class="details-view device-details-connect-view">
   <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceConnect') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>

    <!-- Connect logs -->
    <connect-logs
      :url="`/devices/${$route.params.id}/connect_logs?deviceType=1`">
    </connect-logs>
  </div>
</template>


<script>
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import DeviceDetailTabs from '../components/DeviceDetailTabs'
import ConnectLogs from '../components/ConnectLogs'

export default {
  name: 'device-details-connect-view',

  mixins: [currentDevicesMixin],

  components: {
    EmqDetailsPageHead,
    EmqTag,
    DeviceDetailTabs,
    ConnectLogs,
  },

  data() {
    return {
      url: '/devices',
    }
  },

  computed: {
  },

  methods: {
  },
}
</script>
