<template>
  <div class="profile-reviews-view">
    <emq-crud
      url="/codec"
      ref="crud">

      <template v-if="tenantType === 0" v-slot:crudTabsHead>
        <tabs-card-head :tabs="productsTabsHead"></tabs-card-head>
      </template>

      <template slot="tableColumns">
        <el-table-column prop="tenantName" :label="$t('profiles.tenantName')"></el-table-column>
        <el-table-column prop="tenantTypeLabel" :label="$t('profiles.tenantType')"></el-table-column>
        <el-table-column prop="contactPhone" :label="$t('profiles.contactPhone')"></el-table-column>
        <el-table-column prop="productName" :label="$t('profiles.productName')"></el-table-column>
        <el-table-column prop="codeStatusLabel" :label="$t('profiles.codeStatus')">
          <template v-slot="scope">
            {{ scope.row.codeStatusLabel }}
            <a
              v-if="scope.row.codeStatus === 3"
              @click="showReviewOpinion(scope.row.reviewOpinion)">[{{ $t('profiles.reason') }}]</a>
          </template>
        </el-table-column>
      </template>
      <template v-slot:customOper="props">
        <div
          @click="showDialog(props.row, 'detail')"
          class="oper-button">
          <i class="iconfont icon-view" :title="$t('profiles.show')"></i>
        </div>
        <div
          v-if="props.row.codeStatus === 1"
          @click="showDialog(props.row, 'review')"
          class="oper-button">
          <i class="iconfont oper-button custom-text" :title="$t('profiles.review')">{{ $t('profiles.iconText') }}</i>
        </div>
      </template>
    </emq-crud>

    <emq-dialog
      width="60%"
      isView
      class="decode-view"
      :title="$t('profiles.show')"
      :visible.sync="profileDialogVisible">
      <code-editor
        lang="python"
        height="400px"
        v-model="profileInfo.code"
        disabled>
      </code-editor>
    </emq-dialog>

    <emq-dialog
      :title="$t('profiles.review')"
      :visible.sync="reviewDialogVisible"
      @confirm="profileReview">
      <el-form
        ref="review"
        label-position="top"
        label-width="82px"
        :model="review"
        :rules="rules">
        <el-form-item
          prop="codeStatus"
          class="code-status"
          :label="$t('profiles.reviewResult')">
          <el-radio-group v-model="review.codeStatus">
            <el-radio :label="2">{{ $t('profiles.pass') }}</el-radio>
            <el-radio :label="3">{{ $t('profiles.fail') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          v-if="review.codeStatus === 3"
          prop="reviewOpinion"
          :label="$t('profiles.reviewOpinion')">
          <el-input
            type="textarea"
            maxlength="1000"
            v-model="review.reviewOpinion"
            :placeholder="$t('profiles.opinionRequired')"
            :rows="2">
          </el-input>
        </el-form-item>
      </el-form>
    </emq-dialog>
  </div>
</template>


<script>
import EmqCrud from '@/components/EmqCrud'
import EmqDialog from '@/components/EmqDialog'
import TabsCardHead from '@/components/TabsCardHead'
import CodeEditor from '@/components/CodeEditor'
import { httpPut } from '@/utils/api'

export default {
  name: 'profile-reviews-view',

  components: {
    EmqCrud,
    EmqDialog,
    CodeEditor,
    TabsCardHead,
  },

  data() {
    return {
      profileDialogVisible: false,
      reviewDialogVisible: false,
      productsTabsHead: [
        {
          code: 'products',
          order: 1,
          url: '/products',
        },
        {
          code: 'profilesReview',
          order: 2,
          url: '/codec',
        },
      ],
      review: {},
      profileInfo: {},
      tenantType: this.$store.state.accounts.user.tenantType,
      rules: {
        codeStatus: [
          { required: true, message: this.$t('profiles.reviewResultRequired'), trigger: 'blur' },
        ],
        reviewOpinion: [
          { required: true, message: this.$t('profiles.opinionRequired'), trigger: 'blur' },
        ],
      },
    }
  },

  methods: {
    showDialog(row, oper) {
      this.profileInfo = row
      if (oper === 'detail') {
        this.profileDialogVisible = true
      } else if (oper === 'review') {
        this.reviewDialogVisible = true
      }
    },
    profileReview() {
      this.$refs.review.validate((valid) => {
        if (!valid) {
          return false
        }
      })
      httpPut(`/codec/${this.profileInfo.id}`, this.review).then(() => {
        this.$message.success(this.$t('profiles.success'))
        this.reviewDialogVisible = false
        this.$refs.crud.loadRecords()
      })
    },
    showReviewOpinion(content) {
      this.$alert(content, this.$t('profiles.failReason'), { showConfirmButton: false });
    },
  },
}
</script>


<style lang="scss">
.profile-reviews-view {
  .emq-dialog .el-dialog__header {
    border-bottom: 1px solid var(--color-line-bg);
  }
  .emq-dialog.decode-view .el-dialog__body {
    padding: 0 2px 2px;
  }
  .code-status .el-form-item__content {
    line-height: 22px;
  }
}
.el-message-box__message p {
  word-break: break-all;
}
</style>
