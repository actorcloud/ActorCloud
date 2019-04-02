<template>
  <el-row v-loading="loading" class="data-points-form-view" :gutter="40">
    <el-form
      ref="record"
      :label-position="accessType === 'view' ? 'left' : 'top'"
      label-width="130px"
      :class="disabled ? 'is-details-form' : ''"
      :model="record"
      :rules="disabled ? {} : rules">
      <el-col :span="12">
        <el-form-item :label="$t('products.dataPointName')" prop="dataPointName">
          <el-input
            type="text"
            v-model="record.dataPointName"
            :placeholder="disabled ? '' : '请输入功能点名称'"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="功能点标识" prop="dataPointID">
          <el-popover
            placement="top-start"
            width="200"
            trigger="hover"
            content="数据传输时的变量名，支持英文字母、数字、下划线组合，需以英文字母开头">
          </el-popover>
          <i
            slot="reference"
            class="el-icon-question tips-icon"
            style="left: -50px;">
          </i>
          <el-input
            type="text"
            v-model="record.dataPointID"
            :placeholder="disabled ? '' : '请输入设备上报的属性名称'"
            :disabled="accessType !== 'create'">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="数据类型" prop="pointDataType">
          <el-select
            v-model="record.pointDataType"
            style="width: 100%;"
            :placeholder="disabled ? '' : '请选择'"
            :disabled="accessType !== 'create'"
            @input="handlePointType">
            <el-option
              v-for="item in pointDataTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
      </el-col>
      <el-col v-show="record.pointDataType === 6" :span="12">
        <el-form-item  v-if="record.pointDataType === 6" label="位置类型" prop="locationType">
          <emq-select
            v-model="record.locationType"
            :field="{ key: 'locationType' }"
            :record="record"
            :placeholder="disabled ? '' : '请选择'"
            :disabled="accessType !== 'create'">
          </emq-select>
        </el-form-item>
      </el-col>
      <el-col v-if="currentProduct.cloudProtocol === ModBus" :span="12">
        <el-form-item label="地址" prop="registerAddr">
          <el-input
            type="text"
            v-model="record.registerAddr"
            placeholder="请输入地址"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="数据传输类型" prop="dataTransType">
          <emq-select
            v-model="record.dataTransType"
            :field="{ key: 'dataTransType' }"
            :record="record"
            :placeholder="disabled ? '' : '请选择'"
            :disabled="disabled">
          </emq-select>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === 1" :span="12">
        <el-form-item label="单位名称" prop="unitName">
          <el-input
            type="text"
            v-model="record.unitName"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === 1" :span="12">
        <el-form-item label="单位符号" prop="unitSymbol">
          <el-input
            type="text"
            v-model="record.unitSymbol"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === 1" :span="12">
        <el-form-item label="数据范围(上限)" prop="upperLimit">
          <el-input
            type="number"
            v-model="record.upperLimit"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === 1" :span="12">
        <el-form-item label="数据范围(下限)" prop="lowerLimit">
          <el-input
            type="number"
            v-model="record.lowerLimit"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="record.pointDataType === 1" :span="12">
        <el-form-item label="数据步长" prop="dataStep">
          <el-input
            type="number"
            v-model="record.dataStep"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="[1, 3].includes(record.pointDataType)" :span="12">
        <el-form-item label="枚举值" prop="enum" style="min-height: 41px;">
          <el-popover
            v-if="!disabled"
            v-model="popoverVisible"
            popper-class="enum-popover"
            placement="bottom"
            title="添加枚举"
            width="240">
            <el-form label-position="left" label-width="60px">
              <el-form-item label="显示值">
                <el-input
                  v-model="enumValue"
                  :class="{'error': enumValueExist}"
                  :placeholder="enumValueExist"
                  @focus="enumValueExist=undefined">
                </el-input>
              </el-form-item>
              <el-form-item label="原始值">
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
                @click="popoverVisible=false">取消
              </el-button>
              <el-button
                type="success"
                size="mini"
                @click="addEnumItem">确定
              </el-button>
            </div>
            <el-button
              style="margin-right: 20px"
              slot="reference"
              type="success"
              size="mini"
              @click="showPopover">
              + 添加
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
      <el-col v-if="record.pointDataType === 4" :span="12">
        <el-form-item label="故障值" prop="faultValue">
          <el-input
            type="text"
            v-model="record.faultValue"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="备注" prop="detail">
          <el-input
            :type="disabled ? 'text' : 'textarea'"
            :placeholder="disabled ? '' : '请输入功能点描述'"
            v-model="record.detail"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="accessType === 'view'" :span="12">
        <el-form-item label="创建人">
          <el-input
            v-model="record.createUser"
            :disabled="disabled">
          </el-input>
        </el-form-item>
      </el-col>
      <el-col v-if="accessType === 'view'" :span="12">
        <el-form-item label="创建时间">
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
        callback(new Error('请输入功能点标识'))
      } else {
        if (!value.match(/^[a-zA-Z]\w*$/g)) {
          callback(new Error('仅支持英文字母、数字、下划线组合，需以英文字母开头'))
        }
        callback()
      }
    }
    return {
      ModBus: 7,
      loading: false,
      record: {
        dataPointName: undefined,
        dataPointID: undefined,
        pointDataType: undefined,
        dataTransType: 1,
        unitName: undefined,
        unitSymbol: undefined,
        upperLimit: undefined,
        lowerLimit: undefined,
        dataStep: undefined,
        enum: [],
        faultValue: undefined,
        detail: undefined,
        createAt: undefined,
        createUser: undefined,
        isLocationType: 0,
        locationType: undefined,
      },
      rules: {
        dataPointID: [
          { validator: validatePointID, required: true },
        ],
        dataPointName: [
          { required: true, message: '请输入功能点名称' },
        ],
        dataTransType: [
          { required: true, message: '请选择数据传输类型' },
        ],
        registerAddr: [
          { required: true, message: '请输入地址' },
        ],
        pointDataType: [
          { required: true, message: '请选择数据类型' },
        ],
        faultValue: [
          { required: true, message: '请输入故障值' },
        ],
        locationType: [
          { required: true, message: '请选择位置类型' },
        ],
      },
      popoverVisible: false,
      enumValue: undefined,
      rawValue: undefined,
      enumValueExist: undefined,
      rawValueExist: undefined,
      pointDataTypeOptions: [],
    }
  },

  computed: {
    disabled() {
      return this.accessType === 'view'
    },
  },

  methods: {
    // Load data
    loadData() {
      this.setDataTypeOptions()
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
      }
      if (this.$refs.record) {
        this.$refs.record.resetFields()
      }
      this.pointDataTypeOptions = []
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
        this.enumValueExist = '枚举值不能为空'
        return
      }
      if (this.rawValue === undefined) {
        this.rawValueExist = '原始值不能为空'
        return
      }
      if (this.record.enum.some((row) => { return this.enumValue === row[0] })) {
        this.enumValue = undefined
        this.enumValueExist = '枚举值重复'
        return
      }
      if (this.record.enum.some((row) => { return this.rawValue === row[1] })) {
        this.rawValue = undefined
        this.rawValueExist = '原始值重复'
        return
      }
      this.record.enum.push([this.enumValue, this.rawValue])
    },
    removeEnumItem(item) {
      this.record.enum = this.record.enum.filter((row) => {
        return row !== item
      })
    },
    // Reorganize options of data type
    setDataTypeOptions() {
      if (this.currentProduct.cloudProtocol !== this.ModBus) {
        this.pointDataTypeOptions = this.$store.state.base.dictCode.pointDataType.filter(
          item => item.value < 10,
        )
      } else { // Data type of modbus protocol
        this.pointDataTypeOptions = this.$store.state.base.dictCode.pointDataType.filter(
          item => item.value <= 25 && item.value >= 21,
        )
      }
    },
    // Process selected data types
    handlePointType(pointDataType) {
      if (pointDataType === 6) {
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
        data.productIntID = this.currentProduct.productIntID
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
