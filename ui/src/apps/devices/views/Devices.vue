<template>
  <div class="devices-view">
    <client-table
      url="/devices"
      :deviceType="1"
      :tableActions.sync="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions"
      :searchTimeOptions="searchTimeOptions">
    </client-table>
  </div>
</template>


<script>
import ClientTable from '@/apps/devices/components/ClientTable'

export default {
  name: 'devices-view',

  components: {
    ClientTable,
  },

  data() {
    return {
      tableActions: ['search', 'create', 'delete', 'refresh'],
      searchOptions: [
        {
          value: 'deviceName',
          label: this.$t('devices.deviceName'),
        },
        {
          value: 'deviceID',
          label: this.$t('devices.deviceID'),
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
          value: 'deviceStatus',
          label: this.$t('devices.deviceStatus'),
        },
        {
          value: 'cloudProtocol',
          label: this.$t('products.cloudProtocol'),
        },
      ],
      searchTimeOptions: [],
      valueOptions: { // Select of search value option
        authType: this.$store.state.accounts.dictCode.authType,
        deviceStatus: this.$store.state.accounts.dictCode.deviceStatus,
        cloudProtocol: this.$store.state.accounts.dictCode.cloudProtocol,
      },
    }
  },
}
</script>
