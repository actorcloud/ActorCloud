<template>
  <div class="timer-publish-view">
    <emq-crud
      url="/timer_publish"
      crudTitle="定时下发"
      :tableActions="tableActions"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions">
      <template slot="tableColumns">
        <el-table-column prop="taskName" :label="$t('devices.taskName')">
        </el-table-column>
        <el-table-column prop="taskStatusLabel" label="下发状态">
        </el-table-column>
        <el-table-column min-width="110px" label="下发时间">
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
        <el-table-column prop="publishTypeLabel" label="下发方式">
        </el-table-column>
        <el-table-column label="下发对象">
          <template v-slot="{ row }">
            <router-link v-if="row.deviceIntID" :to="`/devices/devices/${row.deviceIntID}`">
              {{ row.deviceName }}
            </router-link>
            <router-link v-else-if="row.groupIntID" :to="`/devices/groups/${row.groupIntID}`">
              {{ row.groupName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column min-width="80px" prop="timerTypeLabel" :label="$t('devices.intervalType')">
        </el-table-column>
        <el-table-column prop="username" :label="$t('devices.createUser')">
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
        { label: '任务名称', value: 'taskName' },
        { label: '定时类型', value: 'timerType' },
        { label: '下发方式', value: 'publishType' },
      ],
      valueOptions: {
        timerType: this.$store.state.base.dictCode.timerType,
        publishType: this.$store.state.base.dictCode.publishType,
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
        publishTime = `${this.$t('devices.everyHour')} ${timer.intervalTime.minute} ${this.$t('devices.minutes')}`
      }
      return publishTime
    },
  },
}
</script>
