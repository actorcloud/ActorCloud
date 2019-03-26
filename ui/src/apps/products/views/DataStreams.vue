<template>
  <div class="details-view data-streams-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/products` }">产品</el-breadcrumb-item>
        <el-breadcrumb-item>
          <product-breadcrumb
            :currentProduct="currentProduct || {}">
          </product-breadcrumb>
        </el-breadcrumb-item>
        <el-breadcrumb-item>数据流</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>
    <div v-if="currentProduct" class="detail-tabs">
      <emq-button
        v-if="has('POST,/data_streams')"
        class="custom-button"
        @click="$router.push({
          path: `${$route.path}/0`,
          query: { oper: 'create' }})">
        + {{ $t('oper.createBtn') }}
      </emq-button>
      <product-detail-tabs v-if="currentProduct"></product-detail-tabs>
    </div>
    <emq-crud
      v-if="currentProduct"
      class="emq-crud--details"
      :url="`/data_streams?productID=${this.currentProduct.productID}`"
      :tableActions="tableActions">
      <template slot="tableColumns">
        <el-table-column label="数据流名称" prop="streamName">
          <template v-slot="scope">
            <router-link
              :to="{
                  path: `/products/${productIntID}/data_streams/${scope.row.id}`,
                  query: { oper: 'view' }
                }">
              {{ scope.row.streamName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="主题" prop="topic"></el-table-column>
        <el-table-column label="流类型" prop="streamTypeLabel"></el-table-column>
        <el-table-column label="数据格式" prop="streamDataTypeLabel"></el-table-column>
      </template>
    </emq-crud>
  </div>
</template>


<script>
import { currentProductsMixin } from '@/mixins/currentProducts'
import EmqCrud from '@/components/EmqCrud'
import EmqButton from '@/components/EmqButton'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import ProductDetailTabs from '@/apps/products/components/ProductDetailTabs'
import ProductBreadcrumb from '../components/ProductBreadcrumb'

export default {
  name: 'data-streams-view',

  mixins: [currentProductsMixin],

  components: {
    EmqButton,
    EmqDetailsPageHead,
    ProductDetailTabs,
    EmqCrud,
    ProductBreadcrumb,
  },

  data() {
    return {
      productIntID: this.$route.params.id,
      tableActions: ['edit', 'delete'],
    }
  },
}
</script>
