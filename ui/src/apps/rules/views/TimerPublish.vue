<template>
  <div class="timer-publish-view">
    <emq-crud
      url="/timer_publish"
      :crudTitle="$t('devices.timingPublish')"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions">
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
        <el-table-column prop="payload" min-width="160px" :label="$t('devices.publishStatusContent')">
          <template v-slot="{ row }">
            {{ row.payload }}
          </template>
        </el-table-column>
        <el-table-column prop="topic" :label="$t('devices.publishTopic')">
          <template v-slot="{ row }">
            {{ row.topic || '-' }}
          </template>
        </el-table-column>
        <el-table-column :label="$t('devices.publishType')">
          <template v-slot="{ row }">
            <router-link
              :to="row.deviceType === 1 ? `/devices/devices/${row.deviceIntID}`
                : `/devices/gateways/${row.deviceIntID}`">
              {{ row.deviceName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column min-width="80px" prop="timerTypeLabel" :label="$t('devices.timingType')">
        </el-table-column>
        <el-table-column prop="createUser" :label="$t('devices.createUser')">
        </el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'

export default {
  name: 'timer-publish-view',

  components: {
    EmqCrud,
  },

  data() {
    return {
      tableActions: ['delete', 'create', 'search'],
      searchOptions: [
        { label: this.$t('devices.taskName'), value: 'taskName' },
        { label: this.$t('devices.timingType'), value: 'timerType' },
      ],
      valueOptions: {
        timerType: this.$store.state.accounts.dictCode.timerType,
      },
      weeks: {
        0: this.$t('devices.Monday'),
        1: this.$t('devices.Tuesday'),
        2: this.$t('devices.Wednesday'),
        3: this.$t('devices.Thursday'),
        4: this.$t('devices.Friday'),
        5: this.$t('devices.Saturday'),
        6: this.$t('devices.Sunday'),
      },
    }
  },

  methods: {
    timeFormat(timer) {
      if (timer.crontabTime && timer.timerType === 1) {
        return timer.crontabTime
      }
      let publishTime = null
      let weekTitle = null
      let minute = null
      weekTitle = this.weeks[timer.intervalTime.weekday]
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
        publishTime = `${this.$t('devices.everyHour', { min: timer.intervalTime.minute })}`
      }
      return publishTime
    },
  },
}
</script>
