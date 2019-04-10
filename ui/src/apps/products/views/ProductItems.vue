<template>
  <div class="details-view product-items-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/products` }">{{ $t('products.product') }}</el-breadcrumb-item>
        <el-breadcrumb-item>
          <product-breadcrumb
            :currentProduct="currentProduct || {}">
          </product-breadcrumb>
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('items.item') }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>
    <div class="detail-tabs">
      <emq-button
        class="custom-button"
        @click="dialogVisible = true">
        + {{ $t('oper.createBtn') }}
      </emq-button>
      <product-detail-tabs v-if="currentProduct"></product-detail-tabs>
    </div>
    <emq-crud
      v-if="currentProduct"
      ref="crud"
      class="emq-crud--details"
      :url="url"
      :tableActions="tableActions">
      <template slot="tableColumns">
        <el-table-column prop="objectID" :label="$t('items.objectID')"></el-table-column>
        <el-table-column prop="itemID" :label="$t('items.itemID')"></el-table-column>
        <el-table-column min-width="180px" prop="itemName" :label="$t('items.itemName')"></el-table-column>
        <el-table-column prop="itemType" :label="$t('items.itemType')"></el-table-column>
        <el-table-column prop="itemUnit" :label="$t('items.itemUnit')"></el-table-column>
        <el-table-column prop="itemOperations" :label="$t('items.itemOperations')"></el-table-column>
        <el-table-column width="60px">
          <template v-slot="props">
            <a
              href="javascript:;"
              @click="deleteRecord(props.row.id)">
              <img src="~@/assets/images/delete.png"/>
            </a>
          </template>
        </el-table-column>
      </template>
    </emq-crud>

    <!-- Add attribute -->
    <emq-dialog
      width="650px"
      :title="$t('items.addItem')"
      :visible.sync="dialogVisible"
      :btnDisabled="btnDisabled"
      @confirm="save">
      <el-row :gutter="10">
        <el-form
          ref="itemForm"
          :model="itemForm"
          :rules="itemFormRules">
          <el-col :span="10">
            <el-form-item prop="objectID">
              <el-input
                clearable
                v-model="itemForm.objectID"
                size="medium"
                :placeholder="$t('items.objectIDReruired')">
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item prop="itemID">
              <el-input
                clearable
                v-model="itemForm.itemID"
                size="medium"
                :placeholder="$t('items.itemIDRequired')">
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <emq-button class="search-button" @click="searchItem">{{ $t('oper.search') }}</emq-button>
          </el-col>
        </el-form>
        <el-col :span="24">
        <el-table
          v-loading="loading"
          class="item-table"
          size="medium"
          :data="records"
          :empty-text="$t('oper.noData')">
          <el-table-column prop="objectID" :label="$t('items.objectID')"></el-table-column>
          <el-table-column prop="itemID" :label="$t('items.itemID')"></el-table-column>
          <el-table-column prop="itemName" min-width="180px" :label="$t('items.itemName')"></el-table-column>
          <el-table-column prop="itemType" :label="$t('items.itemType')"></el-table-column>
        </el-table>
        </el-col>
      </el-row>
    </emq-dialog>
  </div>
</template>


<script>
import { httpGet, httpPost, httpDelete } from '@/utils/api'

import { currentProductsMixin } from '@/mixins/currentProducts'
import EmqCrud from '@/components/EmqCrud'
import EmqButton from '@/components/EmqButton'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqDialog from '@/components/EmqDialog'
import ProductDetailTabs from '@/apps/products/components/ProductDetailTabs'
import ProductBreadcrumb from '../components/ProductBreadcrumb'

export default {
  name: 'product-items-view',

  mixins: [currentProductsMixin],

  components: {
    EmqButton,
    EmqDetailsPageHead,
    ProductDetailTabs,
    EmqDialog,
    EmqCrud,
    ProductBreadcrumb,
  },

  data() {
    return {
      dialogVisible: false,
      loading: false,
      btnDisabled: true,
      itemForm: {},
      records: [],
      itemFormRules: {
        objectID: [
          { required: true, message: this.$t('items.objectIDReruired'), trigger: 'blur' },
        ],
        itemID: [
          { required: true, message: this.$t('items.itemIDRequired'), trigger: 'blur' },
        ],
      },
      productIntID: this.$route.params.id,
      tableActions: ['delete'],
    }
  },

  computed: {
    url() {
      return `/products/${this.$route.params.id}/lwm2m_items`
    },
  },

  watch: {
    dialogVisible() {
      if (!this.dialogVisible) {
        this.itemForm = {}
        this.$refs.itemForm.resetFields()
        this.btnDisabled = true
        this.records = []
      }
    },
  },

  methods: {
    save() {
      if (!this.records.length) {
        this.$message.error(this.$t('items.itemRequired'))
      }
      httpPost(this.url, this.itemForm).then(() => {
        this.$message.success(this.$t('oper.addSuccess'))
        this.dialogVisible = false
        this.$refs.crud.loadData()
      })
    },
    searchItem() {
      this.$refs.itemForm.validate((valid) => {
        if (!valid) {
          return false
        }
        this.records = [] // Empty the table after each search
        this.loading = true
        httpGet(`/lwm2m_items?objectID=${this.itemForm.objectID}&itemID=${this.itemForm.itemID}`)
          .then((response) => {
            this.btnDisabled = false
            this.records.push(response.data)
            this.loading = false
          }).catch((error) => {
            if (error.response.status === 404) {
              this.$message.error(this.$t('items.lwm2mItemRequired'))
              this.btnDisabled = true
              this.loading = false
            }
          })
      })
    },
    deleteRecord(ids) {
      this.$confirm(this.$t('oper.confirmDelete'), this.$t('oper.warning'), {
        confirmButtonText: this.$t('oper.confirm'),
        cancelButtonText: this.$t('oper.cancel'),
        cancelButtonClass: 'cancel-button',
        type: 'warning',
      }).then(() => {
        httpDelete(this.url, { params: { ids } }).then(() => {
          this.$message.success(this.$t('oper.deleteSuccess'))
          this.$refs.crud.loadData()
        })
      }).catch(() => {})
    },
  },
}
</script>


<style lang="scss">
.product-items-view {
  .emq-dialog {
    .search-button {
      margin-top: 3px;
    }
    .item-table {
      border: 1px solid var(--color-line-card);
      border-bottom: none;
      margin-bottom: 10px;
    }
  }
}
</style>
