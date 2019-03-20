<template>
  <el-select
    class="emq-search-select"
    filterable
    remote
    :size="size"
    :placeholder="placeholder"
    :multiple="multiple"
    :disabled="selectDisabled"
    :value="secureValue"
    :remote-method="remoteMethod"
    :loading="loading"
    :clearable="clearable"
    :collapse-tags="collapseTags"
    @input="change"
    @focus="handleAutoComplete">
    <div v-if="field.url">
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
import select from '@/mixins/select'

export default {
  name: 'emq-search-select',
  mixins: [select],
  data() {
    return {
    }
  },
  methods: {
    // Remote search
    remoteMethod(searchValue) {
      clearTimeout(this.timer)
      if (!searchValue) {
        return
      }
      this.timer = setTimeout(() => {
        let params = Object.assign({}, this.field.params)
        if (this.field.searchKey) {
          const searchKey = `${this.field.searchKey}_like`
          params = Object.assign({}, params, { [searchKey]: searchValue })
        }
        // Get the data using detailsKey filtering
        if (this.selectDisabled || !this.editing) {
          delete params[`${this.field.searchKey}_like`]
          params[this.field.detailsKey] = this.value
        }
        this.loading = true
        httpGet(this.field.url, { params }).then((response) => {
          // Remote search edit status: options always keep the value of the selected option to avoid overwriting the search results
          if (this.field.state === 'edit') {
            const hash = {}
            // The selected value, hash
            this.secureValue.forEach((value) => {
              hash[value] = true
            })
            // Selected option
            const options = this.options.filter($ => hash[$.value])
            // Array deduplication -> option
            response.data.forEach((item) => {
              if (!hash[item.value]) {
                options.push(item)
              }
            })
            this.options = options
          } else {
            this.options = response.data
          }
          this.loading = false
        }).catch(() => {
          this.loading = false
        })
      }, 200)
    },
    // Focus first gives partial options
    handleAutoComplete() {
      if (this.visibleChange()) {
        this.loadOptions()
      }
    },
    // Judgment dependent field
    visibleChange() {
      this.editing = true
      if (this.field.rely && !this.relyData) {
        this.$message.error(`请先选择${this.field.relyName}！`)
        return false
      }
      return true
    },
    // Assemble the options
    handleOptions() {
      if (this.field.options && this.field.options.length) {
        this.options = this.field.options
      }
    },
  },
  mounted() {
    this.handleOptions()
  },
}
</script>


<style lang="scss">
.emq-search-select {
  width: 100%;
}
</style>
