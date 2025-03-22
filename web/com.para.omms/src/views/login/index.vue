<template>
  <div class="login-container">
    <div class="login-box">
      <!-- 左侧信息展示区 -->
      <div class="login-left">
        <div class="left-content">
          <h1 class="system-name">OMMS</h1>
          <h2 class="system-desc">运维管理与监控系统</h2>
          <p class="system-intro">
            为企业提供全方位的运维管理与监控解决方案，
            助力企业数字化转型，提升运维效率。
          </p>
          <div class="feature-list">
            <div class="feature-item">
              <el-icon><el-icon-monitor /></el-icon>
              <span>实时监控</span>
            </div>
            <div class="feature-item">
              <el-icon><el-icon-warning /></el-icon>
              <span>告警管理</span>
            </div>
            <div class="feature-item">
              <el-icon><el-icon-data-analysis /></el-icon>
              <span>数据分析</span>
            </div>
            <div class="feature-item">
              <el-icon><el-icon-setting /></el-icon>
              <span>配置管理</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧登录表单区 -->
      <div class="login-right">
        <div class="login-form">
          <div class="form-header">
            <h2>系统登录</h2>
            <p>欢迎回来，请登录您的账号</p>
          </div>
          
          <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef">
            <el-form-item prop="username">
              <el-input 
                v-model="loginForm.username" 
                placeholder="用户名"
                :prefix-icon="User"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="密码"
                :prefix-icon="Lock"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <a href="javascript:void(0)" class="forgot-password">忘记密码？</a>
            </div>
            <el-form-item>
              <el-button 
                type="primary" 
                :loading="loading" 
                class="login-button" 
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
          
          <div class="form-footer">
            <p>© 2023 OMMS 运维管理与监控系统</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, 
  Lock, 
  Monitor as ElIconMonitor, 
  Warning as ElIconWarning,
  DataAnalysis as ElIconDataAnalysis,
  Setting as ElIconSetting
} from '@element-plus/icons-vue'

const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)
const rememberMe = ref(false)

// 登录表单
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度应在3到50个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
}

// 登录方法
const handleLogin = () => {
  loginFormRef.value.validate((valid: boolean) => {
    if (valid) {
      loading.value = true
      
      // 这里应该调用登录API
      setTimeout(() => {
        loading.value = false
        
        // 模拟登录成功
        localStorage.setItem('token', 'mock-token')
        ElMessage.success('登录成功')
        router.push('/')
      }, 1000)
    } else {
      return false
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
}

.login-box {
  display: flex;
  width: 900px;
  height: 560px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

/* 左侧样式 */
.login-left {
  width: 45%;
  background: linear-gradient(135deg, #3494e6 0%, #ec6ead 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.left-content {
  max-width: 100%;
}

.system-name {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 10px;
}

.system-desc {
  font-size: 20px;
  margin-bottom: 20px;
  opacity: 0.9;
}

.system-intro {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 30px;
  opacity: 0.8;
}

.feature-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.feature-item .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

/* 右侧样式 */
.login-right {
  width: 55%;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-form {
  width: 80%;
  max-width: 350px;
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-header h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 10px;
}

.form-header p {
  font-size: 14px;
  color: #909399;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
}

.forgot-password {
  color: #409EFF;
  text-decoration: none;
}

.login-button {
  width: 100%;
  height: 40px;
  border-radius: 4px;
}

.form-footer {
  margin-top: 30px;
  text-align: center;
  font-size: 12px;
  color: #909399;
}
</style>