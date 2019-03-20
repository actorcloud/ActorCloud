import { httpGet } from '@/utils/api'
import { mapActions } from 'vuex'

export const currentProductsMixin = {

  data() {
    return {
      tempProduct: {},
    }
  },

  computed: {
    currentProducts() {
      return this.$store.state.products.currentProducts
    },
    currentProduct: {
      get() {
        const currentProducts = JSON.parse(localStorage.getItem('currentProducts')) || []
        this.tempProduct = currentProducts.find(
          item => item.productIntID === parseInt(this.$route.params.id, 10),
        )
        return this.tempProduct
      },
      set(newVal) {
        this.tempProduct = newVal
      },
    },
  },

  methods: {
    ...mapActions(['STORE_PRODUCTS']),
    loadProduct(id = undefined) {
      const queryID = id || this.$route.params.id
      if (queryID !== 0) {
        httpGet(`/products/${queryID}`).then((res) => {
          this.localCache(res.data)
          this.processProduct(res.data)
        })
      }
    },
    localCache(cache) {
      const currentProducts = this.currentProducts.slice()
      const currentProduct = {
        productName: cache.productName,
        productIntID: cache.id,
        cloudProtocol: cache.cloudProtocol,
        gatewayProtocol: cache.gatewayProtocol,
        productID: cache.productID,
        productType: cache.productType,
      }
      this.currentProduct = currentProduct
      const hasExist = currentProducts.find(
        item => item.productIntID === cache.id,
      )
      if (!hasExist) { // The product is added to the cache only when it is not in the cache
        currentProducts.push(currentProduct)
      }
      this.STORE_PRODUCTS({ currentProducts })
    },
    updateLocalCache(cache) {
      const currentProducts = this.currentProducts.slice()
      let itemIndex = 0
      currentProducts.forEach((item) => {
        if (item.productIntID === parseInt(this.record.id, 10)) { // Sync changes to the local cache
          itemIndex = currentProducts.indexOf(item)
        }
      })
      currentProducts.splice(itemIndex, 1, cache)
      this.STORE_PRODUCTS({ currentProducts })
    },
    // eslint-disable-next-line
    processProduct(record) {},
    handleProductChanged(productIntID) {
      this.loadProduct(productIntID)
    },
  },

  created() {
    // Only is the product details page
    const isProductDetails = this.$route.fullPath.split('/').length === 3
    if (!this.currentProduct && !isProductDetails) {
      this.loadProduct()
    }
  },
}

export default {}
