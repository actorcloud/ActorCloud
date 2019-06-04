<template>
  <tabs-card-head class="crud-title--in-details" :tabs="tabs"></tabs-card-head>
</template>


<script>
import TabsCardHead from '@/components/TabsCardHead'
import { mapActions } from 'vuex'

export default {
  name: 'gateway-detail-tabs',

  components: { TabsCardHead },

  data() {
    return {
      deviceIntID: this.$route.params.id,
    }
  },

  computed: {
    currentDevices() {
      return this.$store.state.devices.currentDevices
    },
    tabs() {
      const { id } = this.$route.params
      const currentDevices = JSON.parse(localStorage.getItem('currentDevices')) || []
      const currentDevice = currentDevices.find(
        item => item.deviceIntID === parseInt(id, 10),
      )
      const data = [
        { code: 'gateway_info', url: `/devices/gateways/${id}` },
        { code: 'devices', url: `/devices/gateways/${id}/devices` },
        { code: 'deviceConnect', url: `/devices/gateways/${id}/connect_logs` },
        { code: 'gateway_event', url: `/devices/gateways/${id}/events` },
        { code: 'devices_data', url: `/devices/gateways/${id}/devices_data` },
      ]
      if (currentDevice.cloudProtocol === this.$variable.cloudProtocol.MODBUS) {
        data.splice(1, 0, { code: 'gateway_setting', url: `/devices/gateways/${id}/setting` })
      }
      return data
    },
  },

  methods: {
    ...mapActions(['STORE_DEVICES']),
  },

  beforeDestroy() {
    const urls = this.$route.path
    if (!(/\/gateways\/[0-9]+/ig.test(urls))) { // Regular match url, clear cache when leaving device detail page
      const currentDevices = this.currentDevices.filter(
        currentDevice => currentDevice.deviceIntID !== parseInt(this.deviceIntID, 10),
      )
      this.STORE_DEVICES({ currentDevices })
    }
  },
}
</script>
