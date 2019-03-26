<template>
  <div class="details-view data-points-details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/products/${this.$route.params.id}/data_points` }">功能点</el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>
    <div>
      <el-card :class="disabled ? 'is-details-form' : ''">
        <edit-toggle-button
          :url="url"
          :disabled="disabled"
          :accessType="accessType"
          @toggleStatus="toggleStatus">
        </edit-toggle-button>
        <el-row :gutter="40">
          <el-form
            ref="record"
            label-position="left"
            label-width="130px"
            :model="record"
            :rules="disabled ? {} : rules">
            <el-col :span="12">
              <el-form-item label="功能点名称" prop="dataPointName">
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
                  <el-option-group
                    v-for="group in pointDataTypeOptions"
                    :key="group.label"
                    :label="group.label">
                    <el-option
                      v-for="item in group.options"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value">
                    </el-option>
                  </el-option-group>
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
            <!-- Binary types correspond to different length fields -->
            <el-col v-if="[11, 13, 19, 21, 22, 23, 24, 25].includes(record.pointDataType)" :span="12">
              <el-form-item
                prop="binarySize"
                :label="record.pointDataType === 19 ? '长度（bit）' : record.pointDataType === 23 ? '第几位' : '长度（字节）'">
                <el-input
                  v-model.number="record.binarySize"
                  type="number"
                  :placeholder="disabled ? '' : '请输入'"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="record.pointDataType === 21" :span="12">
              <el-form-item
                prop="decimal"
                label="小数位">
                <el-input
                  v-model.number="record.decimal"
                  type="number"
                  :placeholder="disabled ? '' : '请输入'"
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
            <el-col v-if="[1, 3, 11, 12, 15, 16, 19].includes(record.pointDataType)" :span="12">
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
            <!-- <el-col v-if="record.pointDataType === 4" :span="12">
              <el-form-item label="故障时丢弃消息" prop="isDiscard">
                <el-select
                  v-model="record.isDiscard"
                  style="width: 100%;"
                  :placeholder="disabled ? '' : '请选择故障时是否丢弃消息'"
                  :disabled="disabled">
                  <el-option label="是" :value="1"></el-option>
                  <el-option label="否" :value="0"></el-option>
                </el-select>
              </el-form-item>
            </el-col> -->
            <el-col
              v-if="[15, 16, 17, 18].includes(record.pointDataType)"
              :span="12">
              <el-form-item label="长度（字节）" prop="binarySize">
                <el-select
                  v-model="record.binarySize"
                  style="width: 100%;"
                  :placeholder="disabled ? '' : '请选择长度'"
                  :disabled="disabled || [17, 18].includes(record.pointDataType)">
                  <el-option label="1字节" :value="1"></el-option>
                  <el-option label="2字节" :value="2"></el-option>
                  <el-option label="4字节" :value="4"></el-option>
                  <el-option
                    v-if="[16, 18].includes(record.pointDataType)"
                    label="8字节"
                    :value="8">
                  </el-option>
                </el-select>
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
        <emq-button v-if="!disabled" icon="save" @click="save">
          完成
        </emq-button>
      </el-card>
    </div>
  </div>
</template>


<script>
import detailsPage from '@/mixins/detailsPage'
import EmqSelect from '@/components/EmqSelect'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqButton from '@/components/EmqButton'

export default {
  name: 'product-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    EmqSelect,
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
      url: '/data_points',
      ModBus: 7,
      record: {
        dataPointName: undefined,
        dataPointID: undefined,
        productIntID: this.$route.path.split('/')[2] || undefined,
        pointDataType: undefined,
        dataTransType: undefined,
        unitName: undefined,
        unitSymbol: undefined,
        upperLimit: undefined,
        lowerLimit: undefined,
        dataStep: undefined,
        enum: [],
        faultValue: undefined,
        // isDiscard: undefined,
        detail: undefined,
        createAt: undefined,
        createUser: undefined,
        isLocationType: 0,
        locationType: undefined,
        binarySize: undefined,
      },
      rules: {
        dataPointID: [
          { validator: validatePointID, required: true, trigger: 'blur' },
        ],
        dataPointName: [
          { required: true, message: '请输入功能点名称', trigger: 'blur' },
        ],
        dataTransType: [
          { required: true, message: '请选择数据传输类型', trigger: 'blur' },
        ],
        registerAddr: [
          { required: true, message: '请输入地址' },
        ],
        pointDataType: [
          { required: true, message: '请输入数据类型', trigger: 'blur' },
        ],
        faultValue: [
          { required: true, message: '请输入故障值', trigger: 'blur' },
        ],
        // isDiscard: [
        //   { required: true, message: '请选择故障时是否丢弃消息', trigger: 'blur' },
        // ],
        locationType: [
          { required: true, message: '请选择位置类型', trigger: 'blur' },
        ],
        binarySize: [
          { required: true, message: '请输入长度', trigger: 'blur' },
        ],
        decimal: [
          { type: 'number', required: true, message: '请输入小数位', trigger: 'blur' },
          { pattern: /^\d+$/, message: '请输入正整数', trigger: 'change' },
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

  watch: {
    'record.pointDataType': 'pointDataTypeChange',
  },

  computed: {
    currentProduct() {
      const { currentProducts } = this.$store.state.products
      return currentProducts.find(item => item.productIntID === parseInt(this.$route.params.id, 10))
    },
  },

  methods: {
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
    pointDataTypeChange(newValue) {
      if (newValue === 17) {
        this.record.binarySize = 4
      } else if (newValue === 18) {
        this.record.binarySize = 8
      }
    },
    // Reorganize options of data type
    pointDataTypeOptionsGroup() {
      if (this.currentProduct.cloudProtocol !== this.ModBus) {
        const pointDataTypeJson = this.$store.state.base.dictCode.pointDataType.filter((item) => {
          return item.value < 10
        })
        const pointDataTypeBinary = this.$store.state.base.dictCode.pointDataType.filter((item) => {
          return item.value > 10 && item.value < 21
        })
        const jsonOptions = { options: pointDataTypeJson }
        const binaryOptions = { options: pointDataTypeBinary }
        if (this.record.pointDataType > 10) {
          this.pointDataTypeOptions.push(binaryOptions)
        } else if (this.record.pointDataType < 10) {
          this.pointDataTypeOptions.push(jsonOptions)
        } else {
          jsonOptions.label = 'JSON类型'
          binaryOptions.label = '二进制类型'
          this.pointDataTypeOptions = [jsonOptions, binaryOptions]
        }
      } else { // Data type of modbus protocol
        const modBusPointType = this.$store.state.base.dictCode.pointDataType.filter((item) => {
          return item.value <= 25 && item.value >= 21
        })
        this.pointDataTypeOptions.push({ options: modBusPointType })
      }
    },
    processLoadedData() {
      this.pointDataTypeOptionsGroup()
    },
    // Process selected data types
    handlePointType(pointDataType) {
      if (pointDataType === 6) {
        this.record.isLocationType = 1
      } else {
        this.record.isLocationType = 0
      }
    },
  },

  created() {
    if (this.accessType === 'create') {
      this.pointDataTypeOptionsGroup()
    }
  },
}
</script>


<style lang="scss">
.data-points-details-view {
  .el-form {
    .el-form-item__content {
      position: relative;
      .tips-icon {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
      }
    }
    .el-tag {
      margin-right: 8px;
    }
  }
}

.enum-popover {
  padding: 16px 20px;
  .el-popover__title {
    margin-bottom: 24px;
    font-size: 15px;
    font-weight: 400;
  }
}
</style>
