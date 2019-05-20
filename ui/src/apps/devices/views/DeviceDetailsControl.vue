<template>
  <div class="details-view device-details-control-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceControl') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>

    <el-row class="radio-header">
      <el-col :span="16">
        <el-radio-group class="search-radio" v-model="instructionType">
          <el-radio-button :label="0">{{ $t('devices.instructRecords') }}</el-radio-button>
          <el-radio-button :label="1">{{ $t('devices.intervalTask') }}</el-radio-button>
        </el-radio-group>
      </el-col>
      <el-col :span="8">
        <emq-button
          icon="create"
          @click="addVisible = true">
          {{ $t('oper.createBtn') }}
        </emq-button>
      </el-col>
    </el-row>

    <!-- Control table -->
    <emq-crud
      v-show="instructionType === 0"
      ref="controlCrud"
      class="emq-crud--details"
      :url="controlUrl"
      :tableActions="[]">
      <template slot="tableColumns">
        <el-table-column
          width="160px"
          prop="publishStatusLabel"
          :label="$t('devices.publishStatusLabel')">
        </el-table-column>
        <el-table-column
          prop="payload"
          min-width="180px"
          :label="$t('devices.publishStatusContent')">
        </el-table-column>

        <el-table-column
          v-if="currentDevice.cloudProtocol !== $variable.cloudProtocol.LWM2M"
          width="140px"
          prop="topic"
          :label="$t('devices.publishTopic')">
        </el-table-column>
        <el-table-column
          v-else
          width="140px"
          prop="topic"
          :label="$t('devices.publishTopic')">
        </el-table-column>

        <el-table-column
          min-width="60px"
          prop="msgTime"
          :label="$t('devices.publishCreateAt')">
        </el-table-column>
      </template>
    </emq-crud>

    <!-- Timer table -->
    <emq-crud
      v-show="instructionType === 1"
      ref="timerCrud"
      class="emq-crud--details"
      :url="timerUrl"
      :autoLoad="false"
      :tableActions="['delete']">
      <template slot="tableColumns">
        <el-table-column prop="taskName" :label="$t('devices.taskName')">
        </el-table-column>
        <el-table-column prop="taskStatusLabel" :label="$t('devices.publishStatusLabel')">
        </el-table-column>
        <el-table-column min-width="110px" :label="$t('devices.publishCreateAt')">
          <template v-slot="{ row }">
            {{ timeFormat(row) }}
          </template>
        </el-table-column>
        <el-table-column
          min-width="260px"
          prop="payload"
          :label="$t('devices.publishStatusContent')">
          <template v-slot="{ row }">
            {{ row.payload }}
          </template>
        </el-table-column>
        <el-table-column
          prop="timerTypeLabel"
          :label="$t('devices.intervalType')">
        </el-table-column>
      </template>
    </emq-crud>

    <!-- Instruction Dialog -->
    <instruction-dialog
      postUrl="/device_publish"
      :visible.sync="addVisible"
      :instructionType="instructionType"
      :currentDevice="currentDevice">
    </instruction-dialog>
  </div>
</template>


<script>
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqCrud from '@/components/EmqCrud'
import EmqTag from '@/components/EmqTag'
import EmqButton from '@/components/EmqButton'
import DeviceDetailTabs from '../components/DeviceDetailTabs'
import InstructionDialog from '../components/InstructionDialog'

export default {
  name: 'device-details-events-view',

  mixins: [currentDevicesMixin],

  components: {
    EmqDetailsPageHead,
    EmqTag,
    DeviceDetailTabs,
    EmqCrud,
    EmqButton,
    InstructionDialog,
  },

  data() {
    return {
      instructionType: 0, // Control: 0, Timer: 1
      addVisible: false,
      weeks: [
        { value: 0, label: this.$t('devices.Monday') },
        { value: 1, label: this.$t('devices.Tuesday') },
        { value: 2, label: this.$t('devices.Wednesday') },
        { value: 3, label: this.$t('devices.Thursday') },
        { value: 4, label: this.$t('devices.Friday') },
        { value: 5, label: this.$t('devices.Saturday') },
        { value: 6, label: this.$t('devices.Sunday') },
      ],
    }
  },

  watch: {
    instructionType(newVal) {
      if (newVal === 0) {
        this.$refs.controlCrud.loadData()
      } else {
        this.$refs.timerCrud.loadData()
      }
    },
    addVisible(newVal) {
      if (!newVal && this.instructionType === 0) {
        this.$refs.controlCrud.loadData()
      } else if (!newVal && this.instructionType === 1) {
        this.$refs.timerCrud.loadData()
      }
    },
  },

  computed: {
    controlUrl() {
      return `/devices/${this.currentDevice.deviceIntID}/publish_logs`
    },
    timerUrl() {
      return `/timer_publish?deviceID=${this.currentDevice.deviceID}`
    },
  },

  methods: {
    // Format time
    timeFormat(timer) {
      if (timer.crontabTime && timer.timerType === 1) {
        return timer.crontabTime
      }
      let publishTime = null
      let weekTitle = null
      let minute = null
      this.weeks.forEach((week) => {
        if (week.value === timer.intervalTime.weekday) {
          weekTitle = week.label
        }
      })
      if (timer.intervalTime.minute || timer.intervalTime.minute === 0) {
        minute = timer.intervalTime.minute <= 9
          ? `0${timer.intervalTime.minute}`
          : timer.intervalTime.minute
      }
      if (weekTitle) {
        publishTime = `${weekTitle} ${timer.intervalTime.hour}:${minute}`
      } else if (timer.intervalTime.hour) {
        publishTime = `${this.$t('devices.everyDay')} ${timer.intervalTime.hour}:${minute}`
      } else {
        publishTime = `${this.$t('devices.everyHour')} ${timer.intervalTime.minute} ${this.$t('devices.minutes')}`
      }
      return publishTime
    },
  },
}
</script>


<style lang="scss">
.device-details-control-view {
  .emq-crud {
    margin-top: 25px;
  }
}
</style>
