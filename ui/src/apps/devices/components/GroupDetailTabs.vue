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
      const data = [
        { code: 'groupInfo', url: `/devices/groups/${id}` },
        { code: 'proxySubscriptions', url: `/devices/groups/${id}/subscriptions` },
      ]
      if (this.$store.state.accounts.permissions['/metrics']) {
        data.splice(3, 0, { code: 'groupMetricsData', url: `/devices/groups/${id}/metrics_data` })
      }
      return data
    },
  },
}
</script>
