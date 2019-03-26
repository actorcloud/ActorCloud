<template>
  <emq-dialog
    class="details-view instructions-dialog-view"
    width="512px"
    :title="!instructionType ? $t('devices.publishInstruct') : $t('devices.publishTask')"
    :visible.sync="showDialog"
    :saveLoading="btnLoading"
    @confirm="save"
    @close="hideDialog">
    <el-radio-group class="command-type" v-model="commandType">
      <el-radio :label="0">{{ $t('devices.customInstruct') }}</el-radio>
      <el-radio
        v-if="showPlatForm"
        :label="1">
        {{ $t('devices.platformInstruct') }}</el-radio>
      <el-radio
        v-if="showOta"
        :label="2">{{ $t('devices.updateInstruct') }}</el-radio>
      <el-radio
        v-if="showLwM2M"
        :label="3">LwM2M 标准指令</el-radio>
    </el-radio-group>

    <!-- Custom -->
    <instruction-custom
      v-if="commandType === 0"
      ref="instructionCustom"
      :postUrl="postUrl"
      timerUrl="/timer_publish"
      :instructionType="instructionType"
      :currentDevice="currentDevice"
      :currentGroup="currentGroup"
      :btnLoading.sync="btnLoading"
      @close-form="hideDialog">
    </instruction-custom>

    <!-- Platform -->
    <instruction-platform
      v-if="commandType === 1"
      ref="instructionPlatform"
      :postUrl="postUrl"
      timerUrl="/timer_publish"
      :instructionType="instructionType"
      :currentDevice="currentDevice"
      :btnLoading.sync="btnLoading"
      @close-form="hideDialog">
    </instruction-platform>

    <!-- OTA -->
    <instruction-ota
      v-if="commandType === 2"
      ref="instructionOta"
      :postUrl="postUrl"
      timerUrl="/timer_publish"
      :instructionType="instructionType"
      :currentDevice="currentDevice"
      :currentGroup="currentGroup"
      :btnLoading.sync="btnLoading"
      @close-form="hideDialog">
    </instruction-ota>

    <!-- LwM2M -->
    <instruction-lwM2M
      v-if="commandType === 3"
      ref="instructionLwm2m"
      :postUrl="postUrl"
      timerUrl="/timer_publish"
      :instructionType="instructionType"
      :currentDevice="currentDevice"
      :currentGroup="currentGroup"
      :btnLoading.sync="btnLoading"
      @close-form="hideDialog">
    </instruction-lwM2M>
  </emq-dialog>
</template>


<script>
import EmqDialog from '@/components/EmqDialog'
import InstructionCustom from './InstructionCustom'
import InstructionPlatform from './InstructionPlatform'
import InstructionOta from './InstructionOta'
import InstructionLwM2M from './InstructionLwM2M'

export default {
  name: 'instruction-dialog-view',

  components: {
    EmqDialog,
    InstructionCustom,
    InstructionPlatform,
    InstructionOta,
    InstructionLwM2M,
  },

  props: {
    visible: {
      type: Boolean,
      required: true,
    },
    instructionType: {
      type: Number,
      required: true,
    },
    postUrl: {
      type: String,
      required: true,
    },
    currentDevice: {
      type: Object,
      default: () => ({ cloudProtocol: 0 }),
    },
    currentGroup: {
      type: Object,
      default: () => ({}),
    },
  },

  data() {
    return {
      btnLoading: false,
      showDialog: this.visible,
      commandType: 0, // 0 Custom, 1 Platform, 2 OTA, 3 lwm2m
    }
  },

  watch: {
    visible(newVal) {
      if (!newVal) {
        if (this.commandType === 0) {
          this.$refs.instructionCustom.initData()
        }
      } else {
        this.commandType = 0
      }
      this.showDialog = newVal
    },
  },

  computed: {
    showPlatForm() {
      if (this.currentDevice.deviceID) {
        const { cloudProtocol } = this.currentDevice
        return cloudProtocol === this.$variable.cloudProtocol.MQTT
          || cloudProtocol === this.$variable.cloudProtocol.LWM2M
      }
      return false
    },
    showOta() {
      let cloudProtocol = 0
      if (this.currentDevice.deviceID) {
        cloudProtocol = this.currentDevice.cloudProtocol
      } else if (this.currentGroup.groupID) {
        cloudProtocol = this.currentGroup.cloudProtocol
      }
      return cloudProtocol !== this.$variable.cloudProtocol.LWM2M
    },
    showLwM2M() {
      let cloudProtocol = 0
      if (this.currentDevice.deviceID) {
        cloudProtocol = this.currentDevice.cloudProtocol
      } else if (this.currentGroup.groupID) {
        cloudProtocol = this.currentGroup.cloudProtocol
      }
      return cloudProtocol === this.$variable.cloudProtocol.LWM2M
    },
  },

  methods: {
    save() {
      if (this.commandType === 0) {
        this.$refs.instructionCustom.save()
      } else if (this.commandType === 1) {
        this.$refs.instructionPlatform.save()
      } else if (this.commandType === 2) {
        this.$refs.instructionOta.save()
      } else if (this.commandType === 3) {
        this.$refs.instructionLwm2m.save()
      }
    },
    hideDialog() {
      this.$emit('update:visible', false)
    },
  },
}
</script>


<style lang="scss">
.emq-dialog.instructions-dialog-view {
  .el-dialog__headerbtn {
    top: 14px;
  }
  .el-dialog__body {
    padding: 8px 20px 20px 20px;
    .command-type {
      margin: 10px 0;
    }
    .el-form-item.is-required:not(.is-no-asterisk)
    >.el-form-item__label:before {
      color: var(--color-main-pink);
    }
    .CodeMirror-scroll {
      margin-right: 0;
    }
    .required {
      padding-left: 2px;
      color: var(--color-main-pink);
      font-size: 16px;
    }
    .form-item {
      margin: 20px 0 10px 0;
      label {
        float: left;
      }
    }
    .form-tips {
      color: var(--color-text-light);
      .el-icon-warning {
        margin-left: 15px;
        color: #ffc741;
      }
    }
  }
}
</style>
