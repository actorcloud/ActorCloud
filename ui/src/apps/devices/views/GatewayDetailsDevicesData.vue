<template>
  <div class="details-view gateway-details-devices-data-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="record">{{ record.gatewayName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('gateways.deviceData') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="record" class="emq-tag-group" slot="tag">
        <emq-tag>{{ record.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>
    <emq-crud
      class="emq-crud--details"
      :url="url"
      :tableActions="tableActions"
      :searchOptions="searchOptions">
      <template slot="tableColumns">
        <el-table-column :label="$t('devices.deviceName')" prop="deviceName">
          <template v-slot="scope">
            <router-link :to="{ path: `/devices/devices/${scope.row.deviceIntID}`, query: { oper: 'view' } }">
              {{ scope.row.deviceName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="dataPointName" :label="$t('products.dataPoints')"></el-table-column>
        <el-table-column prop="value" :label="$t('devices.reportedValue')"></el-table-column>
        <el-table-column prop="msgTime" :label="$t('devices.msgTime')"></el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import EmqCrud from '@/components/EmqCrud'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import GatewayDetailTabs from '../components/GatewayDetailTabs'

export default {
  name: 'gateway-details-devices-data-view',

  components: {
    GatewayDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    EmqCrud,
  },

  data() {
    return {
      gatewayIntID: this.$route.params.id,
      loading: false,
      url: `/gateways/${this.$route.params.id}/devices_data`,
      record: {},
      tableActions: ['search'],
      searchOptions: [
        {
          value: 'deviceName',
          label: this.$t('devices.deviceName'),
        },
      ],
    }
  },

  created() {
    httpGet(`/gateways/${this.gatewayIntID}`).then((res) => {
      this.record = res.data
    })
  },
}
</script>
