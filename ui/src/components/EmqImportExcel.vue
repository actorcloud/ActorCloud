<template>
  <div class="emq-import-excel">
    <el-dialog
      title="批量导入"
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
        :action="action"
        :accept="accept"
        :data="uploadData"
        :before-upload="beforeUpload"
        :on-success="handleSuccess"
        :on-error="handleError"
        :file-list="fileList">
        <emq-button :disabled="!buttonVisible">选择文件</emq-button>
      </el-upload>
      <p style="text-align: center;">
        {{ state.message }}
        <span v-if="state.result.excelPath && state.result.excelPath !== ''"> 点击
          <a
            download="errors.xlsx"
            :href="`/api/v1/${state.result.excelPath}&token=${token}`"> 下载
          </a>
          失败条目
        </span>
      </p>
      <p slot="footer" class="dialog-footer">
        <span v-show="uploadData.type==='import'">
          注：1、<a download="template.xlsx" :href="exampleUrl">下载 </a>
          导入模板；2、按模板示例整理好数据，并点击“选择文件”
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
        token: '',
        name: this.url.replace('/', ''),
        type: 'import',
      },
      fileTypeErrorMessage: '请上传正确的excel文件',
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
      this.exampleUrl = `/api/v1/download?fileType=template&filename=${url}_template.xlsx&token=${this.token}`
    },
    // Get the import progress
    getImportProgress(url) {
      httpGet(url).then((response) => {
        if (response.status === 500) {
          this.state.message = '服务器错误'
          return
        }
        this.state = response.data
      })
    },
    beforeUpload() {
      this.uploadLoding = true
      this.buttonVisible = false
      const user = JSON.parse(sessionStorage.getItem('user'))
        || JSON.parse(localStorage.getItem('user'))
      if (user) {
        this.uploadData.token = user.token
      }
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
        this.$message.error('导入失败')
        this.buttonVisible = true
      }
    },
    handleError(error) {
      if (error.status === 401) {
        this.$message.error('请登录')
      } else if (error.status === 400) {
        this.$message.error(this.fileTypeErrorMessage)
      } else {
        clearInterval(this.poll)
        this.$message.error('服务器错误，上传失败!')
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
