<template>
  <div class="details-view device-details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceInfo') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag
          v-if="record.deviceStatusLabel"
          :class="record.deviceStatus === 1 ? 'online' : 'offline'">
          {{ record.deviceStatusLabel }}
        </emq-tag>
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>

    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>

    <client-details
      :disabled="disabled"
      :loading="loading"
      :record="record"
      @toggleStatus="showDetails">
      <template v-slot:detailsForm="{ lang }">
        <el-row :gutter="20">
          <el-form
            ref="record"
            size="medium"
            :label-width="lang === 'en' ? '120px' : '82px'"
            :label-position="disabled ? 'left' : 'top'"
            :class="{ 'is-disabled': disabled }"
            :disabled="disabled"
            :model="record"
            :rules="disabled ? {} : deviceInfoRules">
            <el-col :span="12">
              <el-form-item prop="deviceName" :label="$t('devices.deviceName')">
                <el-input type="text" v-model="record.deviceName" :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="productID" :label="$t('devices.productName')">
                <el-input v-if="!disabled" type="text" v-model="record.productName" disabled>
                </el-input>
                <router-link
                  v-else
                  style="margin-left: 0px;float: left;line-height:41px"
                  :to="{ path: `/products/${record.productIntID}` }">
                  {{ record.productName }}
                </router-link>
              </el-form-item>
            </el-col>
            <!-- Uplink system -->
            <el-col v-if="record.cloudProtocol !== $variable.cloudProtocol.LWM2M" :span="12">
              <el-form-item
                prop="upLinkSystem"
                :label="$t('devices.upLinkSystem')">
                <emq-select
                  v-model="record.upLinkSystem"
                  :field="{ key: 'upLinkSystem' }"
                  :record="record"
                  :placeholder="disabled ? '' : $t('oper.select')"
                  :disabled="false">
                </emq-select>
              </el-form-item>
            </el-col>
            <!-- Parent device -->
            <el-col
              v-if="record.upLinkSystem === Device
                && record.cloudProtocol !== $variable.cloudProtocol.LWM2M"
              :span="12">
              <el-form-item
                prop="parentDevice"
                :label="$t('devices.parentDevice')">
                <emq-search-select
                  v-model="record.parentDevice"
                  :placeholder="disabled ? '' : $t('oper.devicesSearch')"
                  :field="{
                    url: '/emq_select/devices',
                    params: { deviceType: 1 },
                    options: [{ value: record.parentDevice, label: record.parentDeviceName }],
                    searchKey: 'deviceName',
                  }"
                  :record="record"
                  :disabled="!!$route.query.gateway || !!$route.query.parentDevice"
                  @input="handleParentDevice">
                </emq-search-select>
              </el-form-item>
            </el-col>
            <el-col
              v-if="record.upLinkSystem === Gateway
                && record.cloudProtocol !== $variable.cloudProtocol.LORA"
              :span="12">
              <el-form-item
                prop="gateway"
                :label="$t('devices.gateway')">
                <emq-search-select
                  v-if="!disabled"
                  v-model.number="record.gateway"
                  :placeholder="disabled ? '' : $t('oper.gatewaySearch')"
                  :field="{
                    url: '/emq_select/devices',
                    params: { deviceType: 2 },
                    options: [{ value: record.gateway, label: record.gatewayName }],
                    searchKey: 'gatewayName',
                  }"
                  :record="record"
                  :disabled="disabled"
                  @input="handleParentGatway">
                </emq-search-select>
                <router-link
                  v-else
                  style="margin-left: 0px;float: left;"
                  :to="{ path: `/devices/gateways/${record.gateway}` }">
                  {{ record.gatewayName }}
                </router-link>
              </el-form-item>
            </el-col>
            <!-- Auth type -->
            <el-col v-if="record.upLinkSystem !== Gateway" :span="12">
              <el-form-item
                prop="authType"
                :label="$t('devices.authType')">
                <emq-select
                  v-if="record.authType"
                  v-model="record.authType"
                  :field="{ key: 'authType' }"
                  :record="record"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col
              v-if="record.authType === Cert
                && record.upLinkSystem !== Gateway"
              :span="12">
              <el-form-item
                prop="certs"
                :label="$t('devices.certs')">
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
            <el-col :span="12">
              <el-form-item class="groups" prop="groups" :label="$t('groups.group')">
                <emq-search-select
                  v-if="!disabled"
                  ref="groupSelect"
                  size="medium"
                  v-model="record.groups"
                  multiple
                  :placeholder="disabled ? '' : $t('groups.groupNameRequired')"
                  :field="{
                    url: '/emq_select/groups',
                    searchKey: 'groupName',
                    state: 'create',
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

            <!-- loRa device start -->
            <template v-if="record.cloudProtocol === $variable.cloudProtocol.LORA">
              <!-- Not gateway -->
              <el-col :span="12">
                <el-form-item prop="loraData.type" :label="$t('devices.loraType')">
                  <emq-select
                    v-model="record.loraData.type"
                    :field="{ options: [
                      { label: 'OTAA', value: 'otaa' },
                      { label: 'ABP', value: 'abp' }]
                    }"
                    :record="record.loraData"
                    :disabled="disabled">
                  </emq-select>
                </el-form-item>
              </el-col>

              <!-- abp lora device
                DevAddr deviceID 8
                Region  region
                NwkSKey nwkSKey
                AppSKey appSKey
                FCnt Up fcntUp
                FCnt Down fcntDown
                FCnt Check  fcntCheck
              -->
              <template v-if="record.loraData.type === 'abp'">
                <el-col :span="12">
                  <el-form-item prop="deviceID" label="DevAddr" :rules="deviceInfoRules.devAddr">
                    <el-input disabled v-model="record.deviceID"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.region" :label="$t('devices.region')">
                    <el-input v-model="record.loraData.region"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.nwkSKey" label="NwkSKey">
                    <el-input v-model="record.loraData.nwkSKey" maxlength="32"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.appSKey" label="AppSKey">
                    <el-input v-model="record.loraData.appSKey" maxlength="32"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.fcntUp" label="FCnt Up">
                    <el-input v-model.number="record.loraData.fcntUp" type="number"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.fcntDown" label="FCnt Down">
                    <el-input v-model.number="record.loraData.fcntDown" type="number"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.fcntCheck" label="FCnt Check">
                    <emq-select
                      v-model="record.loraData.fcntCheck"
                      :record="record.loraData"
                      :field="{ key: 'fcntCheck' }"
                      :disabled="disabled">
                    </emq-select>
                  </el-form-item>
                </el-col>
              </template>

              <!-- otaa device
                DevEUI  deviceID 16
                Region  region
                AppEUI  appEUI
                AppKey  appKey
                FCnt Check  fcntCheck
                Allowed to join canJoin
                -->
              <template v-else-if="record.loraData.type === 'otaa'">
                <el-col :span="12">
                  <el-form-item prop="deviceID" label="DevEUI" :rules="deviceInfoRules.devEUI">
                    <el-input disabled v-model="record.deviceID"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.region" :label="$t('devices.region')">
                    <emq-select
                      v-model="record.loraData.region"
                      :record="record.loraData"
                      :field="{ key: 'region' }"
                      :disabled="disabled">
                    </emq-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.appEUI" label="AppEUI">
                    <el-input v-model="record.loraData.appEUI" maxlength="16"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.fcntCheck" label="FCnt Check">
                    <emq-select
                      v-model="record.loraData.fcntCheck"
                      :record="record.loraData"
                      :field="{ key: 'fcntCheck' }"
                      :disabled="disabled">
                    </emq-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.appKey" label="AppKey">
                    <el-input v-model="record.loraData.appKey" maxlength="32"></el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item prop="loraData.canJoin" :label="$t('devices.canJoin')">
                    <emq-select
                      v-model="record.loraData.canJoin"
                      :record="record.loraData"
                      :field="{ options: [
                        { label: $t('oper.isTrue'), value: 1 },
                        { label: $t('oper.isFalse'), value: 0 }]
                        }"
                      :disabled="disabled">
                    </emq-select>
                  </el-form-item>
                </el-col>
              </template>
            </template>
            <!-- loRa device end -->

            <el-col class="auto-sub" v-if="record.cloudProtocol === $variable.cloudProtocol.LWM2M" :span="12">
              <el-form-item prop="lwm2mData.autoSub" :label="$t('devices.autoSub')">
                <el-select v-model="record.lwm2mData.autoSub" style="width: 100%;">
                  <el-option :label="$t('oper.isTrue')" :value="1"></el-option>
                  <el-option :label="$t('oper.isFalse')" :value="0"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col
              v-if="record.cloudProtocol === $variable.cloudProtocol.LWM2M"
              :span="12">
              <el-form-item
                prop="lwm2mData.IMEI"
                label="IMEI">
                <el-input
                  type="text"
                  maxlength="15"
                  disabled
                  v-model="record.lwm2mData.IMEI"
                  :placeholder="disabled ? '' : $t('devices.IMEIRequired')">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="record.cloudProtocol === $variable.cloudProtocol.LWM2M"
              :span="12">
              <el-form-item
                prop="lwm2mData.IMSI"
                label="IMSI">
                <el-input
                  type="text"
                  disabled
                  v-model="record.lwm2mData.IMSI"
                  :placeholder="disabled ? '' : $t('devices.IMSIRequired')">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="carrier" :label="$t('devices.carrier')">
                <emq-select
                  v-model="record.carrier"
                  :field="{ key: 'carrier' }"
                  :record="record"
                  :placeholder="disabled ? '' : $t('oper.select')"
                  :disabled="false">
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
                  :disabled="false">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="description" :label="$t('devices.description')">
                <el-input type="text" v-model="record.description" :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="serialNumber" :label="$t('devices.serialNumber')">
                <el-input type="text" v-model="record.serialNumber" :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="softVersion" :label="$t('devices.softVersion')">
                <el-input type="text" v-model="record.softVersion" :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="hardwareVersion" :label="$t('devices.hardwareVersion')">
                <el-input type="text" v-model="record.hardwareVersion" :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12" class="mac">
              <el-form-item prop="mac" :label="$t('gateways.mac')">
                <el-input
                  type="text"
                  v-model="record.mac"
                  :placeholder="disabled ? '' : $t('gateways.macRequired')"
                  :disabled="false">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="manufacturer" :label="$t('devices.manufacturer')">
                <el-input type="text" v-model="record.manufacturer" :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="metaData" :label="$t('devices.metaData')">
                <el-input v-if="!disabled" type="text" v-model="record.metaData" @focus="openMetaDataDialog">
                </el-input>
                <div v-else class="link">
                  <a
                    href="javascript:;"
                    style="float: none;">
                    <el-tag size="small" @click="openMetaDataDialog">
                      {{ $t('oper.clickView') }}
                    </el-tag>
                  </a>
                </div>
              </el-form-item>
            </el-col>
            <!-- <el-col v-if="record.upLinkSystem !== Gateway" :span="12">
              <el-form-item
                prop="deviceConsoleIP"
                :label="$t('devices.deviceConsoleIP')">
                <el-input v-model="record.deviceConsoleIP">
                </el-input>
              </el-form-item>
            </el-col> -->
            <!-- <el-col v-if="record.upLinkSystem !== Gateway" :span="12">
              <el-form-item
                prop="deviceConsolePort"
                :label="$t('devices.deviceConsolePort')">
                <el-input v-model.number="record.deviceConsolePort" type="number" placeholder="22">
                </el-input>
              </el-form-item>
            </el-col> -->
            <!-- <el-col v-if="record.upLinkSystem !== Gateway" :span="12">
              <el-form-item
                prop="deviceConsoleUsername"
                :label="$t('devices.deviceConsoleUsername')">
                <el-input v-model="record.deviceConsoleUsername">
                </el-input>
              </el-form-item>
            </el-col> -->
            <el-col v-if="disabled" :span="12">
              <el-form-item prop="createAt" :label="$t('devices.createAt')">
                <el-input type="text" v-model="record.createAt" :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="disabled" :span="12">
              <el-form-item prop="createUser" :label="$t('devices.createUser')">
                <el-input type="text" v-model="record.createUser" :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <div v-if="!disabled" class="btn-bar">
          <emq-button icon="save" :loading="btnLoading" @click="save">
            {{ $t('oper.save') }}
          </emq-button>
          <el-button
            type="text"
            size="small"
            style="float: right;"
            @click="showDetails('view')">
            {{ $t('oper.cancel') }}
          </el-button>
        </div>
      </template>
    </client-details>

    <emq-dialog
      v-model="tempMetaData"
      width="500px"
      class="meta-data__dialog"
      :title="$t('devices.metaDataTitle')"
      :visible.sync="metaDataVisible"
      @confirm="saveMetaData"
      @close="metaDataVisible = false">
      <el-popover placement="right" width="280" trigger="hover">
        <p>{{ $t('devices.metaDataTip') }}</p>
        <i slot="reference" class="el-icon-question meta-data__question" style="color: #888; cursor: pointer;"></i>
      </el-popover>
      <code-editor
        lang="application/json"
        theme="lesser-dark"
        v-model="tempMetaData"
        :disabled="disabled">
      </code-editor>
    </emq-dialog>
  </div>
</template>


<script>
import { httpGet, httpPut } from '@/utils/api'
import { currentDevicesMixin } from '@/mixins/currentDevices'
import CodeEditor from '@/components/CodeEditor'
import EmqDialog from '@/components/EmqDialog'
import EmqSearchSelect from '@/components/EmqSearchSelect'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import DeviceDetailTabs from '../components/DeviceDetailTabs'
import ClientDetails from '../components/ClientDetails'

export default {
  name: 'device-details-view',

  mixins: [currentDevicesMixin],

  components: {
    EmqDetailsPageHead,
    EmqSearchSelect,
    EmqTag,
    DeviceDetailTabs,
    CodeEditor,
    EmqDialog,
    ClientDetails,
  },

  data() {
    return {
      url: '/devices',
      tempDevice: {},
      btnLoading: false,
      loading: false,
      metaDataVisible: false,
      tempMetaData: JSON.stringify({}, null, 2), // Temporary meta data
      deviceIntID: undefined,
      parentGatewayIntID: null,
      parentDeviceIntID: null,
      Device: 2,
      Gateway: 3,
      Cert: 2,
      disabled: this.$route.query.oper !== 'edit',
      record: {
        groups: [],
        deviceType: 1,
        lwm2mData: {
          autoSub: 1,
        },
        loraData: {
          type: 'otaa',
          fcntUp: 0,
          fcntDown: 0,
        },
        modbusData: {},
      },
      stashRecord: {},
      deviceInfoRules: {
        deviceID: [
          { required: true },
        ],
        deviceName: [
          { required: true, message: this.$t('devices.deviceNameRequired') },
        ],
        productID: [
          { required: true, message: this.$t('devices.productNameRequired') },
        ],
        parentDevice: [
          { required: true, message: this.$t('devices.parentDeviceRequired') },
        ],
        authType: [
          { required: true, message: this.$t('devices.authTypeRequired') },
        ],
        certs: [
          { required: true, message: this.$t('devices.certsRequired') },
        ],
        upLinkSystem: [
          { required: true, message: this.$t('devices.upLinkSystemRequired') },
        ],
        gateway: [
          { required: true, message: this.$t('devices.gatewayRequired') },
        ],
        lwm2mData: {
          autoSub: [
            { required: true, message: this.$t('devices.autoSubRequired') },
          ],
          IMSI: [
            { required: true, message: this.$t('devices.IMSIRequired'), trigger: 'blur' },
            { max: 15, message: this.$t('devices.len15'), trigger: 'blur' },
          ],
          IMEI: [
            { required: true, message: this.$t('devices.IMEIRequired'), trigger: 'blur' },
            { min: 15, max: 15, message: this.$t('devices.len15'), trigger: 'blur' },
          ],
        },
        // loRa
        loraData: {
          type: {
            required: true,
            message: this.$t('devices.loraTypeRequired'),
          },
          netID: [
            {
              required: true,
              message: this.$t('devices.netIDRequired'),
            },
            {
              len: 6,
              message: this.$t('devices.netIDlen6'),
            },
          ],
          txChain: {
            required: true,
            message: this.$t('devices.txChain'),
          },
          region: {
            required: true,
            message: this.$t('devices.regionRequired'),
          },
          appEUI: [
            {
              required: true,
              message: this.$t('devices.appEUIRequired'),
            },
            {
              len: 16,
              message: this.$t('devices.appEUILen16'),
            },
          ],
          appKey: [
            {
              required: true,
              message: this.$t('devices.appKeyRequired'),
            },
            {
              len: 32,
              message: this.$t('devices.appkeylen32'),
            },
          ],
          fcntCheck: {
            required: true,
            message: this.$t('devices.fcntCheckRequired'),
          },
          canJoin: {
            required: true,
            message: this.$t('oper.select'),
          },
          nwkSKey: [
            {
              required: true,
              message: this.$t('devices.NwkSKeyRequired'),
            },
            {
              len: 32,
              message: this.$t('devices.NwkSKeyLen32'),
            },
          ],
          appSKey: [
            {
              required: true,
              message: this.$t('devices.appSKeyRequired'),
            },
            {
              len: 32,
              message: this.$t('devices.appSKeylen32'),
            },
          ],
          fcntUp: {
            required: true,
            message: this.$t('devices.fcntUpRequired'),
          },
          fcntDown: {
            required: true,
            message: this.$t('devices.fcntDownRequired'),
          },
        },
        devAddr: [
          { required: true, message: this.$t('devices.DevAddrRequired') },
          { len: 8, message: this.$t('devices.DevAddrLen8') },
        ],
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
    loadData() {
      this.loading = false
      this.deviceIntID = this.$route.params.id
      httpGet(`${this.url}/${this.deviceIntID}`).then((res) => {
        this.record = res.data
        this.processLoadedData(this.record)
        this.loading = false
        if (!this.currentDevice) {
          this.localCache(this.record)
        }
      }).catch(() => {
        this.loading = false
      })
    },

    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        this.btnLoading = true
        let data = { ...this.record }
        // Strictly deserialize into array transfers
        try {
          data.locationScope = JSON.parse(data.locationScope)
          if (!Array.isArray(data.locationScope)) {
            throw new TypeError(`locationScope ${this.$t('devices.typeError')}`)
          }
        } catch (e) {
          data.locationScope = undefined
        }
        data = this.schemaFilter(data)
        httpPut(`${this.url}/${this.deviceIntID}`, data).then(() => {
          const currentDevice = {
            deviceID: this.record.deviceID,
            deviceName: this.record.deviceName,
            deviceIntID: this.record.id,
            cloudProtocol: this.record.cloudProtocol,
            cloudProtocolLabel: this.record.cloudProtocolLabel,
            productIntID: this.record.productIntID,
            productID: this.record.productID,
            token: this.record.token,
            deviceUsername: this.record.deviceUsername,
            upLinkSystem: this.record.upLinkSystem,
          }
          this.loadData()
          this.currentDevice = currentDevice
          this.updateLocalCache(currentDevice)
          this.$message.success(this.$t('oper.editSuccess'))
          this.btnLoading = false
          this.disabled = true
        })
        this.btnLoading = false
      })
    },

    schemaFilter(record) {
      if (!record) {
        return record
      }
      // Remove overfill fields
      if (this.record.cloudProtocol !== this.$variable.cloudProtocol.LORA) {
        delete record.loraData
      } else { // LoRa device
        const keys = Object.keys(record.loraData)
        let fields = []
        if (record.loraData.type === 'otaa') {
          fields = ['region', 'appEUI', 'appKey', 'fcntCheck', 'canJoin', 'type']
        } else if (record.loraData.type === 'abp') {
          fields = ['region', 'nwkSKey', 'appSKey', 'fcntUp', 'fcntDown', 'fcntCheck', 'type']
        }
        keys.forEach((key) => {
          if (!fields.includes(key)) {
            this.$delete(record.loraData, key)
          }
        })
      }
      // LwM2M device
      if (this.record.cloudProtocol !== this.$variable.cloudProtocol.LWM2M) {
        delete record.lwm2mData
      }
      // ModBus Device
      if (this.record.cloudProtocol === this.$variable.cloudProtocol.MODBUS) {
        record.authType = 1
      } else {
        delete record.modbusData
      }
      if (this.parentDeviceIntID && record.upLinkSystem === this.Device) {
        record.parentDevice = this.parentDeviceIntID
      } else if (this.parentGatewayIntID && record.upLinkSystem === this.Gateway) {
        record.gateway = this.parentGatewayIntID
      }
      return record
    },

    openMetaDataDialog() {
      this.tempMetaData = JSON.stringify({}, null, 2)
      if (this.record.metaData) {
        this.tempMetaData = this.record.metaData
      }
      this.metaDataVisible = true
    },

    saveMetaData() {
      if (!this.disabled) {
        this.record.metaData = this.tempMetaData
      }
      this.tempMetaData = JSON.stringify({}, null, 2)
      this.metaDataVisible = false
    },

    processLoadedData(record) {
      // Modify the value of the options selected，Displays label when editing
      if (this.$refs.groupSelect) {
        this.$refs.groupSelect.options = record.groups.map((value, index) => {
          return { value, label: record.groupsIndex[index].label }
        })
      }
      if (this.$refs.certsSelect) {
        this.$refs.certsSelect.options = record.certs.map((value, index) => {
          return { value, label: record.certsIndex[index].label }
        })
      }
    },

    showDetails(operType) {
      const isDetails = operType !== 'edit'
      // Unedit: record content does not change with unsaved entries
      if (!isDetails) {
        this.stashRecord = { ...this.record }
      } else if (this.stashRecord.id) {
        this.record = { ...this.stashRecord }
      }
      if (this.disabled === isDetails) {
        this.disabled = !this.disabled
      } else {
        this.disabled = isDetails
      }
    },

    handleParentDevice(id, selectedItem) {
      if (!id) {
        return
      }
      this.record.parentDevice = id
      this.parentDeviceIntID = selectedItem.attr.deviceIntID
    },

    handleParentGatway(id, selectedItem) {
      if (!id) {
        return
      }
      this.record.gateway = id
      this.parentGatewayIntID = selectedItem.attr.deviceIntID
    },
  },

  created() {
    this.loadData()
  },
}
</script>


<style lang="scss">
.device-details-view {
  .emq-tag {
    &.online {
      .emq-tag__triangle {
        border-right-color: var(--color-main-green);
      }
      .emq-tag__content {
        color: #fff;
        background-color: var(--color-main-green);
      }
    }
    &.offline {
      .emq-tag__triangle {
        border-right-color: var(--color-main-pink);
      }
      .emq-tag__content {
        color: #fff;
        background-color: var(--color-main-pink);
      }
    }
  }
  .is-details-form .group .el-tag {
    margin-right: 8px;
  }
  .meta-data__dialog {
    .meta-data__question {
      position: absolute;
      top: 20px;
      left: 116px;
    }
  }
}
</style>
