<template>
  <div class="details-view group-details-devices-data-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/groups` }">{{ $t('groups.group') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('groups.groupInfo') }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <div class="detail-tabs">
      <group-detail-tabs></group-detail-tabs>
    </div>

    <device-data-table
      :url="url"
      :record="record">
    </device-data-table>
  </div>
</template>


<script>
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import GroupDetailTabs from '../components/GroupDetailTabs'
import DeviceDataTable from '../components/DeviceDataTable'

export default {
  name: 'group-details-devices-data-view',

  components: {
    EmqDetailsPageHead,
    DeviceDataTable,
    GroupDetailTabs,
  },

  data() {
    return {
      groupIntID: this.$route.params.id,
      url: '',
      record: {},
    }
  },

  created() {
    this.url = `/device_capability_data?groupIntID=${this.groupIntID}`
  },
}
</script>
