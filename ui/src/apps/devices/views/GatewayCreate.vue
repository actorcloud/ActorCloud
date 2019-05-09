<template>
  <div class="gateway-create-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/devices/gateways' }">{{ $t('gateways.gateway') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('oper.createBtn') }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <div class="gateway-card-details-body">
      <el-card>
        <!-- Step bar -->
        <div class="emq-steps">
          <div :class="['step', step === 1 ? 'is-active' : '']">
            <i class="step__icon-inner">1</i>
            <span class="step__title">{{ $t('gateways.gatewayInfo') }}</span>
          </div>
          <div class="step__arrow"></div>
          <div :class="['step', step === 2 ? 'is-active' : '']">
            <i class="step__icon-inner">2</i>
            <span class="step__title">
              {{ $t('devices.authInfo') }}
            </span>
          </div>
          <div class="step__process" :style="{ width: `${step / 2 * 100}%` }"></div>
        </div>

        <el-row :gutter="50">
          <el-form
            ref="record"
            label-position="top"
            :model="record"
            :rules="rules">

            <!-- step 1 -->
            <div v-show="step === 1" class="gateways-rows">
              <el-col :span="12">
                <el-form-item prop="deviceName" :label="$t('gateways.gatewayName')">
                  <el-input
                    v-model="record.deviceName"
                    type="text"
                    :placeholder="$t('gateways.gatewayNameRequired')">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="productID" :label="$t('devices.productName')">
                  <emq-search-select
                    ref="productSelect"
                    v-model="record.productID"
                    :placeholder="$t('oper.productsSearch')"
                    :field="productSelectField"
                    :record="record"
                    :disabled="!!$route.query.productID"
                    @input="handleProductSelect">
                  </emq-search-select>
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
                <el-form-item prop="mac" :label="$t('gateways.gatewayMac')">
                  <el-input
                    type="text"
                    v-model="record.mac"
                    :placeholder="$t('gateways.gatewayMacRequired')"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item class="groups" prop="groups" :label="$t('groups.group')">
                  <emq-search-select
                    ref="groupsSelect"
                    class="multiple-select"
                    v-model="record.groups"
                    multiple
                    :placeholder="$t('groups.groupNameRequired')"
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
                <el-form-item prop="location" :label="$t('gateways.gatewayLocation')">
                  <el-input
                    type="text"
                    v-model="record.location"
                    :placeholder="$t('gateways.gatewayLocationRequired')"
                    :disabled="false"
                    @focus="$refs.locationSelect.dialogVisible = true">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="longitude" :label="$t('devices.longitude')">
                  <el-input
                    type="number"
                    v-model.number="record.longitude"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="latitude" :label="$t('devices.latitude')">
                  <el-input
                    type="number"
                    v-model.number="record.latitude"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="manufacturer" :label="$t('devices.manufacturer')">
                  <el-input
                    type="text"
                    v-model="record.manufacturer"
                    :placeholder="$t('devices.manufacturerRequired')"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="serialNumber" :label="$t('devices.serialNumber')">
                  <el-input
                    type="text"
                    v-model="record.serialNumber"
                    :placeholder="$t('devices.serialNumberRequired')"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="softVersion" :label="$t('devices.softVersion')">
                  <el-input
                    type="text"
                    v-model="record.softVersion"
                    :placeholder="$t('devices.softVersionRequired')"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="hardwareVersion" :label="$t('devices.hardwareVersion')">
                  <el-input
                    type="text"
                    v-model="record.hardwareVersion"
                    :placeholder="$t('devices.hardwareVersionRequired')"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="deviceConsoleIP" :label="$t('devices.deviceConsoleIP')">
                  <el-input
                    type="text"
                    v-model="record.deviceConsoleIP"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="deviceConsoleUsername" :label="$t('devices.deviceConsoleUsername')">
                  <el-input
                    type="text"
                    v-model="record.deviceConsoleUsername"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="deviceConsolePort" :label="$t('devices.deviceConsolePort')">
                  <el-input
                    type="text"
                    v-model="record.deviceConsolePort"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="description" :label="$t('gateways.description')">
                  <el-input
                    type="text"
                    v-model="record.description"
                    :placeholder="$t('gateways.descriptionRequired')"
                    :disabled="false">
                  </el-input>
                </el-form-item>
              </el-col>
            </div>

            <!-- step 2 -->
            <div v-if="step === 2" class="gateways-rows">
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
              <el-col v-if="record.authType === Cert"  :span="12">
                <el-form-item prop="certs" :label="$t('devices.certs')">
                  <emq-search-select
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
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="deviceID" :label="$t('gateways.gatewayID')">
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
                <el-form-item prop="token" :label="$t('gateways.gatewayToken')">
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

      <emq-button
        v-if="step === 2"
        icon="save"
        @click="save"
        :loading="btnLoading">
        {{ $t('oper.finish') }}
      </emq-button>
      <emq-button v-if="step === 1" class="step" @click="handleStep">
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
import EmqSearchSelect from '@/components/EmqSearchSelect'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import LocationSelectDialog from '../components/LocationSelectDialog'

export default {
  name: 'gateway-create-view',

  components: {
    EmqDetailsPageHead,
    EmqSearchSelect,
    LocationSelectDialog,
  },

  data() {
    return {
      url: '/devices',
      btnLoading: false,
      step: 1,
      Cert: 2,
      record: {
        productID: this.$route.query.productID,
        gatewayProtocol: this.$route.query.gatewayProtocol,
        groups: [],
        deviceType: 2,
      },
      rules: {
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

    handleProductSelect(productID, selectItem) {
      if (!productID) {
        return
      }
      this.record.gatewayProtocol = selectItem.attr.gatewayProtocol
    },

    locationSelectConfirm() {
      this.record.longitude = this.$refs.locationSelect.position.lng
      this.record.latitude = this.$refs.locationSelect.position.lat
      this.record.location = this.$refs.locationSelect.position.name
      this.$refs.locationSelect.dialogVisible = false
    },

    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        this.btnLoading = true
        const record = { ...this.record }
        // Converts an empty string to a null
        Object.keys(record).forEach((key) => {
          if (record[key] === '') {
            record[key] = null
          }
        })
        httpPost(this.url, record).then(() => {
          this.$message.success(this.$t('oper.createSuccess'))
          const { fromURL } = this.$route.query
          if (fromURL) {
            this.$router.push({ path: fromURL })
          } else {
            this.$router.push({ path: '/devices/gateways' })
          }
          this.btnLoading = false
        })
        this.btnLoading = false
      })
    },
  },
}
</script>


<style lang="scss">
.gateway-create-view {
  .gateway-card-details-body {
    .gateways-rows {
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
