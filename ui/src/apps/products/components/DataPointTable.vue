<template>
  <div class="details-view data-points-table-view">
    <el-table
      v-loading="selectLoading"
      class="select-table"
      ref="multipleTable"
      tooltip-effect="dark"
      style="width: 100%"
      :data="dataPointList.currentPageList"
      @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column :label="$t('products.dataPointName')" prop="dataPointName"></el-table-column>
      <el-table-column :label="$t('dataPoints.dataPointID')" prop="dataPointID"></el-table-column>
      <el-table-column :label="$t('dataPoints.pointDataType')" prop="pointDataTypeLabel"></el-table-column>
      <el-table-column :label="$t('dataPoints.dataTransType')" prop="dataTransTypeLabel"></el-table-column>
      <el-table-column v-if="has('PUT,/certs/:id')" width="60px">
        <template v-slot="{ row }">
          <a
            style="float: none"
            href="javascript:;"
            :title="$t('oper.delete')"
            @click="deleteRecord(row.id)">
            <i class="iconfont icon-emq-delete"></i>
          </a>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-if="count>=5"
      background
      layout="total, prev, pager, next"
      :page-size="5"
      :current-page.sync="params._page"
      :total="count"
      @current-change="loadDataPoint(false)">
    </el-pagination>
  </div>
</template>


<script>
import { httpGet, httpPut, httpDelete } from '@/utils/api'

export default {
  name: 'data-points-table-view',

  props: {
    url: {
      type: String,
      required: true,
    },
    currentStreams: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      selectLoading: false,
      dataPointList: {
        currentPageList: [],
        currentPageActiveList: [],
        selectDataPoint: {},
      },
      streamReacord: {},
      params: {
        _page: 1,
        _limit: 5,
      },
      count: 0,
    }
  },

  methods: {
    loadDataPoint(reload = false) {
      this.selectLoading = true
      this.dataPointList.currentPageActiveList = []
      if (reload) { // Clear selected and reset page number
        this.$set(this.params, '_page', 1)
        this.dataPointList.selectDataPoint = {}
        this.loadSelectedDataPoints()
      }
      const { params } = this
      httpGet(this.url, { params }).then((res) => {
        this.dataPointList.currentPageList = res.data.items
        this.selectLoading = false
        this.handleActiveSelection()
        this.count = res.data.meta.count || 0
      }).catch(() => {
        this.selectLoading = false
      })
    },
    loadSelectedDataPoints() {
      httpGet(`/data_streams/${this.currentStreams.id}/data_points`).then((res) => {
        this.streamReacord.dataPoints = res.data.map($ => $.id)
        // Highlight bound dataPoints
        this.streamReacord.dataPoints.forEach((dataPoint) => {
          this.dataPointList.selectDataPoint[dataPoint] = dataPoint
        })
      })
    },
    // Process selected columns
    handleSelectionChange(row) {
      const ids = row.map(dataPoint => dataPoint.id)
      row.forEach((dataPoint) => {
        // Add
        this.dataPointList.selectDataPoint[dataPoint.id] = dataPoint.id
      })
      this.dataPointList.currentPageActiveList.forEach((id) => {
        // Remove
        if (!ids.includes(id)) {
          delete this.dataPointList.selectDataPoint[id]
        }
      })
    },
    // Highlight, record the selected column of the current page
    handleActiveSelection() {
      setTimeout(() => {
        this.dataPointList.currentPageList.forEach((row) => {
          this.dataPointList.currentPageActiveList.push(row.id)
          if (this.dataPointList.selectDataPoint[row.id]) {
            this.$refs.multipleTable.toggleRowSelection(row)
          }
        })
      }, 10)
    },
    save() {
      const { dataPoints } = this.streamReacord
      const newDataPoints = Object.values(this.dataPointList.selectDataPoint)
      if (newDataPoints.length === 0) {
        this.$message.error(this.$t('dataPoints.dataPointRequired'))
        return
      }
      this.streamReacord.dataPoints = [...new Set([...newDataPoints, ...dataPoints])]
      httpPut(`/data_streams/${this.currentStreams.id}/data_points`, this.streamReacord)
        .then(() => {
          this.$message.success(this.$t('oper.addSuccess'))
          this.$emit('close-table')
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
          this.loadDataPoint()
        })
      }).catch(() => {})
    },
  },
}
</script>


<style lang="scss">
.data-points-table-view {
  .select-table.el-table--fit {
    border: 1px solid var(--color-line-card);
    border-bottom: 0;
  }
  .el-pagination {
    margin: 20px auto;
    float: right;
  }
}
</style>
