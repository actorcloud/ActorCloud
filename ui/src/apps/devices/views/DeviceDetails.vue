<template>
  <div class="details-view device-details-view">

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
            <span>设备状态</span>
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
      <el-col :xs="24" :sm="colSize">
        <el-card v-loading="loading" class="el-card__plain">
          <template slot="header">
            <span>连接日志</span>
            <router-link
              v-if="logData.count > 4"
              :to="{ path: '/device_logs/connect_logs', query: { deviceID: record.deviceID } }">
              查看更多
            </router-link>
          </template>
          <el-scrollbar>
            <div v-if="logData.items.length > 0" class="list-wrap">
              <div v-for="(item, index) in logData.items" class="list-item" :key="index">
                <div class="list-item__title">{{ item.IP }}</div>
                <div class="list-item__label">{{ item.connectStatusLabel }}</div>
                <div class="list-item__create">{{ item.createAt }}</div>
              </div>
            </div>
            <div v-else class="blank-block">
              <img v-if="isDarkTheme" src="../assets/images/log-dark.png">
              <img v-else src="../assets/images/log.png">
              <p>暂无运行日志</p>
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>
      <el-col v-if="has('GET,/current_alerts')" :xs="24" :sm="colSize">
        <el-card v-loading="loading" class="el-card__plain">
          <template slot="header">
            <span>设备告警</span>
            <router-link
              v-if="alertData.count > 4"
              :to="{ path: '/current_alerts', query: { deviceID: record.deviceID } }">
              查看更多
            </router-link>
          </template>
          <el-scrollbar>
            <div v-if="alertData.items.length > 0" class="list-wrap">
              <div v-for="(item, index) in alertData.items" class="list-item" :key="index">
                <div class="list-item__title">{{ item.alertName }}</div>
                <div :class="`${colorsDict[item.alertSeverity]}`">
                  {{ item.alertSeverityLabel }}
                </div>
                <div>{{ item.startTime }}</div>
              </div>
            </div>
            <div v-else class="blank-block">
              <img v-if="isDarkTheme" src="../assets/images/alert-dark.png">
              <img v-else src="../assets/images/alert.png">
              <p>暂无告警消息</p>
            </div>
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
            <span>设备基础信息</span>
            <a
              v-if="has(`PUT,/devices/:id`)"
              :class="['edit-toggle-button', disabled ? '' : 'active']"
              href="javascript:;"
              :title="disabled ? '编辑' : '取消编辑'"
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
                <el-input type="text" v-model="record.deviceName" :disabled="disabled"></el-input>
              </el-form-item>
              <el-form-item prop="productID" :label="$t('devices.productName')">
                <el-input v-if="!disabled" type="text" v-model="record.productName" disabled></el-input>
                <router-link
                  v-else
                  style="margin-left: 0px;float: left;"
                  :to="{ path: `/products/${record.productIntID}` }">
                  {{ record.productName }}
                </router-link>
              </el-form-item>
              <!-- The device index of the ModBus protocol -->
              <el-form-item v-if="record.cloudProtocol === ModBus" prop="modBusIndex" label="索引">
                <el-input
                  v-model.number="record.modBusIndex"
                  type="number"
                  placeholder="请输入索引 (0-255)">
                </el-input>
              </el-form-item>
              <!-- Device type -->
              <el-form-item prop="deviceType" :label="$t('devices.deviceType')">
                <emq-select
                  v-if="!disabled"
                  v-model="record.deviceType"
                  :field="{ key: 'deviceType' }"
                  :record="record"
                  :disabled="disabled || record.deviceType === 2">
                </emq-select>
                <el-tag v-else size="small">
                  {{ record.deviceTypeLabel }}
                </el-tag>
              </el-form-item>
              <!-- Uplink system -->
              <el-form-item
                v-if="record.deviceType === 1 && record.cloudProtocol !== LWM2M"
                prop="upLinkSystem"
                label="上联系统">
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
                v-if="record.deviceType === 1
                && record.upLinkSystem === 3
                && record.cloudProtocol !== LWM2M"
                prop="parentDevice"
                label="所属设备">
                <emq-search-select
                  v-model="record.parentDevice"
                  :placeholder="disabled ? '' : '请输入设备名称搜索'"
                  :field="{
                    url: '/emq_select/devices',
                    options: [{ value: record.parentDevice, label: record.parentDeviceName }],
                    searchKey: 'deviceName',
                  }"
                  :record="record"
                  :disabled="!!$route.query.gateway || !!$route.query.parentDevice">
                </emq-search-select>
              </el-form-item>
              <el-form-item
                v-if="record.deviceType === 1
                && record.upLinkSystem === 2
                && record.cloudProtocol !== loRa"
                prop="gateway"
                label="所属网关">
                <emq-search-select
                  v-if="!disabled"
                  v-model.number="record.gateway"
                  :placeholder="disabled ? '' : '请输入网关名称搜索'"
                  :field="{
                    url: '/emq_select/gateways',
                    options: [{ value: record.gateway, label: record.gatewayName }],
                    searchKey: 'gatewayName',
                  }"
                  :record="record"
                  :disabled="disabled">
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
                v-if="record.cloudProtocol !== loRa
                  && record.cloudProtocol !== ModBus
                  && record.upLinkSystem !== GateWay"
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
                  <span
                    style="float: none;"
                    v-for="tag in record.tagIndex"
                    :key="tag.value">
                    <el-tag size="small">
                      {{ tag.label }}
                    </el-tag>
                  </span>
                </div>
              </el-form-item>

              <!-- loRa device start -->
              <div v-if="record.cloudProtocol === loRa">
                <!-- loRa gateway -->
                <div v-if="record.deviceType === 2">
                  <!-- MAC -->
                  <el-form-item prop="deviceID" :rules="deviceInfoRules.macAddress" label="MAC">
                    <el-input disabled v-model="record.deviceID"></el-input>
                  </el-form-item>
                  <!-- Net ID -->
                  <el-form-item prop="lora.netID" label="网络 ID">
                    <el-input v-model="record.lora.netID"></el-input>
                  </el-form-item>
                  <!-- chain -->
                  <el-form-item prop="lora.txChain" label="链">
                    <el-input v-model.number="record.lora.txChain" type="number"></el-input>
                  </el-form-item>
                </div>

                <!-- lora not gateway -->
                <div v-else>
                  <el-form-item prop="lora.type" label="入网方式">
                    <emq-select
                      v-model="record.lora.type"
                      :field="{ options: [
                        { label: 'OTAA', value: 'otaa' },
                        { label: 'ABP', value: 'abp' }]
                      }"
                      :record="record.lora"
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
                  <div v-if="record.lora.type === 'abp'">
                    <el-form-item prop="gateway" label="所属网关">
                      <emq-search-select
                        v-if="!disabled"
                        v-model="record.gateway"
                        placeholder="请输入网关名称搜索"
                        :field="{
                            url: '/emq_select/gateways',
                            searchKey: 'gatewayName',
                          }"
                        :record="record.lora"
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
                    <el-form-item prop="lora.region" label="发射频率">
                      <el-input v-model="record.lora.region"></el-input>
                    </el-form-item>
                    <el-form-item prop="lora.nwkSKey" label="NwkSKey">
                      <el-input v-model="record.lora.nwkSKey" maxlength="32"></el-input>
                    </el-form-item>
                    <el-form-item prop="lora.appSKey" label="AppSKey">
                      <el-input v-model="record.lora.appSKey" maxlength="32"></el-input>
                    </el-form-item>
                    <el-form-item prop="lora.fcntUp" label="FCnt Up">
                      <el-input v-model.number="record.lora.fcntUp" type="number"></el-input>
                    </el-form-item>
                    <el-form-item prop="lora.fcntDown" label="FCnt Down">
                      <el-input v-model.number="record.lora.fcntDown" type="number"></el-input>
                    </el-form-item>
                    <el-form-item prop="lora.fcntCheck" label="FCnt Check">
                      <emq-select
                        v-model="record.lora.fcntCheck"
                        :record="record.lora"
                        :field="{ key: 'fcntCheck' }"
                        :disabled="disabled">
                      </emq-select>
                    </el-form-item>
                  </div>

                  <!-- otaa 设备
                    DevEUI	deviceID 16
                    Region	region
                    AppEUI	appEUI
                    AppKey	appKey
                    FCnt Check	fcntCheck
                    Allowed to join	canJoin
                   -->
                  <div v-else-if="record.lora.type === 'otaa'">
                    <el-form-item prop="gateway" label="所属网关">
                      <emq-search-select
                        v-if="!disabled"
                        v-model="record.gateway"
                        placeholder="请输入网关名称搜索"
                        :field="{
                            url: '/emq_select/gateways',
                            searchKey: 'gatewayName',
                          }"
                        :record="record.lora"
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
                    <el-form-item prop="lora.region" label="发射频率">
                      <emq-select
                        v-model="record.lora.region"
                        :record="record.lora"
                        :field="{ key: 'region' }"
                        :disabled="disabled">
                      </emq-select>
                    </el-form-item>
                    <el-form-item prop="lora.appEUI" label="AppEUI">
                      <el-input v-model="record.lora.appEUI" maxlength="16"></el-input>
                    </el-form-item>
                    <el-form-item prop="lora.fcntCheck" label="FCnt Check">
                      <emq-select
                        v-model="record.lora.fcntCheck"
                        :record="record.lora"
                        :field="{ key: 'fcntCheck' }"
                        :disabled="disabled">
                      </emq-select>
                    </el-form-item>
                    <el-form-item prop="lora.appKey" label="AppKey">
                      <el-input v-model="record.lora.appKey" maxlength="32"></el-input>
                    </el-form-item>
                    <el-form-item prop="lora.canJoin" label="允许加入">
                      <emq-select
                        v-model="record.lora.canJoin"
                        :record="record.lora"
                        :field="{ options: [
                          { label: '是', value: 1 },
                          { label: '否', value: 0 }]
                          }"
                        :disabled="disabled">
                      </emq-select>
                    </el-form-item>
                  </div>
                </div>
              </div>
              <!-- loRa device end -->

              <el-form-item prop="IMEI" label="IMEI">
                <el-input
                  type="text"
                  maxlength="15"
                  disabled
                  v-model="record.IMEI"
                  :placeholder="disabled ? '' : '请输入设备IMEI'">
                </el-input>
              </el-form-item>
              <el-form-item prop="IMSI" label="IMSI">
                <el-input
                  type="text"
                  v-model="record.IMSI"
                  :placeholder="disabled ? '' : '请输入设备IMSI'">
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
              <el-form-item prop="metaData" label="元数据">
                <el-input v-if="!disabled" type="text" v-model="record.metaData" @focus="openMetaDataDialog">
                </el-input>
                <el-tag v-else>
                  <a href="javascript:;" @click="openMetaDataDialog">点击查看</a>
                </el-tag>
              </el-form-item>
              <el-form-item
                v-if="record.upLinkSystem !== GateWay"
                prop="deviceConsoleIP"
                :label="$t('devices.deviceConsoleIP')">
                <el-input v-model="record.deviceConsoleIP">
                </el-input>
              </el-form-item>
              <el-form-item
                v-if="record.upLinkSystem !== GateWay"
                prop="deviceConsolePort"
                :label="$t('devices.deviceConsolePort')">
                <el-input v-model.number="record.deviceConsolePort" type="number" placeholder="22">
                </el-input>
              </el-form-item>
              <el-form-item
                v-if="record.upLinkSystem !== GateWay"
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
            title="元数据信息"
            :visible.sync="metaDataVisible"
            @confirm="saveMetaData"
            @close="metaDataVisible = false">
            <el-popover placement="right" width="280" trigger="hover">
              <p>您可以添加元数据以定义设备的定制属性，只能以 JSON 格式输入元数据。</p>
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
            <span>位置信息</span>
            <a
              v-if="has(`PUT,/devices/:id`)"
              :class="['edit-toggle-button', mapVisible ? '' : 'active']"
              href="javascript:;"
              :title="mapVisible ? '编辑' : '取消编辑'"
              @click="editLocation">
              <i class="iconfont edit-icon__details icon-emq-edit"></i>
            </a>
          </template>
          <!-- 设备位置地图 -->
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
                  <p>您可以通过在地图上直接选点来选择设备所在的位置，也可以通过直接输入具体的经纬度的方式来进行设备位置的添加。</p>
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
import { Scrollbar } from 'element-ui'
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
    'el-scrollbar': Scrollbar,
  },

  data() {
    const validModBusIndex = (rule, value, callback) => {
      if (value <= 255 && value >= 0) {
        callback()
      }
      callback(new Error('只能输入0-255的数字'))
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
      LWM2M: 3,
      loRa: 4,
      GateWay: 2,
      ModBus: 7,
      disabled: this.$route.query.oper !== 'edit',
      mapVisible: true,
      colSize: this.has('GET,/current_alerts') ? 8 : 12,
      record: {
        tags: [],
      },
      circles: [],
      polygons: [],
      markers: [],
      center: [116.397477, 39.908692],
      windows: [],
      stashRecord: {},
      // Run logs
      logData: {
        items: [],
        count: 0,
      },
      // Alert data
      alertData: {
        items: [],
        count: 0,
      },
      // Alert message colors
      colorsDict: {
        1: 'urgent',
        2: 'main',
        3: 'risk',
        4: 'waring',
      },
      deviceInfoRules: {
        deviceID: { required: true, message: '请输入' },
        deviceName: [
          { required: true, message: this.$t('devices.deviceNameRequired') },
        ],
        productID: [
          { required: true, message: this.$t('devices.productNameRequired') },
        ],
        modBusIndex: [
          { required: true, type: 'number', message: '请输入索引值' },
          { validator: validModBusIndex },
        ],
        deviceType: [
          { required: true, message: this.$t('devices.deviceTypeRequired') },
        ],
        parentDevice: [
          { required: true, message: '请选择所属设备' },
        ],
        authType: [
          { required: true, message: this.$t('devices.authTypeRequired') },
        ],
        upLinkSystem: [
          { required: true, message: '请选择上联系统' },
        ],
        gateway: [
          { required: true, message: '请选择所属网关' },
        ],
        // loRa
        lora: {
          type: {
            required: true,
            message: '请选择入网方式',
          },
          netID: [
            {
              required: true,
              message: '请输入网络 ID',
            },
            {
              len: 6,
              message: '请输入 6 位 网络 ID',
            },
          ],
          txChain: {
            required: true,
            message: '请输入链',
          },
          region: {
            required: true,
            message: '请选择发射频率',
          },
          appEUI: [
            {
              required: true,
              message: '请输入 AppEUI',
            },
            {
              len: 16,
              message: '请输入 16 位 AppEUI',
            },
          ],
          appKey: [
            {
              required: true,
              message: '请输入 AppKey',
            },
            {
              len: 32,
              message: '请输入 32 位 AppKey',
            },
          ],
          fcntCheck: {
            required: true,
            message: '请选择 FCnt Check',
          },
          canJoin: {
            required: true,
            message: '请选择',
          },
          nwkSKey: [
            {
              required: true,
              message: '请输入 NwkSKey',
            },
            {
              len: 32,
              message: '请输入 32 位 nwkSKey',
            },
          ],
          appSKey: [
            {
              required: true,
              message: '请输入 AppSKey',
            },
            {
              len: 32,
              message: '请输入 32 位 AppSKey',
            },
          ],
          fcntUp: {
            required: true,
            message: '请输入 FCnt Up',
          },
          fcntDown: {
            required: true,
            message: '请输入 FCnt Down',
          },
        },
        // Private
        macAddress: [
          {
            required: true,
            message: '请输入网关 MAC 地址',
          },
          {
            pattern: /[a-fA-F0-9]{16}/,
            message: '请输入正确的 16 位 MAC 地址',
          },
        ],
        devEUI: [
          { required: true, message: '请输入 DevEUI' },
          { len: 16, message: '请输入 16 位 DevEUI' },
        ],
        devAddr: [
          { required: true, message: '请输入 DevAddr' },
          { len: 8, message: '请输入 8 位 DevAddr' },
        ],
      },
    }
  },

  computed: {
    isDarkTheme() {
      return this.$store.state.base.currentTheme === 'dark'
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
              设备位置：${this.record.location}
              `,
            })
            this.mapLoading = false
          } else {
            this.windows.push({
              position: lnglatXY,
              content: `
              设备位置：(无法获取该位置信息!)
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
        this.formRulesRequired(res.data.cloudProtocol)
        this.loadAlertRecord()
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

    formRulesRequired(cloudProtocol) {
      if (cloudProtocol === 3) {
        this.deviceInfoRules.IMEI = [
          { required: true, message: '请输入设备IMEI', trigger: 'blur' },
          { min: 15, max: 15, message: 'IMEI长度为15位', trigger: 'blur' },
        ]
      } else {
        this.deviceInfoRules.IMEI = [
          { min: 15, max: 15, message: 'IMEI长度为15位', trigger: 'blur' },
        ]
      }
    },

    loadLogRecord() {
      this.loading = true
      httpGet(`${this.url}/${this.deviceId}/connect_logs`, { params: { _limit: 4, _page: 1 } })
        .then((response) => {
          this.loading = false
          this.logData.count = response.data.meta.count || 0
          this.logData.items = response.data.items
        })
        .catch(() => {
          this.loading = false
        })
    },

    loadAlertRecord() {
      if (!this.has('GET,/current_alerts')) {
        return
      }
      this.loading = true
      httpGet('/current_alerts', { params: { _page: 1, _limit: 4, deviceID: this.record.deviceID } })
        .then((response) => {
          this.loading = false
          this.alertData.count = response.data.meta.count || 0
          this.alertData.items = response.data.items
        }).catch(() => {
          this.loading = false
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
          throw new TypeError('locationScope 数据类型不正确')
        }
      } catch (e) {
        data.locationScope = null
      }
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
            throw new TypeError('locationScope 数据类型不正确')
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
            deviceType: this.record.deviceType,
            deviceTypeLabel: this.record.deviceTypeLabel,
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
      if (record.cloudProtocol !== this.loRa) {
        delete record.lora
        return record
      }
      const keys = Object.keys(record.lora)
      let fields = []
      // Gateway
      if (record.deviceType === 2) {
        record.lora.type = 'gateway'
        fields = ['netID', 'txChain', 'type']
      } else if (record.lora.type === 'otaa') {
        fields = ['region', 'appEUI', 'appKey', 'fcntCheck', 'canJoin', 'type']
      } else if (record.lora.type === 'abp') {
        fields = ['region', 'nwkSKey', 'appSKey', 'fcntUp', 'fcntDown', 'fcntCheck', 'type']
      }
      keys.forEach((key) => {
        if (!fields.includes(key)) {
          this.$delete(record.lora, key)
        }
      })
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
      if (this.$refs.tagsSelect) {
        this.$refs.tagsSelect.options = record.tags.map((value, index) => {
          return { value, label: record.tagIndex[index].label }
        })
      }
      // After saves the data, go back to the view page
      this.isRenderToList = false
    },
  },

  created() {
    this.loadRecord()
    this.loadLogRecord()
  },
}
</script>


<style lang="scss">
.device-details-view {
  .details-running {
    .el-form-item {
      margin-bottom: 0;
    }
  }
  .is-details-form .tag .el-tag {
    margin-right: 8px;
  }
  .el-card {
    .tag .el-input {
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
      .urgent {
        color: var(--alert-urgent-color);
      }
      .main {
        color: var(--alert-main-color);
      }
      .risk {
        color: var(--alert-risk-color);
      }
      .waring {
        color: var(--alert-waring-color);
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
