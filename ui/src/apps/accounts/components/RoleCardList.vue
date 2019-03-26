<template>
  <div class="role-card-list emq-card-list-view">
    <el-row :gutter="20">
      <el-col v-for="(item, index) in records" :key="index" :span="8">
        <el-card class="box-card" @click.native="showDetails(item.id, 'view')">
          <div slot="header" class="clearfix">
            <span>{{ item.roleName }}</span>
            <el-dropdown
              v-if="!item.isShare && (has(`PUT,${url}/:id`) || has(`DELETE,${url}`))"
              class="card-dropdown"
              trigger="click"
              :show-timeout="0">
              <el-button @click.stop type="text">
                <i class="material-icons">more_vert</i>
              </el-button>
              <el-dropdown-menu slot="dropdown">
                <a
                  v-if="has(`PUT,${url}/:id`)"
                  href="javascript:;"
                  @click="showDetails(item.id, 'edit')">
                  <el-dropdown-item>
                    <img src="../../base/assets/images/role-edit.png">
                    {{ $t('roles.edit') }}
                  </el-dropdown-item>
                </a>
                <a
                  v-if="has(`DELETE,${url}`)"
                  href="javascript:;" @click="showConfirmDialog(item.id)">
                  <el-dropdown-item>
                    <img src="../../base/assets/images/role-delete.png">
                    {{ $t('roles.deleted') }}
                  </el-dropdown-item>
                </a>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
          <div class="text item">{{ item.description }}</div>
        </el-card>
      </el-col>
    </el-row>

    <emq-dialog
      :title="$t('roles.waring')"
      :visible.sync="confirmDialogVisible"
      @confirm="deleteRole">
      <span>{{ $t('roles.confirmDeleted') }}</span>
    </emq-dialog>
  </div>
</template>


<script>
import { httpGet, httpDelete } from '@/utils/api'
import EmqDialog from '@/components/EmqDialog'

export default {
  name: 'emq-card-list-view',

  components: {
    EmqDialog,
  },

  props: {
    url: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      willDeleteId: undefined,
      confirmDialogVisible: false,
      records: [],
    }
  },

  methods: {
    loadRoleData() {
      httpGet(this.url).then((response) => {
        this.records = response.data.items
      })
    },
    showConfirmDialog(deleteID = undefined) {
      if (deleteID) {
        this.willDeleteId = deleteID
      }
      this.confirmDialogVisible = true
    },
    deleteRole() {
      httpDelete(`${this.url}?ids=${this.willDeleteId}`).then(() => {
        this.$message.success(this.$t('roles.deleteSuccess'))
        this.confirmDialogVisible = false
        this.loadRoleData()
      })
      this.confirmDialogVisible = false
    },
    showDetails(id, accessType) {
      this.$router.push({ path: `${this.url}/${id}`, query: { oper: accessType, url: this.url } })
    },
  },

  created() {
    this.loadRoleData()
  },
}
</script>


<style lang="scss">
@import '~@/assets/scss/emqCardList.scss';

.role-card-list {
  .el-col-8 {
    min-width: 267px;
  }
}
</style>
