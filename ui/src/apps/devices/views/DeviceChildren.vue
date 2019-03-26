<template>
  <div class="device-children-view details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceChildren') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>

    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>
    <div class="custom-btn--wrapper">
      <emq-button
        v-if="has('POST,/devices')"
        float="none"
        @click="$router.push({
          path: '/devices/devices/0/create_device',
          query: {
            upLinkSystem: 3,
            parentDevice: deviceIntID,
            parentDeviceName: currentDevice.deviceName,
            productName: productName,
            productID: currentDevice.productID,
          }
        })">
        + {{ $t('oper.createBtn') }}
      </emq-button>
    </div>
    <device-table
      :autocomplete="autocomplete"
      :isDetails="true"
      :url="`/devices?parentDevice=${deviceIntID}`"
      :tableActions.sync="tableActions">
    </device-table>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqButton from '@/components/EmqButton'
import EmqTag from '@/components/EmqTag'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import DeviceTable from '@/apps/devices/components/DeviceTable'
import DeviceDetailTabs from '../components/DeviceDetailTabs'

export default {
  name: 'device-children-view',

  mixins: [currentDevicesMixin],
  components: {
    EmqButton,
    EmqTag,
    EmqDetailsPageHead,
    DeviceDetailTabs,
    DeviceTable,
  },

  data() {
    return {
      deviceIntID: this.$route.params.id,
      productName: '',
      record: undefined,
      tableActions: ['delete'],
      autocomplete: {
        deviceName: {
          params: {
            gatewayIntID: this.$route.params.id,
          },
        },
        deviceID: {
          params: {
            gatewayIntID: this.$route.params.id,
          },
        },
      },
    }
  },

  created() {
    httpGet(`/devices/${this.deviceIntID}`).then((response) => {
      this.productName = response.data.productName
    })
  },
}
</script>


<style lang="scss">
.device-children-view {
  .custom-btn--wrapper {
    text-align: right;
  }
  .devices-table-view {
    margin-top: 20px;
  }
}
</style>
