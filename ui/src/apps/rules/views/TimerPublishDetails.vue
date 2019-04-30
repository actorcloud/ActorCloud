<template>
  <div class="timer-publish-details details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item to="/timer_publish">{{ $t('devices.intervalTask') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <el-card class="message-rules-details-body">
      <el-row :gutter="50" :class="disabled ? 'is-details-form' : ''">
        <el-form
          ref="record"
          label-position="left"
          label-width="120px"
          :disabled="disabled"
          :model="record"
          :rules="disabled ? {} : formRules">
          <el-col :span="12">
            <el-form-item prop="taskName" :label="$t('devices.taskName')">
              <el-input v-model="record.taskName"></el-input>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item
              prop="deviceID"
              :label="$t('publish.device')">
              <emq-search-select
                v-model="record.deviceID"
                ref="devices"
                :placeholder="$t('publish.searchDevice')"
                :record="record"
                :field="{
                  url: '/emq_select/clients',
                  searchKey: 'deviceName',
                }"
                @input="handleDeviceSelected">
              </emq-search-select>
            </el-form-item>
          </el-col>

          <!-- Platform instruction, device only -->
          <el-col :span="12">
            <el-form-item prop="timerType" :label="$t('devices.timerType')">
              <emq-select
                v-model.number="record.timerType"
                :record="record"
                :field="{ key: 'timerType' }">
              </emq-select>
            </el-form-item>
          </el-col>

          <!-- Fixed time -->
          <el-col v-if="record.timerType === 1" :span="12">
            <el-form-item prop="crontabTime" :label="$t('devices.publishTime')">
              <el-date-picker
                value-format="yyyy-MM-dd HH:mm:ss"
                v-model="record.crontabTime"
                type="datetime"
                :placeholder="$t('devices.dateTimePlaceholder')"
                :picker-options="pickerOption">
              </el-date-picker>
            </el-form-item>
          </el-col>

          <!-- Interval time -->
          <div v-if="record.timerType === 2">
            <el-col :span="12">
              <el-form-item :label="$t('devices.repeatType')">
                <emq-select
                  v-model.number="repeatType"
                  :record="record"
                  :field="{
                    options: [
                      { label: $t('devices.hour'), value: 0 },
                      { label: $t('devices.day'), value: 1 },
                      { label: $t('devices.week'), value: 2 },
                    ],
                  }">
                </emq-select>
              </el-form-item>
            </el-col>

            <!-- By hour -->
            <el-col v-if="repeatType === 0" :span="12">
              <el-form-item prop="intervalTime.minute" :label="$t('devices.publishTime')">
                <el-input
                  prefix-icon="el-icon-time"
                  v-model.number="record.intervalTime.minute"
                  type="number"
                  :placeholder="$t('devices.hourRequired')">
                </el-input>
              </el-form-item>
            </el-col>

            <!-- By day -->
            <el-col v-if="repeatType === 1" :span="12">
              <el-form-item prop="dateTime" :label="$t('devices.publishTime')">
                <el-time-picker
                  v-model="record.dateTime"
                  :placeholder="$t('devices.dayRequired')">
                </el-time-picker>
              </el-form-item>
            </el-col>

            <!-- By week -->
            <div v-if="repeatType === 2">
              <el-col :span="6">
                <el-form-item prop="intervalTime.weekday" :label="$t('devices.publishTime')">
                  <emq-select
                    v-model="record.intervalTime.weekday"
                    clearable
                    :placeholder="$t('devices.weekRequired')"
                    :record="record"
                    :field="{ options: weeks }">
                  </emq-select>
                </el-form-item>
              </el-col>

              <el-col class="line" :span="1"> -</el-col>

              <el-col :span="5">
                <el-form-item prop="dateTime" class="week-datetime">
                  <el-time-picker
                    v-model="record.dateTime"
                    :placeholder="$t('devices.weekTimeRequired')">
                  </el-time-picker>
                </el-form-item>
              </el-col>

            </div>
          </div>

          <!-- Publish topic, device only -->
          <el-col :span="12">
            <el-form-item prop="topic" :label="$t('devices.publishTopic')">
              <el-input
                v-model="record.topic"
                placeholder="inbox"
                :disabled="deviceCloudProtocol === $variable.cloudProtocol.LWM2M">
              </el-input>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item prop="payload" :label="$t('devices.publishStatusContent')">
              <el-input
                v-model="record.payload"
                type="textarea"
                row="3"
                @focus="dialogVisible = true">
              </el-input>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>

      <!-- JSON Editor -->
      <emq-dialog
        v-model="record.payload"
        width="500px"
        :title="$t('devices.publishStatusContent')"
        :visible.sync="dialogVisible"
        @confirm="dialogVisible = false"
        @close="dialogVisible = false">
        <code-editor
          lang="application/json"
          theme="lesser-dark"
          v-model="record.payload">
        </code-editor>
      </emq-dialog>

      <emq-button v-if="!disabled" icon="save" @click="save">
        {{ $t('oper.finish') }}
      </emq-button>
    </el-card>
  </div>
</template>


<script>
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import CodeEditor from '@/components/CodeEditor'
import EmqDialog from '@/components/EmqDialog'
import EmqSearchSelect from '@/components/EmqSearchSelect'

export default {
  name: 'timer-publish-details',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    CodeEditor,
    EmqDialog,
    EmqSearchSelect,
  },

  data() {
    return {
      url: '/timer_publish',
      packageUrl: '',
      dialogVisible: false,
      deviceCloudProtocol: 0,
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
      repeatType: 0, // By hour: 0， By day: 1，By week: 2
      record: {
        timerType: 1, // Fixed time: 1, Interval time: 2
        taskName: undefined,
        crontabTime: undefined, // Fixed time
        intervalTime: {
          minute: undefined,
          hour: undefined,
          weekday: undefined,
        },
        dateTime: undefined,
        payload: JSON.stringify({ message: 'Hello' }, null, 2),
        topic: '',
      },
      formRules: {
        taskName: { required: true, message: this.$t('devices.taskNameRequired') },
        deviceID: { required: true, message: this.$t('publish.deviceRequired') },
        payload: { required: true, message: this.$t('devices.payloadRequired') },
        timerType: { required: true, message: this.$t('devices.timerTypeRequired') },
        crontabTime: { required: true, message: this.$t('devices.publishTimeRequired') },
        intervalTime: {
          minute: [
            { required: true, message: this.$t('devices.publishTimeRequired') },
            { pattern: /^[1-5]?[0-9]$/, message: this.$t('devices.timerRanger'), trigger: 'change' },
          ],
          hour: { required: true, message: this.$t('devices.publishTimeRequired') },
          weekday: { required: true, message: this.$t('devices.publishTimeRequired') },
        },
      },
    }
  },

  watch: {
    'record.timerType': 'initTimer',
    repeatType() {
      this.record.intervalTime = {}
    },
  },

  methods: {
    initTimer() {
      if (this.timerType === 1) {
        this.record.dateTime = undefined
        this.record.intervalTime = {}
      } else {
        this.record.crontabTime = undefined
      }
    },

    beforePostData(record) {
      if (this.record.timerType === 1) {
        delete record.intervalTime
      }
      if (this.repeatType) {
        record.intervalTime.hour = parseInt(record.dateTime.getHours(), 10)
        record.intervalTime.minute = parseInt(record.dateTime.getMinutes(), 10)
        delete record.dateTime
      }
    },

    handleDeviceSelected(deviceID, selectedItems) {
      if (!deviceID) {
        return
      }
      const { cloudProtocol } = selectedItems.attr
      this.deviceCloudProtocol = cloudProtocol
      if (cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
        this.record.topic = '/19/1/0'
      } else {
        this.record.topic = ''
      }
    },
  },
}
</script>


<style lang="scss">
.timer-publish-details {
  .line {
    margin-top: 15px;
  }
  .week-datetime {
    .el-form-item__content {
      margin-left: 0px !important;
    }
  }
}
</style>
