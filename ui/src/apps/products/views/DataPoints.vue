<template>
  <div class="details-view data-points-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/products` }">产品</el-breadcrumb-item>
        <el-breadcrumb-item>
          <product-breadcrumb
            :currentProduct="currentProduct || {}">
          </product-breadcrumb>
        </el-breadcrumb-item>
        <el-breadcrumb-item>功能点</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>
    <div v-if="currentProduct" class="detail-tabs">
      <emq-button
        v-if="has('POST,/data_points')"
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
      :url="`/data_points?productID=${this.currentProduct.productID}`"
      :tableActions="tableActions">
      <template slot="tableColumns">
        <el-table-column :label="$t('products.dataPointName')" prop="dataPointName">
          <template v-slot="scope">
            <router-link
              :to="{
                  path: `/products/${productIntID}/data_points/${scope.row.id}`,
                  query: { oper: 'view' }
                }">
              {{ scope.row.dataPointName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="功能点标识" prop="dataPointID"></el-table-column>
        <el-table-column label="数据类型" prop="pointDataTypeLabel"></el-table-column>
        <el-table-column label="数据传输类型" prop="dataTransTypeLabel"></el-table-column>
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
  name: 'data-points-view',

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
