<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">页面未找到</h2>
      <p class="error-desc">抱歉，您访问的页面不存在或已被移除</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
}

.not-found-content {
  max-width: 500px;
}

.error-code {
  font-size: 120px;
  margin: 0;
  background: linear-gradient(90deg, #3494e6, #ec6ead);
  background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
}

.error-title {
  font-size: 32px;
  margin: 20px 0;
  color: #303133;
}

.error-desc {
  font-size: 16px;
  color: #909399;
  margin-bottom: 30px;
}
</style>