<template>
  <tabs-card-head class="crud-title--in-details" :tabs="tabs"></tabs-card-head>
</template>


<script>
import TabsCardHead from '@/components/TabsCardHead'
import { mapActions } from 'vuex'

export default {
  name: 'product-detail-tabs',

  components: { TabsCardHead },

  data() {
    return {
      productIntID: this.$route.params.id,
    }
  },

  computed: {
    currentProducts() {
      return this.$store.state.products.currentProducts
    },
    tabs() {
      const MQTT = 1
      const LWM2M = 3
      const LoRa = 4
      const Modbus = 7
      const { id } = this.$route.params
      const currentProducts = JSON.parse(localStorage.getItem('currentProducts')) || []
      const currentProduct = currentProducts.find(
        item => item.productIntID === parseInt(id, 10),
      )
      const data = [
        { code: 'product_info', url: `/products/${id}` },
        { code: 'devices', url: `/products/${id}/devices` },
        { code: 'codec', url: `/products/${id}/codec` },
      ]
      if (currentProduct.cloudProtocol === MQTT) {
        data.push({ code: 'proxySubscriptions', url: `/products/${id}/subscriptions` })
      }
      if (currentProduct.cloudProtocol === LWM2M) {
        data.splice(2, 0, { code: 'definition', url: `/products/${id}/definition` })
        data.splice(4, 0, { code: 'items', url: `/products/${id}/items` })
      }
      if (currentProduct.cloudProtocol === LoRa) {
        data.splice(2, 0, { code: 'definition', url: `/products/${id}/definition` })
      }
      if (this.$store.state.base.permissions['/data_points']
        && currentProduct.cloudProtocol !== LWM2M
        && currentProduct.cloudProtocol !== LoRa) {
        data.splice(2, 0, { code: 'data_points', url: `/products/${id}/data_points` })
      }
      if (this.$store.state.base.permissions['/data_streams']
        && currentProduct.cloudProtocol !== LWM2M
        && currentProduct.cloudProtocol !== Modbus
        && currentProduct.cloudProtocol !== LoRa) {
        data.splice(3, 0, { code: 'data_streams', url: `/products/${id}/data_streams` })
      }
      return data
    },
  },

  methods: {
    ...mapActions(['STORE_PRODUCTS']),
  },

  beforeDestroy() {
    const urls = this.$route.path
    // Regular expression matching url, clear cache when leaving the product detail page
    if (!(/\/products\/[0-9]+/ig.test(urls))) {
      const currentProducts = this.currentProducts.filter(
        currentProduct => currentProduct.productIntID !== parseInt(this.productIntID, 10),
      )
      this.STORE_PRODUCTS({ currentProducts })
    }
  },
}
</script>
