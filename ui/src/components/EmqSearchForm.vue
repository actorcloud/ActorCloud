<template>
  <div class="emq-search-form">
    <el-row type="flex" justify="end" align="middle" :gutter="20">
      <!-- Time serach -->
      <el-col class="search-time" v-if="searchTimeOptions.length > 0" :span="9">
        <div class="search-option--title">
          &nbsp;
        </div>
        <div class="search-option--content">
          <!-- Time search name -->
          <el-select v-model="searchTimeName" size="small" :placeholder="$t('oper.select')">
            <el-option
              v-for="(option, index) in searchTimeOptions"
              :label="option.label"
              :value="option.value"
              :key="index">
            </el-option>
          </el-select>
          <!-- Time search value -->
          <el-date-picker
            size="small"
            v-model="searchTimeValue"
            prefix-icon="el-icon-date"
            class="search-value"
            popper-class="emq-search-form--date-picker"
            type="datetimerange"
            range-separator="-"
            :start-placeholder="$t('oper.startDate')"
            :end-placeholder="$t('oper.endDate')"
            :picker-options="pickerOptions"
            @change="search">
          </el-date-picker>
        </div>
      </el-col>
      <!-- Input search -->
      <el-col class="search-input" v-if="searchOptions.length > 0" :span="9">
        <div class="search-option--title">
          &nbsp;
        </div>
        <div class="search-option--content">
          <!-- Input search name -->
          <el-select v-model="searchKeywordName" size="small" :placeholder="$t('oper.select')">
            <el-option
              v-for="option in searchOptions"
              :label="option.label"
              :value="option.value"
              :key="option.id">
            </el-option>
          </el-select>
          <!-- Text search -->
          <el-input
            v-if="!valueOptions[searchKeywordName]
            && !complete[searchKeywordName]"
            size="small"
            clearable
            class="search-value text-value"
            v-model="searchKeywordValue"
            @clear="search"
            @keyup.enter.native="search">
            <el-button  class="text-search__btn" icon="el-icon-search" slot="append" @click="search"></el-button>
          </el-input>
          <!-- Search with input suggestion text -->
          <el-autocomplete
            v-if="!valueOptions[searchKeywordName]
            && complete[searchKeywordName]"
            v-model="searchKeywordValue"
            clearable
            size="small"
            class="search-value autocomplete-value"
            popper-class="autocomplete"
            :fetch-suggestions="handleComplete"
            @select="search"
            @keyup.enter.native="search">
            <!-- When selected, item.value is assigned to the component value -->
            <template v-slot="{ item }">
              <div class="label">{{ item.label }}</div>
              <div v-if="item.info" class="value">{{ item.info }}</div>
            </template>
            <el-button icon="el-icon-search" slot="append" @click="search"></el-button>
          </el-autocomplete>
          <!-- Select search -->
          <el-select
            v-if="valueOptions[searchKeywordName] && !valueOptions[searchKeywordName].isCascader"
            clearable
            size="small"
            class="search-value select-value"
            v-model="searchKeywordValue"
            :placeholder="$t('oper.select')"
            @change="search">
            <el-option
              v-for="option in valueOptions[searchKeywordName]"
              :label="lang === 'zh' ? option.zhLabel : option.enLabel"
              :value="option.value"
              :key="option.id">
            </el-option>
          </el-select>
          <!-- Cascade serch -->
          <el-cascader
            v-if="valueOptions[searchKeywordName] && valueOptions[searchKeywordName].isCascader"
            clearable
            size="small"
            class="search-value cascader-value"
            expand-trigger="hover"
            v-model="searchCascaderValue"
            :options="valueOptions[searchKeywordName].options"
            @change="search">
          </el-cascader>
        </div>
      </el-col>
    </el-row>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'

export default {
  name: 'emq-search-form',
  /**
   * Search config:
   * { searchKeywordName1: {}, searchKeywordName2: {} }
   * searchKeywordName1:
   *   disabled: <Boolean> Disable the keyword search prompt
   *   handler: <Function> The callback parameter is the current input value and the callback handler
   *   url: <String> REST api
   *   params: <Object> Common query parameters
   *   dataKey: <String> key like { meta: {}, items: [{}, {}] } Use items in the data to get the required data
   *   keyMap: <Object>
   *     { label: 'The main data display key', value: 'Data to populate key', info: 'Secondary data display key' }
   */
  props: {
    // Input search options
    searchOptions: {
      type: Array,
      default: () => [],
    },
    /**
     * Select search config
     *   1. { key: the optional value options }
     *   2. { key：{ options: optional value, isCascader: support cascading } }
     */
    valueOptions: {
      type: Object,
      default: () => {
        return {}
      },
    },
    /**
     * Time search config
     *  value: <Sting> time value
     *  label: <String> time name
     *  filter: <Arrary> time filters, The complete ['hour', 'day', 'week', 'month']
     *  limit: <Object> search limits, The complete {time: <Number> time range, msg: <String> Message for out of range}
     *  defaultValue: <Number> time search default value, the number of milliseconds in the default time interval
     *  disabledDate: <Function> set disabled state
     */
    searchTimeOptions: {
      type: Array,
      default: () => [],
    },
    // Whether or not auto select
    autocomplete: {
      type: Object,
      default: () => ({}),
    },
    // Custom search prompts
    autocompleteMethod: {
      type: Function,
      default: null,
    },
    // Search button loading status
    loading: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    const completeStore = {
      products: [],
      groups: [],
    }
    return {
      searchKeywordName: this.searchOptions.length ? this.searchOptions[0].value : '',
      searchKeywordValue: '',
      tempSearchTimeName: null,
      searchCascaderValue: [],
      tempTimeValue: null,
      tableFilterConditions: {},
      currentSearchTime: {},
      // Default search prompt config
      defaultComplete: {
        deviceName: {
          url: '/emq_select/devices',
          keyMap: {
            label: 'label',
            value: 'label',
            info: 'value',
          },
        },
        deviceID: {
          url: '/emq_select/devices',
          keyMap: {
            label: 'value',
            value: 'value',
            info: 'label',
          },
        },
        productName: {
          handler: async (productName, cb) => {
            if (completeStore.products.length === 0) {
              const { data = [] } = await httpGet('/emq_select/products', { params: { productType: 1 } })
                .catch(() => {})
              completeStore.products = data
            }
            const res = []
            completeStore.products.forEach(({ label, value }) => {
              if (label.toLowerCase()
                .includes(productName.toLowerCase())) {
                res.push({
                  label,
                  value: label,
                  info: value,
                })
              }
            })
            cb(res)
          },
        },
        groupName: {
          handler: async (groupName, cb) => {
            if (completeStore.groups.length === 0) {
              const { data = [] } = await httpGet('/emq_select/groups')
                .catch(() => {})
              completeStore.groups = data
            }
            const res = []
            completeStore.groups.forEach(({ label, value }) => {
              if (label.toLowerCase()
                .includes(groupName.toLowerCase())) {
                res.push({
                  label,
                  value: label,
                  info: value,
                })
              }
            })
            cb(res)
          },
        },
        groupID: {
          handler: async (groupID, cb) => {
            if (completeStore.groups.length === 0) {
              const { data = [] } = await httpGet('/emq_select/groups')
                .catch(() => {})
              completeStore.groups = data
            }
            const res = []
            completeStore.groups.forEach(({ label, value }) => {
              if (value.toLowerCase()
                .includes(groupID.toLowerCase())) {
                res.push({
                  label: value,
                  value,
                  info: label,
                })
              }
            })
            cb(res)
          },
        },
      },
      // The config after merge
      complete: {},
    }
  },

  watch: {
    searchTimeOptions() {
      if (this.searchTimeOptions.length) {
        this.search()
      } else {
        this.searchTimeValue = null
      }
    },
    searchKeywordName() {
      this.searchKeywordValue = this.$route.query.queryLabel || ''
      this.searchTimeValue = []
    },
    autocomplete() {
      this.mergeComplete()
    },
  },

  computed: {
    // time search name
    searchTimeName: {
      get() {
        if (this.tempSearchTimeName) {
          return this.tempSearchTimeName
        }
        return this.searchTimeOptions.length ? this.searchTimeOptions[0].value : ''
      },
      set(newVal) {
        this.tempSearchTimeName = newVal
      },
    },
    // time serch value
    searchTimeValue: {
      get() {
        if (this.searchTimeOptions.length) {
          const currentSearchTime = this.searchTimeOptions.find(option => option.value === this.searchTimeName) || {}
          if (this.currentSearchTime.defaultValue && !this.tempTimeValue) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - currentSearchTime.defaultValue)
            return [start, end]
          }
        }
        return this.tempTimeValue
      },
      set(newVal) {
        this.tempTimeValue = newVal
      },
    },
    // time search options
    pickerOptions() {
      const currentSearchTime = this.searchTimeOptions.find(option => option.value === this.searchTimeName) || {}
      const rangeOption = {
        disabledDate: currentSearchTime.disabledDate,
        shortcuts: [{
          text: this.$t('oper.lastHour'),
          key: 'hour',
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 1)
            picker.$emit('pick', [start, end])
          },
        }, {
          text: this.$t('oper.lastDay'),
          key: 'day',
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 1)
            picker.$emit('pick', [start, end])
          },
        }, {
          text: this.$t('oper.lastWeek'),
          key: 'week',
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
            picker.$emit('pick', [start, end])
          },
        }, {
          text: this.$t('oper.lastMonth'),
          key: 'month',
          onClick(picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
            picker.$emit('pick', [start, end])
          },
        }],
      }
      // Filter the shortcuts option
      if (currentSearchTime.filter) {
        rangeOption.shortcuts = rangeOption
          .shortcuts.filter(shortcut => currentSearchTime.filter.includes(shortcut.key))
      }
      return rangeOption
    },
    // Current language
    lang() {
      return this.$store.state.accounts.lang
    },
  },

  methods: {
    search() {
      const config = { disableLoading: false }
      // Time search limits
      this.currentSearchTime = this.searchTimeOptions.find(option => option.value === this.searchTimeName) || {}
      if (this.currentSearchTime.limit && this.searchTimeValue) {
        if ((this.searchTimeValue[1] - this.searchTimeValue[0]) > this.currentSearchTime.limit.time) {
          this.$message.error(this.currentSearchTime.limit.msg)
          return
        }
      }
      // Click search event
      // @arg input value, select value, table filter, time name, time value
      this.$emit(
        'search',
        this.searchKeywordName,
        this.searchKeywordValue,
        this.tableFilterConditions,
        this.searchTimeName,
        this.searchTimeValue,
        config,
      )
    },

    // Preprocess search prompts
    handleComplete(queryString, cb) {
      cb([])
      const config = this.complete[this.searchKeywordName]
      if (!queryString || !config || config.disabled) {
        return
      }
      if (config.handler) {
        return config.handler(queryString, cb)
      }
      this.completeRequest(queryString, config, cb)
    },

    completeRequest(queryString, config = {}, cb) {
      const { url, params = {}, dataKey, keyMap = { label: 'label', value: 'value' } } = config
      if (!url) {
        return
      }
      params[`${this.searchKeywordName}_like`] = queryString
      httpGet(url, { params })
        .then((response) => {
          const data = dataKey ? response.data[dataKey] : response.data
          const res = data.map(($) => {
            return {
              label: $[keyMap.label],
              value: $[keyMap.value],
              info: $[keyMap.info],
            }
          })
          cb(res)
        })
    },

    // merge complete config
    mergeComplete() {
      this.complete = {}
      const customComplete = this.autocomplete || {}
      Object.entries(this.defaultComplete).forEach((config) => {
        const [key, value] = [config[0], config[1]]
        const complete = customComplete[key] || {}
        this.complete[key] = Object.assign({}, complete, value)
      })
    },
  },

  created() {
    this.mergeComplete()
    // The url containing the queryLabel and queryOption displays the search value in the search bar
    const { queryOption, queryLabel } = this.$route.query
    if (queryOption && queryLabel) {
      this.searchKeywordName = queryOption
    }
    // Direct search if there is a default search time
    if (this.searchTimeValue) {
      this.search()
    }
  },
}
</script>


<style lang="scss">
.emq-search-form {
  margin-bottom: 22px;

  .search-option--title {
    font-size: 14px;
    color: #A0A3AE;
    font-weight: 400;
    display: none;
  }

  .search-option--content {
    margin-top: 4px;
  }

  .el-card__body {
    padding: 20px 30px;
  }
  .el-input__inner {
    border-color: var(--color-line-bg);
  }
  .el-input-group__append, .el-input-group__prepend {
    border-color: var(--color-line-bg);
  }

  .el-select {
    float: left;
    width: 32%;
    margin-right: -1px;

    .el-input.is-focus .el-input__inner {
      border: 1px solid var(--color-line-bg);
    }
    .el-input .el-select__caret {
      color: #A57EBC;
    }
    .el-input__inner:focus {
      border-color: var(--color-line-bg);
    }
    .el-input__inner {
      border-bottom-right-radius: 0;
      border-top-right-radius: 0;
      border-right: none;
      position: relative;
      z-index: 100;
      &:hover, &:focus {
        z-index: 101;
      }
    }
    .el-input__suffix {
      z-index: 101;
    }

    &:not(.search-value) {
      .el-input {
        &.el-input--suffix {
          .el-input__inner {
            padding-left: 26px;
            border-radius: 32px 0 0 32px;
            /*text-align: center;*/
          }
        }
      }
    }
  }

  .search-value {
    float: left;
    width: 68%;
    .el-input__inner {
      border-radius: 0;
      position: relative;
      left: 1px;
      border-right: 1px solid var(--color-line-card);
      &:hover {
        border-right: 1px solid var(--color-line-bg);
      }
      &:focus {
        border-color: var(--color-line-bg);
      }
    }
    .el-input-group__append {
      background-color: var(--color-input-bg);
      position: relative;
      left: 1px;
      border-radius: 0 32px 32px 0;
      color: var(--color-text-light);
    }
    /* 时间搜索 */
    &.el-date-editor {
      border-radius: 0 32px 32px 0;
      .el-input__icon {
        &.el-icon-date {
          color: #A57EBC;
        }
      }
    }
    /* select */
    &.el-select {
      .el-input__inner {
        border-radius: 0 32px 32px 0;
      }
    }
    /* cascader */
    &.el-cascader {
      .el-cascader__label {
        line-height: 33px;
      }
      .el-input__inner {
        border-radius: 0 32px 32px 0;
      }
      .el-input.is-focus .el-input__inner {
        border: 1px solid var(--color-line-bg);
      }
      .el-input__icon {
        color: #A57EBC;
      }
    }
  }

  .time-select-col {
    width: 50%;
    border-right: 1px solid #dadbe1;
    display: flex;
    justify-content: space-between;
  }
  .time-select-col {
    .el-select {
      margin: 0;
      float: left;
      .el-input__inner {
        border-bottom-right-radius: 0;
        border-top-right-radius: 0;
      }
    }
    .el-date-editor.el-input {
      width: 62%;
      .el-input__inner {
        border-bottom-left-radius: 0;
        border-top-left-radius: 0;
        padding-right: 0;
      }
      .el-input__icon {
        display: none;
      }
    }
  }
  .el-date-editor {
    .el-range-separator {
      color: var(--color-text-lighter);
    }
    .el-range-input {
      color: var(--color-text-lighter);
      background-color: var(--color-input-bg);
    }
    .el-input__inner {
      border: none;
    }
  }
  .el-range-editor.el-input__inner {
    z-index: 101;
  }
  .el-range-editor.is-active {
    border-color: var(--color-line-bg);
  }

  .search-btn-wrapper {
    float: right;
  }

  @media screen and (min-width: 1366px) {
    .search-option--title {
      font-size: 14px;
    }

    .el-select {
      .el-input__inner {
        height: 38px;
        line-height: 38px;
      }
      .el-input__icon {
        line-height: 38px;
      }
      &:not(.search-value) {
        .el-input {
          &.el-input--suffix {
            .el-input__inner {
              border-radius: 38px 0 0 38px;
              /*text-align: center;*/
            }
          }
        }
      }
    }

    .search-value {
      .el-input__inner {
        height: 38px;
        line-height: 38px;
        /*border-radius: 0 38px 38px 0;*/
      }

      .el-input__icon {
        line-height: 38px;
      }

      &.el-cascader {
        .el-cascader__label {
          line-height: 39px;
        }
      }

      /* 时间搜索 */
      &.el-date-editor {
        border-radius: 0 38px 38px 0;
        height: 38px;
        line-height: 38px;
        .el-input__icon {
          line-height: 30px;
        }
        .el-range-separator {
          line-height: 32px;
        }
      }
    }
  }
}

.el-date-range-picker {
  background-color: var(--color-bg-card);
  border-color: var(--color-bg-card);
  box-shadow: 0 2px 6px var(--color-shadow);
  color: var(--color-text-lighter);

  .el-date-range-picker__content.is-left {
    border-color: var(--color-line-card);
  }
  .el-date-range-picker__time-header {
    border-color: var(--color-line-card);

    .el-input__inner {
      background-color: var(--color-input-bg);
      border-color: var(--color-line-card);
      color: var(--color-text-lighter);
    }
    .el-time-panel {
      background-color: var(--color-bg-card);
      border-color: var(--color-line-card);
      -webkit-box-shadow: 0 2px 12px 1px var(--color-shadow);
      box-shadow: 0 2px 12px 1px var(--color-shadow);
      color: var(--color-text-lighter);

      .el-time-panel__footer {
        border-color: var(--color-line-card);
      }
      .el-time-spinner__item.active:not(.disabled) {
        color: var(--color-text-lighter);
      }
      .el-time-panel__btn.cancel {
        color: var(--color-text-lighter);
      }
      .el-time-panel__btn.confirm {
        color: var(--color-main-green);
      }
    }
  }
  .el-date-table {
    th {
      border-color: var(--color-line-bg);
    }
    td.next-month,
    td.prev-month {
      color: var(--color-text-default);
    }
    td.today {
      color: var(--color-main-green);
    }
    td.today:before {
      border-top-color: var(--color-main-green);
    }
    td.in-range div {
      background-color: var(--color-bg-upper);
    }
    td.disabled div {
      background-color: var(--color-bg-upper);
      color: var(--color-text-default);
    }
  }
  .el-picker-panel *[slot=sidebar], .el-picker-panel__sidebar {
    background-color: var(--color-bg-card);
    border-color: var(--color-line-card);
  }
  .el-picker-panel__shortcut {
    color: var(--color-text-lighter);
  }
  .el-picker-panel__footer {
    background-color: var(--color-bg-card);
    border-color: var(--color-line-card);

    .el-picker-panel__link-btn {
      &.el-button--text {
        color: var(--color-main-green);
      }
      &.el-button--default {
        color: var(--color-text-lighter);
        background-color: var(--color-bg-card);
        border-color: var(--color-line-card);
      }
    }
    .el-picker-panel__btn {
      border-color: var(--color-line-card);
      color: #ffffff;
    }
  }
}

.el-select-dropdown.el-popper {
  .popper__arrow, .el-popper[x-placement^="bottom"] .popper__arrow {
    left: 60% !important;
  }
}

.el-autocomplete-suggestion.autocomplete {
  li {
    line-height: normal;
    padding: 10px 20px;
  }
  .label {
    text-overflow: ellipsis;
    overflow: hidden;
  }
  .value {
    font-size: 12px;
    text-overflow: ellipsis;
    overflow: hidden;
    color: #b4b4b4;
  }
}

.emq-search-form--date-picker {
  transform: translateX(-10px);
}
</style>
