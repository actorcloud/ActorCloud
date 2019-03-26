<template>
  <div class="role-view emq-crud">
    <div class="crud-header">
      <el-row
        type="flex"
        justify="space-between"
        align="middle">
        <el-col :span="18">
          <span class="crud-title">{{ $t('roles.role') }}</span>
        </el-col>
        <el-col :span="6">
          <emq-button
            v-if="has(`POST,${path}`)"
            class="create-btn"
            @click="newRole">
            + {{ $t('roles.create') }}
          </emq-button>
        </el-col>
      </el-row>
    </div>
    <role-card-list :url="path"></role-card-list>
  </div>
</template>


<script>
import EmqButton from '@/components/EmqButton'
import RoleCardList from './RoleCardList'

export default {
  name: 'role-view',

  components: {
    EmqButton,
    RoleCardList,
  },

  data() {
    return {
      path: this.$route.path,
    }
  },

  methods: {
    newRole() {
      this.$router.push({ path: `${this.path}/0`, query: { oper: 'create', url: this.path } })
    },
  },
}
</script>
