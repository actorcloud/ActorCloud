<template>
  <div class="emq-details-page-head">
    <el-row type="flex" justify="space-between" align="middle">
      <el-col :span="18">
        <!-- 顶部的面包屑 -->
        <slot name="breadcrumb"></slot>
      </el-col>
      <el-col :span="6">
        <!-- 顶部的标签 -->
        <slot name="tag"></slot>
      </el-col>
    </el-row>
  </div>
</template>


<script>
export default {
  name: 'emq-details-page-head',
}
</script>


<style lang="scss">
.emq-details-page-head {
  padding-top: 20px;
  margin-bottom: 20px;
  .el-breadcrumb {
    font-size: 18px;
    min-height: 32px;
    line-height: 32px;
    @media screen and (min-width: 1366px) {
      min-height: 38px;
      line-height: 38px;
    }
    .el-breadcrumb__inner, .el-breadcrumb__inner a {
      font-weight: 400;
      color: var(--color-text-lighter);
    }
    .el-breadcrumb__item:last-child .el-breadcrumb__inner,
    .el-breadcrumb__item:last-child .el-breadcrumb__inner a,
    .el-breadcrumb__item:last-child .el-breadcrumb__inner a:hover,
    .el-breadcrumb__item:last-child .el-breadcrumb__inner:hover {
      color: var(--color-main-green);
    }
    .el-breadcrumb__inner.is-link, .el-breadcrumb__inner a {
      color: var(--color-text-light);
    }
  }
  .emq-tag-group {
    position: absolute;
    right: 0;
    top: 6px;
    display: flex;
  }
}
</style>
