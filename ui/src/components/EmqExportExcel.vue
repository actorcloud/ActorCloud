<template>
  <el-button
    icon="el-icon-download"
    size="small"
    style="color: #2fc285; height: 40px;"
    :loading="loading"
    @click="exportExcel">{{ $t('oper.exportsExcel') }}
  </el-button>
</template>


<script>
import { httpGet } from '@/utils/api'

export default {
  name: 'emq-export-excel',

  props: {
    // The REST api to get data
    url: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      poll: 0,
      loading: false,
      state: {},
    }
  },

  computed: {
    token() {
      return this.$store.state.accounts.user.token
    },
  },

  methods: {
    getStatus(url) {
      httpGet(url).then((res) => {
        if (res.status === 500) {
          return
        }
        this.state = res.data
      })
    },
    download() {
      const element = document.createElement('a')
      const downloadURL = this.state.result.excelPath
      const filename = `${this.url.replace('/', '')}.xlsx`
      element.href = `/api/v1/${downloadURL}&token=${this.token}`
      element.download = filename
      element.click()
    },
    exportExcel() {
      const fullLoading = this.$loading({
        lock: true,
      });
      const [SUCCESS, FAILURE] = [3, 4]
      httpGet(`${this.url}_export`).then((res) => {
        this.loading = true
        this.state.status = 0
        let time = 30 // The polling frequency
        if (res.data.status === SUCCESS) {
          this.poll = setInterval(() => {
            if (this.state.status === SUCCESS) {
              clearInterval(this.poll)
              this.download()
              this.loading = false
              fullLoading.close()
              return
            }
            // if (this.state.status === 'PENDING') {
            //   clearInterval(this.poll)
            //   this.loading = false
            //   this.$message({
            //     message: this.status.msg,
            //     type: 'warning',
            //   })
            //   return
            // }
            if (this.state.status === FAILURE) {
              clearInterval(this.poll)
              this.loading = false
              fullLoading.close()
              this.$message.error(this.status.msg)
              return
            }
            if (!time) { // Limit the number of polls
              clearInterval(this.poll)
              this.loading = false
              fullLoading.close()
              this.$message.error(this.$t('oper.requestTimeout'))
              return 0
            }
            this.getStatus(res.data.result.statusUrl)
            time -= 1
          }, 1000)
        } else if (res.data.status === FAILURE) {
          fullLoading.close()
          this.loading = false
          this.$message.error(this.$t('oper.ExportFailed'))
        }
      }).catch(() => {
        fullLoading.close()
        this.loading = false
        clearInterval(this.poll)
      })
    },
  },
}
</script>
