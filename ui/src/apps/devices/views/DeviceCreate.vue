<template>
  <div class="devices-create-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('oper.createBtn') }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <!-- Create Product -->
    <create-products :dialogVisible.sync="productsDialogVisible"></create-products>

    <div class="devices-card-details-body">
      <el-card>
        <!-- Step bar -->
        <div class="emq-steps">
          <div :class="['step', step === 1 ? 'is-active' : '']">
            <i class="step__icon-inner">1</i>
            <span class="step__title">
              {{ $t('devices.deviceInfo') }}
            </span>
          </div>
          <div v-if="cloudProtocol !== $variable.cloudProtocol.MODBUS" class="step__arrow"></div>
          <div v-if="cloudProtocol !== $variable.cloudProtocol.MODBUS" :class="['step', step === 2 ? 'is-active' : '']">
            <i class="step__icon-inner">2</i>
            <span class="step__title">
              {{ cloudProtocol !== $variable.cloudProtocol.LORA ? $t('devices.authInfo') : $t('devices.loraInfo') }}
            </span>
          </div>
          <div v-if="cloudProtocol !== $variable.cloudProtocol.MODBUS"  class="step__process" :style="{ width: `${step / 2 * 100}%` }"></div>
          <div v-else class="step__process" style="width: 100%"></div>
        </div>

        <el-row :gutter="50">
          <el-form
            ref="record"
            label-position="top"
            :model="record"
            :rules="deviceInfoRules">

            <!-- step 1 -->
            <div v-show="step === 1" class="devices-rows">
              <el-col :span="12">
                <el-form-item prop="deviceName" :label="$t('devices.deviceName')">
                  <el-input
                    v-model="record.deviceName"
                    type="text"
                    :placeholder="$t('devices.deviceNameRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <span
                  v-if="has('POST,/products') && !$route.query.productID"
                  class="product-button">
                  {{ $t('devices.or') }}
                  <a href="javascript:;" @click="productsDialogVisible = true">
                    {{ $t('devices.createProduct') }}
                  </a>
                </span>
                <el-form-item prop="productID" :label="$t('devices.productName')">
                  <emq-search-select
                    ref="selectProduct"
                    v-model="record.productID"
                    :placeholder="disabled ? '' : this.$t('oper.productsSearch')"
                    :field="productSelectField"
                    :record="record"
                    :disabled="!!$route.query.productID"
                    @input="handleProductSelect">
                  </emq-search-select>
                </el-form-item>
              </el-col>
              <el-col
                class="modBus-index"
                v-if="cloudProtocol === $variable.cloudProtocol.MODBUS
                  || $route.query.cloudProtocol === $variable.cloudProtocol.MODBUS"
                :span="12">
                <el-form-item prop="modbusData.modBusIndex" :label="$t('devices.index')">
                  <el-input
                    v-model.number="record.modbusData.modBusIndex"
                    type="number"
                    :placeholder="$t('devices.indexRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col
                class="uplink-system"
                v-if="cloudProtocol !== $variable.cloudProtocol.LWM2M" :span="12">
                <el-form-item prop="upLinkSystem" :label="this.$t('devices.upLinkSystem')">
                  <emq-select
                    v-model="record.upLinkSystem"
                    :field="{ key: 'upLinkSystem' }"
                    :record="record"
                    :placeholder="$t('oper.select')"
                    :disabled="!!$route.query.upLinkSystem || !!$route.query.parentDevice">
                  </emq-select>
                </el-form-item>
              </el-col>
              <el-col
                class="parent-device"
                v-if="record.upLinkSystem === Device
                && cloudProtocol !== $variable.cloudProtocol.LWM2M"
                :span="12">
                <el-form-item prop="parentDevice" :label="$t('devices.parentDevice')">
                  <emq-search-select
                    v-model="record.parentDevice"
                    :placeholder="disabled ? '' : this.$t('oper.devicesSearch')"
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
                class="gateway"
                v-if="record.upLinkSystem === Gateway"
                :span="12">
                <el-form-item prop="gateway" :label="$t('devices.gateway')">
                  <emq-search-select
                    v-model="record.gateway"
                    :placeholder="disabled ? '' : $t('oper.gatewaySearch')"
                    :field="{
                      url: '/emq_select/devices',
                      params: { deviceType: 2 },
                      options: [{ value: record.gateway, label: record.gatewayName }],
                      searchKey: 'gatewayName',
                    }"
                    :record="record"
                    :disabled="!!$route.query.gateway"
                    @input="handleParentGatway">
                  </emq-search-select>
                </el-form-item>
              </el-col>
              <!-- The first step shows non-lora -->
              <el-col class="auto-sub" v-if="cloudProtocol === $variable.cloudProtocol.LWM2M" :span="12">
                <el-form-item prop="lwm2mData.autoSub" :label="$t('devices.autoSub')">
                  <el-select v-model="record.lwm2mData.autoSub" style="width: 100%;">
                    <el-option :label="$t('oper.isTrue')" :value="1"></el-option>
                    <el-option :label="$t('oper.isFalse')" :value="0"></el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col
                v-if="cloudProtocol === $variable.cloudProtocol.LWM2M"
                class="IMEI"
                :span="12">
                <el-form-item prop="lwm2mData.IMEI" label="IMEI">
                  <el-input
                    type="text"
                    maxlength="15"
                    :placeholder="$t('devices.IMEIRequired')"
                    v-model="record.lwm2mData.IMEI">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col
                v-if="cloudProtocol === $variable.cloudProtocol.LWM2M"
                :span="12">
                <el-form-item prop="lwm2mData.IMSI" label="IMSI">
                  <el-input
                    type="text"
                    maxlength="15"
                    :placeholder="$t('devices.IMSIRequired')"
                    v-model="record.lwm2mData.IMSI">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="groups" :label="$t('groups.group')">
                  <emq-search-select
                    ref="groupSelect"
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
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="carrier" :label="$t('devices.carrier')">
                  <emq-select
                    v-model="record.carrier"
                    :field="{ key: 'carrier' }"
                    :record="record"
                    :placeholder="$t('oper.select')"
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
                    :placeholder="$t('oper.select')"
                    :disabled="false">
                  </emq-select>
                </el-form-item>
              </el-col>
              <el-col :span="12" class="mac">
                <el-form-item prop="mac" :label="$t('gateways.mac')">
                  <el-input
                    type="text"
                    v-model="record.mac"
                    :placeholder="$t('gateways.macRequired')"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="manufacturer" :label="$t('devices.manufacturer')">
                  <el-input
                    v-model="record.manufacturer"
                    type="text"
                    :placeholder="$t('devices.manufacturerRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="serialNumber" :label="$t('devices.serialNumber')">
                  <el-input
                    v-model="record.serialNumber"
                    type="text"
                    :placeholder="$t('devices.serialNumberRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="softVersion" :label="$t('devices.softVersion')">
                  <el-input
                    v-model="record.softVersion"
                    type="text"
                    :placeholder="$t('devices.softVersionRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="hardwareVersion" :label="$t('devices.hardwareVersion')">
                  <el-input
                    v-model="record.hardwareVersion"
                    type="text"
                    :placeholder="$t('devices.hardwareVersionRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="description" :label="$t('devices.description')">
                  <el-input
                    v-model="record.description"
                    type="text"
                    :placeholder="$t('devices.descriptionRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="location" :label="$t('devices.location')">
                  <el-input
                    v-model="record.location"
                    type="text"
                    :placeholder="$t('devices.locationRequired')"
                    @focus="$refs.locationSelect.dialogVisible = true">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="longitude" :label="$t('devices.longitude')">
                  <el-input type="number" v-model.number="record.longitude">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="latitude" :label="$t('devices.latitude')">
                  <el-input type="number" v-model.number="record.latitude">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="metaData" :label="$t('devices.metaData')">
                  <el-input type="text" v-model="record.metaData" @focus="metaDataVisible = true">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col class="device-console-ip" v-if="record.upLinkSystem !== Gateway" :span="12">
                <el-form-item prop="deviceConsoleIP" :label="$t('devices.deviceConsoleIP')">
                  <el-input v-model="record.deviceConsoleIP">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col class="device-console-username" v-if="record.upLinkSystem !== Gateway" :span="12">
                <el-form-item
                  prop="deviceConsoleUsername"
                  :label="$t('devices.deviceConsoleUsername')">
                  <el-input v-model="record.deviceConsoleUsername">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col class="device-console-port" v-if="record.upLinkSystem !== Gateway" :span="12">
                <el-form-item prop="deviceConsolePort" :label="$t('devices.deviceConsolePort')">
                  <el-input
                    v-model.number="record.deviceConsolePort"
                    type="number"
                    placeholder="22">
                  </el-input>
                </el-form-item>
              </el-col>
            </div>

            <!-- step 2 -->
            <div v-if="step === 2" class="devices-rows">
              <el-col class="auth-type" :span="12">
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
              <el-col v-if="record.authType === Cert"  :span="12">
                <el-form-item prop="certs" :label="$t('devices.certs')">
                  <emq-search-select
                    multiple
                    v-model="record.certs"
                    :field="{
                      url: `/emq_select/certs`,
                      searchKey: 'certName',
                    }"
                    :placeholder="$t('oper.select')">
                  </emq-search-select>
                </el-form-item>
              </el-col>

              <template v-if="cloudProtocol !== $variable.cloudProtocol.LORA">
                <el-col class="device-id" v-if="cloudProtocol !== $variable.cloudProtocol.LWM2M" :span="12">
                  <el-form-item prop="deviceID" :label="$t('devices.deviceID')">
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
                <el-col class="device-username" v-if="record.upLinkSystem !== Gateway" :span="12">
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
                <el-col class="token" v-if="record.upLinkSystem !== Gateway" :span="12">
                  <el-form-item prop="token" :label="$t('devices.token')">
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
              </template>

              <!-- step 2 loRa-->
              <template v-if="cloudProtocol === $variable.cloudProtocol.LORA">
                <!-- lora not gateway -->
                <div>
                  <el-col :span="12">
                    <el-form-item prop="loraData.type" :label="$t('devices.loraType')">
                      <emq-select
                        v-model="record.loraData.type"
                        :field="{ options: [
                          { label: 'OTAA', value: 'otaa' },
                          { label: 'ABP', value: 'abp' }
                        ] }"
                        :record="record.loraData"
                        :disabled="false"
                        @input="handleTypeSelected">
                      </emq-select>
                    </el-form-item>
                  </el-col>
                  <!-- abp device
                    DevAddr	deviceID 8
                    Region	region
                    NwkSKey	nwkSKey
                    AppSKey	appSKey
                    FCnt Up	fcntUp
                    FCnt Down	fcntDown
                    FCnt Check	fcntCheck
                  -->
                  <div v-if="record.loraData.type === 'abp'">
                    <el-col :span="12">
                      <el-form-item prop="deviceID" label="DevAddr">
                        <el-input v-model="record.deviceID" maxlength="8"></el-input>
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
                          :disabled="false">
                        </emq-select>
                      </el-form-item>
                    </el-col>
                  </div>
                  <!-- otaa device
                    DevEUI	deviceID 16
                    Region	region
                    AppEUI	appEUI
                    AppKey	appKey
                    FCnt Check	fcntCheck
                    Can Join	canJoin
                  -->
                  <div v-else-if="record.loraData.type === 'otaa'">
                    <el-col :span="12">
                      <el-form-item prop="deviceID" label="DevEUI">
                        <el-input
                          v-model="record.deviceID"
                          maxlength="16"
                          :placeholder="$t('devices.char16')"></el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item prop="loraData.region" :label="$t('devices.region')">
                        <emq-select
                          v-model="record.loraData.region"
                          :record="record.loraData"
                          :field="{ key: 'region' }"
                          :disabled="false">
                        </emq-select>
                      </el-form-item>
                    </el-col>
                    <el-col class="token" :span="12">
                      <el-form-item prop="token" label="token">
                        <el-input
                          v-model="record.token"
                          type="text"
                          :placeholder="$t('devices.deviceIDRequired')">
                        </el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item prop="loraData.fcntCheck" label="FCnt Check">
                        <emq-select
                          v-model="record.loraData.fcntCheck"
                          :record="record.loraData"
                          :field="{ key: 'fcntCheck' }"
                          :disabled="false">
                        </emq-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item prop="loraData.appEUI" label="AppEUI">
                        <el-input
                          v-model="record.loraData.appEUI"
                          maxlength="16"
                          :placeholder="$t('devices.char16')"></el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item prop="loraData.canJoin" :label="$t('devices.canJoin')">
                        <emq-select
                          v-model="record.loraData.canJoin"
                          :record="record.loraData"
                          :field="{
                            options: [
                              { label: $t('oper.isTrue'), value: 1 },
                              { label: $t('oper.isFalse'), value: 0 }
                            ]}"
                          :disabled="false">
                        </emq-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item prop="loraData.appKey" label="AppKey">
                        <el-input
                          v-model="record.loraData.appKey"
                          maxlength="32"
                          :placeholder="$t('devices.char32')"></el-input>
                      </el-form-item>
                    </el-col>
                  </div>
                </div>
              </template>
            </div>

          </el-form>
        </el-row>

        <!-- JSON Editor -->
        <emq-dialog
          v-model="tempMetaData"
          width="500px"
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
            v-model="tempMetaData">
          </code-editor>
        </emq-dialog>
      </el-card>

      <emq-button
        v-if="step === 2 || cloudProtocol === $variable.cloudProtocol.MODBUS"
        class="save"
        icon="save"
        :loading="btnLoaing"
        @click="save">
        {{ $t('oper.finish') }}
      </emq-button>

      <emq-button
        v-if="step === 1 && cloudProtocol !== $variable.cloudProtocol.MODBUS"
        class="next-step"
        @click="handleStep">
        {{ $t('devices.nextStep') }}
      </emq-button>

      <a
        v-if="step === 2"
        class="back-setup"
        href="javascript:;"
        @click="handleStep(false)">
        &lt;&lt; {{ $t('devices.backStep') }}
      </a>
    </div>

    <location-select-dialog ref="locationSelect" :confirm="locationSelectConfirm">
    </location-select-dialog>

  </div>
</template>


<script>
import { httpPost } from '@/utils/api'
import CodeEditor from '@/components/CodeEditor'
import EmqDialog from '@/components/EmqDialog'
import EmqButton from '@/components/EmqButton'
import EmqSelect from '@/components/EmqSelect'
import EmqSearchSelect from '@/components/EmqSearchSelect'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import CreateProducts from '../components/CreateProducts'
import LocationSelectDialog from '../components/LocationSelectDialog'

export default {
  name: 'devices-create-view',

  components: {
    EmqDialog,
    EmqDetailsPageHead,
    CreateProducts,
    EmqButton,
    EmqSelect,
    LocationSelectDialog,
    EmqSearchSelect,
    CodeEditor,
  },

  data() {
    const validModBusIndex = (rule, value, callback) => {
      if (value <= 255 && value >= 0) {
        callback()
      }
      callback(new Error(this.$t('devices.num0to255')))
    }
    return {
      productsDialogVisible: false,
      metaDataVisible: false,
      btnLoaing: false,
      url: '/devices',
      step: 1,
      Device: 2,
      Gateway: 3,
      Cert: 2,
      disabled: false,
      parentGatewayIntID: null,
      parentDeviceIntID: null,
      tempMetaData: JSON.stringify({}, null, 2), // Temporary meta data
      record: {
        productID: this.$route.query.productID,
        upLinkSystem: this.$route.query.upLinkSystem,
        parentDevice: this.$route.query.parentDevice,
        parentDeviceName: this.$route.query.parentDeviceName,
        gateway: this.$route.query.gateway,
        gatewayName: this.$route.query.gatewayName,
        deviceID: undefined,
        longitude: undefined,
        latitude: undefined,
        location: '',
        cloudProtocol: null,
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
      productSelectField: {
        url: '/emq_select/products?productType=1',
        options: [{
          value: this.$route.query.productID,
          label: this.$route.query.productName,
        }],
        searchKey: 'productName',
      },
      deviceInfoRules: {
        deviceName: [
          { required: true, message: this.$t('devices.deviceNameRequired') },
        ],
        productID: [
          { required: true, message: this.$t('devices.productNameRequired') },
        ],
        longitude: [
          { type: 'number', message: this.$t('devices.longitudeIsNumber') },
        ],
        latitude: [
          { type: 'number', message: this.$t('devices.latitudeIsNumber') },
        ],
        upLinkSystem: [
          { required: true, message: this.$t('devices.upLinkSystemRequired') },
        ],
        parentDevice: [
          { required: true, message: this.$t('devices.parentDeviceRequired') },
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
        modbusData: {
          modBusIndex: [
            { required: true, type: 'number', message: this.$t('devices.indexRequired') },
            { validator: validModBusIndex },
          ],
        },
        // step 2
        deviceID: { min: 8, max: 36, message: this.$t('devices.len8to36'), trigger: 'change' },
        authType: [
          { required: true, message: this.$t('devices.authTypeRequired') },
        ],
        certs: [
          { required: true, message: this.$t('devices.certsRequired') },
        ],
        deviceUsername: [
          { min: 8, max: 36, message: this.$t('devices.len8to36'), trigger: 'change' },
        ],
        token: [
          { min: 8, max: 36, message: this.$t('devices.len8to36'), trigger: 'change' },
        ],
        // lora
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
      },
      cloudProtocol: undefined,
    }
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
          // lora
          if (this.cloudProtocol === this.$variable.cloudProtocol.LORA) {
            this.handleTypeSelected('otaa')
          } else {
            this.deviceInfoRules.deviceID = { min: 8, max: 36, message: this.$t('devices.len8to36'), trigger: 'blur' }
          }
          this.step = 2
        })
      } else {
        this.step = 1
      }
    },

    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        this.btnLoading = true
        const record = { ...this.record }
        // Remove overfill fields
        if (this.cloudProtocol !== this.$variable.cloudProtocol.LORA) {
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
        if (this.cloudProtocol !== this.$variable.cloudProtocol.LWM2M) {
          delete record.lwm2mData
        }
        // ModBus Device
        if (this.cloudProtocol === this.$variable.cloudProtocol.MODBUS) {
          record.authType = 1
        } else {
          delete record.modbusData
        }
        if (this.parentDeviceIntID && record.upLinkSystem === this.Device) {
          record.parentDevice = this.parentDeviceIntID
        } else if (this.parentGatewayIntID && record.upLinkSystem === this.Gateway) {
          record.gateway = this.parentGatewayIntID
        }
        // Converts an empty string to a null
        Object.keys(record).forEach((key) => {
          if (record[key] === '') {
            record[key] = null
          }
        })
        httpPost(this.url, record).then(() => {
          const { fromURL } = this.$route.query
          this.$message.success(this.$t('oper.createSuccess'))
          if (fromURL) {
            this.$router.push({ path: fromURL })
          } else if (this.$route.query.productID) {
            if (this.$route.query.parentDevice) {
              this.$router.push({ path: `/devices/devices/${this.$route.query.parentDevice}/children` })
            } else {
              this.$router.push({ path: `/products/${this.$route.query.productIntID}/devices` })
            }
          } else if (this.$route.query.gateway) {
            this.$router.push({ path: `/devices/gateways/${this.$route.query.gateway}/devices` })
          } else {
            this.$router.push({ path: '/devices/devices' })
          }
          this.btnLoading = false
        })
        this.btnLoading = false
      })
    },

    locationSelectConfirm() {
      this.record.longitude = this.$refs.locationSelect.position.lng
      this.record.latitude = this.$refs.locationSelect.position.lat
      this.record.location = this.$refs.locationSelect.position.name
      this.$refs.locationSelect.dialogVisible = false
    },

    // Special treatment from the product details page
    handleProductProp() {
      if (this.$route.query.productID) {
        const value = this.$route.query.productID
        const productItem = {
          attr: {
            cloudProtocol: this.$route.query.cloudProtocol,
            productIntID: this.$route.query.productIntID,
          },
        }
        this.handleProductSelect(value, productItem)
      }
    },

    handleProductSelect(value, selectedItem) {
      if (!value) {
        return
      }
      if (selectedItem && selectedItem.attr) {
        const { cloudProtocol } = selectedItem.attr
        this.cloudProtocol = cloudProtocol
      }
    },

    handleTypeSelected(_type) {
      const type = this.record.loraData.type || _type
      if (!type) {
        return
      }
      // Clear input value and validation
      const fields = this.$refs.record.fields
      for (let i = 0; i < fields.length; i += 1) {
        if (fields[i].prop === 'deviceID') {
          // The input is determined by the unique prop property having the same value
          fields[i].resetField()
          break
        }
      }
      this.record.loraData = {
        type,
        fcntUp: 0,
        fcntDown: 0,
      }
      if (type === 'otaa') {
        this.deviceInfoRules.deviceID = [
          { required: true, message: this.$t('devices.DevEUIRequried') },
          { len: 16, message: this.$t('devices.DevEUILen16') },
        ]
        this.deviceInfoRules.token = [
          { min: 8, max: 36, message: this.$t('devices.len8to36'), trigger: 'change' },
          { required: true, message: this.$t('devices.tokenRequired') },
        ]
      } else {
        this.deviceInfoRules.deviceID = [
          { required: true, message: this.$t('devices.DevAddrRequired') },
          { len: 8, message: this.$t('devices.DevAddrLen8') },
        ]
        this.deviceInfoRules.token = [
          { min: 8, max: 36, message: this.$t('devices.len8to36'), trigger: 'change' },
        ]
      }
    },

    handleParentDevice(id, selectedItem) {
      if (!id) {
        return
      }
      this.parentDeviceIntID = selectedItem.attr.deviceIntID
    },

    handleParentGatway(id, selectedItem) {
      if (!id) {
        return
      }
      this.parentGatewayIntID = selectedItem.attr.deviceIntID
    },

    selectNewProduct(p) {
      const currentSelect = [
        {
          value: p.productID,
          label: p.productName,
          attr: { cloudProtocol: p.cloudProtocol },
        },
      ]
      this.handleProductSelect(p.productID, currentSelect[0])
      this.$refs.selectProduct.options = currentSelect
      setTimeout(() => {
        this.record.productID = p.productID
      }, 500)
    },

    saveMetaData() {
      this.record.metaData = this.tempMetaData
      this.metaDataVisible = false
    },
  },

  created() {
    this.handleProductProp()
  },

}
</script>


<style lang="scss">
.devices-create-view {
  .devices-card-details-body {
    .devices-rows {
      padding: 8px 20px 0;
    }
    .el-card {
      margin: 20px 0 20px 0;
      padding: 0 0 20px 0;
      .el-card__body {
        padding: 0;
        .el-form .el-form-item__label {
          color: var(--color-text-light);
          padding-bottom: 0;
        }
      }
      .product-button {
        color: var(--color-text-light);
        position: relative;
        top: 10px;
        float: right;
      }
      .meta-data__question {
        position: absolute;
        top: 20px;
        left: 116px;
      }
    }
    .back-setup {
      float: right;
      margin: 10px 25px 0 0;
    }
  }
  .form__tips {
    color: var(--color-text-lighter);
    position: relative;
    top: 2px;
  }
}
</style>
