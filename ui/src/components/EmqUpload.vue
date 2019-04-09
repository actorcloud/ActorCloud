<template>
  <div class="emq-upload">
    <el-upload
      :class="{ disabled: disabled }"
      :action="action"
      :accept="accept"
      :data="uploadToken"
      :headers="headers"
      :on-preview="handlePreview"
      :on-remove="handleRemove"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
      :limit="field.limit"
      :list-type="listType"
      :file-list="fileList"
      :disabled="disabled">
      <el-button size="small" type="success" :disabled="fileList.length >= field.limit">
        {{ $t('oper.upload') }}
      </el-button>
    </el-upload>
    <el-dialog :visible.sync="photoDetailDialogVisible" width="70%" :append-to-body="appendToBody">
      <img :src="detailPhotoURL"/>
    </el-dialog>
  </div>
</template>


<script>
export default {
  name: 'emq-upload',

  props: {
    // The value of the component binding
    value: {
      required: true,
    },
    // Fields required for el-upload
    field: {
      type: Object,
      required: true,
    },
    // The type of the file list
    listType: {
      type: String,
      default: 'text',
    },
    // Disabled
    disabled: {
      type: Boolean,
      default: false,
    },
    appendToBody: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      uploadLoading: false,
      photoDetailDialogVisible: false,
      action: '',
      accept: '',
      uploadToken: { token: '' },
      headers: { Authorization: '' },
      fileTypeErrorMessage: '',
      fileList: [],
      detailPhotoURL: '', // Display the image preview
    }
  },

  watch: {
    value(newValue) {
      if (newValue && newValue.length > 0 && newValue[0]) {
        if (newValue[0].name) {
          this.fileList = newValue
        }
      } else {
        return null
      }
    },

    fileList(newValue) {
      const ids = newValue.map(file => file.uploadID)
      if (this.field.limit === 1) {
        // Triggered on successful operation
        this.$emit('input', ids[0])
      } else {
        this.$emit('input', ids)
      }
    },
  },

  methods: {
    uploadConfig() {
      switch (this.field.type) {
        case 'uploadPackage':
          this.action = '/api/v1/upload?fileType=package'
          this.accept = 'application/zip, application/gz, application/tar, application/tgz'
          this.fileTypeErrorMessage = this.$t('errors.fileTypeError')
          break
        default:
          this.action = '/api/v1/upload?fileType=image'
          this.accept = 'image/*'
          this.fileTypeErrorMessage = this.$t('errors.imageTypeError')
      }
      if (this.field.url) {
        this.action = this.field.url
      }
    },
    handleRemove(file, fileList) {
      this.fileList = fileList
    },
    handlePreview(file) {
      const { token } = this.$store.state.accounts.user
      this.detailPhotoURL = `${file.url}`
      if (this.field.type === 'uploadPhoto') {
        this.photoDetailDialogVisible = true
      } else {
        window.location.href = `${file.url}&token=${token}`
      }
    },
    handleSuccess(response, file, fileList) {
      file.uploadID = response.uploadID
      this.fileList = fileList
      this.$message.success(this.$t('oper.uploadSuccess'))
      this.uploadLoding = false
    },
    handleError(error) {
      if (error.status === 401) {
        this.$message.error(this.$t('oper.loginRequired'))
      } else if (error.status === 400) {
        this.$message.error(this.fileTypeErrorMessage)
      } else {
        this.$message.error(this.$t('errors.INTERNAL_ERROR'))
      }
      this.uploadLoding = false
    },
    beforeUpload() {
      this.uploadLoding = true
      this.headers.Authorization = `Bearer ${this.$store.state.accounts.user.token}`
    },
  },

  created() {
    this.uploadConfig()
  },
}
</script>


<style lang="scss">
.emq-upload {
  .el-dialog img {
    max-width: 100%;
  }
  .disabled {
    .el-upload-list {
      clear: left;
      padding-top: 1px;
      display: inline;
    }
    .el-upload--text,
    .el-upload-list .el-upload-list__item-status-label,
    .el-upload-list .el-icon-close {
      display: none;
    }
  }
  .el-upload-list--picture .el-upload-list__item {
    background-color: transparent;
    border-color: var(--color-line-card);
  }
  .el-upload-list__item {
    a {
      float: none !important;
    }
    &:hover {
      .el-icon-close {
        color: #2fc285;
      }
    }
  }
}
</style>
