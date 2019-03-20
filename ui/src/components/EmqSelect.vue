<template>
  <el-select
    class="emq-select"
    :size="size"
    :placeholder="placeholder"
    :multiple="multiple"
    :collapse-tags="collapseTags"
    :disabled="selectDisabled"
    :value="secureValue"
    :loading="loading"
    :clearable="clearable"
    @visible-change="visibleChange"
    @input="change"
    @clear="resetValue">
    <!-- Locking dependencies apply only to non-server loads -->
    <div v-if="!relyLocked">
      <el-option
        v-for="option in options"
        :key="option.value"
        :label="option.label"
        :value="option.value"
        :disabled="disableOptions.includes(option.value)">
      </el-option>
    </div>
  </el-select>
</template>


<script>
import { httpGet } from '@/utils/api'

import loadDictCode from '@/mixins/loadDictCode'
import select from '@/mixins/select'

export default {
  name: 'emq-select',
  mixins: [loadDictCode, select],
  props: {
    // Whether to select for auto
    autoSelect: {
      type: Boolean,
      default: true,
    },
    // The default reset value
    defaultResetValue: {
      default: undefined,
    },
  },
  data() {
    return {
    }
  },
  watch: {
    'field.options': 'autoSelectFirst',
    // Listen for changes in the values of the fields on which select depends
    relyData(newValue, oldValue) {
      if (oldValue !== undefined) {
        this.$emit('input', undefined, null)
      }
      if (this.field.options) {
        return
      }
      this.loadWithRely()
    },
  },
  computed: {
    dictCode() {
      return this.$store.state.base.dictCode
    },
  },
  methods: {
    loadData() {
      // Use the prop options
      if (this.field.options) {
        this.options = this.field.options
        this.autoSelectFirst()
        return
      }
      // Load dictcode
      if (!this.field.url) {
        this.options = this.dictCode[this.field.key] || []
        if (this.field.rely) {
          this.relyLocked = true
        }
        this.autoSelectFirst()
        return
      }
      if (this.field.rely || this.field.visibleLoad) {
        return
      }
      this.loadOptions()
    },
    // Load options based on the dependent data
    loadWithRely() {
      if (this.relyData) {
        if (this.field.url) {
          httpGet(this.field.url, { params: { [this.field.rely]: this.relyData } })
            .then((response) => {
              this.options = response.data
            })
        } else {
          this.relyLocked = false
        }
      } else if (this.field.url) { // If the dependent fields are null, your own drop-down list is also null
        this.options = []
      } else { // Lock dependencies and hide drop-down lists
        this.relyLocked = true
      }
    },
    // The first is selected by default
    autoSelectFirst() {
      if (this.autoSelect && !this.multiple && !this.value && this.options[0]) {
        this.$emit('input', this.options[0].value, this.options[0])
      }
    },
    // Customize the reset value after deselect
    resetValue() {
      // Select the successful trigger event
      this.$emit('input', this.defaultResetValue, null)
    },
    visibleChange(visible) {
      this.editing = true
      if (visible && this.field.rely && !this.relyData) {
        this.$message.error(`请先选择${this.field.relyName}！`)
      } else if (visible) {
        this.relyLocked = false
        if (this.field.visibleLoad) {
          this.loadOptions()
        }
      }
    },
  },
}
</script>


<style lang="scss">
.emq-select {
  width: 100%;
}
</style>
