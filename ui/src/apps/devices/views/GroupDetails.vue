<template>
  <div class="details-view group-details-view">
   <emq-details-page-head>
      <el-breadcrumb slot="breadcrumb">
        <el-breadcrumb-item :to="{ path: `/devices/groups` }">{{ $t('groups.group') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ $t('groups.groupInfo') }}</el-breadcrumb-item>
      </el-breadcrumb>
    </emq-details-page-head>

    <!-- <div v-if="accessType !== 'create'" class="detail-tabs">
      <group-detail-tabs></group-detail-tabs>
    </div> -->
    <div class="groups-card-details-body">
      <el-card :class="disabled ? 'is-details-form' : ''">
        <edit-toggle-button
          :url="url"
          :disabled="disabled"
          :accessType="accessType"
          @toggleStatus="toggleStatus">
        </edit-toggle-button>
        <el-row :gutter="50">
          <el-form
            ref="record"
            :label-width="lang === 'en' ? '120px' : '82px'"
            :label-position="disabled ? 'left' : 'top'"
            :model="record"
            :rules="disabled ? {} : rules">
            <el-col :span="12">
              <el-form-item :label="$t('groups.groupName')" prop="groupName">
                <el-input
                  type="text"
                  v-model="record.groupName"
                  :placeholder="disabled ? '' : $t('groups.groupNameRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'view'" :span="12">
              <el-form-item :label="$t('groups.groupID')" prop="groupID">
                <el-input
                  type="text"
                  v-model="record.groupID"
                  :placeholder="disabled ? '' : $t('groups.groupIDRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item :label="$t('groups.description')" prop="description">
                <el-input
                  type="text"
                  v-model="record.description"
                  :placeholder="disabled ? '' : $t('groups.descriptionRequired')"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'view'" :span="12">
              <el-form-item :label="$t('groups.createUser')">
                <el-input
                  v-model="record.username"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
            <el-col v-if="accessType === 'view'" :span="12">
              <el-form-item :label="$t('groups.createAt')">
                <el-input
                  v-model="record.createAt"
                  :disabled="disabled">
                </el-input>
              </el-form-item>
            </el-col>
          </el-form>
        </el-row>
        <emq-button v-if="!disabled" icon="save" @click="save">
          {{ $t('oper.save') }}
        </emq-button>
      </el-card>

      <!-- Contains the device -->
      <add-device
        v-if="accessType !== 'create'"
        url="/groups"
        :detailsID="parseInt(detailsID)">
      </add-device>
    </div>

    <el-dialog
      class="emq-dialog create-success"
      width="420px"
      :visible.sync="createVisable"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false">
      <img src="~@/assets/images/created.png" width="180">
      <h1>{{ $t('groups.isCreated') }}</h1>
      <div class="create-success__oper">
        <el-button
          class="add-button"
          @click="createGroup">
          {{ $t('groups.addDevice') }}
        </el-button>
        <el-button
          class="cancel"
          @click="backGroups">
          {{ $t('groups.addCancel') }}
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>


<script>
import { httpPost, httpPut } from '@/utils/api'
import detailsPage from '@/mixins/detailsPage'
import EmqButton from '@/components/EmqButton'
import EmqDetailsPageHead from '@/components/EmqDetailsPageHead'
import AddDevice from '../components/AddDevice'

export default {
  name: 'group-details-view',

  mixins: [detailsPage],

  components: {
    EmqDetailsPageHead,
    EmqButton,
    AddDevice,
  },

  data() {
    return {
      url: '/groups',
      creaetdRecord: {},
      createVisable: false,
      rules: {
        groupName: [
          { required: true, message: this.$t('groups.groupNameRequired'), trigger: 'blur' },
        ],
        productID: [
          { required: true, message: this.$t('groups.productIDRequired'), trigger: 'blur' },
        ],
      },
    }
  },

  methods: {
    save() {
      this.$refs.record.validate((valid) => {
        if (!valid) {
          return false
        }
        if (this.accessType === 'create') {
          httpPost(this.url, this.record).then((response) => {
            this.creaetdRecord = response.data
            this.createVisable = true
          })
        } else if (this.accessType === 'edit') {
          httpPut(`${this.url}/${this.detailsID}`, this.record).then(() => {
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
    createGroup() {
      this.$router.push({
        path: '/temp_page',
        query: { link: `/devices/groups/${this.creaetdRecord.id}?oper=view` },
      })
    },
    backGroups() {
      this.$router.push({ path: this.listPageURL })
    },
  },
}
</script>
