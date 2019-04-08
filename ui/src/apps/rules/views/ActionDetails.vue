<template>
  <div class="action-details-view details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item to="/business_rules/actions">动作</el-breadcrumb-item>
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
            <el-form-item prop="actionName" label="动作名称">
              <el-input v-model="record.actionName" :placeholder="disabled ? '' : '请输入动作名称'"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="actionType" label="动作类型">
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
          <!-- Station alarm -->
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
              <el-form-item prop="config.title" label="告警标题">
                <el-input v-model="record.config.title" :placeholder="disabled ? '' : '请输入告警标题'"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="config.content" :label="$t('alerts.alertContent')">
                <el-input v-model="record.config.content" :placeholder="disabled ? '' : '请输入告警内容'"></el-input>
              </el-form-item>
            </el-col>
          </div>

          <!-- Mail configuration -->
          <div v-if="record.actionType === $variable.actionType.EMAIL">
            <el-col :span="12">
              <el-form-item prop="config.emails" label="邮箱地址">
                <el-input v-model="record.config.emails" :placeholder="disabled ? '' : '多个地址使用逗号分隔'"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="config.title" label="通知标题">
                <el-input v-model="record.config.title" :placeholder="disabled ? '' : '请输入通知标题'"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="config.content" label="通知内容">
                <el-input v-model="record.config.content" :placeholder="disabled ? '' : '请输入通知内容'"></el-input>
              </el-form-item>
            </el-col>
          </div>

          <!-- webhook -->
          <div v-if="record.actionType === $variable.actionType.WEBHOOK">
            <el-col :span="12">
              <el-form-item prop="config.url" label="URL">
                <el-input v-model="record.config.url" :placeholder="disabled ? '' : '请输入 URL 地址'"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="config.token" label="Token">
                <el-input v-model="record.config.token" :placeholder="disabled ? '' : '请输入 token'"></el-input>
              </el-form-item>
            </el-col>
          </div>

          <!-- Publish instruct -->
          <div v-if="record.actionType === $variable.actionType.COMMAND">
            <el-col :span="12">
              <el-form-item prop="config.publishType" label="下发对象">
                <emq-select
                  v-model.number="record.config.publishType"
                  ref="publishType"
                  :record="record.config"
                  :field="{ options: [ { label: '设备', value: 1 }, { label: '分组', value: 2 } ] }">
                </emq-select>
              </el-form-item>
            </el-col>
            <!-- Select device -->
            <div v-if="record.config.publishType === 1">
              <el-col :span="12">
                <el-form-item prop="config.deviceID" label="下发设备">
                  <emq-search-select
                    ref="devices"
                    v-model="record.config.deviceID"
                    placeholder="请输入设备名称搜索"
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
                <el-form-item label="下发主题">
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
                  <el-form-item prop="config.controlType" label="操作类型">
                    <emq-select
                      v-model="record.config.controlType"
                      :record="record.config"
                      :field="{ options: [
                        { label: '读', value: 2 },
                        { label: '写', value: 3 },
                        { label: '执行', value: 4 }
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
            </div>

            <!-- Group -->
            <el-col v-if="record.config.publishType === 2" :span="12">
              <el-form-item prop="config.groupID" label="下发分组">
                <emq-search-select
                  ref="groups"
                  v-model="record.config.groupID"
                  :record="record.config"
                  :field="{
                    url: '/emq_select/publish/groups',
                    options: [{label: record.config.groupName, value: record.config.groupID}],
                    searchKey: 'groupName',
                  }">
                </emq-search-select>
              </el-form-item>
            </el-col>

            <!-- Not lwm2m: The device needs to fill in the publish content -->
            <el-col v-if="selectedData.cloudProtocol !== $variable.cloudProtocol.LWM2M" :span="12">
              <el-form-item prop="config.payload" label="下发内容">
                <el-input
                  v-model="record.config.payload"
                  type="textarea"
                  :placeholder="disabled ? '' : '请输入下发内容'"
                  @focus="dialogVisible = true">
                </el-input>
              </el-form-item>
            </el-col>
          </div>

          <!-- IFTTT -->
          <div v-if="record.actionType === $variable.actionType.IFTTT">
            <el-col :span="12">
              <el-form-item prop="config.accessKey" label="Access Key">
                <el-input v-model="record.config.accessKey" :placeholder="disabled ? '' : '请输入 Access Key'"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="config.accessToken" label="Access Token">
                <el-input v-model="record.config.accessToken" :placeholder="disabled ? '' : '请输入 Access Token'"></el-input>
              </el-form-item>
            </el-col>
          </div>

          <!-- SMS -->
          <el-col v-if="record.actionType === $variable.actionType.SMS" :span="12">
            <el-form-item prop="config.phoneNumber" label="电话号码">
              <el-input v-model="record.config.phoneNumber" :placeholder="disabled ? '' : '请输入电话号码'"></el-input>
            </el-form-item>
          </el-col>
          <el-col v-if="record.actionType === $variable.actionType.MQTT" :span="12">
            <el-form-item prop="config.topic" label="MQTT 主题">
              <el-input v-model="record.config.topic" :placeholder="disabled ? '' : '请输入 MQTT 主题'"></el-input>
            </el-form-item>
          </el-col>

          <!-- Detail page display -->
          <div v-if="accessType === 'view'">
            <el-col :span="12">
              <el-form-item label="创建人">
                <el-input v-model="record.createUser"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="创建时间">
                <el-input v-model="record.createAt"></el-input>
              </el-form-item>
            </el-col>
          </div>
          <el-col :span="12">
            <el-form-item prop="description" label="描述">
              <el-input v-model="record.description" :plceholder="disabled ? '' : '描述'"></el-input>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>

      <emq-dialog
        title="下发内容"
        width="500px"
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
        完成
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
        return callback(new Error('请输入邮箱地址'))
      }
      const errors = []
      value.split(/[,，]/).forEach((email, index) => {
        if (!email || errors.length > 0) {
          return
        }
        if (!/^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/g.test(email)) {
          errors.push(`第${index + 1}个地址有误`)
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
          { required: true, message: '请输入动作名称' },
        ],
        actionType: [
          { required: true, message: '请选择动作类型' },
        ],
        config: {
          alertSeverity: [
            { required: true, message: '请选择告警等级' },
          ],
          emails: [
            { required: true, message: '请输入邮箱地址' },
            { validator: validateEmail, trigger: ['change', 'blur'] },
          ],
          title: [
            { required: true, message: '请输入标题' },
          ],
          content: [
            { required: true, message: '请输入内容' },
          ],
          url: [
            { required: true, message: '请 URL 地址' },
          ],
          token: [
            { required: true, message: '请输入 Token' },
          ],
          accessKey: [
            { required: true, message: '请输入 AccessKey' },
          ],
          accessToken: [
            { required: true, message: '请输入 Access Token' },
          ],
          phoneNumber: [
            { required: true, message: '请输入电话号码' },
          ],
          // publish instruct
          publishType: { required: true, message: '请选择下发对象' },
          deviceID: { required: true, message: '请选择下发设备' },
          groupID: { required: true, message: '请选择下发分组' },
          controlType: { required: true, message: '请选择操作类型' },
          payload: { required: true, message: '请输入内容' },
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
      if (record.actionType === this.$variable.actionType.COMMAND) {
        setTimeout(() => {
          if (this.$refs.publishType) {
            this.$refs.publishType.loadData()
          }
        }, 10)
      }
    },
    // Control the loading of select options with publish object and alarm level
    handleActionTypeSelected() {
      this.record.config = {}
      if (this.record.actionType === this.$variable.actionType.COMMAND) {
        this.record.config.payload = JSON.stringify({ message: 'Hello' }, null, 2)
        setTimeout(() => {
          if (this.$refs.publishType) {
            this.$refs.publishType.loadData()
          }
        }, 10)
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
          this.$message.error('该设备暂无属性')
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
    changeTarget(record, publishType) {
      if (publishType === 2) { // Group
        delete record.config.deviceID
        delete record.config.deviceIntID
        delete record.config.deviceName
      } else if (publishType === 1) { // Device
        delete record.config.groupID
        delete record.config.groupName
      }
      return record
    },
    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        let record = JSON.parse(JSON.stringify(this.record))
        record = this.changeTarget(record, record.config.publishType)
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
            this.$message.success('动作新建成功!')
            const { fromURL } = this.$route.query
            if (fromURL) {
              this.$router.push({ path: fromURL })
            } else {
              this.$router.push({ path: this.listPageURL })
            }
          })
        } else if (this.accessType === 'edit') {
          httpPut(`${this.url}/${this.detailsID}`, record).then(() => {
            this.$message.success('动作编辑成功!')
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
