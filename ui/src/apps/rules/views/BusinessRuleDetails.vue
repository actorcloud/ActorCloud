<template>
  <div class="details-view business-rule-details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/business_rules/business_rules` }">{{ $t('rules.businessRule') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <el-card>
      <edit-toggle-button
        :url="url"
        :disabled="disabled"
        :accessType="accessType"
        @toggleStatus="toggleStatus">
      </edit-toggle-button>
      <el-row :gutter="50">
        <el-form
          v-if="!disabled"
          ref="record"
          label-position="top"
          :model="record"
          :rules="formRules">
          <el-col :span="12">
            <el-form-item prop="ruleName" :label="$t('rules.ruleName')">
              <el-input
                v-model="record.ruleName"
                :placeholder="$t('rules.ruleNameRequired')">
              </el-input>
            </el-form-item>
            <el-form-item prop="productID" :label="$t('rules.product')">
              <emq-search-select
                ref="product"
                v-show="record.productID || accessType === 'create'"
                v-model="record.productID"
                :placeholder="$t('rules.productRequired')"
                :disabled="false"
                :field="{
                  url: '/emq_select/products',
                  options: [{value: record.productID, label: record.productName }],
                  searchKey: 'productName',
                }"
                :record="record"
                @input="handleProductSelected">
              </emq-search-select>
            </el-form-item>
            <el-form-item prop="actions" :label="$t('rules.action')">
              <span v-if="!disabled && has('POST,/actions')" class="role-button">
                {{ $t('oper.or') }}&nbsp;
                <a href="javascript:;" @click="newAnotherPageData">{{ $t('rules.addAction') }}</a>
              </span>
              <emq-search-select
                ref="actionsSelect"
                v-model="record.actions"
                multiple
                :placeholder="$t('rules.actionRequired')"
                :disabled="false"
                :field="{
                  url: '/emq_select/actions',
                  searchKey: 'actionName',
                  state: accessType,
                }"
                :record="record">
              </emq-search-select>
            </el-form-item>
            <el-form-item prop="frequencyInput" :label="$t('rules.frequency')">
              <el-popover
                v-if="accessType !== 'view' && accessType !== 'edit'"
                v-model="frequencyPopoverVisible"
                popper-class="business_rules-popover frequency-popover"
                placement="bottom"
                width="340"
                :title="$t('rules.frequencyRequired')">
                <el-radio-group v-model="frequency.type">
                  <el-radio :disabled="record.conditionType === 3" :label="1">{{ $t('rules.everyTime') }}</el-radio>
                  <el-radio :disabled="record.conditionType === 3" :label="2">{{ $t('rules.someTime') }}
                    <div class="frequency-content">
                      <el-input type="number" v-model.number="frequency.times"></el-input>
                      次：
                      <el-input type="number" v-model.number="frequency.period"></el-input>
                      <select v-model="frequency.unit">
                        <option value="m">{{ $t('rules.minute') }}</option>
                        <option value="h">{{ $t('rules.hour') }}</option>
                      </select>
                    </div>
                  </el-radio>
                  <el-radio :label="3">{{ $t('rules.continueTime') }}
                    <div class="frequency-content">
                      <el-input type="number" v-model.number="frequency.continuePeriod"></el-input>
                      <select type="number" v-model.number="frequency.continueUnit">
                        <option value="m">{{ $t('rules.minute') }}</option>
                        <option value="h">{{ $t('rules.hour') }}</option>
                      </select>
                    </div>
                  </el-radio>
                </el-radio-group>
                <div class="btn-bar" style="text-align: right;">
                  <el-button
                    type="text"
                    size="mini"
                    @click="frequencyPopoverVisible=false">{{ $t('oper.cancel') }}
                  </el-button>
                  <el-button
                    class="btn-bar__confirm"
                    type="success"
                    size="mini"
                    @click="selectFrequency">{{ $t('oper.save') }}
                  </el-button>
                </div>
                <a slot="reference" class="frequency-click"></a>
              </el-popover>
              <el-input
                v-model="record.frequencyInput"
                disabled
                :placeholder="$t('rules.frequencyRequired')"
                :class="['frequency-input', {'frequency-disabled': accessType !== 'create'}]">
              </el-input>
            </el-form-item>
            <el-form-item prop="deviceID" :label="$t('rules.device')">
              <emq-search-select
                ref="device"
                v-model="record.deviceID"
                clearable
                :placeholder="$t('rules.deviceRequired')"
                :disabled="false"
                :field="{
                  url: '/emq_select/devices',
                  params: { productID: record.productID },
                  options: [{ label: record.deviceName, value: record.deviceID }],
                  rely: 'productID',
                  relyName: $t('rules.product'),
                  searchKey: 'deviceName',
                }"
                :record="record"
                @input="handleDeviceSelected">
              </emq-search-select>
            </el-form-item>
            <el-form-item prop="groupID" :label="$t('rules.group')">
              <emq-search-select
                ref="group"
                v-model="record.groupID"
                clearable
                :placeholder="$t('rules.groupRequired')"
                :disabled="false"
                :field="{
                  url: '/emq_select/groups',
                  params: { productID: record.productID },
                  options: [{ label: record.groupName, value: record.groupID }],
                  rely: 'productID',
                  relyName: $t('rules.product'),
                  searchKey: 'groupName',
                }"
                :record="record"
                @input="handleGroupSelected">
              </emq-search-select>
            </el-form-item>
            <el-form-item prop="remark" :label="$t('rules.remark')">
              <el-input
                v-model="record.remark"
                type="textarea"
                :placeholder="$t('rules.remarkRequired')">
              </el-input>
            </el-form-item>
          </el-col>

          <el-col class="conditions" :span="12">
            <el-form-item prop="conditionType" :label="$t('rules.conditionType')">
              <emq-select
                ref="conditionType"
                v-model="record.conditionType"
                :disabled="accessType !== 'create'"
                :autoSelect="false"
                :field="{
                  options: conditionTypeOption,
                  rely: 'productID',
                  relyName: $t('rules.product'),
                }"
                :record="record">
              </emq-select>
            </el-form-item>
            <el-form-item prop="conditions" :model="condition" :label="$t('rules.condition')">
              <el-popover
                ref="popover"
                v-model="popoverVisible"
                popper-class="business_rules-popover"
                placement="bottom"
                width="422"
                :title="$t('rules.setCondition')">
                <condition-form
                  ref="conditionForm"
                  :propCondition="condition"
                  :propRecord="record"
                  :popoverVisible.sync="popoverVisible"
                  :editPopoverVisible.sync="editPopoverVisible"
                  :dataPoints="dataPoints"
                  :propDataPointType.sync="dataPointType"
                  :showRelation="showRelation"
                  :disabled="disabled">
                </condition-form>

                <el-button
                  v-show="record.conditionType !== 3"
                  slot="reference"
                  type="success"
                  round
                  size="mini"
                  @click="showConditionPopover">
                  + {{ $t('rules.addCondition') }}
                </el-button>
              </el-popover>

              <el-popover
                ref="editPopover"
                v-if="record.conditions.length"
                v-model="editPopoverVisible"
                popper-class="business_rules-popover"
                placement="bottom"
                width="422"
                :title="$t('rules.editCondition')">
                <condition-form
                  ref="conditionForm"
                  :propCondition="condition"
                  :propRecord="record"
                  :popoverVisible.sync="popoverVisible"
                  :editPopoverVisible.sync="editPopoverVisible"
                  :dataPoints="dataPoints"
                  :propDataPointType.sync="dataPointType"
                  :showRelation="showRelation"
                  :disabled="disabled">
                </condition-form>
              </el-popover>

              <!-- List -->
              <el-row :gutter="20">
                <el-col v-if="record.conditionType === 3" :span="12">
                  <el-tag class="data-tag">
                    <p>{{ $t('rules.unreported') }}</p>
                  </el-tag>
                </el-col>
                <el-col
                  v-else
                  v-for="(tag,index) in record.conditions"
                  :key="index"
                  :span="12"
                  style="margin-top: 10px;">
                  <a
                    v-if="record.conditionType !== 3"
                    v-popover:editPopover
                    :class="[{'disabled': disabled}, 'condition']">
                    <condition-tag
                      :accessType="accessType"
                      :record="record"
                      :tag="tag"
                      @editConditionItem="editConditionItem(tag, index)"
                      @removeConditionItem="removeConditionItem">
                    </condition-tag>
                  </a>
                </el-col>
              </el-row>

            </el-form-item>
          </el-col>
        </el-form>

        <!-- Detail list -->
        <el-form
          v-else
          ref="record"
          label-position="left"
          class="rule-view-style"
          :model="record">
          <el-col :span="12">
            <el-form-item :label="`${$t('rules.ruleName')} : `" prop="ruleName">
              {{ record.ruleName }}
            </el-form-item>
            <el-form-item :label="`${$t('rules.product')} : `" prop="productName">
              <router-link style="float: none;" :to="`/products/${record.productIntID}`">
                {{ record.productName }}
              </router-link>
            </el-form-item>
            <el-form-item :label="`${$t('rules.device')} : `" prop="deviceName">
              <router-link style="float: none;" :to="`/devices/devices/${record.deviceIntID}`">
                {{ record.deviceName }}
              </router-link>
            </el-form-item>
            <el-form-item :label="`${$t('rules.group')} : `" prop="groupName">
              <router-link style="float: none;" :to="`/devices/groups/${record.groupIntID}`">
                {{ record.groupName }}
              </router-link>
            </el-form-item>
            <el-form-item :label="`${$t('rules.action')} : `" prop="actions" class="data-point-link">
              <router-link
                style="float: none;"
                v-for="(action, actionIndex) in record.actions"
                :key="actionIndex"
                :to="`/business_rules/actions/${action}`">
                <el-tag size="small">
                  {{ record.actionNames[actionIndex] }}
                </el-tag>
              </router-link>
            </el-form-item>
            <el-form-item :label="`${$t('rules.frequency')} : `" prop="frequency">
              {{ record.frequencyInput }}
            </el-form-item>
            <el-form-item :label="`${$t('rules.remark')} : `" prop="remark">
              {{ record.remark }}
            </el-form-item>
            <el-form-item :label="`${$t('rules.conditionType')} : `" prop="conditionType">
              <span>
                {{ record.conditionType === 1 ? $t('rules.dataPoint')
                : record.conditionType === 2 ? $t('rules.expressionsMetric')
                : record.conditionType === 3 ? $t('rules.unreported')
                : 'PATH' }}
              </span>
            </el-form-item>
          </el-col>
          <el-col class="conditions" :span="12">
            <el-form-item label="条件" prop="conditions" :model="condition">
              <el-row :gutter="20">
                <el-col v-if="record.conditionType === 3" :span="12">
                  <el-tag class="data-tag">
                    <p>{{ $t('rules.unreported') }}</p>
                  </el-tag>
                </el-col>
                <el-col v-else v-for="(tag,index) in record.conditions" :key="index" :span="12" style="margin-top: 10px;">
                  <condition-tag
                    :accessType="accessType"
                    :record="record"
                    :tag="tag">
                  </condition-tag>
                </el-col>
              </el-row>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>
      <emq-button v-if="!disabled" icon="save" @click="save">
        {{ $t('users.done') }}
      </emq-button>
    </el-card>
  </div>
</template>


<script>
// import { httpGet } from '@/utils/api'
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqButton from '@/components/EmqButton'
import EmqSelect from '@/components/EmqSelect'
import EmqSearchSelect from '@/components/EmqSearchSelect'
import ConditionForm from '../components/ConditionForm'
import ConditionTag from '../components/ConditionTag'

export default {
  name: 'business-rule-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqSelect,
    EmqSearchSelect,
    ConditionForm,
    ConditionTag,
  },

  data() {
    return {
      url: '/business_rules',
      LWM2M: 3,
      formRules: {
        ruleName: [
          { required: true, message: this.$t('rules.ruleNameRequired') },
        ],
        productID: [
          { required: true, message: this.$t('rules.productRequired') },
        ],
        actions: [
          { required: true, message: this.$t('rules.actionRequired') },
        ],
        frequencyInput: [
          { required: true, message: this.$t('rules.frequencyRequired') },
        ],
        conditionType: [
          { required: true, message: this.$t('rules.conditionTypeRequired') },
        ],
        conditions: [
          { required: true, message: this.$t('rules.conditionRequired') },
        ],
      },
      conditionTypeOption: [],
      showRelation: false,
      popoverVisible: false,
      editPopoverVisible: false,
      frequencyPopoverVisible: false,
      frequency: {
        type: 1,
        times: undefined,
        period: '',
        unit: 'm',
        continuePeriod: '',
        continueUnit: 'm',
      },
      dataPoints: [],
      condition: {
        data_point: undefined,
        data_point_name: undefined,
        metric: undefined,
        operator: '>',
        compare_type: 1,
        compare_path: null,
        relation: 'and',
      },
      record: {
        conditions: [],
        cloudProtocol: undefined,
        conditionType: null,
        dataStreamIntID: null,
        frequencyInput: '', // This value is only used for frequency input box value display and verification
      },
      dataPointType: 1, // 1: Numerical type
      localRecordName: 'businessRuleRecord',
      toURL: '/business_rules/actions/0?oper=create',
    }
  },

  watch: {
    'record.conditionType': 'conditionTypeChanged',
    disabled() {
      if (!this.disabled) {
        this.$nextTick(() => { // After DOM update
          this.setSelectOptions()
        })
      }
    },
  },

  methods: {
    processLoadedData(loadrecord) {
      // Configure the value of the frequency popover when editing and viewing
      const frequencyData = loadrecord.frequency
      const frequencyPeriod = frequencyData.period ? parseInt(frequencyData.period, 0) : ''
      const frequencyUnit = frequencyData.period ? frequencyData.period.replace(/[^a-z]+/ig, '') : ''
      const frequencyUnitName = frequencyUnit === 'm' ? this.$t('rules.minute') : this.$t('rules.hour')
      if (frequencyData.type === 1) {
        this.record.frequencyInput = this.$t('rules.everyTime')
      } else if (frequencyData.type === 2) {
        this.record.frequencyInput = this.$t('rules.someTimeItem', {
          period: frequencyPeriod,
          unitName: frequencyUnitName,
          times: frequencyData.times })
      } else if (frequencyData.type === 3) {
        this.record.frequencyInput = this.$t('rules.continueTimeItem', {
          period: frequencyPeriod,
          unitName: frequencyUnitName })
      }
      this.frequency = {
        type: frequencyData.type,
        times: frequencyData.times,
        period: frequencyData.type === 2 ? frequencyPeriod : '',
        unit: frequencyData.type === 2 ? frequencyUnit : 'm',
        continuePeriod: frequencyData.type === 3 ? frequencyPeriod : '',
        continueUnit: frequencyData.type === 3 ? frequencyUnit : 'm',
      }
      if (!loadrecord.conditions || !loadrecord.conditions.length) {
        this.formRules.conditions = []
      }
      if (this.accessType === 'edit') {
        this.setSelectOptions()
      }
      this.record.conditions.forEach((item) => {
        if (typeof item.threshold === 'boolean') {
          item.threshold = JSON.stringify(item.threshold)
        }
      })
      this.recordCache = { ...this.record }
    },
    beforePostData(data) {
      delete data.frequencyInput
      data.conditions.forEach((item) => {
        if (['true', 'false'].includes(item.threshold)) {
          item.threshold = JSON.parse(item.threshold)
        }
      })
    },
    selectFrequency() {
      let frequency = {}
      const unit = this.frequency.unit === 'm' ? this.$t('rules.minute') : this.$t('rules.hour')
      const continueUnit = this.frequency.continueUnit === 'm'
        ? this.$t('rules.minute') : this.$t('rules.hour')
      if (this.frequency.type === 1) {
        frequency = {
          type: this.frequency.type,
        }
        this.record.frequencyInput = this.$t('rules.everyTime')
      } else if (this.frequency.type === 2 && this.frequency.period && this.frequency.times) {
        if (!this.validateTime(this.frequency.unit, this.frequency.period)) {
          return
        }
        frequency = {
          type: 2,
          period: `${this.frequency.period}${this.frequency.unit}`,
          times: this.frequency.times,
        }
        this.record.frequencyInput = this.$t('rules.someTimeItem', {
          period: this.frequency.period,
          unitName: unit,
          times: frequency.times })
      } else if (this.frequency.type === 3 && this.frequency.continuePeriod) {
        if (!this.validateTime(this.frequency.continueUnit, this.frequency.continuePeriod)) {
          return
        }
        frequency = {
          type: 3,
          period: `${this.frequency.continuePeriod}${this.frequency.continueUnit}`,
        }
        this.record.frequencyInput = this.$t('rules.continueTimeItem', {
          period: this.frequency.continuePeriod,
          unitName: continueUnit })
      } else {
        this.$message.error(this.$t('rules.deployRequired'))
        return
      }
      this.record.frequency = frequency
      this.frequencyPopoverVisible = false
    },
    showConditionPopover() {
      this.condition = {
        data_point: undefined,
        data_point_name: undefined,
        metric: undefined,
        operator: '>',
        compare_type: 1,
        compare_path: null,
        relation: 'and',
      }
      this.dataPointType = 1
      this.showRelation = this.record.conditions && this.record.conditions.length > 0
    },
    editConditionItem(item, index) {
      if (this.disabled) {
        return
      }
      this.$refs.conditionForm.setConditionOptions(item)
      let compareType = 1
      if (item.compare_data_point || item.compare_path) {
        compareType = 2
      } else if (item.difference) {
        compareType = 3
      }
      this.condition = {
        ...item,
        tagindex: index,
        compare_type: compareType,
        relation: item.relation || 'and',
      }
      this.$refs.conditionForm.initEditForm(item)
      this.showRelation = index !== 0
      this.editPopoverVisible = true
    },
    removeConditionItem(item) {
      this.record.conditions = this.record.conditions.filter((row) => {
        return row !== item
      })
      if (this.record.conditions[0]) {
        delete this.record.conditions[0].relation
      }
    },
    validateTime(dateType, time) {
      time = parseInt(time, 0)
      if (dateType === 'h' && (time > 24 || time < 1)) {
        this.$message.error(this.$t('rules.hourLimit'))
        return false
      }
      if (dateType === 'm' && (time < 1 || time > 1440)) {
        this.$message.error(this.$t('rules.minuteLimit'))
        return false
      }
      return true
    },
    handleProductSelected(productIntID, selectedItems) {
      if (selectedItems) {
        this.record.productIntID = selectedItems.attr.productIntID
        this.record.cloudProtocol = selectedItems.attr.cloudProtocol
        this.record.productName = selectedItems.label
      }
      this.setSelectOptions()
    },
    handleDeviceSelected(deviceID, selectedItems) {
      this.record.deviceName = selectedItems && selectedItems.label
      this.record.deviceIntID = selectedItems && selectedItems.attr.deviceIntID
    },
    handleGroupSelected(groupID, selectedItems) {
      this.record.groupName = selectedItems && selectedItems.label
      this.record.groupIntID = selectedItems && selectedItems.attr.groupIntID
    },
    setSelectOptions() {
      this.conditionTypeOption = [
        { label: this.$t('rules.dataPoint'), value: 1 },
        { label: this.$t('rules.expressionsMetric'), value: 2 },
        { label: this.$t('rules.unreported'), value: 3 },
      ]
      if (this.record.cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
        this.conditionTypeOption.push({ label: 'PATH', value: 4 })
      }
      this.$refs.product.options = [
        { value: this.record.productID, label: this.record.productName },
      ]
      this.$refs.conditionType.options = this.conditionTypeOption
      this.$refs.device.options = [{ value: this.record.deviceID, label: this.record.deviceName }]
      this.$refs.group.options = [{ value: this.record.groupID, label: this.record.groupName }]
      if (this.record.actions) {
        this.$refs.actionsSelect.options = this.record.actions.map((value, index) => {
          return { value, label: this.record.actionNames[index] }
        })
      }
    },
    conditionTypeChanged() {
      if (this.disabled || this.accessType === 'edit') {
        return
      }
      this.record.conditions = []
      this.record.dataStreamIntID = null
      if (this.record.conditionType === 3) {
        if (this.frequency.type !== 3) {
          this.record.frequencyInput = ''
          this.frequency = {
            type: 3,
            times: undefined,
            period: '',
            unit: 'm',
            continuePeriod: '',
            continueUnit: 'm',
          }
        }
        this.formRules.conditions = []
      } else {
        this.formRules.conditions = [
          { required: true, message: this.$t('rules.conditionRequired') },
        ]
      }
    },
  },

  mounted() {
    if (this.accessType !== 'view') {
      this.setSelectOptions()
    }
  },
}
</script>


<style lang="scss">
.business-rule-details-view {
  .el-card a.condition {
    float: none;
  }
  .role-button {
    position: absolute;
    top: -40px;
    right: 0;
  }
  .el-input {
    height: auto;
  }
  .el-form-item__content .frequency-click {
    display: block;
    width: 100%;
    height: 40px;
    position: absolute;
    z-index: 1;
  }
  .conditions {
    .data-tag {
      text-align: center;
      p {
        margin-top: 20px !important;
      }
    }
    a.condition:not(.disabled):hover .el-tag {
      cursor: pointer;
      border-color: var(--color-main-green);
    }
    .el-tag {
      height: 70px;
      width: 100%;
      position: relative;
      font-size: 14px;
      line-height: 32px;
      background-color: #fbfbfb;
      border-color: #ddd;

      .el-icon-close {
        position: absolute;
        top: 5px;
        right: 4px;
        &:hover {
          color: var(--color-main-green);
          background-color: transparent;
        }
      }
      .relation {
        margin-top: 4px;
        position: absolute;
      }
      p {
        margin: 0;
        color: var(--color-text-lighter);
        overflow: hidden;
        margin-top: 30px;
        .float-left {
          float: left;
        }
        .float-right {
          float: right;
        }
      }
    }
  }

  .rule-view-style {
    .el-form-item {
      margin-bottom: 0;
      &.data-point-link a {
        .el-tag {
          cursor: pointer;
          margin-right: 4px;
        }
      }
      .el-form-item__content {
        margin-left: 100px;
      }
    }
    .conditions {
      .el-form-item__label {
        float: none;
      }
      .el-form-item__content {
        margin-left: 0;
        height: 180px;
        overflow-y: scroll;
      }
    }
  }
}
.business_rules-popover {
  padding: 0;
  .el-popover__title {
    padding: 20px 30px;
    border-bottom: 1px solid var(--color-line-card);
    font-size: 18px;
    color: var(--color-text-lighter);
  }
  .el-form {
    padding: 0 30px;
    .el-form-item {
      margin-bottom: 16px;
      .el-form-item__label {
        color: var(--color-text-light);
      }
    }
  }
  .btn-bar {
    padding: 0 30px 20px;
    .btn-bar__confirm {
      border-radius: 32px;
    }
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
          input::-webkit-outer-spin-button,
          input::-webkit-inner-spin-button {
            -webkit-appearance: none;
          }
          input[type="number"]{
            -moz-appearance: textfield;
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
    border-color: var(--color-line-card);
    color: var(--color-text-lighter);
  }
  &.frequency-disabled .el-input__inner {
    background-color: var(--color-input-bg);
    border-color: var(--color-line-card);
    color: var(--color-text-lighter);
  }
}
.el-radio-button--small .el-radio-button__inner {
  font-size: 14px;
  font-weight: 300;
  color: var(--color-text-light);
}
.el-button--success,
.el-button--success:hover,
.el-button--success:focus,
.el-button--success:active {
  background-color: var(--color-main-green);
}
.el-radio-button__inner {
  background-color: var(--color-bg-card);
  border-color: var(--color-line-bg);
}
.el-radio__input.is-checked + .el-radio__label, .el-radio__label {
  color: var(--color-text-light);
  font-weight: 300;
}
</style>
