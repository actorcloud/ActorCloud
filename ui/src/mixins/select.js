import { httpGet } from '@/utils/api'

export default {
  inject: {
    elForm: {
      default: '',
    },
  },

  props: {
    value: {
      required: true,
    },
    /**
     * {
     *    url: 'remote REST url',
     *    key: 'local load dictCode key',
     *    params: {}, // Query Parameters,
     *    searchKey: 'The searchValue keyword forms a value in params',
     *    options: 'The options value of the assembly',
     *    visibleLoad: 'When a search is not entered, visibleLoad is not loaded by default until it is true, and only when it is focused,
     *    other,
     * }
     */
    field: {
      type: Object,
      required: true,
    },
    // The rely scene requires the record
    record: {
      type: Object,
      default: () => {
        return {}
      },
    },
    disabled: {
      type: Boolean,
    },
    placeholder: {
      type: String,
    },
    clearable: {
      type: Boolean,
      default: false,
    },
    multiple: {
      type: Boolean,
      default: false,
    },
    // Options value that need to be disabled
    disableOptions: {
      type: Array,
      default: () => ([]),
    },
    // Input size
    size: {
      type: String,
      default: null,
    },
    // Collapse tags
    collapseTags: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      loading: false,
      timer: 0,
      options: [],
      relyLocked: false,
      editing: false,
    }
  },

  computed: {
    secureValue() {
      if (this.multiple && !this.value) {
        return []
      }
      return this.value
    },
    relyData() {
      if (this.field.rely) {
        return this.record[this.field.rely]
      }
    },
    selectDisabled() {
      const rely = this.field.rely && !this.record[this.field.rely]
      return this.disabled || (this.elForm || {}).disabled || rely;
    },
    lang() {
      return this.$store.state.accounts.lang
    },
  },

  watch: {
    // Clears the current selection in the forbidden selection if it is currently selected
    disableOptions(newValue = []) {
      if (newValue.includes(this.value)) {
        this.$emit('input', undefined, null)
      }
    },
  },

  methods: {
    loadOptions() {
      let params = ''
      if (this.field.params) {
        params = Object.assign({}, this.field.params)
      }
      httpGet(this.field.url, { params }).then((response) => {
        this.options = response.data
        // Add extra options event when the api request is completed
        this.$emit('addExtraOptions')
        if (this.field.lazyInput && ![null, '', undefined].includes(this.secureValue)) {
          const selectedItem = this.options.find($ => $.value === this.secureValue)
          this.$emit('input', this.secureValue, selectedItem)
        }
      })
    },
    // When the select value changes, the v-model binding of the parent component is triggered
    change(value) {
      const selectedItem = this.options.find($ => $.value === value)
      this.$emit('input', value, selectedItem)
    },
  },
}
