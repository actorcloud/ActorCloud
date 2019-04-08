<template>
  <div class="details-view device-details-security-view">
   <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceSecurity') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>
    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>

    <div class="devices-card-details-body">
      <!-- code information -->
      <device-details-code></device-details-code>

      <el-row :gutter="20">
        <!-- Bound cert -->
        <el-col :span="8">
          <el-card class="device-security-list" v-loading="certLoading">
            <div slot="header">
              <span>{{ $t('devices.bindCerts') }}</span>
              <a
                v-if="has('PUT,/groups/:id')"
                @click="loadSelectCerts">
                {{ $t('devices.addCert') }}
              </a>
            </div>
            <el-scrollbar>
              <div v-for="(cert, index) in certsData" :key="index" class="security-table">
                <div class="table-row">
                  <el-row>
                    <el-col :span="12">
                      <span>{{ cert.name }}</span>
                    </el-col>
                    <el-col :span="12">
                      <div style="float: right">
                        <a
                          style="float: none"
                          href="javascript:;"
                          @click="downloadFile(cert.id)">
                          <img src="../../../assets/images/list-download.png"/>
                        </a>
                        <a
                          style="float: none"
                          href="javascript:;"
                          :title="$t('oper.delete')"
                          @click="showConfirmDialog(cert.id, 'certs')">
                          <img src="../../../assets/images/list-delete.png"/>
                        </a>
                      </div>
                    </el-col>
                  </el-row>
                </div>
              </div>
            </el-scrollbar>
          </el-card>
        </el-col>

        <!-- Bound policy -->
        <el-col :span="8">
          <el-card class="device-security-list" v-loading="policyLoading">
            <div slot="header">
              <span>{{ $t('devices.bindPolicies') }}</span>
              <a
                v-if="has('PUT,/groups/:id')"
                @click="loadSelectPolicies">
                {{ $t('devices.addPolicie') }}
              </a>
            </div>
            <el-scrollbar>
              <div v-for="(policy, index) in policiesData" :key="index" class="security-table">
                <div class="table-row">
                  <el-row>
                    <el-col :span="12">
                      <span>{{ policy.name }}</span>
                    </el-col>
                    <el-col :span="12">
                      <div style="float: right">
                        <a
                          style="float: none"
                          href="javascript:;"
                          @click="viewPolicy(policy.id)">
                          <img src="../../../assets/images/list-view.png"/>
                        </a>
                        <a
                          style="float: none"
                          href="javascript:;"
                          :title="$t('oper.delete')"
                          @click="showConfirmDialog(policy.id, 'policies')">
                          <img src="../../../assets/images/list-delete.png"/>
                        </a>
                      </div>
                    </el-col>
                  </el-row>
                </div>
              </div>
            </el-scrollbar>
          </el-card>
        </el-col>

        <!-- Proxy subscription -->
        <el-col :span="8">
          <el-card class="device-security-list" v-loading="certLoading">
             <div slot="header" class="clearfix">
              <span>{{ $t('devices.proxy') }}</span>
              <el-popover
                placement="left"
                width="450"
                trigger="hover">
                <p>
                  {{ $t('devices.proxyInfo1') }}
                  <span style="color: #ff7956;">{{ $t('devices.proxyInfoWarning') }}</span>
                </p>
                <p>
                  {{ $t('devices.proxyInfo2') }}
                  {{ $t('devices.proxyInfo3') }}
                </p>
                <p>
                  {{ $t('devices.proxyInfo4') }}
                </p>
                <i slot="reference" class="el-icon-question"></i>
              </el-popover>
              <a
                v-if="tenantType"
                icon="create"
                @click="topicDialogVisible = true">
                {{ $t('devices.addSubscibe') }}
              </a>
            </div>
            <el-scrollbar>
              <div v-for="(subscription, index) in subscriptions" :key="index" class="security-table">
                <div class="table-row">
                  <el-row>
                    <el-col :span="8">
                      <span>{{ subscription.topic }}</span>
                    </el-col>
                    <el-col :span="8">
                      <span style="margin:2px 0 0 35%;color:#B7B7B7">QoS {{ subscription.qos }}</span>
                    </el-col>
                    <el-col :span="8">
                      <div style="float: right">
                      <a
                        style="float: none"
                        href="javascript:;"
                        :title="$t('oper.delete')"
                        @click="showConfirmDialog(subscription.id, 'topic')">
                        <img src="../../../assets/images/list-delete.png"/>
                      </a>
                    </div>
                    </el-col>
                  </el-row>
                </div>
              </div>
            </el-scrollbar>
          </el-card>
        </el-col>
      </el-row>

      <!-- Cert -->
      <emq-dialog
        :title="certsDialogType === 'add' ? $t('devices.addCert') : $t('devices.createCert')"
        :visible.sync="certsDialogVisible"
        @confirm="certsDialogType === 'add' ? addCerts() : createCert()">
        <!-- Add cert -->
        <div v-show="certsDialogType === 'add'">
          <p>
            {{ $t('devices.certInfo') }}，{{ $t('devices.or') }}
            <a href="javascript:;" @click="certsDialogType = 'create'">
              {{ $t('devices.createCert') }}
            </a>
          </p>
          <emq-search-select
            multiple
            v-model="selectedCerts"
            :field="{
              url: `/emq_select/devices/${this.detailsID}/not_joined_certs`,
              searchKey: 'name',
            }"
            :placeholder="$t('oper.select')">
          </emq-search-select>
        </div>
        <!-- Create cert -->
        <div v-show="certsDialogType === 'create'" class="create-cert">
          <el-form
            ref="cert"
            label-position="top"
            :model="cert"
            :rules="formRules">
            <a
              href="javascript:;"
              class="el-icon-back"
              style="float: right; margin-top: -60px;"
              @click="certsDialogType = 'add'">
              {{ $t('devices.addCert') }}
            </a>
            <el-col :span="12">
              <el-form-item :label="$t('certs.name')" prop="name">
                <el-input v-model="cert.name" :placeholder="$t('certs.nameRequired')"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('certs.enable')" prop="enable">
                <emq-select
                  v-model="cert.enable"
                  :field="{ key: 'certEnable'}"
                  :cert="cert"
                  :placeholder="$t('oper.select')"
                  :disabled="false">
                </emq-select>
              </el-form-item>
            </el-col>
          </el-form>
        </div>
      </emq-dialog>

      <!-- Add policy -->
      <emq-dialog
        :title="$t('devices.addPolicie')"
        :visible.sync="policiesDialogVisible"
        @confirm="addPolicies">
        <p>
          {{ $t('devices.policieInfo') }}，{{ $t('devices.or') }}
          <router-link to="/security/policies/0?oper=create">
            {{ $t('devices.createPolicie') }}
          </router-link>
        </p>
        <emq-search-select
          multiple
          v-model="selectedPolicies"
          :field="{
            url: `/emq_select/devices/${this.detailsID}/not_joined_policies`,
            searchKey: 'name',
          }"
          :placeholder="$t('oper.select')">
        </emq-search-select>
      </emq-dialog>

      <!-- Policy details -->
      <emq-dialog
        :visible.sync="policiesViewDialogVisible"
        :title="$t('devices.policy')"
        @confirm="policiesViewDialogVisible = false">
        <div v-loading="policyDetailsLoading">
          <el-row class="policy-view">
            <el-col :span="5">
              <span>{{ $t('policies.name') }}：</span>
            </el-col>
            <el-col :span="11" :offset="3">
              <span class="policy-view-content">{{ policy.name }}</span>
            </el-col>
          </el-row>
          <el-row class="policy-view">
            <el-col :span="5">
              <span>{{ $t('policies.topic') }}：</span>
            </el-col>
            <el-col :span="11" :offset="3">
              <span class="policy-view-content">{{ policy.topic }}</span>
            </el-col>
          </el-row>
          <el-row class="policy-view">
            <el-col :span="5">
              <span>{{ $t('policies.accessLabel') }}：</span>
            </el-col>
            <el-col :span="11" :offset="3">
              <span class="policy-view-content">{{ policy.accessLabel }}</span>
            </el-col>
          </el-row>
          <el-row class="policy-view">
            <el-col :span="5">
              <span>{{ $t('policies.allowLabel') }}：</span>
            </el-col>
            <el-col :span="11" :offset="3">
              <span class="policy-view-content">{{ policy.allowLabel }}</span>
            </el-col>
          </el-row>
          <el-row class="policy-view">
            <el-col :span="5">
              <span>{{ $t('policies.createUser') }}：</span>
            </el-col>
            <el-col :span="11" :offset="3">
              <span class="policy-view-content">{{ policy.createUser }}</span>
            </el-col>
          </el-row>
          <el-row class="policy-view">
            <el-col :span="5">
              <span>{{ $t('policies.description') }}：</span>
            </el-col>
            <el-col :span="11" :offset="3">
              <span class="policy-view-content">{{ policy.description }}</span>
            </el-col>
          </el-row>
        </div>
      </emq-dialog>

      <!-- Add topic subscriptions -->
      <emq-dialog
        class="add-topic-dialog"
        :title="$t('devices.addTopic')"
        :visible.sync="topicDialogVisible"
        @confirm="addTopic">
        <el-form
          ref="topic"
          :model="topicForm"
          :rules="topicRules">
          <el-form-item :label="$t('devices.topic')" prop="topic">
            <el-input v-model="topicForm.topic" :placeholder="$t('devices.topicRequired')"></el-input>
          </el-form-item>
        </el-form>
      </emq-dialog>

      <!-- Delete Confirm -->
      <emq-dialog
        :title="$t('oper.warning')"
        :visible.sync="dialogVisible"
        @confirm="deleteRecords">
        <span>{{ $t('oper.confirmDelete') }}?</span>
      </emq-dialog>
    </div>
  </div>
</template>


<script>
import JSzip from 'jszip'
import { httpGet, httpPost, httpDelete } from '@/utils/api'
import { currentDevicesMixin } from '@/mixins/currentDevices'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import EmqDialog from '@/components/EmqDialog'
import EmqSearchSelect from '@/components/EmqSearchSelect'
import DeviceDetailTabs from '../components/DeviceDetailTabs'
import DeviceDetailsCode from '../components/DeviceDetailsCode'

export default {
  name: 'device-details-security-view',

  mixins: [currentDevicesMixin],

  components: {
    EmqDetailsPageHead,
    EmqTag,
    EmqDialog,
    EmqSearchSelect,
    DeviceDetailTabs,
    DeviceDetailsCode,
  },

  data() {
    return {
      url: '/devices',
      certLoading: false,
      policyLoading: false,
      topicLoading: false,
      policyDetailsLoading: false,
      dialogVisible: false,
      policiesDialogVisible: false,
      policiesViewDialogVisible: false,
      certsDialogVisible: false,
      certsDialogType: 'add',
      topicDialogVisible: false,
      confirmCertsVisible: false,
      confirmPoliciesVisible: false,
      confirmTopicVisible: false,
      willDeleteId: undefined,
      policiesTotal: 0,
      certsTotal: 0,
      pageSize: 100,
      timer: 0,
      policy: {}, // Policy details
      policiesData: [], // Contain the policies
      selectedPolicies: [], // Selected policies
      cert: {},
      certsData: [], // Contain the cert
      selectedCerts: [], // Selected cert
      subscriptions: [], // Proxy subscription
      topicForm: {},
      topicRules: {
        topic: [
          { required: true, message: this.$t('devices.topicRequired') },
        ],
      },
      formRules: {
        name: [
          { required: true, message: this.$t('certs.nameRequired') },
        ],
        enable: [
          { required: true, message: this.$t('certs.enableRequired') },
        ],
      },
    }
  },

  computed: {
    detailsID() {
      return this.$route.params.id
    },
    tenantType() {
      return this.$store.state.accounts.user.tenantType
    },
  },

  methods: {
    // Load the added policy
    loadPolicies() {
      if (!this.detailsID) {
        return false
      }
      this.policyLoading = true
      httpGet(`${this.url}/${this.detailsID}/policies?_page=1&_limit=${this.pageSize}`)
        .then((response) => {
          this.policiesData = response.data.items
          this.policiesTotal = response.data.meta.count
          this.policyLoading = false
        }).catch((error) => {
          this.policyLoading = false
          this.$message.error(error.response.data.message)
        })
    },
    // Load the added cert
    loadCerts() {
      if (!this.detailsID) {
        return false
      }
      this.certLoading = true
      httpGet(`${this.url}/${this.detailsID}/certs?_page=1&_limit=${this.pageSize}`)
        .then((response) => {
          this.certsData = response.data.items
          this.certsTotal = response.data.meta.count
          this.certLoading = false
        }).catch((error) => {
          this.certLoading = false
          this.$message.error(error.response.data.message)
        })
    },
    // Load the optional policy
    loadSelectPolicies() {
      if (!this.detailsID) {
        return false
      }
      this.policiesDialogVisible = true
    },
    // Load the optional cert
    loadSelectCerts() {
      if (!this.detailsID) {
        return false
      }
      this.certsDialogVisible = true
    },
    // Load proxy subscription
    loadTopics() {
      this.topicLoading = true
      httpGet(`${this.url}/${this.detailsID}/subscriptions`).then((response) => {
        this.subscriptions = response.data.items
        this.topicLoading = false
      })
    },
    // Add the policy to the device
    addPolicies() {
      if (this.selectedPolicies.length === 0) {
        this.$message.error(this.$t('devices.policieNotNull'))
        return
      }
      httpPost(`${this.url}/${this.detailsID}/policies`, { ids: this.selectedPolicies })
        .then(() => {
          this.$message.success(this.$t('oper.addSuccess'))
          this.loadPolicies()
          this.selectedPolicies = []
          this.policiesDialogVisible = false
        })
    },
    // Add the cert to the device
    addCerts() {
      if (this.selectedCerts.length === 0) {
        this.$message.error(this.$t('devices.certNotNull'))
        return
      }
      httpPost(`${this.url}/${this.detailsID}/certs`, { ids: this.selectedCerts })
        .then(() => {
          this.$message.success(this.$t('oper.addSuccess'))
          this.loadCerts()
          this.selectedCerts = []
          this.certsDialogVisible = false
        })
    },
    // Create cert
    createCert() {
      this.$refs.cert.validate((valid) => {
        if (!valid) {
          return false
        }
        httpPost('/certs', this.cert).then(() => {
          this.$message.success(this.$t('certs.isCreated'))
          this.certsDialogType = 'add'
        })
      })
    },
    // Add proxy subscriptions
    addTopic() {
      this.$refs.topic.validate((valid) => {
        if (!valid) {
          return false
        }
        httpPost(`${this.url}/${this.detailsID}/subscriptions`, this.topicForm).then((response) => {
          if (response.status === 201) {
            this.topicDialogVisible = false
            this.$message.success(this.$t('devices.addTopicSuccess'))
            this.loadTopics()
            this.topicForm = {}
            this.$refs.topic.resetFields()
          }
        })
      })
    },

    showConfirmDialog(deleteID = undefined, name) {
      this.dialogVisible = true
      this.willDeleteId = deleteID
      if (name === 'policies') {
        this.confirmPoliciesVisible = true
      } else if (name === 'certs') {
        this.confirmCertsVisible = true
      } else {
        this.confirmTopicVisible = true
      }
    },

    deleteRecords() {
      if (!this.willDeleteId) {
        return
      }
      this.dialogVisible = false
      if (this.confirmCertsVisible) {
        this.confirmCertsVisible = false
        httpDelete(`${this.url}/${this.detailsID}/certs?ids=${this.willDeleteId}`)
          .then(() => {
            this.$message.success(this.$t('oper.deleteSuccess'))
            this.loadCerts()
          })
          .catch((error) => {
            this.$message.error(error.response.data.message || this.$t('oper.deleteFail'))
          })
      } else if (this.confirmPoliciesVisible) {
        this.confirmPoliciesVisible = false
        httpDelete(`${this.url}/${this.detailsID}/policies?ids=${this.willDeleteId}`)
          .then(() => {
            this.$message.success(this.$t('oper.deleteSuccess'))
            this.loadPolicies()
          })
          .catch((error) => {
            this.$message.error(error.response.data.message || this.$t('oper.deleteFail'))
          })
      } else {
        this.confirmTopicVisible = false
        httpDelete(`${this.url}/${this.detailsID}/subscriptions?ids=${this.willDeleteId}`)
          .then(() => {
            this.$message.success(this.$t('oper.deleteSuccess'))
            this.loadTopics()
          })
      }
    },
    // Download the cert
    downloadFile(id) {
      const zip = new JSzip()
      const currDate = new Date()
      const dateWithOffset = new Date(currDate.getTime() - (currDate.getTimezoneOffset() * 60000))
      httpGet(`/certs/${id}`).then((response) => {
        const certName = response.data.name
        zip.file(`${certName}.crt`, response.data.cert, { binary: true, date: new Date(dateWithOffset) })
        zip.file(`${certName}.key`, response.data.key, { binary: true, date: new Date(dateWithOffset) })
        zip.file('root_ca.crt', response.data.root, { binary: true, date: new Date(dateWithOffset) })
        zip.generateAsync({ type: 'blob' }).then((content) => {
          const aTag = document.createElement('a')
          aTag.download = `${certName}.zip`
          aTag.href = URL.createObjectURL(content)
          aTag.setAttribute('type', 'hidden')
          document.body.appendChild(aTag)
          aTag.click()
          aTag.remove()
          URL.revokeObjectURL(content)
        })
      }).catch((error) => {
        this.$message.error(error.response.data.message)
      })
    },
    // View policy details
    viewPolicy(policyId) {
      this.policyDetailsLoading = true
      this.policiesViewDialogVisible = true
      httpGet(`policies/${policyId}`).then((response) => {
        this.policy = response.data
        this.policyDetailsLoading = false
      })
    },
  },

  created() {
    this.loadCerts()
    this.loadPolicies()
    this.loadTopics()
  },
}
</script>


<style lang="scss">
.device-details-security-view {
  .device-security-list {
    font-size: 14px;
    overflow: scroll;
    a {
      cursor: pointer;
    }
    img {
      width: 20px !important;
      height: 20px !important;
      position: relative;
      bottom: 2px;
    }
    .el-icon-question {
      margin-left: 4px;
      color: var(--color-text-light);
      cursor: pointer;
    }
    .el-card__header {
      border: none;
      span {
        font-weight: 500;
      }
    }
    .el-card__body  {
      height: 380px;
      overflow: hidden;
      color: var(--color-text-light);
      padding: 0px 0px 20px 20px !important;
      .el-scrollbar__view {
        width: 95%;
      }
      .security-table {
        margin-bottom: 20px;
      }
    }
    .el-pagination {
      margin: 20px 0px;
      float: right;
    }
  }
  .emq-dialog {
    .el-dialog__body {
      padding: 20px;
      word-wrap: break-word;
    }
    .policy-view {
      margin-bottom: 20px;
      .policy-view-content {
        color: var(--color-text-light);
      }
    }
    .el-select {
      .el-input {
        height: auto;
      }
    }
    p {
      margin: 0 0 10px 0;
    }
    .create-cert {
      .el-col-12 {
        width: 100%;
      }
      .el-form--label-top .el-form-item__label {
        padding: 0;
      }
    }
  }
  .add-topic-dialog {
    .el-dialog__body {
      padding: 20px 20px 10px 20px;
    }
  }
}
</style>
