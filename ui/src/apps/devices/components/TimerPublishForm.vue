<template>
  <el-form
    ref="timerForm"
    class="timer-publish-form-view"
    label-width="80px"
    label-position="left"
    :model="timerForm"
    :rules="timerFormRules">
    <el-form-item prop="timerType" :label="`${$t('devices.timerType')}`">
      <el-radio-group class="publish-type-radio" v-model="timerForm.timerType">
        <el-radio :label="1">{{ $t('devices.constantTimer') }}</el-radio>
        <el-radio :label="2">{{ $t('devices.intervalTimer') }}</el-radio>
      </el-radio-group>
    </el-form-item>
    <el-form-item prop="taskName" :label="$t('devices.taskName')">
      <el-input
        v-model="timerForm.taskName"
        type="text"
        :placeholder="$t('devices.taskNameRequired')">
      </el-input>
    </el-form-item>

    <template v-if="timerForm.timerType === 1">
      <el-form-item prop="crontabTime" :label="$t('devices.publishTime')">
        <el-date-picker
          value-format="yyyy-MM-dd HH:mm:ss"
          v-model="timerForm.crontabTime"
          type="datetime"
          :placeholder="$t('devices.dateTimePlaceholder')"
          :picker-options="pickerOption">
        </el-date-picker>
      </el-form-item>
    </template>

    <template v-if="timerForm.timerType === 2">
      <el-form-item prop="repeatType" :label="`${$t('devices.repeatType')}`">
        <el-radio-group class="publish-type-radio" v-model="timerForm.repeatType">
          <el-radio :label="0">{{ $t('devices.hour') }}</el-radio>
          <el-radio :label="1">{{ $t('devices.day') }}</el-radio>
          <el-radio :label="2">{{ $t('devices.week') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="timerForm.repeatType === 0" prop="minute" :label="$t('devices.publishTime')">
        <el-input
          prefix-icon="el-icon-time"
          v-model="timerForm.minute"
          type="number"
          :placeholder="$t('devices.hourRequired')">
        </el-input>
      </el-form-item>
      <el-form-item v-if="timerForm.repeatType === 1" prop="dateTime" :label="$t('devices.publishTime')">
        <el-time-picker
          v-model="timerForm.dateTime"
          :placeholder="$t('devices.dayRequired')">
        </el-time-picker>
      </el-form-item>
      <template v-if="timerForm.repeatType === 2">
        <el-col :span="13">
          <el-form-item prop="weekday" :label="$t('devices.publishTime')">
            <el-select
              v-model="timerForm.weekday"
              clearable
              :placeholder="$t('devices.weekRequired')">
              <el-option
                v-for="week in weeks"
                :key="week.value"
                :label="week.label"
                :value="week.value">
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col class="line" :span="2"> - </el-col>
        <el-col :span="9">
          <el-form-item prop="dateTime" class="week-datetime">
            <el-time-picker
              v-model="timerForm.dateTime"
              :placeholder="$t('devices.weekTimeRequired')">
            </el-time-picker>
          </el-form-item>
        </el-col>
      </template>
    </template>
  </el-form>
</template>


<script>
export default {
  name: 'timer-publish-form-view',

  data() {
    return {
      weeks: [
        { value: 0, label: this.$t('devices.Monday') },
        { value: 1, label: this.$t('devices.Tuesday') },
        { value: 2, label: this.$t('devices.Wednesday') },
        { value: 3, label: this.$t('devices.Thursday') },
        { value: 4, label: this.$t('devices.Friday') },
        { value: 5, label: this.$t('devices.Saturday') },
        { value: 6, label: this.$t('devices.Sunday') },
      ],
      pickerOption: {
        disabledDate(time) {
          return time.getTime() < Date.now()
        },
      },
      timerForm: {
        taskName: null,
        dateTime: null,
        crontabTime: null, // Interval time
        minute: null, // Interval minute
        hour: null, // Interval hour
        weekday: null, // Interval week
        timerType: 1, // Timer type, Constant Timer: 1, Interval timer：2
        repeatType: 0, // Repeat type hour: 0， day: 1，week: 2
      },
      timerFormRules: {
        timerType: [
          { required: true, message: this.$t('devices.timerTypeRequired') },
        ],
        repeatType: [
          { required: true, message: this.$t('devices.repeatTypeRequired') },
        ],
        crontabTime: [
          { required: true, message: this.$t('devices.publishTimeRequired') },
        ],
        minute: [
          { required: true, message: this.$t('devices.publishTimeRequired') },
          { pattern: /^[1-5]?[0-9]$/, message: this.$t('devices.timerRanger'), trigger: 'change' },
        ],
        dateTime: [
          { type: 'date', required: true, message: this.$t('devices.publishTimeRequired') },
        ],
        weekday: [
          { required: true, message: this.$t('devices.publishTimeRequired') },
        ],
        taskName: [
          { required: true, message: this.$t('devices.taskNameRequired') },
        ],
      },
    }
  },

  methods: {
    initData() {
      this.$refs.timerForm.resetFields()
      this.timerForm = {
        taskName: null,
        dateTime: null,
        crontabTime: null,
        minute: null,
        hour: null,
        weekday: null,
        timerType: 1,
        repeatType: 0,
      }
    },

    // Return Promise, formatted data after async validation
    getTimerDate() {
      const timerValidate = new Promise((reslove) => {
        this.$refs.timerForm.validate((valid) => {
          if (valid) {
            const { timerType, repeatType, taskName, crontabTime } = this.timerForm
            const data = { taskName, timerType }
            if (timerType === 2) {
              data.intervalTime = this.formateDate(repeatType)
            } else {
              data.crontabTime = crontabTime
            }
            reslove(data)
          }
        })
      })
      return timerValidate
    },

    // Date is converted to a string
    formateDate(repeatType) {
      const intervalTime = {}
      if (repeatType === 0) {
        intervalTime.minute = parseInt(this.timerForm.minute.replace(/^0/, ''), 10)
      } else {
        intervalTime.weekday = this.timerForm.weekday
        intervalTime.hour = parseInt(this.timerForm.dateTime.getHours(), 10)
        intervalTime.minute = parseInt(this.timerForm.dateTime.getMinutes(), 10)
      }
      if (intervalTime.weekday === null) {
        delete intervalTime.weekday
      }
      return intervalTime
    },
  },
}
</script>


<style lang="scss">
.timer-publish-form-view {
  margin-top: 10px;
  .el-date-editor {
    width: 100%;
  }
  .line {
    text-align: center;
    position: relative;
    top: 8px;
  }
  .week-datetime {
    .el-form-item__content {
      margin-left: 0px !important;
    }
  }
}
</style>
