<template>
  <tabs-card-head class="crud-title--in-details" :tabs="tabs"></tabs-card-head>
</template>


<script>
import TabsCardHead from '@/components/TabsCardHead'

export default {
  name: 'group-detail-tabs',

  components: { TabsCardHead },

  computed: {
    tabs() {
      const { id } = this.$route.params
      return [
        { code: 'gateway_info', url: `/devices/gateways/${id}` },
        { code: 'gateway_setting', url: `/devices/gateways/${id}/setting` },
        { code: 'devices', url: `/devices/gateways/${id}/devices` },
        { code: 'deviceConnect', url: `/devices/gateways/${id}/connect_logs` },
        { code: 'gateway_event', url: `/devices/gateways/${id}/events` },
        { code: 'gateway_control', url: `/devices/gateways/${id}/control` },
        { code: 'devices_data', url: `/devices/gateways/${id}/devices_data` },
      ]
    },
  },
}
</script>
