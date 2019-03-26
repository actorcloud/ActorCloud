<template>
  <div class="products-view emq-crud">
    <div class="crud-header">
      <el-row
        type="flex"
        justify="space-between"
        align="middle">
        <el-col :span="18">
          <template v-if="tenantType === 0" slot.custom-tab="crudTabsHead">
            <tabs-card-head :tabs="productsTabsHead"></tabs-card-head>
          </template>
          <span v-else class="crud-title">{{ $t('products.product') }}</span>
        </el-col>
        <el-col :span="6">
          <emq-button
            v-if="has(`POST,${url}`)"
            class="create-btn"
            @click="newProduct">
            + {{ $t('oper.createBtn') }}
          </emq-button>
        </el-col>
      </el-row>
    </div>
    <empty-page v-if="isEmpty" :emptyInfo="productsEmptyInfo"></empty-page>
    <div class="emq-card-list-view product-card-list">
      <el-row :gutter="20" v-loading="loading">
        <el-col v-for="(record, index) in records" :key="index" :span="8">
          <el-card class="box-card" @click.native="showDetails(record, 'view')">
            <div slot="header" class="clearfix">
              <span>{{ record.productName }}</span>
              <el-dropdown
                v-if="(has(`PUT,${url}/:id`) || has(`DELETE,${url}`))"
                class="card-dropdown"
                trigger="click"
                :show-timeout="0">
                <el-button @click.stop type="text">
                  <i class="material-icons" style="color: #a7a7a7;">more_vert</i>
                </el-button>
                <el-dropdown-menu slot="dropdown">
                  <a
                    v-if="has(`PUT,${url}/:id`)"
                    href="javascript:;"
                    @click="showDetails(record, 'edit')">
                    <el-dropdown-item>
                      <img src="../../base/assets/images/role-edit.png">
                      {{ $t('oper.edit') }}
                    </el-dropdown-item>
                  </a>
                  <a
                    v-if="has(`DELETE,${url}`)"
                    href="javascript:;" @click="showConfirmDialog(record.id)">
                    <el-dropdown-item>
                      <img src="../../base/assets/images/role-delete.png">
                      {{ $t('oper.delete') }}
                    </el-dropdown-item>
                  </a>
                </el-dropdown-menu>
              </el-dropdown>
            </div>
            <el-form>
              <el-row>
                <el-col :span="12">
                  <el-form-item :label="`${$t('products.deviceNum')}：`">
                    <template>
                      <a
                        @click.stop="showDetails(record, 'tab', 'devices')">
                        {{ record.deviceCount }}
                      </a>
                      <span>台</span>
                    </template>
                  </el-form-item>
                </el-col>
                <el-col v-if="record.cloudProtocol === 3" :span="12">
                  <el-form-item :label="`${$t('products.item')}：`">
                    <template>
                        <a
                          @click.stop="showDetails(record, 'tab', 'items')">
                          {{ record.itemCount }}
                        </a>
                        <span>个</span>
                    </template>
                  </el-form-item>
                </el-col>
                <el-col v-if="record.cloudProtocol !== 3" :span="12">
                  <el-form-item :label="`${$t('products.dataPoints')}：`">
                    <template>
                      <span v-if="record.dataPointCount === '-'">{{ record.dataPointCount }}</span>
                      <div v-else>
                        <a
                          @click.stop="showDetails(record, 'tab', 'data_points')">
                          {{ record.dataPointCount }}
                        </a>
                        <span>个</span>
                      </div>
                    </template>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item :label="`${$t('products.application')}：`">
                    <template>
                      <span v-if="record.appCount === '-'">{{ record.appCount }}</span>
                      <div v-else>
                        <a
                          @click.stop="$router.push({ path: '/applications', query: { productID: record.productID } })">
                          {{ record.appCount }}
                        </a>
                        <span>个</span>
                      </div>
                    </template>
                  </el-form-item>
                </el-col>
                <el-col v-if="![3, 7].includes(record.cloudProtocol)" :span="12">
                  <el-form-item :label="`${$t('products.dataStreams')}：`">
                    <template>
                      <span v-if="record.dataStreamCount === '-'">{{ record.dataStreamCount }}</span>
                      <div v-else>
                        <a
                          @click.stop="showDetails(record, 'tab', 'data_streams')">
                          {{ record.dataStreamCount }}
                        </a>
                        <span>个</span>
                      </div>
                    </template>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
            <div class="cloud-protocol-tag">
              <span class="left-triangle"></span>
              <span class="white-point"></span>
              {{ record.cloudProtocolLabel }}
            </div>
          </el-card>
        </el-col>
      </el-row>

      <emq-dialog
        :title="$t('oper.warning')"
        :visible.sync="confirmDialogVisible"
        @confirm="deleteRocord">
        <span>{{ $t('oper.confirmDelete') }}</span>
      </emq-dialog>
    </div>

    <div class="footer">
      <el-pagination
        v-if="total>9"
        background
        layout="prev, pager, next"
        :current-page.sync="currentPage"
        :page-size="pageSize"
        :total="total"
        @current-change="currentPageChanged">
      </el-pagination>
    </div>
  </div>
</template>


<script>
import { httpGet, httpDelete } from '@/utils/api'
import { mapActions } from 'vuex'
import EmqDialog from '@/components/EmqDialog'
import EmptyPage from '@/components/EmptyPage'
import TabsCardHead from '@/components/TabsCardHead'

export default {
  name: 'products-view',

  components: {
    EmptyPage,
    EmqDialog,
    TabsCardHead,
  },

  data() {
    return {
      loading: false,
      confirmDialogVisible: false,
      url: this.$route.path,
      records: [],
      willDeleteId: undefined,
      currentPage: 1,
      pageSize: 9,
      total: 0,
      isEmpty: false,
      tenantType: this.$store.state.accounts.user.tenantType,
      productsTabsHead: [
        {
          code: 'products',
          order: 1,
          url: '/products',
        },
        {
          code: 'profilesReview',
          order: 2,
          url: '/codec',
        },
      ],
      productsEmptyInfo: {
        title: '您还没有任何产品',
        subTitle: '点击右上角进行创建',
      },
    }
  },

  computed: {
    currentProducts() {
      return this.$store.state.products.currentProducts
    },
  },

  methods: {
    ...mapActions(['STORE_PRODUCTS']),
    loadRecords() {
      this.loading = true
      httpGet(`${this.url}?_page=${this.currentPage}&_limit=${this.pageSize}`).then((response) => {
        this.total = response.data.meta.count
        this.records = response.data.items
        if (!this.records.length) {
          this.isEmpty = true
        }
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    newProduct() {
      this.$router.push({ path: `${this.url}/0`, query: { oper: 'create' } })
    },
    showDetails(record, accessType, tab = undefined) {
      this.localCache(record)
      if (accessType === 'tab' && tab) {
        this.$router.push({ path: `/products/${record.id}/${tab}` })
      } else {
        this.$router.push({ path: `${this.url}/${record.id}`, query: { oper: accessType } })
      }
    },
    showConfirmDialog(deleteID = undefined) {
      if (deleteID) {
        this.willDeleteId = deleteID
      }
      this.confirmDialogVisible = true
    },
    deleteRocord() {
      httpDelete(`${this.url}?ids=${this.willDeleteId}`).then(() => {
        this.$message.success(this.$t('oper.deleteSuccess'))
        this.confirmDialogVisible = false
        this.loadRecords()
      })
      this.confirmDialogVisible = false
    },
    currentPageChanged(page) {
      this.currentPage = page
      this.loadRecords()
    },
    localCache(cache) {
      const currentProducts = this.currentProducts.slice()
      const currentProduct = {
        productName: cache.productName,
        productIntID: cache.id,
        cloudProtocol: cache.cloudProtocol,
        gatewayProtocol: cache.gatewayProtocol,
        productID: cache.productID,
        productType: cache.productType,
      }
      const hasExist = currentProducts.find(item => item.productIntID === cache.id)
      if (!hasExist) { // Join the cache when there is no such product in the cache
        currentProducts.push(currentProduct)
      }
      this.STORE_PRODUCTS({ currentProducts })
    },
  },
  
  created() {
    this.loadRecords()
  },
}
</script>


<style lang="scss">
@import '~@/assets/scss/emqCardList.scss';

.products-view {
  .product-card-list {
    .box-card {
      height: auto;
      .el-card__header {
        line-height: 16px;
        padding: 20px 30px;
      }
      .el-card__body {
        padding: 10px 30px 30px;
      }
      .el-form-item {
        margin-bottom: -5px;
        height: 41px;
        .el-form-item__label {
          color: var(--color-text-light);
          font-weight: 500;
        }
        .el-form-item__content a {
          font-size: 18px;
          font-weight: 500;
        }
      }
      .cloud-protocol-tag {
        margin-top: 20px;
        position: relative;
        background-color: var(--color-bg-tag);
        display: inline-block;
        margin-left: 12px;
        line-height: 24px;
        padding: 0 12px;
        color: var(--color-text-lighter);
        .left-triangle {
          position: absolute;
          display: block;
          width: 0;
          height: 0;
          border-width: 12px 12px 12px 0;
          left: -12px;
          border-style: solid;
          border-color: transparent var(--color-bg-tag) transparent transparent;
        }
        .white-point {
          position: absolute;
          display: block;
          width: 6px;
          height: 6px;
          top: 50%;
          left: -1px;
          margin-top: -3px;
          border-radius: 50%;
          background-color: #fff;
        }
      }
    }
    .el-col-8 {
      min-width: 267px;
    }
  }
}
</style>
