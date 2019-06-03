<template>
  <div class="invitations-view">
    <emq-crud
      ref="crud"
      :url="url"
      :tableActions="tableActions">
      <template slot="crudTabsHead">
        <tabs-card-head :tabs="$store.state.accounts.tabs.users"></tabs-card-head>
      </template>
      <template slot="tableColumns">
        <el-table-column :label="$t('invitations.email')" prop="inviteEmail"></el-table-column>
        <el-table-column :label="$t('invitations.roleIntID')" prop="roleName"></el-table-column>
        <el-table-column :label="$t('invitations.username')" prop="username"></el-table-column>
        <el-table-column :label="$t('invitations.invitationStatus')" prop="inviteStatusLabel">
        </el-table-column>
        <el-table-column
          sortable="custom"
          prop="createAt"
          min-width="150px"
          :label="$t('invitations.createAt')">
        </el-table-column>
      </template>
      <emq-button
        v-if="has(`POST,${url}`)"
        slot="createButton"
        class="create-btn"
        @click="invitationsDialog">
        {{ $t('invitations.invitation') }}
      </emq-button>
    </emq-crud>

    <emq-dialog
      :title="$t('invitations.invitationUser')"
      :visible.sync="invitationsVisible"
      @confirm="invitations">
      <el-form
        label-position="left"
        ref="invitationsInfo"
        :model="invitationsInfo"
        :rules="ivitationsRules">
        <el-form-item :label="$t('invitations.roleIntID')" label-width="60px" prop="roleIntID">
          <role-select
            v-model="invitationsInfo.roleIntID"
            :field="{ url: '/select_options/roles' }"
            :placeholder="$t('invitations.roleRequired')"
            :disabled="false">
          </role-select>
        </el-form-item>
        <el-form-item :label="$t('invitations.email')" label-width="60px" prop="inviteEmail">
          <el-input v-model="invitationsInfo.inviteEmail" size="medium"></el-input>
        </el-form-item>
      </el-form>
    </emq-dialog>
  </div>
</template>


<script>
import { httpPost } from '@/utils/api'
import EmqCrud from '@/components/EmqCrud'
import TabsCardHead from '@/components/TabsCardHead'
import EmqButton from '@/components/EmqButton'
import RoleSelect from '../components/RoleSelect'
import EmqDialog from '@/components/EmqDialog'

export default {
  name: 'invitations-view',

  components: {
    EmqCrud,
    TabsCardHead,
    EmqButton,
    EmqDialog,
    RoleSelect,
  },

  data() {
    return {
      url: '/invitations',
      invitationsVisible: false,
      roles: [],
      invitationsInfo: {
        roleIntID: '',
        inviteEmail: '',
      },
      tableActions: ['create', 'delete'],
      ivitationsRules: {
        inviteEmail: [
          { required: true, message: this.$t('invitations.emailRequired'), trigger: 'blur' },
          { type: 'email', message: this.$t('invitations.correctEmailRequired'), trigger: 'blur,change' },
        ],
        roleIntID: [
          { required: true, message: this.$t('invitations.roleRequired'), trigger: 'blur' },
        ],
      },
    }
  },

  methods: {
    invitationsDialog() {
      this.invitationsInfo = {}
      this.invitationsVisible = true
    },
    invitations() {
      this.$refs.invitationsInfo.validate((valid) => {
        if (!valid) {
          return
        }
        httpPost(this.url, this.invitationsInfo).then(() => {
          this.$message.success(this.$t('invitations.invitationSuccess'))
          this.$refs.crud.loadData()
          this.invitationsVisible = false
        })
      })
    },
  },
}
</script>


<style lang="scss">
.invitations-view {
  .el-dialog {
    .el-select {
      width: 100%;
    }
  }
}
</style>
