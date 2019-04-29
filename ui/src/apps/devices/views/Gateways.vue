<template>
  <div class="gateways-view">
    <client-table
      url="/gateways"
      :tableActions.sync="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions"
      :searchTimeOptions="searchTimeOptions"
      :productType="2">
    </client-table>
  </div>
</template>


<script>
import ClientTable from '@/apps/devices/components/ClientTable'

export default {
  name: 'gateways-view',

  components: {
    ClientTable,
  },

  data() {
    return {
      tableActions: ['search', 'create', 'delete', 'refresh'],
      searchOptions: [
        {
          value: 'deviceName',
          label: this.$t('gateways.gatewayName'),
        },
        {
          value: 'deviceID',
          label: this.$t('gateways.gatewayID'),
        },
        {
          value: 'productName',
          label: this.$t('devices.productName'),
        },
        {
          value: 'authType',
          label: this.$t('devices.authType'),
        },
        {
          value: 'gatewayProtocol',
          label: this.$t('products.gatewayProtocol'),
        },
        {
          value: 'deviceStatus',
          label: this.$t('gateways.gatewayStatus'),
        },
      ],
      searchTimeOptions: [],
      valueOptions: {
        gatewayProtocol: this.$store.state.accounts.dictCode.gatewayProtocol,
        deviceStatus: this.$store.state.accounts.dictCode.deviceStatus,
        authType: this.$store.state.accounts.dictCode.authType,
      },
    }
  },
}
</script>
