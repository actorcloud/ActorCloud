<template>
<div></div>
</template>

<script>
export default {
  data() {
    return {
      data: undefined,
    }
  },
  created() {
    this.$router.push(this.$route.query.link)
  },
}
</script>
