<template>
  <div class="details-view product-devices-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/products` }">{{ $t('products.product') }}</el-breadcrumb-item>
        <el-breadcrumb-item>
          <product-breadcrumb
            :currentProduct="currentProduct || {}">
          </product-breadcrumb>
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('products.device') }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>
    <div v-if="currentProduct" class="detail-tabs">
      <emq-button
        v-if="has('POST,/devices')"
        class="custom-button"
        @click="$router.push({
          path: createPath,
          query: {
            productID: currentProduct.productID,
            productIntID: productIntID,
            productName: currentProduct.productName,
            cloudProtocol: currentProduct.cloudProtocol,
            gatewayProtocol: currentProduct.gatewayProtocol,
          }})">
        + {{ $t('oper.createBtn') }}
      </emq-button>
      <product-detail-tabs v-if="currentProduct"></product-detail-tabs>
    </div>
    <client-table
      v-if="currentProduct"
      :autocomplete="autocomplete"
      :isDetails="true"
      :url="getClientsPath"
      :tableActions.sync="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions"
      :productType="currentProduct.productType"
      :deviceType="currentProduct.productType === this.$variable.productType.GATEWAY ? 2 : 1">
    </client-table>
  </div>
</template>


<script>
import EmqButton from '@/components/EmqButton'
import { currentProductsMixin } from '@/mixins/currentProducts'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import ProductDetailTabs from '@/apps/products/components/ProductDetailTabs'
import ClientTable from '@/apps/devices/components/ClientTable'
import ProductBreadcrumb from '../components/ProductBreadcrumb'

export default {
  name: 'product-devices-view',

  mixins: [currentProductsMixin],

  components: {
    EmqButton,
    EmqDetailsPageHead,
    ProductDetailTabs,
    ProductBreadcrumb,
    ClientTable,
  },

  data() {
    return {
      createPath: '/devices/devices/0/create_device',
      getClientsPath: '',
      productIntID: this.$route.params.id,
      tableActions: ['search', 'delete', 'refresh'],
      searchOptions: [ // Search field
        {
          value: 'deviceName',
          label: this.$t('devices.deviceName'),
        },
        {
          value: 'deviceID',
          label: this.$t('devices.deviceID'),
        },
        {
          value: 'authType',
          label: this.$t('devices.authType'),
        },
      ],
      valueOptions: { // Search option
        authType: this.$store.state.accounts.dictCode.authType,
      },
      autocomplete: {
        deviceName: {
          params: {
            productIntID: this.$route.params.id,
          },
        },
        deviceID: {
          params: {
            productIntID: this.$route.params.id,
          },
        },
      },
    }
  },

  methods: {
    setPath(data) {
      if (data.productType === this.$variable.productType.GATEWAY) {
        this.createPath = '/devices/gateways/0/create_gateway'
      }
      this.getClientsPath = `/devices?productID=${data.productID}`
    },
    processProduct(record) {
      this.setPath(record)
    },
  },

  created() {
    if (this.currentProduct) {
      this.setPath(this.currentProduct)
    }
  },
}
</script>
