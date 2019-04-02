<template>
  <div class="timer-publish-details details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item to="/timer_publish">定时下发</el-breadcrumb-item>
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
            <el-form-item prop="taskName" label="任务名称">
              <el-input v-model="record.taskName"></el-input>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item prop="publishType" label="下发对象">
              <emq-select
                v-model.number="record.publishType"
                :record="record"
                :field="{ key: 'publishType' }">
              </emq-select>
            </el-form-item>
          </el-col>

          <el-col v-if="record.publishType" :span="12">
            <el-form-item v-if="record.publishType === 1" prop="deviceID" label="下发设备">
              <emq-search-select
                v-model="record.deviceID"
                ref="devices"
                placeholder="请输入设备名称搜索"
                :record="record"
                :field="{
                  url: '/emq_select/devices',
                  searchKey: 'deviceName',
                }"
                @input="handleDeviceSelected">
              </emq-search-select>
            </el-form-item>

            <el-form-item v-else prop="groupID" label="下发分组">
              <emq-search-select
                v-model="record.groupID"
                ref="groups"
                :record="record"
                :field="{
                  url: '/emq_select/groups',
                  searchKey: 'groupName',
                }"
                @input="handleGroupSelected">
              </emq-search-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item prop="commandType" label="指令类型">
              <emq-select
                v-model.number="record.commandType"
                :record="record"
                :field="{
                  options: [
                    { label: '自定义指令', value: 2 },
                    { label: '升级指令', value: 3 }
                  ],
                  disableOptions: record.publishType === 2 ? [1] : [],
                }">
              </emq-select>
            </el-form-item>
          </el-col>

          <!-- Platform instruction, device only -->
          <!-- Upgrade instruction -->
          <el-col v-if="!disabled && record.commandType === 3" :span="12">
            <el-form-item prop="url" label="软件包">
              <emq-search-select
                v-model="record.url"
                :record="record"
                :field="{
                  url: packageUrl,
                  rely: record.publishType === 1 ? 'deviceIntID' : 'groupIntID',
                  relyName: record.publishType === 1 ? '下发设备' : '下发分组',
                }"
                @input="handleSDKSelect">
              </emq-search-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item prop="timerType" label="下发方式">
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
              <el-form-item label="重复方式">
                <emq-select
                  v-model.number="repeatType"
                  :record="record"
                  :field="{
                    options: [
                      { label: '按小时', value: 0 },
                      { label: '按日', value: 1 },
                      { label: '按周', value: 2 },
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
          <el-col v-if="record.publishType === 1" :span="12">
            <el-form-item prop="topic" label="下发主题">
              <el-input
                v-model="record.topic"
                placeholder="inbox"
                :disabled="deviceCloudProtocol === $variable.cloudProtocol.LWM2M">
              </el-input>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item prop="payload" label="下发内容">
              <el-input v-model="record.payload" type="textarea" row="3" @focus="handlePayloadEdit"></el-input>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>

      <!-- JSON Editor -->
      <emq-dialog
        v-model="record.payload"
        width="500px"
        title="下发内容"
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
        完成
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
        controlType: 1,
        timerType: 1, // Fixed time: 1, Interval time: 2
        publishType: 1, // Device: 1, Group: 2
        taskName: undefined,
        crontabTime: undefined, // Fixed time
        intervalTime: {
          minute: undefined,
          hour: undefined,
          weekday: undefined,
        },
        dateTime: undefined,
        payload: JSON.stringify({ message: 'Hello' }, null, 2),
      },
      formRules: {
        taskName: { required: true, message: '请输入任务名称' },
        publishType: { required: true, message: '请选择下发对象' },
        deviceID: { required: true, message: '请选择下发设备' },
        groupID: { required: true, message: '请选择下发分组' },
        url: { required: true, message: '请选择升级包' },
        payload: { required: true, message: '请输入下发内容' },
        timerType: { required: true, message: this.$t('devices.timerTypeRequired') },
        commandType: { required: true, message: this.$t('devices.repeatTypeRequired') },
        crontabTime: { required: true, message: '请输入下发时间' },
        intervalTime: {
          minute: [
            { required: true, message: '请输入下发时间' },
            { pattern: /^[1-5]?[0-9]$/, message: this.$t('devices.timerRanger'), trigger: 'change' },
          ],
          hour: { required: true, message: '请输入下发时间' },
          weekday: { required: true, message: '请输入下发时间' },
        },
      },
    }
  },

  watch: {
    'record.publishType': 'clearTarget',
    'record.timerType': 'initTimer',
    'record.commandType': 'setPackageUrl',
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
    processLoadedData(record) {
      record.publishType = record.deviceIntID ? 1 : 2
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
      delete record.commandType
      if (record.path) {
        record.topic = ''
      }
    },
    handlePayloadEdit() {
      this.dialogVisible = true
    },
    handleSDKSelect() {
      const url = `${window.location.origin}${this.record.url}`
      this.record.payload = JSON.stringify({ url }, null, 2)
    },
    handleDeviceSelected(deviceIntID, selectedItems) {
      this.record.deviceIntID = selectedItems && selectedItems.attr.deviceIntID
      const { cloudProtocol } = selectedItems.attr
      this.deviceCloudProtocol = cloudProtocol
      this.selectPrompt(cloudProtocol)
      this.setPackageUrl()
    },
    handleGroupSelected(groupIntID, selectedItems) {
      this.record.groupIntID = selectedItems && selectedItems.attr.groupIntID
      this.setPackageUrl()
    },
    setPackageUrl() {
      if (this.record.commandType === 3 && this.record.publishType === 1) {
        this.packageUrl = `/emq_select/sdk_packages?deviceIntID=${this.record.deviceIntID}`
      } else {
        this.packageUrl = `/emq_select/sdk_packages?groupID=${this.record.groupID}`
      }
    },
    clearTarget() {
      if (this.record.publishType === 1) {
        this.record.groupID = undefined
        this.record.groupIntID = undefined
      } else {
        this.record.deviceID = undefined
        this.record.deviceIntID = undefined
      }
    },
    selectPrompt(cloudProtocol) {
      if (cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
        this.record.controlType = 3
        this.record.topic = '/19/1/0'
        this.record.path = '/19/1/0'
      } else if (this.record.controlType === 3 && this.record.path) {
        delete this.record.path
        this.record.controlType = 1
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
