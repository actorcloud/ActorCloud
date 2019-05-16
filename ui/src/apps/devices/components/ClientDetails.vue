<template>
  <div class="details-view clients-details-view">
    <input
      v-model="clipboardContent"
      type="text"
      id="clipboard">
    <el-row :gutter="20">
      <!-- Device and gateway form card -->
      <el-col :span="12" class="">
        <el-card
          v-loading="loading"
          :class="[disabled ? 'is-details-form' : '', 'el-card__plain', 'device-info']">
          <template slot="header">
            <span>{{ $t('devices.deviceInfo') }}</span>
            <edit-toggle-button
              :url="url"
              :disabled="disabled"
              @toggleStatus="$emit('toggleStatus', 'edit')">
            </edit-toggle-button>
          </template>
          <el-scrollbar class="details-form__scrollbar">
            <slot name="detailsForm" :disabled="disabled" :lang="lang">
            </slot>
          </el-scrollbar>
        </el-card>
      </el-col>

      <!-- Certification information -->
      <el-col :span="12" class="">
        <el-card v-loading="loading" class="el-card__plain cert-info">
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

        <!-- Device location -->
        <el-card v-loading="loading" class="el-card__plain map-content">
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
            <div class="btn-bar">
              <emq-button
                :loading="btnLoading"
                icon="save"
                @click="updateLocation">
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
import { httpPut } from '@/utils/api'
import LocationSelectDialog from './LocationSelectDialog'

export default {
  name: 'clients-details-view',

  components: {
    LocationSelectDialog,
  },

  props: {
    record: {
      type: Object,
      required: true,
    },
    disabled: {
      type: Boolean,
      default: true,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    deviceType: {
      type: Number,
      default: 0,
    },
  },

  watch: {
    'record.longitude': 'markMap',
  },

  data() {
    return {
      url: '/devices',
      btnLoading: false,
      Gateway: 3,
      mapVisible: true,
      circles: [],
      polygons: [],
      markers: [],
      center: [116.397477, 39.908692],
      windows: [],
      stashRecord: {},
      // Device certification information
      clipboardContent: '',
      clipboardStatus: this.$t('oper.copy'),
    }
  },

  computed: {
    lang() {
      return this.$store.state.accounts.lang
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
          } else {
            this.windows.push({
              position: lnglatXY,
              content: `
              ${this.$t('devices.location')}: (${this.$t('devices.unableLocation')}!)
              `,
            })
          }
        })
      }
    },

    editLocation() {
      this.mapVisible = !this.mapVisible
    },

    updateLocation() {
      this.btnLoading = true
      const data = { ...this.record }
      delete data.location
      httpPut(`/devices/${this.record.id}`, data).then(() => {
        this.$message.success(this.$t('oper.editSuccess'))
        this.btnLoading = false
        this.mapVisible = true
        this.markMap()
      }).catch(() => {
        this.btnLoading = false
      })
    },

    locationSelectConfirm() {
      this.record.longitude = this.$refs.locationSelect.position.lng
      this.record.latitude = this.$refs.locationSelect.position.lat
      this.record.location = this.$refs.locationSelect.position.name
      this.$refs.locationSelect.dialogVisible = false
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
  },
}
</script>


<style lang="scss">
.clients-details-view {
  #clipboard {
    position: absolute;
    z-index: -1;
  }

  .el-card {
    position: relative;

    &.device-info {
      height: 560px;
      .el-card__body {
        padding: 10px 0 0 10px;
        height: 460px;
        overflow: hidden;
        .el-scrollbar {
          .el-scrollbar__view {
            padding: 0 22px 0 12px;
          }
        }
        .el-form {
          .el-form-item--medium .el-form-item__label {
            line-height: 41px;
          }
        }
      }
    }

    &.cert-info {
      height: 210px;
      .details-code {
        .el-form-item {
          margin-bottom: 5px;
          .el-form-item__content {
            line-height: 41px;
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
      .el-card__body {
        padding: 0px 20px;
      }
    }

    &.map-content {
      .el-card__body {
        padding: 0;
        height: 270px;
      }
      .warp {
        padding: 20px 20px 10px 20px;
        .el-form {
          height: 100%;
        }
      }
    }

    &.el-card__plain {
      margin-bottom: 20px;
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
        .edit-toggle-button {
          width: 26px;
          height: 26px;
          line-height: 26px;
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
    }

    &.is-details-form {
      .el-form-item {
        input {
          line-height: 41px;
        }
      }
    }

    .btn-bar {
      padding: 0 4px 8px 0;
      overflow: hidden;
      .el-button--text {
        margin: 5px 20px;
      }
    }
  }
}
</style>
