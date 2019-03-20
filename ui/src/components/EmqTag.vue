<template>
  <div class="emq-tag">
    <div class="emq-tag__triangle"></div>
    <span class="emq-tag__content">
      <!-- Slot content is displayed tag content -->
      <slot></slot>
    </span>
  </div>
</template>


<script>
export default {
  name: 'emq-tag',
}
</script>


<style lang="scss">
@import "~@/assets/scss/variable.scss";

.emq-tag {
  display: flex;
  .emq-tag__triangle {
    border: 13px solid transparent;
    border-right: 13px solid var(--color-bg-tag);
    width: 0;
    height: 0;
  }
  .emq-tag__content {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    max-width: 120px;
    height: 26px;
    background: var(--color-bg-tag);
    font-size: 14px;
    color: var(--color-text-lighter);
    padding: 0 10px 0 6px;
    &::before {
      content: '';
      position: relative;
      right: 6px;
      bottom: 1px;
      display: inline-block;
      height: 7px;
      width: 7px;
      border-radius: 4px;
      background-color: var(--color-bg-gray);
    }
  }
}
</style>
