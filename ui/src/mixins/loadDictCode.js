import { mapActions } from 'vuex'

export default {
  computed: {
    dictCode() {
      return this.$store.state.base.dictCode
    },
  },
  methods: {
    ...mapActions(['GET_DICT_CODE']),
    loadData() {},
  },
  // Dict is loaded from the serve when it is not found in the vuex
  created() {
    if (this.dictCode && this.dictCode[this.field.key]) {
      this.loadData()
    } else if (!this.field.url && !this.field.options) {
      // Remote load and fixed options select does not trigger a reload
      this.GET_DICT_CODE().then(() => {
        this.loadData()
      })
    } else {
      this.loadData()
    }
  },
}
