<template>
  <div class="details-view device-data-table-view">
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
        <el-table-column prop="dataPointName" :label="$t('products.dataStreams')"></el-table-column>
        <el-table-column prop="value" :label="$t('devices.reportedValue')"></el-table-column>
        <el-table-column prop="msgTime" :label="$t('devices.msgTime')"></el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
// import { httpGet } from '@/utils/api'
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'device-data-table-view',

  props: {
    url: {
      type: String,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
  },

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['search', 'refresh'],
      searchOptions: [
        {
          value: 'deviceName',
          label: this.$t('devices.deviceName'),
        },
      ],
    }
  },
}
</script>
