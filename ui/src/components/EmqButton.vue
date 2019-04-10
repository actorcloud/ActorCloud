<template>
  <el-button
    class="emq-button"
    size="small"
    type="success"
    round
    :loading="loading"
    :disabled="disabled"
    :style="{ float: float }"
    @click="handleClick">
    <i :class="iconClass"></i>
    <span v-if="$slots.default">
      <!-- Custom button content -->
      <slot></slot>
    </span>
  </el-button>
</template>


<script>
export default {
  name: 'emq-button',

  props: {
    // Button icon
    icon: {
      type: String,
      default: '',
    },
    // Button float property
    float: {
      type: String,
      default: 'right',
    },
    // Button status
    loading: Boolean,
    // Whether the available
    disabled: Boolean,
  },

  computed: {
    iconClass() {
      switch (this.icon) {
        case 'create':
          return 'el-icon-plus'
        case 'save':
          return 'el-icon-check'
        default:
          return ''
      }
    },
  },

  methods: {
    handleClick(event) {
      // Triggered when the button is clicked
      this.$emit('click', event)
    },
  },
}
</script>


<style lang="scss">
.emq-button {
  background: #2fc285;
  border-color: #2fc285;
  min-width: 80px;
  font-size: 14px;
  &:not(.create-btn) {
    box-shadow: 0 3px 10px rgba(47, 194, 133, 0.6);
  }
  &:hover {
    background: #23c890;
    border-color: #23c890;
  }
  i {
    font-weight: 600;
  }
  &.disabled {
    background-color: #D7DAE1;
    border-color: #D7DAE1;
    box-shadow: 0 0 2px #D7DAE1;
  }

  @media screen and (min-width: 1366px) {
    border-radius: 38px;
    height: 38px;
    line-height: 20px;
    min-width: 102px;
  }
}
</style>
