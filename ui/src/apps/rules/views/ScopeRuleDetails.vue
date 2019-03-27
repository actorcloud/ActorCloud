<template>
  <div class="details-view scope-rule-details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/business_rules/scope_rules` }">围栏规则</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <div>
      <el-card :class="disabled ? 'is-details-form' : ''">
        <el-row :gutter="50">
          <el-form
            ref="record"
            label-position="left"
            label-width="100px"
            :model="record"
            :rules="accessType !== 'view' ? formRules : {}">
            <el-col :span="12">
              <el-form-item label="规则名称" prop="ruleName">
                <el-input
                  v-model="record.ruleName"
                  :placeholder="disabled ? '' : '请输入规则名称'"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
              <el-form-item label="关联设备" prop="deviceID">
                <el-select
                  v-if="['create', 'edit'].includes(accessType)"
                  v-model="record.deviceID"
                  filterable
                  remote
                  :placeholder="disabled ? '' : '请输入关键词'"
                  :disabled="disabled"
                  :remote-method="devicesSearch"
                  :loading="loading">
                  <el-option
                    v-for="item in deviceOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                  </el-option>
                </el-select>
                <router-link
                  v-else
                  style="float: none;"
                  :to="{ path: `/devices/devices/${record.deviceIntID}` }">
                  {{ record.deviceName }}
                </router-link>
              </el-form-item>
              <el-form-item label="位置功能点" prop="dataPointID">
                <emq-select
                  v-model="record.dataPointID"
                  :disabled="disabled"
                  :placeholder="disabled ? '' : '请选择该设备位置的功能点'"
                  :field="{ url: '/emq_select/data_points', rely: 'dataStreamIntID', relyName: '关联数据流' }"
                  :record="record">
                </emq-select>
              </el-form-item>
              <el-form-item label="频率" prop="frequency">
                <el-popover
                  v-if="accessType !== 'view'"
                  v-model="frequencyPopoverVisible"
                  popper-class="business_rules-popover frequency-popover"
                  placement="bottom"
                  width="340"
                  title="选择规则的频率要求">
                  <el-radio-group v-model="frequency.type">
                    <el-radio :label="1">每次满足条件都触发</el-radio>
                    <el-radio :label="2">满足以下条件时触发
                      <div class="frequency-content">
                        <el-input v-model="frequency.times"></el-input>次：
                        <el-input v-model="frequency.period"></el-input>
                        <select v-model="frequency.unit">
                          <option value="m">分钟</option>
                          <option value="h">小时</option>
                        </select>
                      </div>
                    </el-radio>
                    <el-radio :label="3">条件持久存在时触发
                      <div class="frequency-content">
                        <el-input v-model="frequency.continuePeriod"></el-input>
                        <select v-model="frequency.continueUnit">
                          <option value="m">分钟</option>
                          <option value="h">小时</option>
                        </select>
                      </div>
                    </el-radio>
                  </el-radio-group>
                  <div class="btn-bar" style="text-align: right;">
                    <el-button
                      type="text"
                      size="mini"
                      @click="frequencyPopoverVisible=false">取消
                    </el-button>
                    <el-button
                      type="success"
                      size="mini"
                      @click="selectFrequency()">确定
                    </el-button>
                  </div>
                  <a slot="reference" class="frequency-click"></a>
                </el-popover>
                <el-input
                  placeholder="请选择规律的频率要求"
                  v-model="frequencyInput"
                  disabled
                  :class="['frequency-input', {'frequency-disabled': disabled}]">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="关联产品" prop="productID">
                <emq-select
                  v-if="['create', 'edit'].includes(accessType)"
                  v-model="record.productID"
                  :disabled="disabled"
                  :placeholder="disabled ? '' : '请选择关联产品'"
                  :field="{ url: '/emq_select/products' }"
                  :record="record">
                </emq-select>
                <router-link
                  v-else
                  style="float: none;"
                  :to="{ path: `/products/${record.productIntID}` }">
                  {{ record.productName }}
                </router-link>
              </el-form-item>
              <el-form-item label="关联数据流" prop="dataStreamIntID">
                <emq-select
                  v-if="['create', 'edit'].includes(accessType)"
                  v-model="record.dataStreamIntID"
                  :disabled="disabled"
                  :placeholder="disabled ? '' : '请选择关联数据流'"
                  :field="{ url: '/emq_select/data_streams', rely: 'productID', relyName: '关联产品' }"
                  :record="record">
                </emq-select>
                <router-link
                  v-else
                  style="float: none;"
                  :to="{ path: `/products/${record.productIntID}/data_streams/${record.dataStreamIntID}` }">
                  {{ record.streamName }}
                </router-link>
              </el-form-item>
              <el-form-item label="触发动作" prop="actions">
                <span v-if="!disabled && has('POST,/actions')" class="role-button">
                  或&nbsp;
                  <router-link to="/business_rules/actions/0?oper=create">
                     新建动作
                  </router-link>
                </span>
                <emq-select
                  v-if="['create', 'edit'].includes(accessType)"
                  v-model="record.actions"
                  multiple
                  :disabled="disabled"
                  :placeholder="disabled ? '' : '请选择将会触发的动作'"
                  :field="{ url: '/emq_select/actions' }"
                  :record="record">
                </emq-select>
                <div v-else class="action-link">
                  <router-link
                    style="float: none;"
                    v-for="(action, actionIndex) in record.actions"
                    :key="actionIndex"
                    :to="`/business_rules/actions/${action}`">
                    <el-tag
                      size="small">
                      {{ record.actionNames[actionIndex] }}
                    </el-tag>
                  </router-link>
                </div>
              </el-form-item>
              <el-form-item label="备注" prop="remark">
                <el-input
                  v-model="record.remark"
                  :type=" disabled ? '' : 'textarea'"
                  :placeholder="disabled ? '' : '请填写备注'"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <emq-button v-if="!disabled" icon="save" @click="save">
          {{ $t('users.done') }}
        </emq-button>
      </el-card>
    </div>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqButton from '@/components/EmqButton'
import EmqSelect from '@/components/EmqSelect'

export default {
  name: 'scope-rule-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqSelect,
  },

  data() {
    return {
      url: '/scope_rules',
      formRules: {
        ruleName: [
          { required: true, message: '请输入规则名称' },
        ],
        productID: [
          { required: true, message: '请选择关联产品' },
        ],
        dataStreamIntID: [
          { required: true, message: '请选择关联数据流' },
        ],
        actions: [
          { required: true, message: '请选择将会触发的动作' },
        ],
        frequency: [
          { required: true, message: '请选择规律的频率要求' },
        ],
        deviceID: [
          { required: true, message: '请选择关联设备' },
        ],
        dataPointID: [
          { required: true, message: '请选择该设备位置的功能点' },
        ],
      },
      frequencyPopoverVisible: false,
      frequency: {
        type: 1,
        times: undefined,
        period: '',
        unit: 'm',
        continuePeriod: '',
        continueUnit: 'm',
      },
      // This value is only used for frequency input box value display and verification
      frequencyInput: '',
      loading: false,
      deviceOptions: [],
      deviceSearchKey: '',
    }
  },

  watch: {
    'record.productID': 'productChanged',
  },

  methods: {
    productChanged(newValue, oldValue) {
      if (oldValue) {
        this.record.dataStreamIntID = undefined
        this.record.dataPointID = undefined
        this.record.deviceID = undefined
        this.deviceOptions = []
      }
    },
    selectFrequency() {
      let frequency = {}
      const unit = this.frequency.unit === 'm' ? '分钟' : '小时'
      const continueUnit = this.frequency.continueUnit === 'm' ? '分钟' : '小时'
      if (this.frequency.type === 1) {
        frequency = {
          type: this.frequency.type,
        }
        this.frequencyInput = '每次满足条件都触发'
      } else if (this.frequency.type === 2 && this.frequency.period && this.frequency.times) {
        frequency = {
          type: 2,
          period: `${this.frequency.period}${this.frequency.unit}`,
          times: this.frequency.times,
        }
        this.frequencyInput = `${this.frequency.period}${unit}内满足${frequency.times}次时触发`
      } else if (this.frequency.type === 3 && this.frequency.continuePeriod) {
        frequency = {
          type: 3,
          period: `${this.frequency.continuePeriod}${this.frequency.continueUnit}`,
        }
        this.frequencyInput = `持续满足${this.frequency.continuePeriod}${continueUnit}时触发`
      } else {
        this.$message.error('请填写所选频率要求的配置值')
        return
      }
      this.record.frequency = frequency
      this.frequencyPopoverVisible = false
    },
    processLoadedData(loadedRecord) {
      this.devicesSearch(loadedRecord.deviceName)
      this.record.dataPointID = loadedRecord.conditions[0].data_point
      // Configure the value of the frequency popover when editing and viewing
      const frequencyData = loadedRecord.frequency
      const frequencyPeriod = frequencyData.period ? parseInt(frequencyData.period, 0) : ''
      const frequencyUnit = frequencyData.period ? frequencyData.period.replace(/[^a-z]+/ig, '') : ''
      const frequencyUnitName = frequencyUnit === 'm' ? '分钟' : '小时'
      if (frequencyData.type === 1) {
        this.frequencyInput = '每次满足条件都触发'
      } else if (frequencyData.type === 2) {
        this.frequencyInput = `${frequencyPeriod}${frequencyUnitName}内满足${frequencyData.times}次时触发`
      } else if (frequencyData.type === 3) {
        this.frequencyInput = `持续满足${frequencyPeriod}${frequencyUnitName}时触发`
      }
      this.frequency = {
        type: frequencyData.type,
        times: frequencyData.times,
        period: frequencyData.type === 2 ? frequencyPeriod : '',
        unit: frequencyData.type === 2 ? frequencyUnit : 'm',
        continuePeriod: frequencyData.type === 3 ? frequencyPeriod : '',
        continueUnit: frequencyData.type === 3 ? frequencyUnit : 'm',
      }
    },
    devicesSearch(value) {
      if (!this.record.productID) {
        this.$message.error('请先选择关联产品！')
        return
      }
      if (!value) {
        return
      }
      this.deviceSearchKey = value
      httpGet(`/emq_select/devices?productID=${this.record.productID}&deviceName_like=${value}`).then((response) => {
        this.deviceOptions = response.data
      })
    },
  },
}
</script>


<style lang="scss">
@import '~@/assets/scss/detailsPage.scss';
.scope-rule-details-view {
  .el-card a.condition {
    float: none;
  }
  .role-button {
    position: absolute;
    top: 0;
    right: 10px;
    z-index: 1;
  }
  .el-input {
    height: auto;
  }
  .el-select {
    width: 100%;
  }
  .el-form-item__content .frequency-click {
    display: block;
    width: 100%;
    height: 40px;
    position: absolute;
    z-index: 1;
  }
  .action-link a {
    .el-tag {
      cursor: pointer;
      margin-right: 4px;
    }
  }
}
.business_rules-popover {
  padding: 0;
  .el-popover__title {
    padding: 20px 30px;
    border-bottom: 1px solid #dfe0e4;
    font-size: 18px;
    color: #505050;
    font-weight: normal;
  }
  .el-form {
    padding: 0 30px;
    .el-form-item {
      margin-bottom: 16px;
    }
  }
  .btn-bar {
    padding: 0 30px 20px;
  }
  .el-form-item.is-required .el-form-item__label:before {
    content: none;
  }
  &.frequency-popover .el-radio-group {
    font-size: 14px;
    padding: 6px 30px 0;
    .el-radio {
      display: block;
      margin: 0 0 20px;
      .frequency-content {
        margin-top: 10px;
        .el-input {
          width: 80px;
          .el-input__inner {
            border-width: 0 0 1px 0;
            border-radius: 0;
            height: 24px;
          }
        }
        select {
          height: 24px;
          color: #666;
          width: 80px;
          border-radius: 3px;
          border-color: #ddd;
        }
      }
    }
  }
}
.el-input.frequency-input {
  .el-input__inner {
    background-color: transparent;
    border-color: #dcdfe6;
    color: #606266;
  }
  &.frequency-disabled .el-input__inner {
    background-color: #f5f7fa;
    border-color: #e4e7ed;
    color: #c0c4cc;
  }
}
.el-radio-button--small .el-radio-button__inner {
  font-size: 14px;
  font-weight: 300;
  color: #84868f;
}
.el-button--success,
.el-button--success:hover,
.el-button--success:focus,
.el-button--success:active {
  background-color: #2fc285;
}
.el-radio__input.is-checked + .el-radio__label, .el-radio__label {
  color: #84868f;
  font-weight: 300;
}
</style>
