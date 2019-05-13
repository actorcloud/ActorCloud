<template>
  <div class="gateway-details-view details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="record.deviceName">{{ record.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('gateways.gatewayInfo') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="record" class="emq-tag-group" slot="tag">
        <emq-tag>{{ record.gatewayProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>

    <div class="detail-tabs">
      <gateway-detail-tabs></gateway-detail-tabs>
    </div>

    <client-details
      :disabled="disabled"
      :loading="loading"
      :record="record"
      @toggleStatus="toggleStatus">
      <template v-slot:detailsForm>
        <el-row :gutter="20">
          <el-form
            ref="record"
            label-width="82px"
            size="medium"
            :label-position="disabled ? 'left' : 'top'"
            :class="{ 'is-disabled': disabled }"
            :disabled="disabled"
            :model="record"
            :rules="disabled ? {} : gatewayInfoRules">
            <el-col :span="12">
              <el-form-item prop="deviceName" :label="$t('gateways.gatewayName')">
                <el-input
                  type="text"
                  v-model="record.deviceName"
                  :placeholder="disabled ? '' : $t('gateways.gatewayNameRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="productID" :label="$t('devices.productName')">
                <emq-search-select
                  v-if="!disabled"
                  ref="productSelect"
                  v-model="record.productID"
                  :placeholder="disabled ? '' : $t('oper.productsSearch')"
                  :field="productSelectField"
                  :record="record"
                  :disabled="true"
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
              <el-form-item prop="gatewayProtocol" :label="$t('products.gatewayProtocol')">
                <emq-select
                  v-model="record.gatewayProtocol"
                  :field="{ key: 'gatewayProtocol' }"
                  :record="record"
                  :placeholder="disabled ? '' : $t('oper.select')"
                  :disabled="true">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col v-show="accessType === 'view'" :span="12">
              <el-form-item prop="cloudProtocol" :label="$t('gateways.cloudProtocol')">
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
              <el-form-item prop="upLinkNetwork" :label="$t('gateways.upLinkNetwork')">
                <emq-select
                  v-model="record.upLinkNetwork"
                  :field="{ key: 'upLinkNetwork' }"
                  :record="record"
                  :placeholder="disabled ? '' : $t('oper.select')"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <!-- Auth type -->
            <el-col :span="12">
              <el-form-item prop="authType" :label="$t('gateways.authType')">
                <emq-select
                  v-model="record.authType"
                  :field="{ key: 'authType' }"
                  :record="record"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col v-if="record.authType === Cert"  :span="12">
              <el-form-item prop="certs" :label="$t('devices.certs')">
                <emq-search-select
                  v-if="!disabled"
                  ref="certsSelect"
                  multiple
                  v-model="record.certs"
                  :field="{
                    url: `/emq_select/certs`,
                    searchKey: 'certName',
                  }"
                  :placeholder="$t('oper.select')">
                </emq-search-select>
                <div v-if="disabled" class="link">
                  <router-link
                    style="float: none;"
                    v-for="cert in record.certsIndex"
                    :key="cert.value"
                    :to="`/security/certs/${cert.value}?oper=view`">
                    <el-tag size="small">
                      {{ cert.label }}
                    </el-tag>
                  </router-link>
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="12" class="mac">
              <el-form-item prop="mac" :label="$t('gateways.gatewayMac')">
                <el-input
                  type="text"
                  v-model="record.mac"
                  :placeholder="disabled ? '' : $t('gateways.gatewayMacRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item class="groups" prop="groups" :label="$t('groups.group')">
                <emq-search-select
                  v-if="!disabled"
                  ref="groupsSelect"
                  v-model="record.groups"
                  multiple
                  :placeholder="disabled ? '' : $t('groups.groupNameRequired')"
                  :field="{
                    url: '/emq_select/groups',
                    searchKey: 'groupName',
                    state: 'edit',
                  }"
                  :record="record"
                  :disabled="false">
                </emq-search-select>
                <div v-if="disabled" class="link">
                  <router-link
                    style="float: none;"
                    v-for="group in record.groupsIndex"
                    :key="group.value"
                    :to="`/devices/groups/${group.value}`">
                    <el-tag size="small">
                      {{ group.label }}
                    </el-tag>
                  </router-link>
                </div>
              </el-form-item>
            </el-col>
            <el-col v-if="disabled" :span="12">
              <el-form-item prop="deviceID" :label="$t('gateways.gatewayID')">
                <el-input
                  type="text"
                  v-model="record.deviceID"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="disabled" :span="12">
              <el-form-item prop="deviceUsername" :label="$t('gateways.gatewayUsername')">
                <el-input
                  type="text"
                  v-model="record.deviceUsername"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="disabled" :span="12">
              <el-form-item prop="token" :label="$t('gateways.gatewayToken')">
                <el-input
                  v-model="record.token"
                  type="text"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="record.gatewayProtocol === $variable.cloudProtocol.MODBUS" :span="12">
              <el-form-item prop="channelType" :label="$t('gateways.gatewayChannel')">
                <el-tag class="channel-tag" size="small">
                  <a href="javascript:;" @click="rightbarVisible = !rightbarVisible">{{ $t('oper.clickView') }}</a>
                </el-tag>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="manufacturer" :label="$t('devices.manufacturer')">
                <el-input
                  type="text"
                  v-model="record.manufacturer"
                  :placeholder="disabled ? '' : $t('devices.manufacturerRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="serialNumber" :label="$t('devices.serialNumber')">
                <el-input
                  type="text"
                  v-model="record.serialNumber"
                  :placeholder="disabled ? '' : $t('devices.serialNumberRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="softVersion" :label="$t('devices.softVersion')">
                <el-input
                  type="text"
                  v-model="record.softVersion"
                  :placeholder="disabled ? '' : $t('devices.softVersionRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="hardwareVersion" :label="$t('devices.hardwareVersion')">
                <el-input
                  type="text"
                  v-model="record.hardwareVersion"
                  :placeholder="disabled ? '' : $t('devices.hardwareVersionRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="deviceConsoleIP" :label="$t('devices.deviceConsoleIP')">
                <el-input
                  type="text"
                  v-model="record.deviceConsoleIP"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="deviceConsoleUsername" :label="$t('devices.deviceConsoleUsername')">
                <el-input
                  type="text"
                  v-model="record.deviceConsoleUsername"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="deviceConsolePort" :label="$t('devices.deviceConsolePort')">
                <el-input
                  type="text"
                  v-model="record.deviceConsolePort"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="description" :label="$t('gateways.description')">
                <el-input
                  type="text"
                  v-model="record.description"
                  :placeholder="disabled ? '' : $t('gateways.descriptionRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'view'" :span="12">
              <el-form-item :label="$t('devices.createAt')">
                <el-input
                  v-model="record.createAt"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>

        <div v-if="!disabled" class="btn-bar">
          <emq-button icon="save" @click="save">
            {{ $t('oper.save') }}
          </emq-button>
          <el-button
            type="text"
            size="small"
            style="float: right;"
            @click="toggleStatus(true)">
            {{ $t('oper.cancel') }}
          </el-button>
        </div>
      </template>
    </client-details>

    <channels-rightbar
      v-if="record.gatewayProtocol === $variable.cloudProtocol.MODBUS"
      :rightbarVisible.sync="rightbarVisible"
      :url="`/devices/${this.$route.params.id}/channels`"
      :currentGateway="record">
    </channels-rightbar>
  </div>
</template>


<script>
import detailsPage from '@/mixins/detailsPage'
import EmqButton from '@/components/EmqButton'
import EmqSearchSelect from '@/components/EmqSearchSelect'
import EmqTag from '@/components/EmqTag'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import GatewayDetailTabs from '../components/GatewayDetailTabs'
import ChannelsRightbar from '../components/ChannelsRightbar'
import ClientDetails from '../components/ClientDetails'

export default {
  name: 'gateway-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqTag,
    GatewayDetailTabs,
    ChannelsRightbar,
    EmqSearchSelect,
    ClientDetails,
  },

  data() {
    return {
      loading: false,
      rightbarVisible: false,
      url: '/devices',
      Cert: 2,
      record: {
        productID: this.$route.query.productID,
        gatewayProtocol: this.$route.query.gatewayProtocol,
        groups: [],
        deviceType: 2,
      },
      gatewayInfoRules: {
        deviceName: [
          { required: true, message: this.$t('gateways.gatewayNameRequired'), trigger: 'blur' },
        ],
        productID: [
          { required: true, message: this.$t('devices.productNameRequired'), trigger: 'blur' },
        ],
        upLinkNetwork: [
          { required: true, message: this.$t('gateways.upLinkNetworkRequired'), trigger: 'blur' },
        ],
        longitude: [
          { type: 'number', message: this.$t('devices.longitudeIsNumber') },
        ],
        latitude: [
          { type: 'number', message: this.$t('devices.latitudeIsNumber') },
        ],
        authType: [
          { required: true, message: this.$t('gateways.authTypeRequired'), trigger: 'blur' },
        ],
        certs: [
          { required: true, message: this.$t('devices.certsRequired') },
        ],
        deviceID: { min: 8, max: 36, message: this.$t('devices.len8to36'), trigger: 'change' },
        deviceUsername: [
          { min: 8, max: 36, message: this.$t('devices.len8to36'), trigger: 'change' },
        ],
        token: [
          { min: 8, max: 36, message: this.$t('devices.len8to36'), trigger: 'change' },
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
    disabled(newValue) {
      if (!newValue) {
        setTimeout(() => { this.processLoadedData(this.record) }, 10)
      }
    },
  },

  methods: {
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
        if (this.$refs.groupsSelect) {
          this.$refs.groupsSelect.options = record.groups.map((value, index) => {
            return { value, label: record.groupsIndex[index].label }
          })
        }
        if (this.$refs.certsSelect) {
          this.$refs.certsSelect.options = record.certs.map((value, index) => {
            return { value, label: record.certsIndex[index].label }
          })
        }
      }, 1)
      this.handleProductProcess(this.record.productID, this.record.productName)
      // After saves the data, go back to the view page
      this.isRenderToList = false
    },
  },
}
</script>
