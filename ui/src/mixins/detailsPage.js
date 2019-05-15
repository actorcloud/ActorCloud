import { httpGet, httpPost, httpPut } from '@/utils/api'

export default {
  data() {
    return {
      pageLoading: false,
      saveLoading: false,
      accessType: undefined,
      detailsID: undefined,
      detailsView: undefined,
      url: undefined, // REST api
      currentPageURL: undefined, // The url of the current page
      listPageURL: undefined, // Created or edited successfully, back to the list url
      isRenderToList: true, // Whether to back to the list after editing
      record: {},
      recordCache: {}, // Cache data: unedit and return to details status
    }
  },

  computed: {
    accessTitle() {
      switch (this.accessType) {
        case 'view':
          return this.$t('oper.view')
        case 'create':
          return this.$t('oper.createBtn')
        case 'edit':
          return this.$t('oper.edit')
        default:
          return this.$t('oper.view')
      }
    },
    disabled() {
      if (this.$route.query.oper === 'create') {
        return false
      }
      return this.detailsView !== undefined ? this.detailsView : this.$route.query.oper !== 'edit'
    },
    lang() {
      return this.$store.state.accounts.lang
    },
  },

  watch: {
    '$route.params.id': 'handleIdChange',
  },

  methods: {
    // eslint-disable-next-line
    processLoadedData(record) {}, // Callbacks after data get
    // A callback before a post request to validate sub form, only return true or false
    // eslint-disable-next-line
    validateSubForm(data) { return true },
    // eslint-disable-next-line
    beforePostData(data) {}, // Callbacks before data post
    // eslint-disable-next-line
    requestSuccess(data) {}, // A callback after a post request, only return true or false
    loadData() {
      if (this.accessType === 'create') {
        return
      }
      if (!this.$route.params.id) {
        return
      }
      this.pageLoading = true
      httpGet(`${this.url}/${this.detailsID}`).then((response) => {
        this.record = response.data
        this.recordCache = { ...response.data }
        this.processLoadedData(this.record) // Process the received data
        this.pageLoading = false
      }).catch(() => {
        this.pageLoading = false
      })
    },
    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        if (!this.validateSubForm(this.record)) {
          return false
        }
        const data = {}
        Object.assign(data, this.record)
        this.beforePostData(data) // Process the data before post
        if (this.accessType === 'create') {
          httpPost(this.url, data).then((response) => {
            if (this.requestSuccess(response)) {
              return
            }
            this.$message.success(this.$t('oper.createSuccess'))
            const { fromURL } = this.$route.query
            if (fromURL) {
              this.$router.push({ path: fromURL })
            } else {
              this.$router.push({ path: this.listPageURL })
            }
          })
        } else if (this.accessType === 'edit') {
          httpPut(`${this.url}/${this.detailsID}`, data).then(() => {
            this.$message.success(this.$t('oper.editSuccess'))
            this.recordCache = { ...this.record }
            if (this.isRenderToList) {
              this.$router.push({ path: this.listPageURL })
            } else {
              this.toggleStatus()
              this.loadData()
            }
          })
        }
      })
    },
    permissionCheck() {
      const detailsAPI = `${this.url}/:id`
      //  Check the permission for '/some_path'
      if (this.accessType === 'view' && !this.has(`GET,${this.url}`)) {
        this.$router.push({ path: '/forbidden' })
      } else if (this.accessType === 'edit' && !this.has(`PUT,${detailsAPI}`)) {
        this.$router.push({ path: '/forbidden' })
      } else if (this.accessType === 'create' && !this.has(`POST,${this.url}`)) {
        this.$router.push({ path: '/forbidden' })
      }
    },
    /**
     * Edit, view status switch and restore cache record
     * @param canceled: Whether to cancel data recovery
     */
    toggleStatus(canceled = false) {
      if (this.disabled) {
        // edit
        this.detailsView = false
        this.accessType = 'edit'
        this.recordCache = { ...this.record }
      } else {
        // view
        if (canceled) {
          this.record = { ...this.recordCache }
        }
        this.processLoadedData(this.record)
        this.detailsView = true
        this.accessType = 'view'
      }
    },
    // Create data for another page
    newAnotherPageData() {
      localStorage.setItem(this.localRecordName, JSON.stringify(this.record))
      this.$router.push({
        path: `${this.toURL}&fromURL=${this.$route.fullPath}`,
      })
    },
    handleIdChange(newVal) {
      this.detailsID = newVal
      this.loadData()
    },
  },

  created() {
    this.accessType = this.$route.query.oper
    this.currentPageURL = this.$route.path
    this.listPageURL = this.currentPageURL.replace(/\/\d+$/g, '')
    const detailsID = this.$route.path.split('/').pop()
    if (detailsID && !Number.isNaN(detailsID)) {
      this.detailsID = detailsID
    } else {
      this.$router.push({ path: '/not_found' })
    }
    this.permissionCheck()
    this.loadData()
  },
  mounted() {
    const localRecord = JSON.parse(localStorage.getItem(this.localRecordName))
    if (localRecord) {
      this.record = localRecord
      localStorage.removeItem(this.localRecordName)
    }
  },
}
