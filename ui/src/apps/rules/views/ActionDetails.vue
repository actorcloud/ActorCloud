<template>
  <div class="action-details-view details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item to="/business_rules/actions">
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
          label-position="left"
          label-width="100px"
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
                    url: '/emq_select/publish/devices',
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

            <!-- Lwm2m: Select attribute and controlType -->
            <div v-else>
              <el-col :span="12">
                <el-form-item prop="config.$instanceItems" :label="$t('products.item')">
                  <el-cascader
                    v-model="record.config.$instanceItems"
                    :options="selectedData.instanceItems"
                    @change="handleItemChange" >
                  </el-cascader>
                </el-form-item>
              </el-col>
              <!-- controlType -->
              <el-col :span="12">
                <el-form-item
                  prop="config.controlType"
                  :label="$t('actions.controlType')">
                  <emq-select
                    v-model="record.config.controlType"
                    :record="record.config"
                    :field="{ options: [
                      { label: $t('actions.r'), value: 2 },
                      { label: $t('actions.w'), value: 3 },
                      { label: $t('actions.e'), value: 4 }
                    ]}"
                    :disableOptions="selectedData.disableOptions"
                    :disabled="selectedData.operationDisabled || disabled">
                  </emq-select>
                </el-form-item>
              </el-col>
              <!-- When the operation is write, payload is required, when the operation is execution , payload is optional -->
              <el-col
                v-if="record.config.controlType === this.operationDict.W"
                :span="12">
                <el-form-item prop="config.payload" :label="$t('devices.value')">
                  <el-input v-model="record.config.payload"></el-input>
                </el-form-item>
              </el-col>
              <el-col
                v-if="record.config.controlType === this.operationDict.E"
                :span="12">
                <el-form-item :label="$t('devices.value')">
                  <el-input v-model="record.config.payload"></el-input>
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
                  type="textarea"
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
import { httpGet, httpPost, httpPut } from '@/utils/api'
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
      operationDict: {
        R: 2,
        W: 3,
        E: 4,
      },
      selectedData: {
        instanceItems: [],
        // Operations not supported by the current instance
        disableOptions: [],
        // Disable operation selection
        operationDisabled: false,
      },
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
          controlType: { required: true, message: this.$t('actions.controlTypeRequired') },
          payload: { required: true, message: this.$t('actions.contentRequired') },
          // Lwm2m attribute, non-stored value
          $instanceItems: { required: true, type: 'array', message: this.$t('devices.itemRequired') },
        },
      },
    }
  },

  methods: {
    processLoadedData(record) {
      if (record.config && record.config.emails) {
        record.config.emails = record.config.emails.join(',')
      }
      // Edit, detail loading lwm2m attribute
      const { cloudProtocol } = record.config
      if (record.config.controlType && cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
        this.selectedData.cloudProtocol = cloudProtocol
        record.config.$instanceItems = record.config.path.split('/')
          .slice(1)
          .map($ => parseInt($, 10))
        this.loadInstanceItems(record.config.deviceIntID)
      }
    },
    // Control the loading of select options with publish object and alarm level
    handleActionTypeSelected() {
      this.record.config = {}
      if (this.record.actionType === this.$variable.actionType.COMMAND) {
        this.record.config.payload = JSON.stringify({ message: 'Hello' }, null, 2)
      } else if (this.record.actionType === this.$variable.actionType.ALERT) {
        setTimeout(() => {
          this.$refs.alertSeverity.loadData()
        }, 10)
      }
    },
    handleDeviceSelected(id, selectedItem) {
      if (id && selectedItem && selectedItem.attr) {
        this.selectedData.cloudProtocol = selectedItem.attr.cloudProtocol
        if (selectedItem.attr.cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
          delete this.record.config.payload
          this.record.config.deviceIntID = selectedItem.attr.deviceIntID
          this.loadInstanceItems(selectedItem.attr.deviceIntID)
        } else if (!this.record.config.payload) {
          this.record.config.payload = JSON.stringify({ message: 'Hello' }, null, 2)
        }
      }
    },
    loadInstanceItems(id) {
      httpGet(`/emq_select/lwm2m_items?deviceIntID=${id}`).then((response) => {
        this.selectedData.instanceItems = response.data
        if (response.data.length === 0) {
          this.$message.error(this.$t('actions.itemEmpty'))
        }
      })
    },
    handleItemChange(values) {
      this.record.config.$instanceItems = values
      if (!values) {
        return
      }
      this.record.config.path = `/${values.join('/')}`
      const currentObject = this.selectedData.instanceItems.find(item => item.value === values[0])
      const currentInstance = currentObject.children.find(item => item.value === values[1])
      const currentItem = currentInstance.children.find(item => item.value === values[2])
      if (currentItem.itemOperations === 'RW') {
        this.selectedData.disableOptions = [this.operationDict.E]
        let currentOperation = this.record.config.controlType
        currentOperation = [this.operationDict.R, this.operationDict.W].includes(currentOperation)
          ? currentOperation : this.operationDict.R
        this.$set(this.record.config, 'controlType', currentOperation || this.operationDict.R)
      } else {
        this.selectedData.disableOptions = [this.operationDict.E, this.operationDict.W, this.operationDict.R]
          .filter($ => $ !== this.operationDict[currentItem.itemOperations])
        this.record.config.controlType = this.operationDict[currentItem.itemOperations]
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
          delete record.config.$instanceItems
        } else {
          record.config.controlType = 1
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
