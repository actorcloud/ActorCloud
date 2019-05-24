<template>
  <el-row v-loading="loading" class="data-points-form-view" :gutter="40">
    <el-form
      ref="record"
      :label-width="lang === 'en' ? '150px' : '130px'"
      :label-position="accessType === 'view' ? 'left' : 'top'"
      :class="disabled ? 'is-details-form' : ''"
      :model="record"
      :rules="disabled ? {} : rules">
      <el-col :span="12">
        <el-form-item
          prop="dataPointName"
          :label="$t('products.dataPointName')">
          <el-input
            type="text"
            v-model="record.dataPointName"
            :placeholder="disabled ? '' : $t('dataPoints.dataPointNameRequired')"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item
          prop="dataPointID"
          :label="$t('dataPoints.dataPointID')">
          <el-popover
            placement="top-start"
            width="200"
            trigger="hover"
            :content="$t('dataPoints.dataPointIDTips')">
          </el-popover>
          <i
            slot="reference"
            class="el-icon-question tips-icon"
            style="left: -50px;">
          </i>
          <el-input
            type="text"
            v-model="record.dataPointID"
            :placeholder="disabled ? '' : $t('dataPoints.dataPointIDRequired')"
            :disabled="accessType !== 'create'">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item
          prop="pointDataType"
          :label="$t('dataPoints.pointDataType')">
          <emq-select
            v-model="record.pointDataType"
            :field="{ key: 'pointDataType' }"
            :record="record"
            :placeholder="disabled ? '' : $t('oper.select')"
            :disabled="accessType !== 'create'"
            @input="handlePointType">
          </emq-select>
        </el-form-item>
      </el-col>
      <el-col v-show="record.pointDataType === LOCATION" :span="12">
        <el-form-item
          v-if="record.pointDataType === LOCATION"
          prop="locationType"
          :label="$t('dataPoints.locationType')">
          <emq-select
            v-model="record.locationType"
            :field="{ key: 'locationType' }"
            :record="record"
            :placeholder="disabled ? '' : $t('oper.select')"
            :disabled="accessType !== 'create'">
          </emq-select>
        </el-form-item>
      </el-col>
      <el-col v-if="currentProduct.cloudProtocol === ModBus" :span="12">
        <el-form-item
          prop="registerAddr"
          :label="$t('dataPoints.registerAddr')">
          <el-input
            type="text"
            v-model="record.registerAddr"
            :placeholder="$t('dataPoints.registerAddrRequired')"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item
          prop="dataTransType"
          :label="$t('dataPoints.dataTransType')">
          <emq-select
            v-model="record.dataTransType"
            :field="{ key: 'dataTransType' }"
            :record="record"
            :placeholder="disabled ? '' : $t('oper.select')"
            :disabled="disabled">
          </emq-select>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === NUMBER" :span="12">
        <el-form-item
          prop="extendTypeAttr.unitName"
          :label="$t('dataPoints.unitName')">
          <el-input
            type="text"
            v-model="record.extendTypeAttr.unitName"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === NUMBER" :span="12">
        <el-form-item
          prop="extendTypeAttr.unitSymbol"
          :label="$t('dataPoints.unitSymbol')">
          <el-input
            type="text"
            v-model="record.extendTypeAttr.unitSymbol"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === NUMBER" :span="12">
        <el-form-item
          prop="extendTypeAttr.upperLimit"
          :label="$t('dataPoints.upperLimit')">
          <el-input
            type="number"
            v-model="record.extendTypeAttr.upperLimit"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === NUMBER" :span="12">
        <el-form-item
          prop="extendTypeAttr.lowerLimit"
          :label="$t('dataPoints.lowerLimit')">
          <el-input
            type="number"
            v-model="record.extendTypeAttr.lowerLimit"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === NUMBER" :span="12">
        <el-form-item
          prop="extendTypeAttr.dataStep"
          :label="$t('dataPoints.dataStep')">
          <el-input
            type="number"
            v-model="record.extendTypeAttr.dataStep"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="[NUMBER, STRING].includes(record.pointDataType)" :span="12">
        <el-form-item
          prop="enum"
          style="min-height: 41px;"
          :label="$t('dataPoints.enum')">
          <el-popover
            v-if="!disabled"
            v-model="popoverVisible"
            popper-class="enum-popover"
            placement="bottom"
            width="240"
            :title="$t('dataPoints.addEnum')">
            <el-form label-position="left" label-width="60px">
              <el-form-item :label="$t('dataPoints.enumValue')">
                <el-input
                  v-model="enumValue"
                  :class="{'error': enumValueExist}"
                  :placeholder="enumValueExist"
                  @focus="enumValueExist=undefined">
                </el-input>
              </el-form-item>
              <el-form-item :label="$t('dataPoints.rawValue')">
                <el-input
                  v-model="rawValue"
                  :class="{'error': rawValueExist}"
                  :placeholder="rawValueExist"
                  @focus="rawValueExist=undefined">
                </el-input>
              </el-form-item>
            </el-form>
            <div style="text-align: right;">
              <el-button
                type="text"
                size="mini"
                @click="popoverVisible=false">{{ $t('oper.cancel') }}
              </el-button>
              <el-button
                type="success"
                size="mini"
                @click="addEnumItem">{{ $t('oper.save') }}
              </el-button>
            </div>
            <el-button
              style="margin-right: 20px"
              slot="reference"
              type="success"
              size="mini"
              @click="showPopover">
              + {{ $t('oper.add') }}
            </el-button>
          </el-popover>
          <el-tag
            v-for="tag in record.enum"
            :key="tag[0]"
            :closable="accessType !== 'view'"
            :close-transition="false"
            @close="removeEnumItem(tag)"> {{ tag[0]+ ': ' + tag[1] }}
          </el-tag>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === FAULT" :span="12">
        <el-form-item
          prop="faultValue"
          :label="$t('dataPoints.faultValue')">
          <el-input
            type="text"
            v-model="record.faultValue"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item :label="$t('dataPoints.description')" prop="description">
          <el-input
            v-model="record.description"
            :type="disabled ? 'text' : 'textarea'"
            :placeholder="disabled ? '' : $t('dataPoints.descriptionRequired')"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="accessType === 'view'" :span="12">
        <el-form-item :label="$t('dataPoints.createUser')">
          <el-input
            v-model="record.createUser"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="accessType === 'view'" :span="12">
        <el-form-item :label="$t('dataPoints.createAt')">
          <el-input
            v-model="record.createAt"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
    </el-form>
  </el-row>
</template>


<script>
import { httpGet, httpPost, httpPut } from '@/utils/api'

export default {
  name: 'data-points-form-view',

  props: {
    url: {
      type: String,
      required: true,
    },
    accessType: {
      type: String,
      required: true,
    },
    currentProduct: {
      type: Object,
      required: true,
    },
    currentDataPoint: {
      type: Object,
      required: true,
    },
    currentStreams: {
      type: Object,
      required: true,
    },
  },

  data() {
    const validatePointID = (rule, value, callback) => {
      if (!value) {
        callback(new Error(this.$t('dataPoints.dataPointIDRequired')))
      } else {
        if (!value.match(/^[a-zA-Z]\w*$/g)) {
          callback(new Error(this.$t('dataPoints.dataPointIDTips')))
        }
        callback()
      }
    }
    return {
      NUMBER: 1,
      STRING: 2,
      FAULT: 4,
      LOCATION: 5,
      ModBus: 7,
      loading: false,
      record: {
        dataPointName: undefined,
        dataPointID: undefined,
        pointDataType: undefined,
        dataTransType: 1,
        enum: [],
        faultValue: undefined,
        description: undefined,
        createAt: undefined,
        createUser: undefined,
        isLocationType: 0,
        locationType: undefined,
        extendTypeAttr: {
          unitName: undefined,
          unitSymbol: undefined,
          upperLimit: undefined,
          lowerLimit: undefined,
          dataStep: undefined,
        },
      },
      rules: {
        dataPointID: [
          { validator: validatePointID, required: true },
        ],
        dataPointName: [
          { required: true, message: this.$t('dataPoints.dataPointNameRequired') },
        ],
        dataTransType: [
          { required: true, message: this.$t('dataPoints.dataTransTypeRequired') },
        ],
        registerAddr: [
          { required: true, message: this.$t('dataPoints.registerAddrRequired') },
        ],
        pointDataType: [
          { required: true, message: this.$t('dataPoints.pointDataTypeRequired') },
        ],
        faultValue: [
          { required: true, message: this.$t('dataPoints.faultValueRequired') },
        ],
        locationType: [
          { required: true, message: this.$t('dataPoints.locationTypeRequired') },
        ],
      },
      popoverVisible: false,
      enumValue: undefined,
      rawValue: undefined,
      enumValueExist: undefined,
      rawValueExist: undefined,
    }
  },

  computed: {
    disabled() {
      return this.accessType === 'view'
    },
    lang() {
      return this.$store.state.accounts.lang
    },
  },

  methods: {
    // Load data
    loadData() {
      if (this.accessType === 'create' || !this.$route.params.id) {
        return
      }
      this.loading = true
      httpGet(`${this.url}/${this.currentDataPoint.id}`).then((res) => {
        this.record = res.data
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    initForm() {
      this.record = {
        dataTransType: 1,
        enum: [],
        isLocationType: 0,
        extendTypeAttr: {},
      }
      if (this.$refs.record) {
        this.$refs.record.resetFields()
      }
    },
    // When popover is popped, set the enumeration value, the original value and the error to undefined
    showPopover() {
      this.enumValue = undefined
      this.rawValue = undefined
      this.enumValueExist = undefined
      this.rawValueExist = undefined
    },
    addEnumItem() {
      if (!this.enumValue) {
        this.enumValueExist = this.$t('dataPoints.enumNotNull')
        return
      }
      if (this.rawValue === undefined) {
        this.rawValueExist = this.$t('dataPoints.rawValueNotNull')
        return
      }
      if (this.record.enum.some((row) => { return this.enumValue === row[0] })) {
        this.enumValue = undefined
        this.enumValueExist = this.$t('dataPoints.enumRepeat')
        return
      }
      if (this.record.enum.some((row) => { return this.rawValue === row[1] })) {
        this.rawValue = undefined
        this.rawValueExist = this.$t('dataPoints.rawValueRepeat')
        return
      }
      this.record.enum.push([this.enumValue, this.rawValue])
    },
    removeEnumItem(item) {
      this.record.enum = this.record.enum.filter((row) => {
        return row !== item
      })
    },
    // Process selected data types
    handlePointType(pointDataType) {
      if (pointDataType === this.LOCATION) {
        this.record.isLocationType = 1
      } else {
        this.record.isLocationType = 0
      }
    },
    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        const data = {}
        Object.assign(data, this.record)
        data.productID = this.currentProduct.productID
        if (this.accessType === 'create') {
          httpPost(`/data_streams/${this.currentStreams.id}/data_points`, data)
            .then(() => {
              this.$message.success(this.$t('oper.addSuccess'))
              this.$emit('close-form')
            })
        } else if (this.accessType === 'edit') {
          httpPut(`${this.url}/${this.currentDataPoint.id}`, data).then(() => {
            this.$message.success(this.$t('oper.editSuccess'))
            this.$emit('close-form')
          })
        } else if (this.accessType === 'view') {
          this.$emit('close-form')
        }
      })
    },
  },
}
</script>


<style lang="scss">
.data-point-form .el-form:not(.is-details-form) .el-form-item {
  height: 81px;
}
</style>
