<template>
  <tabs-card-head class="crud-title--in-details" :tabs="tabs">
    <a
      class="custom-tab"
      slot="custom-tab"
      href="javascript:;"
      @click="$router.push({
        path: `/products/${productIntID}`,
        quert: { oper: 'view' },
      })">
      {{ $t('products.viewProductDetail') }}</a>
  </tabs-card-head>
</template>


<script>
import TabsCardHead from '@/components/TabsCardHead'
import { mapActions } from 'vuex'

export default {
  name: 'device-detail-tabs',

  components: { TabsCardHead },

  data() {
    return {
      deviceIntID: this.$route.params.id,
      productIntID: null,
    }
  },

  computed: {
    currentDevices() {
      return this.$store.state.devices.currentDevices
    },
    tabs() {
      const { id } = this.$route.params
      const data = [
        { code: 'deviceInfo', url: `/devices/devices/${id}` },
        { code: 'deviceSecurity', url: `/devices/devices/${id}/security` },
        { code: 'deviceChildren', url: `/devices/devices/${id}/children` },
        { code: 'deviceConnect', url: `/devices/devices/${id}/connect_logs` },
        { code: 'deviceEvent', url: `/devices/devices/${id}/events` },
      ]
      if (this.$store.state.accounts.permissions['/capability_data']) {
        data.push({ code: 'capabilityData', url: `/devices/devices/${id}/capability_data` })
      }
      data.push({ code: 'deviceControl', url: `/devices/devices/${id}/control` })
      return data
    },
  },

  methods: {
    ...mapActions(['STORE_DEVICES']),
  },

  created() {
    const currentDevice = this.currentDevices.find(
      item => item.deviceIntID === parseInt(this.deviceIntID, 10),
    )
    this.productIntID = currentDevice.productIntID
  },

  beforeDestroy() {
    const urls = this.$route.path
    if (!(/\/devices\/[0-9]+/ig.test(urls))) { // Regular match url, clear cache when leaving device detail page
      const currentDevices = this.currentDevices.filter(
        currentDevice => currentDevice.deviceIntID !== parseInt(this.deviceIntID, 10),
      )
      this.STORE_DEVICES({ currentDevices })
    }
  },
}
</script>


<style lang="scss">
.crud-title--in-details {
  .custom-tab {
    float: right;
    font-size: 16px;
  }
}
</style>
