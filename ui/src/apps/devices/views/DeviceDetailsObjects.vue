<template>
  <div class="details-view device-details-objects-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceObjects') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>
    <emq-crud
      ref="crud"
      class="emq-crud--details"
      :url="`/devices/${deviceIntID}/lwm2m_objects`"
      :tableActions="tableActions">
      <template slot="tableColumns">
        <el-table-column :label="$t('devices.objectName')" prop="objectName">
          <template v-slot="scope">
            <router-link
              :to="{
                  path: `/devices/devices/${deviceIntID}/items`,
                  query: { objectID: `${scope.row.objectID}` }
                }">
              {{ scope.row.objectName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column :label="$t('devices.instanceCount')" prop="instanceCount"></el-table-column>
        <el-table-column :label="$t('devices.itemCount')" prop="itemCount"></el-table-column>
        <el-table-column :label="$t('devices.autoSubscibe')" prop="objectAutoSub">
          <template v-slot="scope">
            <el-button
              :loading="scope.row.objectAutoSub === subing || scope.row.objectAutoSub === cancelSubing"
              :class="['sub-button', scope.row.objectAutoSub === subed || scope.row.objectAutoSub === cancelSubing ? 'is-inactive' : 'is-active' ]"
              size="mini"
              @click="autoSubscibe(scope.row)">
              {{ scope.row.objectAutoSub === subed
                ? $t('devices.unsubscribe')
                  : scope.row.objectAutoSub === cancelSubing
                    ? $t('devices.unsubscribing')
                      : scope.row.objectAutoSub === sub
                        ? $t('devices.subscribe') : $t('devices.subscribing')  }}
            </el-button>
          </template>
        </el-table-column>
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
import DeviceDetailTabs from '../components/DeviceDetailTabs'

export default {
  name: 'device-details-objects-view',

  mixins: [currentDevicesMixin],

  components: {
    DeviceDetailTabs,
    EmqDetailsPageHead,
    EmqTag,
    EmqCrud,
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

  computed: {
    deviceIntID() {
      return this.$route.params.id
    },
  },

  methods: {
    autoSubscibe(obj) {
      let msgType = ''
      if (obj.objectAutoSub === this.sub) {
        msgType = 'observe'
      } else if (obj.objectAutoSub === this.subed) {
        msgType = 'cancel-observe'
      }
      const data = {
        objectID: obj.objectID,
        deviceIntID: this.deviceIntID,
        msgType,
      }
      httpPost('/lwm2m/objects/auto_sub', data).then(() => {
        this.$message.success(this.$t('devices.subInstruction'))
        this.$refs.crud.loadData()
      })
    },
  },
}
</script>
