<template>
  <div class="details-view subscriptions-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/products` }">产品</el-breadcrumb-item>
        <el-breadcrumb-item>
          <product-breadcrumb
            :currentProduct="currentProduct || {}">
          </product-breadcrumb>
        </el-breadcrumb-item>
        <el-breadcrumb-item>代理订阅</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>
    <div v-if="currentProduct" class="detail-tabs">
      <emq-button
        class="custom-button"
        @click="handleAddTopic">
        + {{ $t('oper.createBtn') }}
      </emq-button>
      <product-detail-tabs v-if="currentProduct"></product-detail-tabs>
    </div>
    <emq-crud
      v-if="currentProduct"
      ref="crud"
      class="emq-crud--details"
      :url="`/products/${this.currentProduct.productIntID}/subscriptions`"
      :tableActions="[]">
      <template slot="tableColumns">
        <el-table-column label="主题" prop="topic"></el-table-column>
        <el-table-column label="Qos" prop="qos"></el-table-column>
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

    <!-- Add topic -->
    <emq-dialog
      :title="$t('devices.addTopic')"
      :visible.sync="dialogVisible"
      @close="handleClose"
      @confirm="addTopic">
      <el-form
        ref="record"
        :model="record"
        :rules="topicRules">
        <el-form-item prop="topic" :label="$t('devices.topic')">
          <el-input v-model="record.topic" :placeholder="$t('devices.topicRequired')"></el-input>
        </el-form-item>
      </el-form>
    </emq-dialog>
  </div>
</template>


<script>
import { httpPost, httpDelete } from '@/utils/api'
import { currentProductsMixin } from '@/mixins/currentProducts'
import EmqCrud from '@/components/EmqCrud'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import ProductDetailTabs from '@/apps/products/components/ProductDetailTabs'
import EmqDialog from '@/components/EmqDialog'
import ProductBreadcrumb from '../components/ProductBreadcrumb'

export default {
  name: 'subscriptions-view',

  mixins: [currentProductsMixin],

  components: {
    EmqDetailsPageHead,
    ProductDetailTabs,
    EmqCrud,
    EmqDialog,
    ProductBreadcrumb,
  },

  data() {
    return {
      dialogVisible: false,
      confirmDialogVisible: false,
      record: {
        topic: '',
      },
      topicRules: {
        topic: [
          { required: true, message: this.$t('devices.topicRequired') },
        ],
      },
    }
  },

  methods: {
    addTopic() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return
        }
        httpPost(`/products/${this.currentProduct.productIntID}/subscriptions`, this.record)
          .then(() => {
            this.dialogVisible = false
            this.$message.success(this.$t('devices.addTopicSuccess'))
            this.$refs.crud.loadRecords()
          })
      })
    },
    handleAddTopic() {
      this.record.topic = ''
      this.dialogVisible = true
    },
    handleClose() {
      this.$refs.record.resetFields()
      this.record.topic = ''
    },
    deleteRecord(ids) {
      this.$confirm('确认删除', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        cancelButtonClass: 'cancel-button',
        type: 'warning',
      }).then(() => {
        httpDelete(`/products/${this.currentProduct.productIntID}/subscriptions`, { params: { ids } })
          .then(() => {
            this.$message.success('删除成功')
            this.$refs.crud.loadRecords()
          })
      }).catch(() => {})
    },
  },
}
</script>
