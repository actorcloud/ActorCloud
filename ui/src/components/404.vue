<template>
  <div class="not-found">
    <img src="../assets/images/404.png" />
    <p>{{ $t('oper.none') }}</p>
    <emq-button @click="$router.push({ path: '/'  })">{{ $t('oper.back') }}</emq-button>
  </div>
</template>


<script>
export default {
  name: 'NotFound',
}
</script>


<style lang="scss">
@import "~@/assets/scss/variable.scss";

#app {
  background-color: #F0F1F7;
}
.not-found {
   width: 35%;
   position: absolute;
   top: 40%;
   left: 50%;
   transform: translate(-50%, -50%);

   img {
     width: 100%;
   }
   p {
     font-size: 26px;
     font-weight: bolder;
     text-align: center;
     color: #444;
     margin: 4px 0;
   }
   .emq-button {
     position: absolute;
     left: 50%;
     transform: translateX(-50%);
     margin-top: 30px;
     width: 110px;
   }
}
</style>
