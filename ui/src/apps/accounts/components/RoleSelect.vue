<template>
  <!-- The select of roles is a special component, because the response code needs to be translated -->
  <el-select
    class="role-select"
    :size="size"
    :placeholder="placeholder"
    :disabled="disabled"
    :value="value"
    @input="change">
    <el-option
      v-for="option in options"
      :key="option.value"
      :label="option.label | convertRoleName"
      :value="option.value">
    </el-option>
  </el-select>
</template>


<script>
import { httpGet } from '@/utils/api'

export default {
  name: 'role-select',

  props: {
    value: {
      required: true,
    },
    field: {
      type: Object,
      required: true,
    },
    disabled: {
      type: Boolean,
    },
    placeholder: {
      type: String,
    },
    size: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      options: [],
    }
  },

  methods: {
    loadOptions() {
      let params = ''
      if (this.field.params) {
        params = Object.assign({}, this.field.params)
      }
      httpGet(this.field.url, { params }).then((response) => {
        this.options = response.data
      })
    },

    // When the select value changes, the v-model binding of the parent component is triggered
    change(value) {
      const selectedItem = this.options.find($ => $.value === value)
      this.$emit('input', value, selectedItem)
    },
  },

  created() {
    this.loadOptions()
  },
}
</script>


<style lang="scss">
.role-select {
  width: 100%;
}
</style>
