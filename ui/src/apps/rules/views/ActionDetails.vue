<template>
  <div class="action-details-view details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item to="/actions">
        {{ $t('actions.action') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <el-card class="action-details-body">
      <edit-toggle-button
        :url="url"
        :disabled="disabled"
        :accessType="accessType"
        @toggleStatus="toggleStatus">
      </edit-toggle-button>
      <el-row :gutter="50" :class="disabled ? 'is-details-form' : ''">
        <el-form
          ref="record"
          :label-width="lang === 'en' ? '120px' : '82px'"
          :label-position="disabled ? 'left' : 'top'"
          :disabled="disabled"
          :model="record"
          :rules="disabled ? {} : rules">
          <el-col :span="12">
            <el-form-item prop="actionName" :label="$t('actions.actionName')">
              <el-input
                v-model="record.actionName"
                :placeholder="disabled ? '' : $t('actions.actionNameRequired')">
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="actionType" :label="$t('actions.actionType')">
              <emq-select
                v-model="record.actionType"
                :field="{ key: 'actionType' }"
                :record="record"
                :placrholder="disabled ? '' : $t('oper.select')"
                :disabled="false"
                @input="handleActionTypeSelected">
              </emq-select>
            </el-form-item>
          </el-col>

          <!-- Displayed according to the action type -->
          <!-- Alert -->
          <div v-if="record.actionType === $variable.actionType.ALERT">
            <el-col :span="12">
              <el-form-item prop="config.alertSeverity" :label="$t('alerts.alertSeverity')">
                <emq-select
                  ref="alertSeverity"
                  v-model.number="record.config.alertSeverity"
                  :field="{ key: 'alertSeverity' }"
                  :record="record"
                  :placrholder="disabled ? '' : $t('oper.select')"
                  :disabled="false">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                prop="config.alertName"
                :label="$t('actions.alertTitle')">
                <el-input
                  v-model="record.config.alertName"
                  :placeholder="disabled ? '' : $t('actions.alertTitleRequired')">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="config.alertContent" :label="$t('alerts.alertContent')">
                <el-input
                  v-model="record.config.alertContent"
                  :placeholder="disabled ? '' : $t('actions.alertContentRequired')">
                </el-input>
              </el-form-item>
            </el-col>
          </div>

          <!-- Mail configuration -->
          <div v-if="record.actionType === $variable.actionType.EMAIL">
            <el-col :span="12">
              <el-form-item
                prop="config.emails"
                :label="$t('actions.email')">
                <el-input
                  v-model="record.config.emails"
                  :placeholder="disabled ? '' : $t('actions.emailTips')">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                prop="config.title"
                :label="$t('actions.noticeTitle')">
                <el-input
                  v-model="record.config.title"
                  :placeholder="disabled ? '' : $t('actions.noticeTitleRequired')">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                prop="config.content"
                :label="$t('actions.noticeContent')">
                <el-input
                  v-model="record.config.content"
                  :placeholder="disabled ? '' : $t('actions.noticeContentRequired')">
                </el-input>
              </el-form-item>
            </el-col>
          </div>

          <!-- webhook -->
          <div v-if="record.actionType === $variable.actionType.WEBHOOK">
            <el-col :span="12">
              <el-form-item prop="config.url" label="URL">
                <el-input
                  v-model="record.config.url"
                  :placeholder="disabled ? '' : $t('actions.urlRequired')">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="config.token" label="Token">
                <el-input
                  v-model="record.config.token"
                  :placeholder="disabled ? '' : $t('actions.tokenRequired')"></el-input>
              </el-form-item>
            </el-col>
          </div>

          <!-- Publish instruct -->
          <div v-if="record.actionType === $variable.actionType.COMMAND">
            <!-- Select device -->
            <el-col :span="12">
              <el-form-item
                prop="config.deviceID"
                :label="$t('actions.publishDevice')">
                <emq-search-select
                  ref="devices"
                  v-model="record.config.deviceID"
                  :placeholder="$t('actions.searchDevice')"
                  :record="record.config"
                  :field="{
                    url: '/emq_select/devices',
                    options: [{label: record.config.deviceName, value: record.config.deviceID}],
                    searchKey: 'deviceName',
                  }"
                  @input="handleDeviceSelected">
                </emq-search-select>
              </el-form-item>
            </el-col>

            <!-- Not lwm2m: Display the topic field-->
            <el-col v-if="selectedData.cloudProtocol !== $variable.cloudProtocol.LWM2M" :span="12">
              <el-form-item :label="$t('actions.topic')">
                <el-input v-model="record.config.topic" placeholder="inbox"></el-input>
              </el-form-item>
            </el-col>

            <!-- Lwm2m: Path is the topic -->
            <div v-else>
              <el-col :span="12">
                <el-form-item prop="config.topic" :label="$t('actions.topic')">
                  <el-input
                    v-model="record.config.topic"
                    :placeholder="$t('publish.pathRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
              <!-- msgType -->
              <el-col :span="12">
                <el-form-item
                  prop="config.msgType"
                  :label="$t('actions.controlType')">
                  <emq-select
                    v-model="record.config.msgType"
                    :record="record.config"
                    :field="{ options: [
                      { label: $t('actions.r'), value: 'read' },
                      { label: $t('actions.w'), value: 'write' },
                      { label: $t('actions.e'), value: 'execute' },
                    ]}"
                    :disableOptions="selectedData.disableOptions"
                    :disabled="selectedData.operationDisabled || disabled">
                  </emq-select>
                </el-form-item>
              </el-col>
              <!-- When the operation is write, payload is required, when the operation is execution , payload is optional -->
              <el-col
                v-if="record.config.msgType === 'write'"
                :span="12">
                <el-form-item prop="config.value" :label="$t('devices.value')">
                  <el-input
                    v-model="record.config.value"
                    :placeholder="$t('devices.valueRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col
                v-if="record.config.msgType === 'execute'"
                :span="12">
                <el-form-item :label="$t('devices.value')">
                  <el-input
                    v-model="record.config.args"
                    :placeholder="$t('devices.valueRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
            </div>

            <!-- Not lwm2m: The device needs to fill in the publish content -->
            <el-col v-if="selectedData.cloudProtocol !== $variable.cloudProtocol.LWM2M" :span="12">
              <el-form-item
                prop="config.payload"
                :label="$t('actions.publishContent')">
                <el-input
                  v-model="record.config.payload"
                  :placeholder="disabled ? '' : $t('actions.publishContentRequired')"
                  @focus="dialogVisible = true">
                </el-input>
              </el-form-item>
            </el-col>
          </div>

          <!-- IFTTT -->
          <div v-if="record.actionType === $variable.actionType.IFTTT">
            <el-col :span="12">
              <el-form-item prop="config.accessKey" label="Access Key">
                <el-input
                  v-model="record.config.accessKey"
                  :placeholder="disabled ? '' : $t('actions.accessKeyRequired')">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="config.accessToken" label="Access Token">
                <el-input
                  v-model="record.config.accessToken"
                  :placeholder="disabled ? '' : $t('actions.accessTokenRequired')">
                </el-input>
              </el-form-item>
            </el-col>
          </div>

          <!-- SMS -->
          <el-col v-if="record.actionType === $variable.actionType.SMS" :span="12">
            <el-form-item
              prop="config.phoneNumber"
              :label="$t('actions.phone')">
              <el-input
                v-model="record.config.phoneNumber"
                :placeholder="disabled ? '' : $t('actions.phoneRequired')">
              </el-input>
            </el-form-item>
          </el-col>
          <el-col v-if="record.actionType === $variable.actionType.MQTT" :span="12">
            <el-form-item
              prop="config.topic"
              :label="$t('actions.mqttTopic')">
              <el-input v-model="record.config.topic" :placeholder="disabled ? '' : $t('actions.mqttTopicRequired')"></el-input>
            </el-form-item>
          </el-col>

          <!-- Detail page display -->
          <div v-if="accessType === 'view'">
            <el-col :span="12">
              <el-form-item :label="$t('actions.createUser')">
                <el-input v-model="record.createUser"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('actions.createAt')">
                <el-input v-model="record.createAt"></el-input>
              </el-form-item>
            </el-col>
          </div>
          <el-col :span="12">
            <el-form-item prop="description" :label="$t('actions.description')">
              <el-input v-model="record.description" :plceholder="disabled ? '' : $t('actions.description')"></el-input>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>

      <emq-dialog
        width="500px"
        :title="$t('actions.publishContent')"
        :visible.sync="dialogVisible"
        @close="dialogVisible = false"
        @confirm="dialogVisible = false">
        <code-editor
          ref="codeEditor"
          lang="application/json"
          theme="lesser-dark"
          v-model="record.config.payload">
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
import { httpPost, httpPut } from '@/utils/api'
import EmqDialog from '@/components/EmqDialog'
import CodeEditor from '@/components/CodeEditor'
import EmqSearchSelect from '@/components/EmqSearchSelect'

export default {
  name: 'action-details-view',

  mixins: [detailsPage],

  components: {
    CodeEditor,
    EmqDialog,
    EmqSearchSelect,
  },

  data() {
    const validateEmail = (rule, value, callback) => {
      if (!value) {
        return callback(new Error(this.$t('actions.emailRequired')))
      }
      const errors = []
      value.split(/[,，]/).forEach((email, index) => {
        if (!email || errors.length > 0) {
          return
        }
        if (!/^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/g.test(email)) {
          errors.push(this.$t('actions.incorrectAddress', { num: `${index + 1}` }))
        }
      })
      if (errors.length > 0) {
        callback(new Error(errors[0]))
      } else {
        callback()
      }
    }
    return {
      url: '/actions',
      dialogVisible: false,
      selectedData: {},
      record: {
        config: {},
      },
      rules: {
        actionName: [
          { required: true, message: this.$t('actions.actionNameRequired') },
        ],
        actionType: [
          { required: true, message: this.$t('actions.actionTypeRequired') },
        ],
        config: {
          alertSeverity: [
            { required: true, message: this.$t('actions.alertSeverityRequired') },
          ],
          emails: [
            { required: true, message: this.$t('actions.emailRequired') },
            { validator: validateEmail, trigger: ['change', 'blur'] },
          ],
          title: [
            { required: true, message: this.$t('actions.titleRequired') },
          ],
          content: [
            { required: true, message: this.$t('actions.contentRequired') },
          ],
          alertName: [
            { required: true, message: this.$t('actions.titleRequired') },
          ],
          alertContent: [
            { required: true, message: this.$t('actions.contentRequired') },
          ],
          url: [
            { required: true, message: this.$t('actions.urlRequired') },
          ],
          token: [
            { required: true, message: this.$t('actions.tokenRequired') },
          ],
          accessKey: [
            { required: true, message: this.$t('actions.accessKeyRequired') },
          ],
          accessToken: [
            { required: true, message: this.$t('actions.accessTokenRequired') },
          ],
          phoneNumber: [
            { required: true, message: this.$t('actions.phoneRequired') },
          ],
          // publish instruct
          deviceID: { required: true, message: this.$t('actions.publishDeviceRequired') },
          msgType: { required: true, message: this.$t('actions.controlTypeRequired') },
          payload: { required: true, message: this.$t('actions.contentRequired') },
          value: { required: true, message: this.$t('devices.valueRequired') },
          topic: { required: true, message: this.$t('publish.pathRequired') },
        },
      },
    }
  },

  methods: {
    processLoadedData(record) {
      if (record.actionType === this.$variable.actionType.EMAIL) {
        record.config.emails = record.config.emails.join(',')
      }
      if (record.actionType === this.$variable.actionType.COMMAND) {
        const { cloudProtocol } = this.record.config
        const payload = JSON.parse(this.record.config.payload)
        this.selectedData.cloudProtocol = cloudProtocol
        if (cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
          const { msgType, value, args } = payload
          this.$set(record.config, 'msgType', msgType)
          this.$set(record.config, 'value', value)
          this.$set(record.config, 'args', args)
          delete record.config.payload
        }
      }
    },

    // Control the loading of select options with publish object and alarm level
    handleActionTypeSelected() {
      this.record.config = {}
      if (this.record.actionType === this.$variable.actionType.COMMAND) {
        this.rules.config.topic.message = this.$t('publish.pathRequired')
        this.record.config.payload = JSON.stringify({ message: 'Hello' }, null, 2)
      } else if (this.record.actionType === this.$variable.actionType.ALERT) {
        setTimeout(() => {
          this.$refs.alertSeverity.loadData()
        }, 10)
      } else if (this.record.actionType === this.$variable.actionType.MQTT) {
        this.rules.config.topic.message = this.$t('actions.mqttTopicRequired')
      }
    },

    handleDeviceSelected(id, selectedItem) {
      if (id && selectedItem && selectedItem.attr) {
        this.selectedData.cloudProtocol = selectedItem.attr.cloudProtocol
        if (selectedItem.attr.cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
          this.record.config.payload = ''
        } else if (!this.record.config.payload) {
          this.record.config.payload = JSON.stringify({ message: 'Hello' }, null, 2)
        }
      }
    },

    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        const record = JSON.parse(JSON.stringify(this.record))
        if (record.config && record.config.emails) {
          // Delete duplicates
          record.config.emails = [...new Set(record.config.emails.split(/[，,]/).filter($ => !!$))]
        }
        if (this.selectedData.cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
          const { msgType, value, args } = this.record.config
          const payload = {
            msgType,
          }
          delete record.config.msgType
          if (msgType === 'write') {
            payload.value = value
            delete record.config.value
          } else if (msgType === 'execute') {
            payload.args = args
            delete record.config.args
          }
          record.config.payload = JSON.stringify(payload)
        }
        if (this.record.actionType === this.$variable.actionType.COMMAND
          && !this.record.config.topic) {
          record.config.topic = 'inbox'
        }
        if (this.accessType === 'create') {
          httpPost(this.url, record).then(() => {
            this.$message.success(this.$t('oper.createSuccess'))
            const { fromURL } = this.$route.query
            if (fromURL) {
              this.$router.push({ path: fromURL })
            } else {
              this.$router.push({ path: this.listPageURL })
            }
          })
        } else if (this.accessType === 'edit') {
          httpPut(`${this.url}/${this.detailsID}`, record).then(() => {
            this.$message.success(this.$t('oper.editSuccess'))
            this.$router.push({ path: this.listPageURL })
          })
        }
      })
    },
  },
}
</script>


<style lang="scss">
  .action-details-view {
    .el-cascader {
      width: 100%;
    }
  }
</style>
