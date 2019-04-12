<template>
  <div class="devices-view">
    <device-table
      url="/devices"
      :tableActions.sync="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions"
      :searchTimeOptions="searchTimeOptions">
    </device-table>
  </div>
</template>


<script>
import DeviceTable from '@/apps/devices/components/DeviceTable'

export default {
  name: 'devices-view',

  components: {
    DeviceTable,
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
          value: 'deviceType',
          label: this.$t('devices.deviceType'),
        },
        {
          value: 'deviceStatus',
          label: this.$t('devices.deviceStatus'),
        },
        {
          value: 'tagName',
          label: this.$t('devices.tagName'),
        },
      ],
      searchTimeOptions: [],
      valueOptions: { // Select of search value option
        deviceType: this.$store.state.accounts.dictCode.deviceType,
        authType: this.$store.state.accounts.dictCode.authType,
        deviceStatus: this.$store.state.accounts.dictCode.deviceStatus,
      },
    }
  },
}
</script>
