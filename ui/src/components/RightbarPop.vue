<template>
  <transition class="rightbar-pop-view" name="pop">
    <!-- Insert content into this to directly generate a pop-up effect on the right -->
    <slot></slot>
  </transition>
</template>


<script>
export default {
  name: 'rightbar-pop-view',
}
</script>


<style lang="scss">
.pop-enter-active {
  animation: rightbarPop .4s;
}
.pop-leave-active {
  animation: rightbarPop .4s reverse;
}
.rightbar-pop-view {
  @keyframes rightbarPop {
    from {
      right: -316px;
    }
    to {
      right: 0;
    }
  }
}
</style>
