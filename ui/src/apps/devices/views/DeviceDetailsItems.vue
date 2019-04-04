<template>
  <div class="details-view device-details-objects-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: `/devices/devices/${deviceIntID}/objects` }">{{ $t('resource.deviceObjects') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('devices.devicesItems') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <emq-crud
      ref="crud"
      class="emq-crud--details"
      :url="`/devices/${deviceIntID}/lwm2m_items`"
      :tableActions="tableActions">
      <template slot="tableColumns">
        <el-table-column label="PATH" prop="path"></el-table-column>
        <el-table-column prop="itemName" min-width="180px" :label="$t('devices.itemName')"></el-table-column>
        <el-table-column prop="itemType" :label="$t('devices.itemType')"></el-table-column>
        <el-table-column prop="itemUnit" :label="$t('devices.itemUnit')"></el-table-column>
        <el-table-column prop="itemOperations" :label="$t('devices.itemOperations')"></el-table-column>
        <el-table-column prop="itemAutoSub" :label="$t('devices.autoSubscibe')">
          <template v-slot="scope">
            <el-button
              v-if="scope.row.itemOperations !== 'E'"
              :loading="scope.row.itemAutoSub === subing || scope.row.itemAutoSub === cancelSubing"
              :class="['sub-button', scope.row.itemAutoSub === subed ||scope.row.itemAutoSub === cancelSubing ? 'is-inactive' : 'is-active' ]"
              size="mini"
              @click="autoSubscibe(scope.row)">
              {{
              scope.row.itemAutoSub === subed
                ? $t('devices.unsubscribe')
                : scope.row.itemAutoSub === cancelSubing
                ? $t('devices.unsubscribing')
                : scope.row.itemAutoSub === sub
                ? $t('devices.subscribe') : $t('devices.subscribing')
              }}
            </el-button>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="createAt" :label="$t('devices.createAt')"></el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import { httpPost } from '@/utils/api'
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqCrud from '@/components/EmqCrud'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'

export default {
  name: 'device-details-objects-view',

  mixins: [currentDevicesMixin],

  components: {
    EmqDetailsPageHead,
    EmqTag,
    EmqCrud,
  },

  computed: {
    deviceIntID() {
      return this.$route.params.id
    },
    currentDevice() {
      const currentDevices = JSON.parse(localStorage.getItem('currentDevices'))
      return currentDevices.find(item => item.deviceIntID === parseInt(this.$route.params.id, 10))
    },
  },

  data() {
    return {
      tableActions: [],
      sub: 0, // Not subscribe
      subed: 1, // Have subscribed
      subing: 2, // Subscribeing
      cancelSubing: 3, // Unsubscribing
    }
  },

  watch: {
    dialogVisble() {
      if (!this.dialogVisble && this.itemDialogType === 'write') {
        this.$refs.record.resetFields()
      }
    },
  },

  methods: {
    autoSubscibe(item) {
      let msgType = ''
      if (item.itemAutoSub === this.sub) {
        msgType = 'observe'
      } else if (item.itemAutoSub === this.subed) {
        msgType = 'cancel-observe'
      }
      const data = {
        instanceItemIntID: item.instanceItemIntID,
        msgType,
      }
      httpPost('/lwm2m/items/auto_sub', data).then(() => {
        this.$message.success(this.$t('devices.subInstruction'))
        this.$refs.crud.loadData()
      })
    },
  },
}
</script>
