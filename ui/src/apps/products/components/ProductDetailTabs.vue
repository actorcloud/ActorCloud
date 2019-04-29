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
      const { id } = this.$route.params
      const data = [
        { code: 'product_info', url: `/products/${id}` },
        { code: 'devices', url: `/products/${id}/devices` },
        { code: 'definition', url: `/products/${id}/definition` },
        { code: 'codec', url: `/products/${id}/codec` },
      ]
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
