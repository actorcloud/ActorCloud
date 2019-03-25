<template>
  <div class="forbidden">
    <img src="../assets/images/403.png" />
    <p>{{ $t('noAccess.access') }}</p>
  </div>
</template>


<script>
export default {
  name: 'forbidden',
}
</script>


<style lang="scss">
.forbidden {
  width: 600px;
  position: absolute;
  top: 50%;
  left: 50%;
  margin-left: 50px;
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
}
</style>
