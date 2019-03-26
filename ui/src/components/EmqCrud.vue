<template>
  <div class="emq-crud">

    <div class="crud-header default-header">
      <el-row type="flex" justify="space-between" align="middle">
        <el-col :span="16">
          <!-- Custom header tabs -->
          <slot name="crudTabsHead">
            <span class="crud-title">{{ crudTitle }}</span>
          </slot>
        </el-col>
        <el-col :span="8">
          <!-- Create button -->
          <slot name="createButton">
            <emq-button
              v-if="tableActions.includes('create') && has(`POST,${url}`)"
              class="create-btn"
              @click="showDetails('create')">
              + {{ $t('oper.createBtn') }}
            </emq-button>
          </slot>
        </el-col>
      </el-row>
    </div>

    <!-- Search form -->
    <emq-search-form
      v-if="tableActions.includes('search')"
      class="search"
      :searchOptions="searchOptions"
      :valueOptions="valueOptions"
      :timeSearch="timeSearch"
      :searchTimeOptions="searchTimeOptions"
      :autocomplete="autocomplete"
      :customQueryMethod="customQueryMethod"
      :loading="searchLoading"
      @search="search">
    </emq-search-form>

    <!-- Custom button -->
    <div
      v-if="(tableActions.includes('deleteAll') && this.selectedRecords.length !== 0)
        || tableActions.includes('import')
        || (tableActions.includes('export') && this.permissions[`${this.url}_export`])
        || tableActions.includes('refresh')
        || tableActions.includes('custom')"
      class="custom-btn--wrapper">
      <!-- Refresh -->
      <el-button
        v-if="tableActions.includes('refresh')"
        icon="el-icon-refresh"
        class="operation-btn refresh shadow-btn"
        size="small"
        round
        @click="loadRecords">
        刷新
      </el-button>
      <!-- Batch delete -->
      <el-button
        v-if="tableActions.includes('deleteAll') && this.selectedRecords.length !== 0"
        class="operation-btn delete-all shadow-btn"
        icon="el-icon-delete"
        size="small"
        round
        @click="showConfirmDialog()">
        删除
      </el-button>
      <!-- Custom button -->
      <slot name="customButton"></slot>
      <!-- Import -->
      <el-button
        v-if="tableActions.includes('import') && this.permissions[`${this.url}_import`]"
        icon="el-icon-upload2"
        size="small"
        class="operation-btn import shadow-btn"
        @click="$refs.importExcelComp.showDialog()">批量导入
      </el-button>
      <!-- Export -->
      <emq-export-excel
        v-if="tableActions.includes('export') && this.permissions[`${this.url}_export`]"
        class="export shadow-btn"
        :url="url">
      </emq-export-excel>
    </div>

    <el-card class="table-wrapper">
      <div v-if="cardHeader" slot="header">
        <!-- Custom card header -->
        <slot name="el-card-header"></slot>
      </div>
      <!-- table -->
      <el-table
        ref="crudTable"
        v-loading="loading"
        class="my-table"
        size="medium"
        :data="records"
        :empty-text="emptyText"
        :row-key="getRowKeys"
        :expand-row-keys="expands"
        @sort-change="loadRecords"
        @filter-change="dataFilter"
        @selection-change="selectionChange"
        @expand-change="expandChange">
        <el-table-column
          v-if="tableActions.includes('deleteAll') || selection"
          type="selection"
          width="40">
        </el-table-column>
        <!-- Table other columns -->
        <slot name="tableColumns"></slot>
        <!-- Table operation -->
        <el-table-column
          v-if="has(`PUT,${url}/:id`) || has(`DELETE,${url}`)"
          min-width="90px"
          class-name="oper">
          <template v-slot="props">
            <slot name="customOper" :row="props.row"></slot>
            <div
              v-if="tableActions.includes('edit') && has(`PUT,${url.split('?')[0]}/:id`)"
              @click="showDetails('edit', props.row.id)"
              class="oper-button">
              <i class="iconfont icon-emq-edit"></i>
            </div>
            <div
              v-if="tableActions.includes('delete') && has(`DELETE,${url}`)"
              @click="showConfirmDialog(props.row.id)"
              class="oper-button">
              <i class="iconfont icon-emq-delete"></i>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <div class="footer">
      <!-- paging -->
      <el-pagination
        v-if="total>=1"
        background
        layout="sizes, prev, pager, next"
        :current-page.sync="currentPage"
        :page-sizes="[10, 100, 200, 500]"
        :page-size="pageSize"
        :total="total"
        @current-change="currentPageChanged"
        @size-change="handleSizeChange">
      </el-pagination>
    </div>

    <emq-import-excel
      v-if="tableActions.includes('import')"
      ref="importExcelComp"
      :url="url"
      :reloadData="loadRecords">
    </emq-import-excel>

    <emq-dialog
      title="警告"
      :visible.sync="confirmDialogVisible"
      @confirm="deleteRecords">
      <span>确认删除？</span>
    </emq-dialog>

  </div>
</template>


<script>
/* eslint-disable no-underscore-dangle */
import dateformat from 'dateformat'

import { httpGet, httpDelete } from '@/utils/api'
import EmqSearchForm from '@/components/EmqSearchForm'
import EmqDialog from '@/components/EmqDialog'
import EmqButton from '@/components/EmqButton'
import EmqImportExcel from '@/components/EmqImportExcel'
import EmqExportExcel from '@/components/EmqExportExcel'

export default {
  name: 'emq-crud',

  components: {
    EmqSearchForm,
    EmqDialog,
    EmqButton,
    EmqImportExcel,
    EmqExportExcel,
  },

  props: {
    // Table title
    crudTitle: {
      type: String,
    },
    // Auto load or not
    autoLoad: {
      type: Boolean,
      default: true,
    },
    // Operations supported by tables: ['search', 'create','edit', 'delete', 'deleteAll', 'refresh', 'import', 'search', 'custom']
    tableActions: {
      type: Array,
      default: () => ['search', 'create'],
    },
    // Input search opthons
    searchOptions: {
      type: Array,
      default: () => [],
    },
    // Select search options
    valueOptions: {
      type: Object,
      default: () => {
        return {}
      },
    },
    // Search time options
    searchTimeOptions: {
      type: Array,
    },
    // Whether to display time search
    timeSearch: {
      type: Boolean,
      default: false,
    },
    // The REST api to get table data
    url: {
      type: String,
      required: true,
    },
    // Whether to display the header
    cardHeader: {
      type: Boolean,
      default: false,
    },
    // Whether you can check the data
    selection: {
      type: Boolean,
      default: false,
    },
    // Automatically selected values
    autocomplete: {
      type: Object,
      default: () => ({}),
    },
    // Events for custom queries
    customQueryMethod: {
      type: Function,
      default: null,
    },
    // Whether to turn on accordion
    accordion: {
      type: Boolean,
      default: false,
    },
    // Whether there are default expansion rows
    isDefaultExpand: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      loading: false,
      searchLoading: false,
      confirmDialogVisible: false,
      currentPageURL: '',
      searchKeywordName: '',
      searchKeywordValue: '',
      searchTimeName: '',
      searchTimeValue: '',
      tableFilterConditions: {}, // Table fitler
      selectedRecords: [], // The selected record to delete
      willDelectIds: [], // The list of deleted ids
      records: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      permissions: {},
      emptyText: ' ',
      httpConfig: {},
      expands: [], // Expand row，the value is the key value of the row
      getRowKeys(row) { // Gets the key value of the row
        return row.id
      },
    }
  },

  methods: {
    // Load permissions, table data
    loadData(config) {
      Object.assign(this.httpConfig, config)
      this.permissions = this.$store.state.base.permissions || {}
      this.currentPageURL = this.$route.path
      this.loadRecords()
    },

    // Load table data
    loadRecords(
      column,
      searchKeywordName = '',
      searchKeywordValue = '',
      tableFilterConditions = {},
      searchTimeName = '',
      searchTimeValue = '',
    ) {
      if (!this.url) {
        return
      }
      const params = {
        _page: this.currentPage,
        _limit: this.pageSize,
      }
      if (!this.httpConfig.disableLoading) {
        this.loading = true
        this.records = []
      }
      // Query the filter parameters of the route
      const queryKeys = Object.keys(this.$route.query)
      if (queryKeys.length) {
        queryKeys.forEach((key) => {
          params[key] = this.$route.query[key]
        })
      }
      // Sort by field value up/down
      if (column) {
        try {
          const [prop, order] = [column.prop, column.order.replace('ending', '')]
          params._sort = prop
          params._order = order
        } catch (e) {
          // eslint-disable-next-line
          console.log()
        }
      }
      // Field name retrieval
      const validSearchValue = searchKeywordValue || searchKeywordValue === 0
      if (searchKeywordName && validSearchValue) {
        if (typeof (searchKeywordValue) === 'number') { // 数字精确检索
          params[searchKeywordName] = searchKeywordValue
        } else if (typeof (searchKeywordValue) === 'string') { // 字符串模糊检索
          params[`${searchKeywordName}_like`] = searchKeywordValue
        }
      }
      // Header joint filtering
      /* eslint-disable */
      if (Object.keys(tableFilterConditions).length !== 0) {
        for (let item in tableFilterConditions) {
          if (tableFilterConditions[item] !== undefined) {
            params[item] = tableFilterConditions[item]
          }
        }
      }
      // Time search
      if (searchTimeName && searchTimeValue
        && searchTimeValue.length > 0 && searchTimeValue[0] && searchTimeValue[1]) {
        const startTime = dateformat(searchTimeValue[0], 'yyyy-mm-dd HH:MM:ss')
        const endTime = dateformat(searchTimeValue[1], 'yyyy-mm-dd HH:MM:ss')
        params.start_time = startTime
        params.end_time = endTime
        params.time_name = searchTimeName
      }
      httpGet(this.url, { params, ...this.httpConfig }).then((response) => {
        if (response.data.meta) {
          this.total = response.data.meta.count || 0
          if (response.data.items.length === 0 && response.data.meta.page > 1) {
            this.currentPageChanged(this.currentPage - 1)
          }
        }
        const records = response.data.items
        this.searchLoading = false
        this.loading = false
        this.records = records
        if (this.isDefaultExpand) { // Expands the first row when there is a default expanded row
          this.expands.push(this.records[0].id)
        }
        if (this.records.length < 1) {
          this.emptyText = '暂无数据'
        } else {
          this.emptyText = ' '
        }
      }).catch((error) => {
        this.loading = false
        this.searchLoading = false
      })
    },

    // Page switching updates data
    currentPageChanged(page) {
      this.currentPage = page
      this.loadRecords(
        {},
        this.searchKeywordName,
        this.searchKeywordValue,
        this.tableFilterConditions,
        this.searchTimeName,
        this.searchTimeValue,
      )
    },

    // Handle page size change
    handleSizeChange(val) {
      this.pageSize = val
      this.loadRecords(
        {},
        this.searchKeywordName,
        this.searchKeywordValue,
        this.tableFilterConditions,
        this.searchTimeName,
        this.searchTimeValue,
      )
    },

    search(
      searchKeywordName,
      searchKeywordValue,
      tableFilterConditions,
      searchTimeName,
      searchTimeValue,
      config,
    ) {
      this.searchLoading = true
      this.currentPage = 1
      this.searchKeywordName = searchKeywordName
      this.searchKeywordValue = searchKeywordValue
      this.tableFilterConditions = tableFilterConditions
      this.searchTimeName = searchTimeName
      this.searchTimeValue = searchTimeValue
      Object.assign(this.httpConfig, config)
      this.loadRecords(
        {},
        searchKeywordName,
        searchKeywordValue,
        tableFilterConditions,
        searchTimeName,
        searchTimeValue,
      )
    },

    // Delete confirm dialog
    showConfirmDialog(deleteID = undefined) {
      if (deleteID) {
        this.willDelectIds = deleteID
      } else {
        this.willDelectIds = this.selectedRecords.map((record) => {
          return record.id
        })
      }
      this.confirmDialogVisible = true
    },

    // Delete selected records
    deleteRecords() {
      httpDelete(`${this.url.split('?')[0]}?ids=${this.willDelectIds}`).then((response) => {
        if (response.status === 204) {
          this.$message.success('删除成功!')
          this.confirmDialogVisible = false
          this.loadRecords()
        } else {
          this.$message.error('删除失败!')
          this.confirmDialogVisible = false
        }
      })
    },

    // Check the callback for each record to be selected
    selectionChange(selections) {
      this.selectedRecords = selections
      // Triggered when a single item of data is ticked
      this.$emit('selection-change', this.selectedRecords)
    },

    // A callback that is triggered when a row is expanded
    expandChange(row, expanded) {
      this.$emit('expand-change', row, expanded)
      if (this.accordion && this.$refs.crudTable) {
        this.$refs.crudTable.store.states.expandRows = expanded.length ? [row] : []
      }
    },

    // To view details
    showDetails(accessType, id = 0) {
      // Special treatment from the product details page
      const arrURL = this.currentPageURL.split('/')
      if (arrURL.includes('devices') && arrURL.includes('products')) {
        this.currentPageURL = '/devices/devices'
      }
      this.$router.push({
        path: `${this.currentPageURL}/${id}`,
        query: { oper: accessType }
      })
    },

    // Header fitler
    dataFilter(value) {
      this.tableFilterConditions[Object.keys(value)[0]] = Object.values(value)[0][0]
      this.loadRecords(
        {},
        this.searchKeywordName,
        this.searchKeywordValue,
        this.tableFilterConditions,
        this.searchTimeName,
        this.searchTimeValue,
      )
    },
  },

  created() {
    if (this.autoLoad) {
      this.loadData()
    }
  },
}
</script>
