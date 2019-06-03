<template>
  <emq-search-select
    ref="productBreadcrumb"
    class="product-breadcrumb"
    v-model="productID"
    size="small"
    :field="{
      url: '/select_options/products',
      searchKey: 'productName',
    }"
    @input="handleProductSelect">
  </emq-search-select>
</template>


<script>
import { mapActions } from 'vuex'
import EmqSearchSelect from '@/components/EmqSearchSelect'

export default {
  name: 'product-breadcrumb',

  components: {
    EmqSearchSelect,
  },

  props: {
    currentProduct: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      productID: '',
    }
  },

  methods: {
    ...mapActions(['STORE_PRODUCTS']),

    handleProductSelect(id, selectItem) {
      const { productIntID } = selectItem.attr
      const intId = parseInt(this.$route.params.id, 10)
      if (!id || productIntID === intId) {
        return
      }
      this.clearProductCache()
      this.$emit('selectedChange', productIntID)
      this.$router.push({ path: `/products/${productIntID}` })
    },

    // Remove current product after selection
    clearProductCache() {
      const currentProducts = this.$store.state.products.currentProducts.filter(
        $ => $.productIntID !== parseInt(this.$route.params.id, 10),
      )
      this.STORE_PRODUCTS({ currentProducts })
    },

    setProductOptions() {
      if (this.currentProduct) {
        this.productID = this.currentProduct.productID
        this.$refs.productBreadcrumb.options = [
          {
            label: this.currentProduct.productName,
            value: this.currentProduct.productID,
          },
        ]
      }
    },
  },

  mounted() {
    this.setProductOptions()
  },
}
</script>


<style lang="scss">
.emq-search-select.product-breadcrumb {
  width: 88%;
  .el-input .el-input__inner {
    border-radius: 38px;
    font-size: 18px;
  }
}
</style>
