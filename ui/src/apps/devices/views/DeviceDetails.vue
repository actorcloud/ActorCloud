<template>
  <div class="details-view device-details-view">
    <input
      v-model="clipboardContent"
      type="text"
      id="clipboard">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/devices` }">{{ $t('devices.device') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentDevice">{{ currentDevice.deviceName }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('resource.deviceInfo') }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div v-if="currentDevice" class="emq-tag-group" slot="tag">
        <emq-tag>{{ currentDevice.cloudProtocolLabel }}</emq-tag>
      </div>
    </emq-details-page-head>

    <div class="detail-tabs">
      <device-detail-tabs v-if="currentDevice"></device-detail-tabs>
    </div>

    <!-- Runing status -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="colSize">
        <el-card v-loading="loading" class="el-card__plain">
          <template slot="header">
            <span>{{ $t('devices.deviceStatus') }}</span>
          </template>
          <el-scrollbar>
            <el-form
              ref="record"
              label-position="left"
              class="details-running"
              :model="record"
              :disabled="disabled">
              <el-form-item :label="`${$t('devices.deviceStatusLabel')}：`">
                <template>
                  <span :class="[record.deviceStatus === 1 ? 'online' : 'offline' ]">
                    {{ record.deviceStatusLabel }}
                  </span>
                </template>
              </el-form-item>
              <el-form-item :label="`${$t('devices.connectedAt')}：`">
                <template>
                  <span>{{ record.connectedAt }}</span>
                </template>
              </el-form-item>
              <el-form-item :label="`${$t('devices.clientIP')}：`">
                <template>
                  <span>{{ record.clientIP }}</span>
                </template>
              </el-form-item>
              <el-form-item :label="`${$t('devices.keepAlive')}：`">
                <template>
                  <span>{{ record.keepAlive }}</span>
                </template>
              </el-form-item>
            </el-form>
          </el-scrollbar>
        </el-card>
      </el-col>

      <!-- Certification information -->
      <el-col :xs="24" :sm="colSize">
        <el-card v-loading="loading" class="el-card__plain">
          <template slot="header">
            <span>{{ $t('devices.deviceCode') }}</span>
            <el-popover placement="top" width="290" trigger="hover">
              <p>{{ $t('devices.mqttWarning') }}</p>
              <i slot="reference" class="el-icon-question"></i>
            </el-popover>
          </template>
          <el-scrollbar>
            <el-form label-position="left" class="details-code">
              <el-form-item :label="`${$t('devices.deviceID')}：`">
                <template>
                  <el-tooltip effect="dark" :content="clipboardStatus" placement="top">
                    <i
                      v-show="record.deviceID"
                      class="material-icons copy-icon"
                      @click="copyText(record.deviceID)">
                      check
                    </i>
                  </el-tooltip>
                  <span>{{ record.deviceID }}</span>
                </template>
              </el-form-item>
              <el-form-item :label="`${$t('devices.token')}：`">
                <template v-if="record.upLinkSystem !== Gateway">
                  <el-tooltip effect="dark" :content="clipboardStatus" placement="top">
                    <i
                      v-show="record.token"
                      class="material-icons copy-icon"
                      @click="copyText(record.token)">
                      check
                    </i>
                  </el-tooltip>
                  <span>{{ record.token }}</span>
                </template>
                <template v-else>
                  <span style="right: 0px"> — </span>
                </template>
              </el-form-item>
              <el-form-item :label="`${$t('devices.username')}：`">
                <template v-if="record.upLinkSystem !== Gateway">
                  <el-tooltip effect="dark" :content="clipboardStatus" placement="top">
                    <i
                      v-show="record.deviceUsername"
                      class="material-icons copy-icon"
                      @click="copyText(record.deviceUsername)">
                      check
                    </i>
                  </el-tooltip>
                  <span>{{ record.deviceUsername }}</span>
                </template>
                <template v-else>
                  <span style="right: 0px"> — </span>
                </template>
              </el-form-item>
            </el-form>
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>

    <!-- Device basic information -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="8">
        <el-card
          v-loading="loading"
          class="el-card__plain device-details"
          :class="{'is-details-form': disabled}">
          <template slot="header">
            <span>{{ $t('devices.deviceBaseInfo') }}</span>
            <a
              v-if="has(`PUT,/devices/:id`)"
              :class="['edit-toggle-button', disabled ? '' : 'active']"
              href="javascript:;"
              :title="disabled ? $t('oper.edit') : $t('oper.cancelEdit')"
              @click="showDetails('edit')">
              <i class="iconfont edit-icon__details icon-emq-edit"></i>
            </a>
          </template>
          <el-scrollbar :class="{ 'is-edit__scrollbar': !disabled }">
            <el-form
              ref="record"
              label-position="left"
              label-width="96px"
              size="medium"
              :class="{ 'is-disabled': disabled }"
              :disabled="disabled"
              :model="record"
              :rules="disabled ? {} : deviceInfoRules">
              <el-form-item prop="deviceName" :label="$t('devices.deviceName')">
                <el-input type="text" v-model="record.deviceName" :disabled="disabled">
                </el-input>
              </el-form-item>
              <el-form-item prop="productID" :label="$t('devices.productName')">
                <el-input v-if="!disabled" type="text" v-model="record.productName" disabled>
                </el-input>
                <router-link
                  v-else
                  style="margin-left: 0px;float: left;"
                  :to="{ path: `/products/${record.productIntID}` }">
                  {{ record.productName }}
                </router-link>
              </el-form-item>
              <!-- The device index of the ModBus protocol -->
              <el-form-item
                v-if="record.cloudProtocol === $variable.cloudProtocol.MODBUS"
                prop="modbusData.modBusIndex"
                :label="$t('devices.index')">
                <el-input
                  v-model.number="record.modbusData.modBusIndex"
                  type="number"
                  :placeholder="$t('devices.indexRequired')">
                </el-input>
              </el-form-item>
              <!-- Uplink system -->
              <el-form-item
                v-if="record.cloudProtocol !== $variable.cloudProtocol.LWM2M"
                prop="upLinkSystem"
                :label="this.$t('devices.upLinkSystem')">
                <emq-select
                  v-model="record.upLinkSystem"
                  :field="{ key: 'upLinkSystem' }"
                  :record="record"
                  :placeholder="disabled ? '' : $t('oper.select')"
                  :disabled="false">
                </emq-select>
              </el-form-item>
              <!-- Parent device -->
              <el-form-item
                v-if="record.upLinkSystem === Device
                && record.cloudProtocol !== $variable.cloudProtocol.LWM2M"
                prop="parentDevice"
                :label="$t('devices.parentDevice')">
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
              <el-form-item
                v-if="record.upLinkSystem === Gateway
                && record.cloudProtocol !== $variable.cloudProtocol.LORA"
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
              <!-- Auth type -->
              <el-form-item
                v-if="record.upLinkSystem !== Gateway"
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
              <el-form-item
                v-if="record.authType === Cert
                  && record.upLinkSystem !== Gateway"
                prop="certs"
                :label="$t('devices.certs')">
                <emq-search-select
                  v-if="!disabled"
                  ref="certsSelect"
                  class="multiple-select"
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
              <el-form-item class="groups" prop="groups" :label="$t('groups.group')">
                <emq-search-select
                  v-if="!disabled"
                  ref="groupSelect"
                  class="multiple-select"
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

              <!-- loRa device start -->
              <div v-if="record.cloudProtocol === $variable.cloudProtocol.LORA">
                <!-- lora not gateway -->
                <div>
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

                  <!-- abp device
                    DevAddr	deviceID 8
                    发射频率	region
                    NwkSKey	nwkSKey
                    AppSKey	appSKey
                    FCnt Up	fcntUp
                    FCnt Down	fcntDown
                    FCnt Check	fcntCheck
                  -->
                  <div v-if="record.loraData.type === 'abp'">
                    <el-form-item prop="gateway" :label="$t('devices.gateway')">
                      <emq-search-select
                        v-if="!disabled"
                        v-model="record.gateway"
                        :placeholder="$t('oper.gatewaySearch')"
                        :field="{
                            url: '/emq_select/devices',
                            params: { deviceType: 2 },
                            searchKey: 'gatewayName',
                          }"
                        :record="record.loraData"
                        :disabled="disabled">
                      </emq-search-select>
                      <router-link
                        v-else
                        style="margin-left: 0px;float: left;"
                        :to="{ path: `/devices/gateways/${record.gateway}` }">
                        {{ record.gatewayName }}
                      </router-link>
                    </el-form-item>
                    <el-form-item prop="deviceID" label="DevAddr" :rules="deviceInfoRules.devAddr">
                      <el-input disabled v-model="record.deviceID"></el-input>
                    </el-form-item>
                    <el-form-item prop="loraData.region" :label="$t('devices.region')">
                      <el-input v-model="record.loraData.region"></el-input>
                    </el-form-item>
                    <el-form-item prop="loraData.nwkSKey" label="NwkSKey">
                      <el-input v-model="record.loraData.nwkSKey" maxlength="32"></el-input>
                    </el-form-item>
                    <el-form-item prop="loraData.appSKey" label="AppSKey">
                      <el-input v-model="record.loraData.appSKey" maxlength="32"></el-input>
                    </el-form-item>
                    <el-form-item prop="loraData.fcntUp" label="FCnt Up">
                      <el-input v-model.number="record.loraData.fcntUp" type="number"></el-input>
                    </el-form-item>
                    <el-form-item prop="loraData.fcntDown" label="FCnt Down">
                      <el-input v-model.number="record.loraData.fcntDown" type="number"></el-input>
                    </el-form-item>
                    <el-form-item prop="loraData.fcntCheck" label="FCnt Check">
                      <emq-select
                        v-model="record.loraData.fcntCheck"
                        :record="record.loraData"
                        :field="{ key: 'fcntCheck' }"
                        :disabled="disabled">
                      </emq-select>
                    </el-form-item>
                  </div>

                  <!-- otaa device
                    DevEUI	deviceID 16
                    Region	region
                    AppEUI	appEUI
                    AppKey	appKey
                    FCnt Check	fcntCheck
                    Allowed to join	canJoin
                   -->
                  <div v-else-if="record.loraData.type === 'otaa'">
                    <el-form-item prop="gateway" :label="$t('devices.gateway')">
                      <emq-search-select
                        v-if="!disabled"
                        v-model="record.gateway"
                        :placeholder="$t('oper.gatewaySearch')"
                        :field="{
                            url: '/emq_select/devices',
                            params: { deviceType: 2 },
                            searchKey: 'gatewayName',
                          }"
                        :record="record.loraData"
                        :disabled="disabled">
                      </emq-search-select>
                      <router-link
                        v-else
                        style="margin-left: 0px;float: left;"
                        :to="{ path: `/devices/gateways/${record.gateway}` }">
                        {{ record.gatewayName }}
                      </router-link>
                    </el-form-item>
                    <el-form-item prop="deviceID" label="DevEUI" :rules="deviceInfoRules.devEUI">
                      <el-input disabled v-model="record.deviceID"></el-input>
                    </el-form-item>
                    <el-form-item prop="loraData.region" :label="$t('devices.region')">
                      <emq-select
                        v-model="record.loraData.region"
                        :record="record.loraData"
                        :field="{ key: 'region' }"
                        :disabled="disabled">
                      </emq-select>
                    </el-form-item>
                    <el-form-item prop="loraData.appEUI" label="AppEUI">
                      <el-input v-model="record.loraData.appEUI" maxlength="16"></el-input>
                    </el-form-item>
                    <el-form-item prop="loraData.fcntCheck" label="FCnt Check">
                      <emq-select
                        v-model="record.loraData.fcntCheck"
                        :record="record.loraData"
                        :field="{ key: 'fcntCheck' }"
                        :disabled="disabled">
                      </emq-select>
                    </el-form-item>
                    <el-form-item prop="loraData.appKey" label="AppKey">
                      <el-input v-model="record.loraData.appKey" maxlength="32"></el-input>
                    </el-form-item>
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
                  </div>
                </div>
              </div>
              <!-- loRa device end -->

              <el-form-item
                v-if="record.cloudProtocol === $variable.cloudProtocol.LWM2M"
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
              <el-form-item
                v-if="record.cloudProtocol === $variable.cloudProtocol.LWM2M"
                prop="lwm2mData.IMSI"
                label="IMSI">
                <el-input
                  type="text"
                  disabled
                  v-model="record.lwm2mData.IMSI"
                  :placeholder="disabled ? '' : $t('devices.IMSIRequired')">
                </el-input>
              </el-form-item>
              <el-form-item prop="carrier" :label="$t('devices.carrier')">
                <emq-select
                  v-model="record.carrier"
                  :field="{ key: 'carrier' }"
                  :record="record"
                  :placeholder="disabled ? '' : $t('oper.select')"
                  :disabled="false">
                </emq-select>
              </el-form-item>
              <el-form-item prop="physicalNetwork" :label="$t('devices.physicalNetwork')">
                <emq-select
                  v-model="record.physicalNetwork"
                  :field="{ key: 'physicalNetwork' }"
                  :record="record"
                  :placeholder="disabled ? '' : $t('oper.select')"
                  :disabled="false">
                </emq-select>
              </el-form-item>
              <el-form-item prop="description" :label="$t('devices.description')">
                <el-input type="text" v-model="record.description" :disabled="disabled">
                </el-input>
              </el-form-item>
              <el-form-item prop="serialNumber" :label="$t('devices.serialNumber')">
                <el-input type="text" v-model="record.serialNumber" :disabled="disabled">
                </el-input>
              </el-form-item>
              <el-form-item prop="softVersion" :label="$t('devices.softVersion')">
                <el-input type="text" v-model="record.softVersion" :disabled="disabled">
                </el-input>
              </el-form-item>
              <el-form-item prop="hardwareVersion" :label="$t('devices.hardwareVersion')">
                <el-input type="text" v-model="record.hardwareVersion" :disabled="disabled">
                </el-input>
              </el-form-item>
              <el-form-item prop="manufacturer" :label="$t('devices.manufacturer')">
                <el-input type="text" v-model="record.manufacturer" :disabled="disabled">
                </el-input>
              </el-form-item>
              <el-form-item prop="metaData" :label="$t('devices.metaData')">
                <el-input v-if="!disabled" type="text" v-model="record.metaData" @focus="openMetaDataDialog">
                </el-input>
                <el-tag v-else>
                  <a href="javascript:;" @click="openMetaDataDialog">{{ $t('oper.clickView') }}</a>
                </el-tag>
              </el-form-item>
              <el-form-item
                v-if="record.upLinkSystem !== Gateway"
                prop="deviceConsoleIP"
                :label="$t('devices.deviceConsoleIP')">
                <el-input v-model="record.deviceConsoleIP">
                </el-input>
              </el-form-item>
              <el-form-item
                v-if="record.upLinkSystem !== Gateway"
                prop="deviceConsolePort"
                :label="$t('devices.deviceConsolePort')">
                <el-input v-model.number="record.deviceConsolePort" type="number" placeholder="22">
                </el-input>
              </el-form-item>
              <el-form-item
                v-if="record.upLinkSystem !== Gateway"
                prop="deviceConsoleUsername"
                :label="$t('devices.deviceConsoleUsername')">
                <el-input v-model="record.deviceConsoleUsername">
                </el-input>
              </el-form-item>
              <el-form-item prop="createAt" v-if="disabled" :label="$t('devices.createAt')">
                <el-input type="text" v-model="record.createAt" :disabled="disabled">
                </el-input>
              </el-form-item>
              <el-form-item v-if="disabled" prop="createUser" :label="$t('devices.createUser')">
                <el-input type="text" v-model="record.createUser" :disabled="disabled">
                </el-input>
              </el-form-item>
              <div style="clear: both;"></div>
            </el-form>
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
          </el-scrollbar>

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
              v-model="tempMetaData"
              :disabled="disabled">
            </code-editor>
          </emq-dialog>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="16">
        <el-card v-loading="mapLoading" class="el-card__plain map-content">
          <template slot="header">
            <span>{{ $t('devices.locationInfo') }}</span>
            <a
              v-if="has(`PUT,/devices/:id`)"
              :class="['edit-toggle-button', mapVisible ? '' : 'active']"
              href="javascript:;"
              :title="mapVisible ? $t('oper.edit') : $t('oper.cancelEdit')"
              @click="editLocation">
              <i class="iconfont edit-icon__details icon-emq-edit"></i>
            </a>
          </template>
          <!-- Location Map -->
          <el-amap
            v-show="mapVisible"
            vid="amap-detail"
            style="height: 100%;"
            :center="center"
            :zoom="12">
            <el-amap-circle
              v-for="(circle, index) in circles"
              fillColor="#89b283"
              :key="`circle-${index}`"
              :center="circle.center"
              :radius="circle.radius * 1000"
              :fill-opacity="circle.fillOpacity">
            </el-amap-circle>
            <el-amap-polygon
              v-for="(polygon, index) in polygons"
              fillColor="#89b283"
              :key="`polygon-${index}`"
              :vid="index"
              :ref="`polygon_${index}`"
              :path="polygon.path"
              :draggable="polygon.draggable"
              :events="polygon.events">
            </el-amap-polygon>
            <el-amap-marker v-for="(marker, index) in markers" :key="index" :position="marker">
            </el-amap-marker>
            <el-amap-info-window
              v-for="window in windows"
              :key="window.index"
              :position="window.position"
              :content="window.content">
            </el-amap-info-window>
          </el-amap>
          <div v-if="!mapVisible" class="warp">
            <el-form
              label-position="left"
              label-width="96px"
              size="medium"
              :model="record">
              <el-form-item prop="location" :label="$t('devices.location')">
                <el-popover
                  ref="deviceLocation"
                  placement="right"
                  width="360"
                  trigger="hover">
                  <p>{{ $t('devices.locationPopover') }}</p>
                </el-popover>
                <a href="javascript:;" v-popover:deviceLocation class="location-location-question">
                  <i class="el-icon-question" style="color: #888;"></i>
                </a>
                <el-input
                  type="text"
                  v-model="record.location"
                  @focus="$refs.locationSelect.dialogVisible = true">
                </el-input>
              </el-form-item>
              <el-form-item prop="longitude" :label="$t('devices.longitude')">
                <el-input type="text" v-model="record.longitude"></el-input>
              </el-form-item>
              <el-form-item prop="latitude" :label="$t('devices.latitude')">
                <el-input type="text" v-model="record.latitude"></el-input>
              </el-form-item>
            </el-form>
            <emq-button icon="save" :loading="btnLoading" @click="updateLocation">
              {{ $t('oper.save') }}
            </emq-button>
            <el-button
              type="text"
              size="small"
              style="float: right;"
              @click="editLocation">
              {{ $t('oper.cancel') }}
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <location-select-dialog
      ref="locationSelect"
      :deviceLocation="center"
      :confirm="locationSelectConfirm">
    </location-select-dialog>

  </div>
</template>


<script>
import { httpGet, httpPut } from '@/utils/api'
import { currentDevicesMixin } from '@/mixins/currentDevices'
import CodeEditor from '@/components/CodeEditor'
import EmqDialog from '@/components/EmqDialog'
import EmqButton from '@/components/EmqButton'
import EmqSelect from '@/components/EmqSelect'
import EmqSearchSelect from '@/components/EmqSearchSelect'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqTag from '@/components/EmqTag'
import DeviceDetailTabs from '../components/DeviceDetailTabs'
import LocationSelectDialog from '../components/LocationSelectDialog'

export default {
  name: 'device-details-view',

  mixins: [currentDevicesMixin],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqSelect,
    EmqSearchSelect,
    EmqTag,
    DeviceDetailTabs,
    LocationSelectDialog,
    CodeEditor,
    EmqDialog,
  },

  data() {
    const validModBusIndex = (rule, value, callback) => {
      if (value <= 255 && value >= 0) {
        callback()
      }
      callback(new Error(this.$t('devices.num0to255')))
    }
    return {
      url: '/devices',
      tempDevice: {},
      btnLoading: false,
      loading: false,
      mapLoading: false,
      metaDataVisible: false,
      tempMetaData: JSON.stringify({}, null, 2), // Temporary meta data
      deviceId: undefined,
      parentGatewayIntID: null,
      parentDeviceIntID: null,
      Device: 2,
      Gateway: 3,
      Cert: 2,
      disabled: this.$route.query.oper !== 'edit',
      mapVisible: true,
      colSize: 12,
      record: {
        groups: [],
        deviceType: 1,
      },
      circles: [],
      polygons: [],
      markers: [],
      center: [116.397477, 39.908692],
      windows: [],
      stashRecord: {},
      // Device certification information
      clipboardContent: '',
      clipboardStatus: this.$t('oper.copy'),
      lwm2mData: {},
      loraData: {
        type: 'otaa',
        fcntUp: 0,
        fcntDown: 0,
      },
      modbusData: {},
      deviceInfoRules: {
        deviceID: { required: true, message: '请输入' },
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
        modbusData: {
          modBusIndex: [
            { required: true, type: 'number', message: this.$t('devices.indexRequired') },
            { validator: validModBusIndex },
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
        devEUI: [
          { required: true, message: this.$t('devices.DevEUIRequried') },
          { len: 16, message: this.$t('devices.DevEUILen16') },
        ],
        devAddr: [
          { required: true, message: this.$t('devices.DevAddrRequired') },
          { len: 8, message: this.$t('devices.DevAddrLen8') },
        ],
      },
    }
  },

  computed: {
    isDarkTheme() {
      return this.$store.state.accounts.currentTheme === 'dark'
    },
  },

  watch: {
    '$route.params.id': 'loadRecord',
    disabled(newValue) {
      if (!newValue) {
        setTimeout(() => { this.processLoadedData(this.record) }, 10)
      }
    },
  },

  methods: {
    // Map markers
    markMap() {
      this.markers = []
      if (this.record.longitude && this.record.latitude) {
        const lnglatXY = [this.record.longitude, this.record.latitude]
        this.center = lnglatXY // If there is a device location, the center of the map is the device location
        this.markers.push(lnglatXY)
        this.$refs.locationSelect.markers = [lnglatXY]
        this.$refs.locationSelect.mapCenter = lnglatXY
        // Get the address information by latitude and longitude and display it on the map
        // eslint-disable-next-line
        const geocoder = new AMap.Geocoder({
          radius: 1000,
          extensions: 'all',
        })
        geocoder.getAddress(lnglatXY, (status, result) => {
          if (status === 'complete' && result.info === 'OK') {
            this.record.location = result.regeocode.formattedAddress
            this.windows.push({
              position: lnglatXY,
              content: `
              ${this.$t('devices.location')}: ${this.record.location}
              `,
            })
            this.mapLoading = false
          } else {
            this.windows.push({
              position: lnglatXY,
              content: `
              ${this.$t('devices.location')}: (${this.$t('devices.unableLocation')}!)
              `,
            })
            this.mapLoading = false
          }
        })
      } else {
        // If there is no device location，the center of the map is set to the location of the first fence
        // The first point of a polygon or the center of a circle
        this.center = this.record.scopes[0][0]
        this.mapLoading = false
      }
    },

    loadRecord() {
      this.mapLoading = true
      this.deviceId = this.$route.params.id
      httpGet(`${this.url}/${this.deviceId}`).then((res) => {
        this.record = res.data
        this.processLoadedData(this.record)
        this.loading = false
        this.mapLoading = false
        if (!this.currentDevice) {
          this.localCache(this.record)
        }
        this.record.scopes.forEach((item) => {
          if (item.length === 2) { // Circular fence
            this.circles.push({ center: item[0], radius: item[1] })
          } else if (item.length > 2) { // Polygonal fence
            this.polygons.push({ path: item })
          }
        })
        this.markMap()
      }).catch(() => {
        this.loading = false
        this.mapLoading = false
      })
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

    editLocation() {
      if (this.mapVisible) {
        this.stashRecord = { ...this.record }
      } else if (this.stashRecord.id) {
        this.record = { ...this.stashRecord }
      }
      this.mapVisible = !this.mapVisible
    },

    updateLocation() {
      this.btnLoading = true
      const data = { ...this.record }
      // Strictly deserialize into array transfers
      try {
        data.locationScope = JSON.parse(data.locationScope)
        if (!Array.isArray(data.locationScope)) {
          throw new TypeError(`locationScope ${this.$t('devices.typeError')}`)
        }
      } catch (e) {
        data.locationScope = null
      }
      delete data.location
      httpPut(`/devices/${this.deviceId}/location`, data).then(() => {
        this.$message.success(this.$t('oper.editSuccess'))
        this.btnLoading = false
        this.mapVisible = true
        this.loadRecord()
        this.markMap()
      }).catch(() => {
        this.btnLoading = false
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
        httpPut(`${this.url}/${this.deviceId}`, data).then(() => {
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
          this.loadRecord()
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
      return record
    },

    locationSelectConfirm() {
      this.record.longitude = this.$refs.locationSelect.position.lng
      this.record.latitude = this.$refs.locationSelect.position.lat
      this.record.location = this.$refs.locationSelect.position.name
      this.$refs.locationSelect.dialogVisible = false
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
      // After saves the data, go back to the view page
      this.isRenderToList = false
    },

    copyText(content) {
      this.clipboardContent = content
      this.clipboardStatus = this.$t('oper.copySuccess')
      setTimeout(() => {
        document.querySelector('#clipboard').select()
        document.execCommand('Copy')
        setTimeout(() => {
          this.clipboardStatus = this.$t('oper.copy')
        }, 500)
      }, 500)
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
    this.loadRecord()
  },
}
</script>


<style lang="scss">
.device-details-view {
  #clipboard {
    position: absolute;
    z-index: -1;
  }
  .details-running {
    .el-form-item {
      margin-bottom: 0;
    }
  }
  .details-code {
    padding-bottom: 25px;
    .el-form-item {
      margin-bottom: 5px;
      .el-form-item__content {
        line-height: 40px;
        span {
          color: var(--color-text-default);
          position: relative;
          right: 17px;
        }
      }
      .copy-icon {
        display: inline-block;
        position: relative;
        top: 5px;
        right: 17px;
        margin-right: 4px;
        color: var(--color-main-green);
        font-size: 24px;
        cursor: pointer;
      }
    }
  }
  .is-details-form .group .el-tag {
    margin-right: 8px;
  }
  .el-card {
    .group .el-input {
      height: auto;
    }
    .btn-bar {
      padding: 0 4px 8px 0;
      overflow: hidden;
    }
    .meta-data__question {
      position: absolute;
      top: 20px;
      left: 116px;
    }
    &.el-card__plain {
      margin-bottom: 20px;
      min-height: 226px;
      white-space: nowrap;
      overflow-x: scroll;
      .el-card__header {
        border-bottom: none;
        font-size: 16px;
        .el-icon-question {
          color: var(--color-text-light);
          cursor: pointer;
          margin-left: 4px;
        }
      }
      .el-card__body {
        padding: 0 20px 10px;
      }
    }
    &.device-details {
      .el-card__body {
        height: 432px;
        overflow: hidden;
        padding-right: 0;
        .is-edit__scrollbar {
          .el-scrollbar__view {
            padding: 0 22px 0 12px;
            width: auto !important;
          }
          .el-scrollbar__bar.is-horizontal {
            display: none;
          }
        }
      }
      @media (min-height: 1000px) {
        .el-card__body {
          height: 800px;
          overflow: hidden;
          padding-right: 0;
        }
      }
    }
    &.map-content {
      .el-card__body {
        padding: 0;
        height: 442px;
      }
      @media (min-height: 1000px) {
        .el-card__body {
          height: 810px;
          padding: 0;
        }
      }
      .warp {
        height: 388px;
        padding: 0 20px 10px;
        .el-form {
          height: 100%;
        }
      }
    }
  }
  .list-wrap {
    .list-item {
      height: 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: var(--color-text-light);
      .list-item__title {
        font-weight: 400;
        margin-right: 10px;
        width: 110px;
      }
      .list-item__create {
        margin-left: 10px;
      }
    }
  }
  .blank-block {
    height: 160px;
    width: 100%;
    text-align: center;
    color: var(--color-text-default);
    font-size: 16px;
    img {
      width: 100px;
    }
  }
  .location-location-question,
  .location-scope-question {
    position: absolute;
    left: -30px;
    z-index: 999;
  }
  .details-running {
    span {
      color: var(--color-text-lighter);
    }
    .offline {
      color: var(--color-main-pink);
    }
    .online {
      color: var(--color-main-green);
    }
  }
  .device-detail-tabs {
    margin-bottom: 20px;
    border-bottom: 1px solid var(--color-line-card);
    line-height: 50px;
    .crud-title {
      font-size: 16px;
      display: inline-block;
    }
  }
  .el-card {
    position: relative;
    .edit-toggle-button {
      width: 24px;
      height: 24px;
      line-height: 24px;
      text-align: center;
      top: 14px;
      right: 20px;
      position: absolute;
      z-index: 1;
      background: linear-gradient(180deg,rgba(51,199,145,1) 0%,rgba(14,192,125,1) 100%);
      border-radius: 50%;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      color: #fff;
      &:hover {
        box-shadow: 0 2px 12px 4px rgba(0, 0, 0, 0.1);
      }
      &.active {
        background: var(--color-bg-tag);
      }
    }
  }
  .el-button--text {
    font-size: 14px;
    margin-right: 24px;
  }
  .el-pagination.is-background {
    margin: 20px 0;
    float: right;
  }
  .child-list {
    .default-header {
      display: none;
    }
  }
}
</style>
