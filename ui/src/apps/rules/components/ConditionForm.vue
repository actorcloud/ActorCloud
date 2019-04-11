<template>
  <div class="condition-form-view">
    <!-- Condition form -->
    <el-form
      ref="condition"
      class="condition-form"
      label-position="left"
      label-width="100px"
      :model="condition"
      :rules="conditionRules">
      <!-- DataPoint -->
      <el-form-item
        v-if="record.conditionType === 1"
        prop="streamDataPoint"
        :label="$t('rules.dataPoint')">
        <el-cascader
          ref="data_point"
          clearable
          expand-trigger="hover"
          v-model="condition.streamDataPoint"
          :options="dataPointOptions"
          @visible-change="handleVisible"
          @change="handleDataPoints">
        </el-cascader>
      </el-form-item>
      <!-- Metric -->
      <el-form-item
        v-if="record.conditionType === 2"
        prop="metric"
        :label="$t('rules.metric')">
        <emq-search-select
          ref="metric"
          v-model="condition.metric"
          :disabled="false"
          :field="{
            url: '/emq_select/rules/metrics',
            params: { productID: record.productID },
            searchKey: 'metricName',
            rely: 'productID',
            relyName: $t('rules.product')
          }"
          :record="record"
          @input="handleMetricSelected">
        </emq-search-select>
      </el-form-item>
      <!-- LWM2M -->
      <el-form-item
        v-if="record.conditionType === 4"
        prop="path"
        :label="$t('rules.path')">
        <el-input
          v-model="condition.path"
          :placeholder="disabled ? '' : $t('rules.pathRequired')">
        </el-input>
      </el-form-item>

      <el-form-item prop="operator" :label="$t('rules.operator')">
        <el-radio-group v-model="condition.operator" size="small">
          <el-radio-button label=">" :disabled="notNumberDataPoint"></el-radio-button>
          <el-radio-button label=">=" :disabled="notNumberDataPoint"></el-radio-button>
          <el-radio-button label="<" :disabled="notNumberDataPoint"></el-radio-button>
          <el-radio-button label="<=" :disabled="notNumberDataPoint"></el-radio-button>
          <el-radio-button label="=="></el-radio-button>
          <el-radio-button label="!=" :disabled="dataPointType === 5"></el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item prop="compare_type" :label="$t('rules.compareType')">
        <el-radio-group v-model="condition.compare_type">
          <el-radio :label="1">{{ $t('rules.staticValue') }}</el-radio>
          <!-- <el-radio :label="2" v-if="record.conditionType === 1">
            {{ record.cloudProtocol !== LWM2M ? '功能点' : 'PATH' }}
          </el-radio> -->
          <el-radio :label="3">{{ $t('rules.variableValue') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item
        v-if="condition.compare_type === 1"
        prop="threshold"
        :label="$t('rules.staticValue')">
        <!-- Number -->
        <el-input
          v-if="!notNumberDataPoint"
          v-model.number="condition.threshold"
          type="number"
          :placeholder="$t('rules.staticValueRequired')">
        </el-input>
        <!-- Character -->
        <el-input
          v-if="dataPointType === 3 || dataPointType === 11"
          v-model="condition.threshold"
          :placeholder="$t('rules.staticValueRequired')">
        </el-input>
        <!-- Enum -->
        <el-radio-group
          v-if="dataPointType === 2"
          v-model="condition.threshold"
          size="small">
          <el-radio-button
            v-for="(item, index) in dataPointEnumList"
            :key="index"
            :label="item[1]">
            {{ item[0] }}
          </el-radio-button>
        </el-radio-group>
        <!-- Malfunction -->
        <el-input
          v-if="dataPointType === 4"
          v-model="condition.threshold"
          disabled>
        </el-input>
        <!-- Boolean -->
        <el-radio-group
          v-if="dataPointType === 5"
          v-model="condition.threshold">
          <el-radio :label="JSON.stringify(true)"></el-radio>
          <el-radio :label="JSON.stringify(false)"></el-radio>
        </el-radio-group>
      </el-form-item>
      <!-- Contrast datapoint -->
      <!-- <el-form-item
        v-show="condition.compare_type === 2 && record.cloudProtocol !== LWM2M"
        prop="compare_data_point"
        :label="$t('rules.dataPoint')">
        <emq-select
          ref="compare_data_point"
          v-model="condition.compare_data_point"
          :disabled="false"
          :disableOptions="[condition.data_point]"
          :field="{
            url: '/emq_select/data_points',
            params: dataPointsParams,
            visibleLoad: true,
          }"
          :record="record"
          @input="handleCompareDataPoint">
        </emq-select>
      </el-form-item> -->
      <!-- Contrast PATH -->
      <!-- <el-form-item
        v-if="condition.compare_type === 2 && record.cloudProtocol === LWM2M"
        prop="compare_path"
        label="PATH: ">
        <el-input
          v-model="condition.compare_path"
          :placeholder="disabled ? '' : $t('rules.pathRequired')">
        </el-input>
      </el-form-item> -->
      <el-form-item
        v-if="condition.compare_type === 3"
        prop="difference"
        :label="$t('rules.variableValue')">
        <!-- Number -->
        <el-input
          v-if="!notNumberDataPoint || isNumberProductItem"
          v-model.number="condition.difference"
          type="number"
          :placeholder="$t('rules.variableValueRequired')">
        </el-input>
      </el-form-item>
      <el-form-item v-if="showRelation" prop="relation" :label="$t('rules.relation')">
        <el-radio-group v-model="condition.relation">
          <el-radio label="and">AND</el-radio>
          <el-radio label="or">OR</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <div class="btn-bar" style="text-align: right;">
      <el-button
        type="text"
        size="mini"
        @click="cancelCondition">{{ $t('oper.cancel') }}
      </el-button>
      <el-button
        class="btn-bar__confirm"
        type="success"
        size="mini"
        @click="handleCondition(editPopoverVisible)">{{ $t('oper.save') }}
      </el-button>
    </div>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import EmqSearchSelect from '@/components/EmqSearchSelect'

export default {
  name: 'condition-form-view',

  components: {
    EmqSearchSelect,
  },

  props: {
    propCondition: {
      type: Object,
      required: true,
    },
    propRecord: {
      type: Object,
      required: true,
    },
    dataPoints: {
      type: Array,
      default: () => [],
    },
    popoverVisible: {
      type: Boolean,
      default: false,
    },
    editPopoverVisible: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    showRelation: {
      type: Boolean,
      default: false,
    },
    propDataPointType: {
      type: Number,
      default: 1,
    },
  },

  data() {
    return {
      LWM2M: 3,
      dataPointType: 1,
      dataPointOptions: [],
      numberDataPointType: [1, 15, 16, 17, 18, 19, 21, 22, 25], // Number type data point
      dataPointEnumList: [], // Stores a list of enum when the datapoint is enum type
      conditionRules: {
        streamDataPoint: [
          { required: true, message: this.$t('rules.dataPointRequired') },
        ],
        metric: [
          { required: true, message: this.$t('rules.metricRequired') },
        ],
        compare_data_point: [
          { required: false, message: this.$t('rules.dataPointRequired') },
        ],
        threshold: [
          { required: true, message: this.$t('rules.staticValueRequired') },
        ],
        path: [
          { required: true, message: this.$t('rules.pathRequired') },
        ],
        // compare_path: [
        //   { required: true, message: this.$t('rules.pathRequired') },
        // ],
      },
    }
  },

  watch: {
    propDataPointType() {
      if (this.propDataPointType === 1) {
        this.dataPointType = this.propDataPointType
      }
    },
  },

  computed: {
    condition() {
      return this.propCondition
    },
    record() {
      return this.propRecord
    },
    notNumberDataPoint() {
      return !this.numberDataPointType.includes(this.dataPointType)
    },
  },

  methods: {
    // Initialize correlation values when the selected datapoint changes
    handleDataPoints(selectedItems) {
      if (selectedItems.length === 0) {
        return
      }
      let currentDataPoint = {}
      if (this.record.cloudProtocol === this.$variable.cloudProtocol.MODBUS) {
        this.condition.data_point = selectedItems[0]
        currentDataPoint = this.dataPointOptions.find($ => $.value === selectedItems[0])
      } else {
        this.record.dataStreamIntID = selectedItems[0]
        currentDataPoint = this.dataPointOptions.find($ => $.value === selectedItems[0])
          .children
          .find($ => $.value === selectedItems[1])
        this.condition.data_point = selectedItems[1]
      }
      this.condition.data_point_name = currentDataPoint.label
      this.dataPointType = currentDataPoint.attr.pointDataType
      this.$emit('update:propDataPointType', this.dataPointType)
      // Set operator defaults based on datapoint type
      this.condition.operator = this.numberDataPointType.includes(this.dataPointType) ? '>' : '=='
      // Initialize static values based on datapoint type
      if (this.dataPointType === 2) {
        this.dataPointEnumList = selectedItems.attr.enum
      }
    },

    // Get the selected comparison datapoint name
    // handleCompareDataPoint(dataPoint, selectedItems) {
    //   if (!dataPoint) {
    //     return
    //   }
    //   this.condition.compare_data_point_name = selectedItems.label
    // },

    // Update form fields after selecting metrics
    handleMetricSelected(metric, selectedItems) {
      this.condition.metricName = selectedItems.label
      if (this.record.cloudProtocol === this.$variable.cloudProtocol.LWM2M) {
        this.condition.path = selectedItems.attr.path
      } else {
        this.condition.data_point = metric
        delete this.condition.data_point_name
      }
    },
    // Processing conditions
    handleCondition(oper) {
      const isLWM2M = this.record.cloudProtocol === this.$variable.cloudProtocol.LWM2M
      this.$refs.condition.validate((valid) => {
        if (!valid) {
          return
        }
        if (!isLWM2M) {
          delete this.condition.path
        }
        // According to the type, it is necessary to delete the static value or the function point or the difference
        if (this.condition.compare_type === 1) {
          delete this.condition.compare_data_point
          delete this.condition.compare_data_point_name
          delete this.condition.compare_path
          delete this.condition.difference
        } else if (this.condition.compare_type === 2) {
          delete this.condition.threshold
          delete this.condition.difference
        } else if (this.condition.compare_type === 3) {
          delete this.condition.compare_data_point
          delete this.condition.compare_data_point_name
          delete this.condition.compare_path
          delete this.condition.threshold
        }
        if (this.condition.compare_data_point
          && this.condition.compare_data_point === this.condition.data_point) {
          this.$message.error(this.$t('rules.dataPointNotSame'))
          return
        }
        // if (this.condition.path
        //   && this.condition.path === this.condition.compare_path) {
        //   this.$message.error(this.$t('rules.pathNotSame'))
        //   return
        // }
        if (!this.showRelation) {
          delete this.condition.relation
        }
        delete this.condition.compare_type
        if (!oper) {
          delete this.condition.streamDataPoint
          this.record.conditions.push(this.condition)
          this.$emit('update:popoverVisible', false)
        } else {
          // Save subscript
          const { tagindex } = this.condition
          delete this.condition.tagindex
          // If there is a subscript value, it means that the current state is editing a condition.
          if (tagindex >= 0) {
            this.record.conditions[tagindex] = this.condition
            this.$emit('update:editPopoverVisible', false)
            return
          }
          this.$emit('update:editPopoverVisible', false)
        }
      })
    },
    cancelCondition() {
      if (this.editPopoverVisible) {
        this.$emit('update:editPopoverVisible', false)
      } else {
        this.$emit('update:popoverVisible', false)
      }
    },
    // Set the options for the conditional form
    setConditionOptions(condition) {
      if (this.record.conditionType === 1) {
        if (this.record.cloudProtocol === this.$variable.cloudProtocol.MODBUS) {
          condition.streamDataPoint = [condition.data_point]
        }
        condition.streamDataPoint = [this.record.dataStreamIntID, condition.data_point]
        // this.$refs.compare_data_point.options = [
        //   { label: condition.compare_data_point_name, value: condition.compare_data_point },
        // ]
        this.loadStreamPoint()
      } else if (this.record.conditionType === 2) {
        this.$refs.metric.options = [
          { label: condition.metricName, value: condition.metric },
        ]
      }
    },
    // Set different values depending on the type of datapoint
    initEditForm(condition) {
      if (['true', 'false'].includes(condition.threshold)) {
        this.dataPointType = 5
      }
      if (this.record.cloudProtocol !== this.$variable.cloudProtocol.LWM2M
        && this.record.conditionType !== 2) {
        const dataPoint = this.dataPoints.find(row => row.dataPointID === condition.data_point)
        if (!dataPoint) {
          return
        }
        if (this.dataPointType === 2) {
          this.dataPointEnumList = dataPoint.enum
        }
      }
    },
    loadStreamPoint() {
      httpGet(`/emq_select/stream_datapoints?productID=${this.record.productID}`)
        .then((res) => {
          this.dataPointOptions = res.data
        })
    },
    handleVisible(val) {
      if (val) {
        this.loadStreamPoint()
      }
    },
  },
}
</script>


<style lang="scss">
.condition-form-view {
  .el-button--text {
    color: var(--color-text-light);
    &:hover {
      color: var(--color-main-green);
    }
  }
  .condition-form {
    .el-radio__label {
      padding-left: 5px;
    }
    .el-cascader {
      width: 100%;
    }
  }
}
</style>
