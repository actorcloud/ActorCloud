<template>
  <div class="create-products-view">
    <emq-dialog
      :title="$t('products.createProduct')"
      :visible.sync="visible"
      width="40%"
      @confirm="save">
      <el-form
        ref="record"
        :rules="rules"
        :model="record">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item :label="$t('products.productName')" prop="productName">
              <el-input
                type="text"
                :placeholder="$t('products.productNameRequired')"
                v-model="record.productName">
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="$t('products.cloudProtocol')" prop="cloudProtocol">
              <emq-select
                v-model="record.cloudProtocol"
                :autoSelect="true"
                :field="{ key: 'cloudProtocol' }"
                :record="record"
                :placeholder="$t('oper.select')"
                :disabled="false">
              </emq-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="$t('products.productType')" prop="productType">
              <emq-select
                v-model="record.productType"
                :field="{ key: 'productType' }"
                :record="record"
                :placeholder="$t('oper.select')"
                :disabled="false">
              </emq-select>
            </el-form-item>
          </el-col>
          <el-col v-if="record.productType === 2" :span="24">
            <el-form-item :label="$t('products.gatewayProtocol')" prop="gatewayProtocol">
              <emq-select
                v-model="record.gatewayProtocol"
                :field="{ key: 'gatewayProtocol' }"
                :record="record"
                :placeholder="$t('oper.select')"
                :disabled="false">
              </emq-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="$t('products.productDescription')" prop="description">
              <el-input
                type="textarea"
                :placeholder="$t('products.descriptionRequired')"
                v-model="record.description">
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </emq-dialog>
  </div>
</template>


<script>
import EmqDialog from '@/components/EmqDialog'
import { httpPost } from '@/utils/api'

export default {
  name: 'create-products-view',

  components: {
    EmqDialog,
  },

  props: {
    dialogVisible: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      record: {},
      rules: {
        productName: [
          { required: true, message: this.$t('products.productNameRequired'), trigger: 'blur' },
        ],
        cloudProtocol: [
          { required: true, message: this.$t('products.cloudProtocolRequired'), trigger: 'blur' },
        ],
        productType: [
          { required: true, message: this.$t('products.productTypeRequired'), trigger: 'blur' },
        ],
        gatewayProtocol: [
          { required: true, message: this.$t('products.gatewayProtocolRequired'), trigger: 'blur' },
        ],
      },
    }
  },

  computed: {
    visible: {
      get() {
        return this.dialogVisible
      },
      set(val) {
        this.$emit('update:dialogVisible', val)
        this.$refs.record.resetFields()
      },
    },
  },

  methods: {
    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        httpPost('/products', this.record).then((res) => {
          this.record = {}
          this.$refs.record.resetFields()
          this.$message.success(this.$t('oper.createSuccess'))
          this.$emit('update:dialogVisible', false)
          this.$parent.selectNewProduct(res.data)
        })
      })
    },
  },
}
</script>
