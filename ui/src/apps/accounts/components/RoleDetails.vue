<template>
  <div class="details-view role-details-view">
      <emq-details-page-head>
        <el-breadcrumb slot="breadcrumb">
          <el-breadcrumb-item :to="{ path: path }">{{ $t('roles.role') }}</el-breadcrumb-item>
          <el-breadcrumb-item>{{ accessTitle }}</el-breadcrumb-item>
        </el-breadcrumb>
      </emq-details-page-head>
      <el-form
        ref="record"
        label-width="82px"
        :label-position="disabled ? 'left' : 'top'"
        :model="record"
        :rules="$route.query.oper !== 'view' ? rules : {}">
        <template v-if="record.tenantID || accessType === 'create'">
          <el-card :class="{ 'is-details-form': disabled }">
            <el-form-item
              v-if="record.roleName || accessType === 'create'"
              prop="roleName"
              :label="$t('roles.roleName')">
              <el-input
                v-model="record.roleName"
                type="text"
                :placeholder="$t('roles.roleNameRequired')"
                :disabled="disabled">
              </el-input>
            </el-form-item>
            <el-form-item
              v-if="record.description || accessType === 'create'"
              prop="description"
              :label="$t('roles.description')">
              <el-input
                v-model="record.description"
                :type=" disabled ? '' : 'textarea'"
                :placeholder="disabled ? '' : $t('roles.roleDescriptionRequired')"
                :disabled="disabled">
              </el-input>
            </el-form-item>
          </el-card>
        </template>

        <template v-if="!record.tenantID && accessType !== 'create'">
          <el-card v-loading="pageLoading" :class="{ 'is-details-form': disabled }">
            <el-form-item v-if="record.roleName" prop="roleName" :label="$t('roles.roleName')">
              <span>{{ $t(`roles.${record.roleName}`) }}</span>
            </el-form-item>
            <el-form-item v-if="record.description"  prop="description" :label="$t('roles.description')">
              <span>{{ $t(`roles.${record.roleName}_desc`) }}</span>
            </el-form-item>
          </el-card>
        </template>

        <el-card>
          <div class="card-title">{{ $t('roles.permission') }}</div>
          <el-tree
            ref="tree"
            show-checkbox
            node-key="id"
            default-expand-all
            :expand-on-click-node="false"
            :props="defaultTreeProps"
            :data="permissions"
            @check-change="handleCheckChange">
          </el-tree>
        </el-card>
      </el-form>
      <emq-button
        v-if="!disabled"
        icon="save"
        :disabled="record.permissions.length === 0"
        @click="save">
        {{ $t('roles.save') }}
      </emq-button>
  </div>
</template>


<script>
import { httpGet } from '@/utils/api'
import detailsPage from '@/mixins/detailsPage'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import EmqButton from '@/components/EmqButton'

export default {
  name: 'role-details-view',

  mixins: [detailsPage],

  components: {
    EmqButton,
    EmqDetailsPageHead,
  },

  data() {
    return {
      defaultTreeProps: {
        label: 'label',
        children: 'children',
      },
      record: {
        permissions: [],
      },
      permissions: [],
      path: this.$route.query.url,
      url: this.$route.query.url,
      rules: {
        roleName: [
          { required: true, message: this.$t('roles.roleNameRequired'), trigger: 'blur' },
        ],
      },
    }
  },

  methods: {
    processLoadedData(record) {
      this.$refs.tree.setCheckedKeys(record.permissions)
    },
    loadPermissions() {
      const permission = this.path === '/roles' ? 'all_permissions' : 'all_app_permissions'
      httpGet(`/${permission}`).then((response) => {
        this.translate(response.data)
        setTimeout(() => {
          this.permissions = response.data
        }, 10)
      })
    },
    // Recursive call to translate the label of the permission
    translate(data = []) {
      data.forEach((item) => {
        item.label = this.$t(`resource.${item.label}`)
        item.disabled = this.disabled
        if (item.children && item.children.length) {
          this.translate(item.children)
        }
      })
    },
    handleCheckChange() {
      this.record.permissions = this.$refs.tree.getCheckedKeys()
    },
  },

  created() {
    this.loadPermissions()
  },
}
</script>


<style lang="scss">
.role-details-view {
  .el-tree-node__content {
    border-top: 1px solid var(--color-line-card);
    padding: 5px 0 5px 0;
    &:hover {
      background: var(--color-bg-hover);
    }
  }
}
</style>
