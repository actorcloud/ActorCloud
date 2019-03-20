<template>
  <transition class="rightbar-pop-view" name="pop">
    <!-- 将内容插入此可直接生成右侧弹出特效 -->
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
