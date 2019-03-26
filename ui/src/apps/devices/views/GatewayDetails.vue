<template>
  <div :class="['gateway-details-view', accessType === 'create' ? '' : 'details-view']">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">网关</el-breadcrumb-item>
        <el-breadcrumb-item v-if="record.gatewayName && accessType !== 'create'">{{ record.gatewayName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessType !== 'create' ? '网关信息' : '新建' }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="record && accessType !== 'create'" class="emq-tag-group" slot="tag">
        <emq-tag>{{ record.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>

    <div v-if="accessType !== 'create'" class="detail-tabs">
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>

    <div class="gateway-card-details-body">
      <el-card :class="disabled ? 'is-details-form' : 'is-create-form'">
        <!-- Step bar -->
        <div class="emq-steps" v-if="accessType === 'create'">
          <div :class="['step', step === 1 ? 'is-active' : '']">
            <i class="step__icon-inner">1</i>
            <span class="step__title">网关信息</span>
          </div>
          <div class="step__arrow"></div>
          <div :class="['step', step === 2 ? 'is-active' : '']">
            <i class="step__icon-inner">2</i>
            <span class="step__title">
              认证信息
            </span>
          </div>
          <div class="step__process" :style="{ width: `${step / 2 * 100}%` }"></div>
        </div>

        <edit-toggle-button
          :url="url"
          :disabled="disabled"
          :accessType="accessType"
          @toggleStatus="toggleStatus">
        </edit-toggle-button>
        <el-row :class="accessType === 'edit' ? 'el-row__edit' : ''" :gutter="50">
          <el-form
            ref="record"
            :class="!disabled ? 'gateway-form-create' : 'gateway-form'"
            label-width="100px"
            :label-position="accessType === 'create' ? 'top' : 'left'"
            :model="record"
            :rules="disabled ? {} : rules">
            <div v-if="step === 1">
              <el-col :span="12">
                <el-form-item prop="gatewayName" label="网关名称">
                  <el-input
                    type="text"
                    v-model="record.gatewayName"
                    :placeholder="disabled ? '' : '请输入网关名称'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="productID" label="所属产品">
                  <emq-search-select
                    v-if="!disabled"
                    ref="productSelect"
                    v-model="record.productID"
                    :placeholder="disabled ? '' : '请输入产品名称搜索'"
                    :field="productSelectField"
                    :record="record"
                    :disabled="!!$route.query.productID"
                    @input="handleProductSelect">
                  </emq-search-select>
                  <el-input
                    v-else
                    type="text"
                    v-model="record.productName"
                    disabled></el-input>
                </el-form-item>
              </el-col>
              <el-col v-show="accessType === 'view'" :span="12">
                <el-form-item prop="gatewayProtocol" label="网关协议">
                  <emq-select
                    v-model="record.gatewayProtocol"
                    :field="{ key: 'gatewayProtocol' }"
                    :record="record"
                    :placeholder="disabled ? '' : $t('oper.select')"
                    :disabled="accessType !== 'create'">
                  </emq-select>
                </el-form-item>
              </el-col>
              <el-col v-show="accessType === 'view'" :span="12">
                <el-form-item prop="cloudProtocol" label="上联协议">
                  <emq-select
                    v-model="record.cloudProtocol"
                    :field="{ key: 'cloudProtocol' }"
                    :record="record"
                    :placeholder="disabled ? '' : $t('oper.select')"
                    :disabled="disabled">
                  </emq-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="upLinkNetwork" label="上联网络">
                  <emq-select
                    v-model="record.upLinkNetwork"
                    :field="{ key: 'upLinkNetwork' }"
                    :record="record"
                    :placeholder="disabled ? '' : $t('oper.select')"
                    :disabled="disabled">
                  </emq-select>
                </el-form-item>
              </el-col>
              <el-col class="gateway-model" v-if="record.gatewayProtocol === ModBus" :span="12">
                <el-form-item prop="gatewayModel" label="网关型号">
                  <emq-select
                    v-model="record.gatewayModel"
                    :field="{ options: gatewayModelOptions }"
                    :record="record"
                    :placeholder="disabled ? '' : $t('oper.select')"
                    :disabled="accessType !== 'create'">
                  </emq-select>
                </el-form-item>
              </el-col>
              <!-- Auth type -->
              <el-col v-if="accessType === 'edit'" :span="12">
                <el-form-item prop="authType" label="认证方式">
                  <emq-select
                    v-model="record.authType"
                    :field="{ key: 'authType' }"
                    :record="record"
                    :disabled="disabled">
                  </emq-select>
                </el-form-item>
              </el-col>
              <el-col :span="12" class="mac">
                <el-form-item prop="mac" label="网关MAC" :class="{ 'is-required': MACRequiredClass}">
                  <el-input
                    type="text"
                    v-model="record.mac"
                    :placeholder="disabled ? '' : '请输入网关MAC'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item class="tag" prop="tags" label="标签">
                  <emq-search-select
                    v-if="!disabled"
                    ref="tagsSelect"
                    v-model="record.tags"
                    multiple
                    :placeholder="disabled ? '' : '请输入标签名称搜索'"
                    :field="{
                      url: '/emq_select/tags',
                      searchKey: 'tagName',
                      state: 'create',
                    }"
                    :record="record"
                    :disabled="false">
                  </emq-search-select>
                  <div v-if="disabled" class="link">
                    <router-link
                      style="float: none;"
                      v-for="tag in record.tagIndex"
                      :key="tag.value"
                      to="">
                      <el-tag size="small">
                        {{ tag.label }}
                      </el-tag>
                    </router-link>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="location" label="网关位置">
                  <el-input
                    type="text"
                    v-model="record.location"
                    :placeholder="disabled ? '' : '请输入网关位置'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="longitude" :label="$t('devices.longitude')">
                  <el-input
                    type="number"
                    v-model.number="record.longitude"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="latitude" :label="$t('devices.latitude')">
                  <el-input
                    type="number"
                    v-model.number="record.latitude"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col v-if="disabled" :span="12">
                <el-form-item prop="deviceID" label="网关编号">
                  <el-input
                    type="text"
                    v-model="record.deviceID"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col v-if="disabled" :span="12">
                <el-form-item prop="deviceUsername" label="网关用户名">
                  <el-input
                    type="text"
                    v-model="record.deviceUsername"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col v-if="disabled" :span="12">
                <el-form-item prop="token" label="网关密钥">
                  <el-input
                    v-model="record.token"
                    type="text"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col v-if="accessType !== 'create' && record.gatewayProtocol === ModBus" :span="12">
                <el-form-item prop="channelType" label="网关通道">
                  <el-tag class="channel-tag" size="small">
                    <a href="javascript:;" @click="rightbarVisible = !rightbarVisible">点击查看</a>
                  </el-tag>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="manufacturer" label="制造商">
                  <el-input
                    type="text"
                    v-model="record.manufacturer"
                    :placeholder="disabled ? '' : '请输入制造商'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="serialNumber" label="序列号">
                  <el-input
                    type="text"
                    v-model="record.serialNumber"
                    :placeholder="disabled ? '' : '请输入序列号'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="softVersion" label="软件版本">
                  <el-input
                    type="text"
                    v-model="record.softVersion"
                    :placeholder="disabled ? '' : '请输入软件版本'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="hardwareVersion" label="硬件版本">
                  <el-input
                    type="text"
                    v-model="record.hardwareVersion"
                    :placeholder="disabled ? '' : '请输入硬件版本'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="deviceConsoleIP" label="控制台IP">
                  <el-input
                    type="text"
                    v-model="record.deviceConsoleIP"
                    :placeholder="disabled ? '' : '控制台IP'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="deviceConsoleUsername" label="控制台用户">
                  <el-input
                    type="text"
                    v-model="record.deviceConsoleUsername"
                    :placeholder="disabled ? '' : '控制台用户'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="deviceConsolePort" label="控制台端口">
                  <el-input
                    type="text"
                    v-model="record.deviceConsolePort"
                    :placeholder="disabled ? '' : '控制台端口'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="description" label="网关描述">
                  <el-input
                    type="text"
                    v-model="record.description"
                    :placeholder="disabled ? '' : '请输入网关描述'"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col v-if="accessType === 'view'" :span="12">
                <el-form-item :label="$t('groups.createAt')">
                  <el-input
                    v-model="record.createAt"
                    :disabled="disabled">
                  </el-input>
                </el-form-item>
              </el-col>
            </div>

            <!-- step 2 -->
            <div v-if="step === 2 && accessType === 'create'" class="gateways-rows">
              <el-col :span="12">
                <el-form-item prop="authType" :label="$t('devices.authType')">
                  <emq-select
                    v-model="record.authType"
                    :field="{ key: 'authType' }"
                    :record="record"
                    :placeholder="$t('oper.select')"
                    :disabled="false">
                  </emq-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="deviceID" label="网关编号">
                  <el-input
                    type="text"
                    :placeholder="$t('devices.deviceIDRequired')"
                    v-model="record.deviceID">
                  </el-input>
                  <div class="el-form-item__error form__tips">
                    <i class="el-icon-warning" style="color: #ffc741;"></i>
                    {{ $t('devices.warning') }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="deviceUsername" :label="$t('devices.username')">
                  <el-input
                    type="text"
                    :placeholder="$t('devices.deviceIDRequired')"
                    v-model="record.deviceUsername">
                  </el-input>
                  <div class="el-form-item__error form__tips">
                    <i class="el-icon-warning" style="color: #ffc741;"></i>
                    {{ $t('devices.usernameWarnig') }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="token" label="网关密钥">
                  <el-input
                    v-model="record.token"
                    type="text"
                    :placeholder="$t('devices.deviceIDRequired')">
                  </el-input>
                  <div class="el-form-item__error form__tips">
                    <i class="el-icon-warning" style="color: #ffc741;"></i>
                    {{ $t('devices.warning') }}
                  </div>
                </el-form-item>
              </el-col>
            </div>
          </el-form>
        </el-row>
      </el-card>
      <a
        v-if="accessType === 'create' && step === 2"
        class="back-setup"
        href="javascript:;"
        @click="handleStep(false)">
        &lt;&lt; {{ $t('devices.backStep') }}
      </a>
      <emq-button v-if="!disabled && step === 2" icon="save" @click="save">
        {{ $t('oper.finish') }}
      </emq-button>
      <emq-button v-if="accessType === 'create' && step === 1" class="step" @click="handleStep">
        下一步
      </emq-button>
      <emq-button v-if="accessType === 'edit'" icon="save" @click="save">
        {{ $t('oper.finish') }}
      </emq-button>
    </div>

    <channels-rightbar
      v-if="record.gatewayProtocol === ModBus"
      :rightbarVisible.sync="rightbarVisible"
      :url="`/gateways/${this.$route.params.id}/channels`"
      :currentGateway="record">
    </channels-rightbar>
  </div>
</template>


<script>
import detailsPage from '@/mixins/detailsPage'
import EmqButton from '@/components/EmqButton'
import EmqSelect from '@/components/EmqSelect'
import EmqSearchSelect from '@/components/EmqSearchSelect'
import EmqTag from '@/components/EmqTag'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import GatewayDetailTabs from '../components/GatewayDetailTabs'
import ChannelsRightbar from '../components/ChannelsRightbar'

export default {
  name: 'gateway-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqSelect,
    EmqTag,
    GatewayDetailTabs,
    ChannelsRightbar,
    EmqSearchSelect,
  },

  data() {
    return {
      rightbarVisible: false,
      url: '/gateways',
      step: 1,
      ModBus: 7,
      record: {
        productID: this.$route.query.productID,
        gatewayProtocol: this.$route.query.gatewayProtocol,
        tags: [],
      },
      gatewayModelOptions: [{ Label: 'Neuron', value: 'Neuron' }],
      rules: {
        gatewayName: [
          { required: true, message: '请输入网关名称', trigger: 'blur' },
        ],
        productID: [
          { required: true, message: '请选择所属产品', trigger: 'blur' },
        ],
        upLinkNetwork: [
          { required: true, message: '请选择上联网络', trigger: 'blur' },
        ],
        gatewayModel: [
          { required: true, message: '请选择网关型号' },
        ],
        longitude: [
          { type: 'number', message: this.$t('devices.longitudeIsNumber') },
        ],
        latitude: [
          { type: 'number', message: this.$t('devices.latitudeIsNumber') },
        ],
        authType: [
          { required: true, message: '请选择认证方式', trigger: 'blur' },
        ],
        deviceID: { min: 8, max: 36, message: '长度为8-36位', trigger: 'change' },
        deviceUsername: [
          { min: 8, max: 36, message: '长度为8-36位', trigger: 'change' },
        ],
        token: [
          { min: 8, max: 36, message: '长度为8-36位', trigger: 'change' },
        ],
      },
      productSelectField: {
        url: '/emq_select/products?productType=2',
        options: [],
        searchKey: 'productName',
      },
    }
  },
  watch: {
    '$route.params.id': 'handleIdChanged',
    'record.gatewayProtocol': 'MACRequired',
    accessType(newValue) {
      if (newValue === 'edit') {
        setTimeout(() => { this.processLoadedData(this.record) }, 100)
      }
    },
  },
  computed: {
    MACRequiredClass() {
      return this.record.gatewayProtocol === 4 && !this.disabled
    },
  },
  methods: {
    handleStep(next = true) {
      document.body.scrollTop = 0
      document.documentElement.scrollTop = 0
      if (next) {
        this.$refs.record.validate((valid) => {
          if (!valid) {
            return false
          }
          this.step = 2
        })
      } else {
        this.step = 1
      }
    },
    // According to the gateway protocol
    MACRequired() {
      if (this.record.gatewayProtocol === 4) {
        this.rules.mac = [
          { required: true, message: '请输入网关MAC', trigger: 'blur' },
        ]
      } else {
        delete this.rules.mac
      }
    },
    handleProductSelect(productID, selectItem) {
      if (!productID) {
        return
      }
      this.record.gatewayProtocol = selectItem.attr.gatewayProtocol
    },
    // Special treatment from the product details page
    handleProductProcess(productID, productName) {
      if (this.$refs.productSelect) {
        this.$refs.productSelect.options = [{
          value: productID,
          label: productName,
        }]
      }
    },
    processLoadedData(record) {
      // Modify the value of the options selected，Displays label when editing
      setTimeout(() => {
        if (this.$refs.tagsSelect) {
          this.$refs.tagsSelect.options = record.tags.map((value, index) => {
            return { value, label: record.tagIndex[index].label }
          })
        }
      }, 1)
      this.handleProductProcess(this.record.productID, this.record.productName)
      // After saves the data, go back to the view page
      this.isRenderToList = false
    },
    beforePostData(data) {
      if (this.accessType === 'create') {
        delete data.gatewayProtocol
        delete data.cloudProtocol
      }
    },
    handleIdChanged() {
      this.detailsID = this.$route.params.id
      this.loadData()
    },
  },
  mounted() {
    if (this.accessType === 'create' && this.$route.query.productID) {
      this.handleProductProcess(this.$route.query.productID, this.$route.query.productName)
    }
  },
  created() {
    this.MACRequired()
  },
}
</script>


<style lang="scss">
  .gateway-details-view {
    .gateway-card-details-body {
      .el-card {
        .el-card__body {
          position: relative;
          padding-top: 50px;
        }
        .channel-tag {
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
        }
        .gateway-form {
          .el-col {
            height: 41px;
          }
        }
        .el-form-item__label {
          color: var(--color-text-light);
        }
      }
      .is-details-form .tag .el-tag {
        margin-right: 8px;
      }
      .el-row {
        margin-bottom: 20px;
      }
      .el-row__edit {
        padding-top: 50px;
      }
      .is-create-form {
        margin-bottom: 20px;
        .el-card__body {
          padding: 0;
          .gateway-form-create {
            padding: 8px 30px;
          }
        }
      }
      .form__tips {
        color: var(--color-text-lighter);
        position: relative;
        top: 2px;
      }
      .back-setup {
        position: absolute;
        right: 130px;
        margin-top: 8px;
      }
    }
  }
</style>
