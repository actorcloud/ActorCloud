<template>
  <div class="details-view product-details-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/products` }">{{ $t('products.product') }}</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentProduct">
          <product-breadcrumb
            :currentProduct="currentProduct">
          </product-breadcrumb>
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ accessType !== 'create' ? $t('products.productInfo') : '新建' }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <!-- Not displayed only when created -->
    <div v-if="accessType !== 'create'" class="detail-tabs">
      <product-detail-tabs v-if="currentProduct"></product-detail-tabs>
    </div>
    <div class="product-card-details-body">
      <el-card v-loading="pageLoading" :class="disabled ? 'is-details-form' : ''">
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
            label-width="82px"
            :model="record"
            :rules="disabled ? {} : rules">
            <el-col :span="12">
              <el-form-item :label="$t('products.productName')" prop="productName">
                <el-input
                  type="text"
                  :placeholder="disabled ? '' : $t('products.productNameRequired')"
                  v-model="record.productName"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-show="disabled || $route.query.oper === 'create' " :span="12">
              <el-form-item :label="$t('products.cloudProtocol')" prop="cloudProtocol">
                <emq-select
                  v-model="record.cloudProtocol"
                  :field="{ key: 'cloudProtocol' }"
                  :record="record"
                  :placeholder="$t('oper.select')"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col v-if="disabled" :span="12">
              <el-form-item :label="$t('products.productID')" prop="productID">
                <el-input
                  type="text"
                  v-model="record.productID"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="产品类型" prop="productType">
                <emq-select
                  v-model="record.productType"
                  :field="{ key: 'productType' }"
                  :record="record"
                  :placeholder="$t('oper.select')"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col v-if="(disabled || $route.query.oper === 'create') && record.productType === 2" :span="12">
              <el-form-item label="网关协议" prop="gatewayProtocol">
                <emq-select
                  v-model="record.gatewayProtocol"
                  :field="{ key: 'gatewayProtocol' }"
                  :record="record"
                  :placeholder="$t('oper.select')"
                  :disabled="disabled">
                </emq-select>
              </el-form-item>
            </el-col>
            <el-col v-if="disabled" :span="12">
              <el-form-item label="设备数量">
                <el-input
                  v-model="record.deviceCount"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('products.productDescription')" prop="description">
                <el-input
                  :type="disabled ? 'text' : 'textarea'"
                  :placeholder="disabled ? '' : $t('products.descriptionRequired')"
                  v-model="record.description"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="disabled" :span="12">
              <el-form-item :label="$t('products.createUser')">
                <el-input
                  v-model="record.createUser"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="disabled" :span="12">
              <el-form-item :label="$t('products.createAt')">
                <el-input
                  v-model="record.createAt"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <emq-button v-if="!disabled" icon="save" :loading="btnLoading"  @click="save">
          {{ $t('oper.finish') }}
        </emq-button>
      </el-card>
    </div>

    <el-dialog
      class="emq-dialog create-success"
      width="420px"
      :visible.sync="createVisable"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false">
      <img src="~@/assets/images/created.png" width="180">
      <h1>产品创建成功</h1>
      <div class="create-success__oper">
        <el-button
          class="add-button"
          @click="createDevice">
          {{ record.productType === 2 ? '立即添加网关' : '立即添加设备' }}
        </el-button>
        <el-button
          class="cancel"
          @click="backProducts">
          暂不添加
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>


<script>
import { httpPost, httpPut } from '@/utils/api'
import detailsPage from '@/mixins/detailsPage'
import { currentProductsMixin } from '@/mixins/currentProducts'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqButton from '@/components/EmqButton'
import ProductDetailTabs from '@/apps/products/components/ProductDetailTabs'
import ProductBreadcrumb from '../components/ProductBreadcrumb'

export default {
  name: 'product-details-view',

  mixins: [detailsPage, currentProductsMixin],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    ProductDetailTabs,
    ProductBreadcrumb,
  },

  data() {
    return {
      creaetdRecord: {}, // Information returned by the backend after successful creation
      tempProduct: {},
      url: '/products',
      createVisable: false,
      btnLoading: false,
      tempLink: '/devices/devices/0/create_device', // Jump to the create device/gateway link after successful creation
      rules: {
        productName: [
          { required: true, message: this.$t('products.productNameRequired'), trigger: 'blur' },
        ],
        cloudProtocol: [
          { required: true, message: this.$t('products.cloudProtocolRequired'), trigger: 'blur' },
        ],
        gatewayProtocol: [
          { required: true, message: '请选择网关协议', trigger: 'blur' },
        ],
        productType: [
          { required: true, message: '请选择产品类型', trigger: 'blur' },
        ],
      },
    }
  },

  methods: {
    showDetails() {
      this.disabledState = !this.disabledState
      // Cancel editing: Record content does not change with unsaved items
      if (!this.disabledState) {
        this.$router.push({ path: this.$route.path, query: { oper: 'edit', url: '/products' } })
        this.stashRecord = { ...this.record }
      } else {
        this.$router.push({ path: this.$route.path, query: { oper: 'view', url: '/products' } })
        this.record = { ...this.stashRecord }
      }
    },
    // Save or edit
    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        this.btnLoading = true
        if (this.accessType === 'create') {
          httpPost(this.url, this.record).then((response) => {
            this.creaetdRecord = response.data
            this.btnLoading = false
            this.createVisable = true
          }).catch(() => {
            this.btnLoading = false
          })
        } else if (this.accessType === 'edit' || !this.disabled) {
          httpPut(`${this.url}/${this.detailsID}`, this.record).then(() => {
            const currentProduct = {
              productName: this.record.productName,
              productIntID: this.record.id,
              cloudProtocol: this.record.cloudProtocol,
              gatewayProtocol: this.record.gatewayProtocol,
              productID: this.record.productID,
              productType: this.record.productType,
            }
            this.btnLoading = false
            this.currentProduct = currentProduct // 更新成功后修改当前产品
            this.updateLocalCache(currentProduct)
            this.$message.success('编辑成功!')
            this.loadData()
            this.toggleStatus()
          })
        }
      })
    },
    processLoadedData(record) {
      // In the edit state, save the current record, used to restore data when canceling editing
      if (this.accessType === 'edit') {
        this.stashRecord = { ...this.record }
      }
      if (!this.currentProduct) {
        this.localCache(record)
      }
    },
    createDevice() {
      if (this.record.productType === 2) {
        this.tempLink = '/devices/gateways/0?oper=create'
      }
      this.$router.push({
        path: this.tempLink,
        query: {
          productID: this.creaetdRecord.productID,
          productIntID: this.creaetdRecord.id,
          cloudProtocol: this.creaetdRecord.cloudProtocol,
          gatewayProtocol: this.creaetdRecord.gatewayProtocol,
          productName: this.creaetdRecord.productName,
        },
      })
    },
    backProducts() {
      this.$router.push({ path: this.listPageURL })
    },
  },
}
</script>
