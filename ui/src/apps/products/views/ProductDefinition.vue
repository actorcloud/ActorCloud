<template>
  <div class="details-view product-definition-view">
    <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/products` }">{{ $t('products.product') }}</el-breadcrumb-item>
        <el-breadcrumb-item>
          <product-breadcrumb
            :currentProduct="currentProduct || {}">
          </product-breadcrumb>
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('definition.definition') }}</el-breadcrumb-item>
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
      ref="crud"
      class="emq-crud--details"
      :url="`/data_streams?productID=${this.currentProduct.productID}`"
      :tableActions="tableActions"
      :accordion="true"
      :isDefaultExpand="isExpand"
      @expand-change="handleExpand">
      <template slot="tableColumns">

        <el-table-column type="expand">
          <template v-slot="{row}">
            <div class="expand-table">
              <el-row class="expand-table__header" :gutter="10">
                <el-col :span="16">{{ $t('dataPoints.containDataPoint') }}</el-col>
                <el-col :span="8">
                  <a
                    v-if="has('POST,/data_points')"
                    class="header-oper__right"
                    href="javascript:;"
                    @click="addDataPoint('create')">+ {{ $t('dataPoints.addDataPoint') }}</a>
                  <a
                    class="header-oper__right"
                    href="javascript:;"
                    @click="viewDecode(row)">{{ $t('definition.viewDecode') }}</a>
                </el-col>
              </el-row>
              <el-table
                v-loading="loading"
                class="expand-table__body"
                border
                size="medium"
                :data="expandRecords">
                <el-table-column :label="$t('products.dataPointName')" prop="dataPointName"></el-table-column>
                <el-table-column :label="$t('dataPoints.dataPointID')" prop="dataPointID"></el-table-column>
                <el-table-column :label="$t('dataPoints.pointDataType')" prop="pointDataTypeLabel"></el-table-column>
                <el-table-column :label="$t('dataPoints.dataTransType')" prop="dataTransTypeLabel"></el-table-column>
                <el-table-column width="40px">
                  <template v-slot="props">
                    <a
                      href="javascript:;"
                      :title="$t('dataPoints.view')"
                      @click="addDataPoint('view', props.row)">
                      <i class="iconfont icon-view"></i>
                    </a>
                  </template>
                </el-table-column>
                <el-table-column width="40px">
                  <template v-slot="props">
                    <a
                      href="javascript:;"
                      :title="$t('dataPoints.edit')"
                      @click="addDataPoint('edit', props.row)">
                      <i class="iconfont icon-emq-edit"></i>
                    </a>
                  </template>
                </el-table-column>
                <el-table-column width="40px">
                  <template v-slot="props">
                    <a
                      href="javascript:;"
                      :title="$t('dataPoints.unbind')"
                      @click="unbindDataPoint(props.row.id)">
                      <i class="iconfont icon-unbind"></i>
                    </a>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="streamName" :label="$t('dataStreams.streamName')">
          <template v-slot="scope">
            <router-link
              :to="{
                  path: `/products/${productIntID}/definition/${scope.row.id}`,
                  query: { oper: 'view' }
                }">
              {{ scope.row.streamName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="streamID" :label="$t('dataStreams.streamID')"></el-table-column>
        <el-table-column prop="topic" :label="$t('dataStreams.topic')"></el-table-column>
        <el-table-column prop="streamTypeLabel" :label="$t('dataStreams.streamType')"></el-table-column>
      </template>
    </emq-crud>

    <emq-dialog
      width="500px"
      class="decode-view"
      :title="$t('definition.decode')"
      :isView="true"
      :visible.sync="decodeVisible">
      <p class="diglog-tip">{{ $t('definition.decodeTips') }}</p>
      <code-editor
        height="400px"
        lang="application/json"
        v-model="code"
        :disabled="true">
      </code-editor>
    </emq-dialog>

    <data-point-dialog
      v-if="currentProduct"
      ref="dataPointDialog"
      :accessType="dataPointOper"
      :currentProduct="currentProduct"
      :currentStreams="currentStreams"
      :currentDataPoint="currentDataPoint"
      :visible.sync="addVisible">
    </data-point-dialog>
  </div>
</template>


<script>
import { httpGet, httpDelete } from '@/utils/api'
import { currentProductsMixin } from '@/mixins/currentProducts'
import EmqCrud from '@/components/EmqCrud'
import EmqDialog from '@/components/EmqDialog'
import EmqButton from '@/components/EmqButton'
import CodeEditor from '@/components/CodeEditor'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import ProductDetailTabs from '@/apps/products/components/ProductDetailTabs'
import DataPointDialog from '../components/DataPointDialog'
import ProductBreadcrumb from '../components/ProductBreadcrumb'

export default {
  name: 'product-definition-view',

  mixins: [currentProductsMixin],

  components: {
    CodeEditor,
    EmqDialog,
    EmqButton,
    EmqDetailsPageHead,
    ProductDetailTabs,
    EmqCrud,
    DataPointDialog,
    ProductBreadcrumb,
  },

  data() {
    return {
      productIntID: this.$route.params.id,
      tableActions: ['edit', 'delete'],
      decodeVisible: false,
      addVisible: false,
      loading: false,
      dataPointOper: 'create',
      currentStreams: {},
      currentDataPoint: {},
      code: JSON.stringify({ data_type: 'event' }, null, 2),
      expandRecords: [],
    }
  },

  watch: {
    addVisible(newVal) {
      if (!newVal) {
        this.loadDataPoint(this.currentStreams.id)
      }
    },
  },

  computed: {
    isExpand() {
      const { queryID } = this.$route.query
      if (queryID) {
        this.handleExpand({ id: queryID })
        return true
      }
      return false
    },
  },

  methods: {
    addDataPoint(oper, row = null) {
      this.dataPointOper = oper
      if (oper !== 'create' && row) {
        this.currentDataPoint = row
      }
      this.addVisible = true
    },
    // Processing the expansion row
    handleExpand(row) {
      this.expandRecords = []
      this.currentStreams = row
      this.loadDataPoint(row.id)
    },
    loadDataPoint(id) {
      if (!id) {
        return
      }
      this.loading = true
      httpGet(`/data_streams/${id}/data_points`).then((res) => {
        this.expandRecords = res.data
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    unbindDataPoint(id) {
      this.$confirm(this.$t('dataPoints.unbindTips'), this.$t('dataPoints.dataPointUnbind'), {
        confirmButtonText: this.$t('oper.confirm'),
        cancelButtonText: this.$t('oper.cancel'),
        cancelButtonClass: 'cancel-button',
        type: 'warning',
      }).then(() => {
        httpDelete(`/data_streams/${this.currentStreams.id}/data_points?ids=${id}`)
          .then(() => {
            this.$message.success(this.$t('dataPoints.unbindSuccess'))
            this.loadDataPoint(this.currentStreams.id)
          })
      }).catch(() => {})
    },
    viewDecode(row) {
      const decode = {}
      const { LWM2M, LORA } = this.$variable.cloudProtocol
      const judgeCloudProtocol = [LWM2M, LORA].includes(this.currentProduct.cloudProtocol)
      if (judgeCloudProtocol && this.expandRecords.length) {
        decode.data_type = 'events'
        decode.stream_id = row.streamID
        decode.data = {}
        this.expandRecords.forEach((record) => {
          let value = null
          switch (record.pointDataType) {
            case this.$variable.pointDataType.NUMERICAL:
              value = 'Number'
              break
            case this.$variable.pointDataType.STRING:
              value = 'String'
              break
            case this.$variable.pointDataType.BOOLEAN:
              value = 'Boolean'
              break
            default:
              value = 'Number'
          }
          decode.data[record.dataPointID] = {
            time: 1547661822,
            value,
          }
        })
      }
      this.code = JSON.stringify(decode, null, 2)
      this.decodeVisible = true
    },
  },
}
</script>


<style lang="scss">
.product-definition-view {
  .emq-dialog .el-dialog__header {
    border-bottom: 1px solid var(--color-line-bg);
  }
  .emq-dialog.decode-view .el-dialog__body {
    .diglog-tip {
      color: var(--color-main-yellow);
      margin-left: 20px;
      line-height: 1.6;
    }
    padding: 2px;
  }
}
</style>
