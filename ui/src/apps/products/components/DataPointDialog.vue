<template>
  <el-dialog
    ref="dataPointsDialog"
    width="700px"
    :class="['details-view', 'data-points-dialog-view',
      accessType === 'create' ? 'hide-title' : '']"
    :visible.sync="showDialog"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @close="hideDialog">

    <template v-if="accessType !== 'create'" v-slot:title>
      <span class="el-dialog__title">{{ dataPointOper }}</span>
    </template>

    <el-tabs
      v-model="activeType"
      :class="accessType !== 'create' ? 'hide-tabs' : ''"
      @tab-click="handleTabsClick">
      <el-tab-pane :label="dataPointOper" name="add">
        <data-point-form
          ref="dataPointForm"
          class="data-point-form"
          :url="url"
          :currentProduct="currentProduct"
          :currentStreams="currentStreams"
          :currentDataPoint="currentDataPoint"
          :accessType="accessType"
          @close-form="hideDialog">
        </data-point-form>
      </el-tab-pane>

      <el-tab-pane
        v-if="accessType === 'create'"
        name="select"
        :label="$t('dataPoints.selectDataPoint')">
        <data-point-table
          ref="dataPointTable"
          class="data-point-table"
          :url="`${url}?productID=${currentProduct.productID}`"
          :currentStreams="currentStreams"
          @close-table="hideDialog">
        </data-point-table>
      </el-tab-pane>
    </el-tabs>

    <div slot="footer" class="dialog-footer">
      <el-button
        class="cancel"
        type="text"
        size="small"
        @click="hideDialog">{{ $t('oper.cancel') }}
      </el-button>
      <emq-button
        v-if="accessType !== 'view'"
        class="save"
        :loading="saveLoading"
        @click="confirmClick">{{ $t('oper.save') }}
      </emq-button>
    </div>
  </el-dialog>
</template>


<script>
import EmqButton from '@/components/EmqButton'
import DataPointTable from './DataPointTable'
import DataPointForm from './DataPointForm'

export default {
  name: 'data-points-dialog-view',

  props: {
    visible: {
      type: Boolean,
      required: true,
    },
    accessType: {
      type: String,
      required: true,
    },
    currentStreams: {
      type: Object,
      required: true,
    },
    currentDataPoint: {
      type: Object,
      required: true,
    },
    currentProduct: {
      type: Object,
      required: true,
    },
  },

  components: {
    EmqButton,
    DataPointTable,
    DataPointForm,
  },

  data() {
    return {
      url: '/data_points',
      saveLoading: false,
      showDialog: this.visible,
      activeType: 'add',
    }
  },

  watch: {
    visible(val) {
      if (val) {
        setTimeout(() => {
          this.$refs.dataPointForm.loadData()
        }, 500)
      } else {
        this.$refs.dataPointForm.initForm()
      }
      this.showDialog = val
      this.activeType = 'add'
    },
  },

  computed: {
    dataPointOper() {
      switch (this.accessType) {
        case 'create':
          return this.$t('dataPoints.addDataPoint')
        case 'edit':
          return this.$t('dataPoints.editDataPoint')
        case 'view':
          return this.$t('dataPoints.viewDataPoint')
        default:
          return this.$t('dataPoints.addDataPoint')
      }
    },
  },

  methods: {
    confirmClick() {
      if (this.activeType === 'add') {
        this.$refs.dataPointForm.save()
      } else if (this.activeType === 'select') {
        this.$refs.dataPointTable.save()
      }
    },
    // Hide dialog
    hideDialog() {
      this.$emit('update:visible', false)
    },
    handleTabsClick() {
      if (this.activeType === 'select') {
        this.$refs.dataPointTable.loadDataPoint(true)
      } else if (this.activeType === 'add' && this.accessType !== 'create') {
        this.$refs.dataPointForm.loadData()
      }
    },
  },
}
</script>


<style lang="scss">
.data-points-dialog-view {

  .el-dialog__header {
    border-bottom: 1px solid var(--color-line-bg);
    padding: 20px;
    .el-dialog__title {
      color: var(--color-text-lighter);
    }
  }

  .el-dialog__body {
    padding: 5px 20px 20px 20px;
    .el-form--label-top .el-form-item__label {
      padding: 0px;
    }
  }

  .el-dialog__footer .el-button--text {
    font-size: 14px;
    margin-right: 24px;
    color: var(--color-text-light);
    &:hover {
      color: var(--color-main-green);
    }
  }

  .data-point-table {
    margin-top: 10px;
  }

  .hide-tabs.el-tabs {
    .el-tabs__nav-scroll {
      display: none;
    }
  }
}

.hide-title.el-dialog__wrapper {
  .el-dialog__header {
    display: none;
  }
}
</style>
