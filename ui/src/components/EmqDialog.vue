<template>
  <el-dialog
    class="emq-dialog"
    :visible.sync="showDialog"
    :title="title"
    :width="width"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @open="open"
    @close="close">
    <!-- The contents of the popover -->
    <slot></slot>
    <div v-if="!isView" slot="footer" class="dialog-footer">
      <el-button class="cancel" type="text" size="small" @click="hideDialog">取 消</el-button>
      <emq-button
        class="save"
        :loading="saveLoading"
        :disabled="btnDisabled"
        @click="confirmClick">确定
      </emq-button>
    </div>
  </el-dialog>
</template>


<script>
import EmqButton from '@/components/EmqButton'

export default {
  name: 'emq-dialog',
  components: {
    EmqButton,
  },
  props: {
    // The title name to display
    title: {
      type: String,
      required: true,
    },
    // The width of the dialog
    width: {
      type: String,
      default: '400px',
    },
    // Show dialog
    visible: {
      type: Boolean,
      default: false,
    },
    // Whether to show bottom operation
    isView: {
      type: Boolean,
      default: false,
    },
    // Button status
    saveLoading: {
      type: Boolean,
      default: false,
    },
    // Button
    btnDisabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      showDialog: this.visible,
    }
  },
  watch: {
    visible(val) {
      this.showDialog = val
    },
  },
  methods: {
    confirmClick() {
      // Confirm event
      this.$emit('confirm')
    },
    open() {
      // Open the dialog event
      this.$emit('open')
    },
    close() {
      this.$emit('update:visible', false)
      // Close the dialog event
      this.$emit('close')
    },
    hideDialog() {
      // Hide the Dialog event
      this.$emit('update:visible', false)
    },
  },
}
</script>


<style lang="scss">
.emq-dialog {
  .el-dialog__header {
    padding: 0 20px;
    line-height: 56px;
    .el-dialog__title {
      color: var(--color-text-lighter);
    }
    .el-icon-close {
      vertical-align: middle;
    }
  }
  .el-dialog__body {
    padding: 20px 20px 10px;
    .el-form-item__label {
      color: var(--color-text-light)
    }
  }
  .el-dialog__footer {
    padding: 5px 20px 20px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    .el-button--text {
      font-size: 14px;
      margin-right: 24px;
      color: var(--color-text-light);
      &:hover {
        color: var(--color-main-green);
      }
    }
  }
}
</style>
