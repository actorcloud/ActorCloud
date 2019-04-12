<template>
  <div class="emq-import-excel">
    <el-dialog
      :title="$t('oper.imports')"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :visible.sync="dialogVisible"
      @close="closeDialog">
      <div>
        <div style="display: flex; justify-content: center;">
          <img src="../assets/images/select-file.png" />
        </div>
        <el-progress
          v-show="progressVisible"
          status="success"
          style="margin-top: 10px;"
          :text-inside="true"
          :stroke-width="18"
          :percentage="state.progress || 0">
        </el-progress>
      </div>
      <el-upload
        class="upload-excel"
        :show-file-list="false"
        :headers="{Authorization: `Bearer ${token}`}"
        :action="action"
        :accept="accept"
        :data="uploadData"
        :before-upload="beforeUpload"
        :on-success="handleSuccess"
        :on-error="handleError"
        :file-list="fileList">
        <emq-button :disabled="!buttonVisible">{{ $t('oper.selectFile') }}</emq-button>
      </el-upload>
      <p style="text-align: center;">
        {{ state.message }}
        <span v-if="state.result.excelPath && state.result.excelPath !== ''">{{ $t('oper.click') }}
          <a
            download="errors.xlsx"
            :href="`/api/v1/${state.result.excelPath}&token=${token}`"> {{ $t('oper.downloadLower') }}
          </a>
          {{ $t('oper.failedItem') }}
        </span>
      </p>
      <p slot="footer" class="dialog-footer">
        <span v-show="uploadData.type==='import'">
          {{ $t('oper.note') }}：1、<a download="template.xlsx" :href="exampleUrl">{{ $t('oper.downloadLower') }}</a>
          {{ $t('oper.importTemplate') }}；2、{{ $t('oper.organizeData') }}
        </span>
      </p>
    </el-dialog>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'

export default {
  name: 'emq-import-excel',

  props: {
    // Gets the progress of the import api
    url: {
      type: String,
      required: true,
    },
    // Reload data
    reloadData: {
      type: Function,
      required: true,
    },
  },

  data() {
    return {
      exampleUrl: '',
      dialogVisible: false,
      fileList: [],
      action: `/api/v1${this.url}_import`,
      accept: `application/vnd.ms-excel,
        application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`,
      uploadData: {
        name: this.url.replace('/', ''),
        type: 'import',
      },
      fileTypeErrorMessage: this.$t('errors.ExcelTypeError'),
      progressVisible: false,
      buttonVisible: true,
      poll: undefined,
      state: {
        progress: 0,
        message: '',
        status: 0,
        result: {},
      },
    }
  },

  computed: {
    token() {
      return this.$store.state.accounts.user.token
    },
  },

  methods: {
    showDialog() {
      this.getExampleUrl()
      this.dialogVisible = true
      this.state.message = ''
      this.fileList = []
      this.progressVisible = false
      this.state.progress = 0
      this.state.status = 0
    },
    // Get the template download url
    getExampleUrl() {
      const url = this.url.replace('/', '')
      const lang = this.$store.state.accounts.lang
      this.exampleUrl = `/api/v1/download?fileType=template&filename=${url}_template_${lang}.xlsx&token=${this.token}`
    },
    // Get the import progress
    getImportProgress(url) {
      const errorCode = {
        4001: this.$t('errors.UPLOADED'),
        4002: this.$t('errors.READING'),
        4003: this.$t('errors.VALIDATING'),
        4004: this.$t('errors.IMPORTING'),
        4005: this.$t('errors.COMPLETED'),
        4006: this.$t('errors.TEMPLATE_ERROR'),
        4007: this.$t('errors.ABNORMAL'),
        4008: this.$t('errors.LIMITED'),
        4009: this.$t('errors.FAILED'),
      }
      httpGet(url).then((response) => {
        if (response.data.result.code) {
          const code = response.data.result.code
          this.state = response.data
          this.state.message = errorCode[code]
          return
        }
        this.state = response.data
      })
    },
    beforeUpload() {
      this.uploadLoding = true
      this.buttonVisible = false
    },
    handleSuccess(response, file, fileList) {
      const [SUCCESS, FAILURE] = [3, 4]
      this.state.message = ''
      this.state.excelPath = ''
      file.uploadID = response.uploadID
      this.fileList = fileList
      this.uploadLoding = false
      this.progressVisible = true
      // Poll for progress status
      if (response.status === SUCCESS) {
        this.poll = setInterval(() => {
          if (this.state.progress === 100 || this.state.status === FAILURE) {
            clearInterval(this.poll)
            this.buttonVisible = true
            this.state.status = 0
            this.reloadData()
            return
          }
          this.getImportProgress(response.result.statusUrl)
        }, 200)
      } else if (response.status === FAILURE) {
        this.$message.error(this.$t('oper.importFailed'))
        this.buttonVisible = true
      }
    },
    handleError(error) {
      if (error.status === 401) {
        this.$message.error(this.$t('oper.loginRequired'))
      } else if (error.status === 400) {
        this.$message.error(this.fileTypeErrorMessage)
      } else {
        clearInterval(this.poll)
        this.$message.error(this.$t('errors.uploadError'))
      }
      this.buttonVisible = true
      this.uploadLoding = false
    },
    closeDialog() {
      this.dialogVisible = false
      this.state.result.excelPath = ''
    },
  },
}
</script>


<style lang="scss">
.emq-import-excel {
  .el-button--danger{
    float: right;
    margin-top: -75px;
    color: var(--color-main-pink);
    background-color: #fff;
  }
  .upload-excel {
    text-align: center;
    margin-top: 20px;
  }
  .el-dialog__header {
    border-bottom: 1px solid var(--color-line-card);
    .el-dialog__title {
      color: var(--color-text-lighter);
    }
  }
  .el-dialog__body {
    padding: 30px 20px 0;
  }
  .dialog-footer {
    text-align: center;
    font-size: .9rem;
  }
}
</style>
