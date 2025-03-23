<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo-container">
        <h1 class="logo-text" v-if="!isCollapse">OMMS</h1>
        <h1 class="logo-text logo-collapsed" v-else>O</h1>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        :collapse="isCollapse"
        background-color="#1e3c72"
        text-color="#bfcbd9"
        active-text-color="#ffffff"
        router
      >
        <el-menu-item index="dashboard">
          <el-icon><el-icon-odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        
        <!-- 服务器管理菜单组 -->
        <el-sub-menu index="server">
          <template #title>
            <el-icon><el-icon-monitor /></el-icon>
            <span>服务器管理</span>
          </template>
          <el-menu-item index="gpu">
            <el-icon><el-icon-cpu /></el-icon>
            <span>GPU管理</span>
          </el-menu-item>
          <el-menu-item index="cpu">
            <el-icon><el-icon-cpu /></el-icon>
            <span>CPU管理</span>
          </el-menu-item>
          <el-menu-item index="storage">
            <el-icon><el-icon-files /></el-icon>
            <span>存储管理</span>
          </el-menu-item>
        </el-sub-menu>
        
        <!-- 告警监控 -->
        <el-menu-item index="alarm">
          <el-icon><el-icon-warning /></el-icon>
          <span>告警监控</span>
        </el-menu-item>
        
        <!-- 维修工单菜单组 -->
        <el-sub-menu index="repair">
          <template #title>
            <el-icon><el-icon-document /></el-icon>
            <span>维修工单</span>
          </template>
          <el-menu-item index="repair-pending">
            <el-icon><el-icon-timer /></el-icon>
            <span>未处理</span>
          </el-menu-item>
          <el-menu-item index="repair-processing">
            <el-icon><el-icon-loading /></el-icon>
            <span>处理中</span>
          </el-menu-item>
          <el-menu-item index="repair-completed">
            <el-icon><el-icon-circle-check /></el-icon>
            <span>已完成</span>
          </el-menu-item>
        </el-sub-menu>
        
        <!-- 基础设置菜单组 -->
        <el-sub-menu index="basic">
          <template #title>
            <el-icon><el-icon-tools /></el-icon>
            <span>基础设置</span>
          </template>
          <el-menu-item index="device">
            <el-icon><el-icon-box /></el-icon>
            <span>设备管理</span>
          </el-menu-item>
          <el-menu-item index="supplier">
            <el-icon><el-icon-office-building /></el-icon>
            <span>供应商管理</span>
          </el-menu-item>
          <el-menu-item index="model">
            <el-icon><el-icon-notebook /></el-icon>
            <span>设备型号</span>
          </el-menu-item>
        </el-sub-menu>
        
        <!-- 系统管理菜单组 -->
        <el-sub-menu index="system">
          <template #title>
            <el-icon><el-icon-setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="user">
            <el-icon><el-icon-user /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="role">
            <el-icon><el-icon-key /></el-icon>
            <span>角色管理</span>
          </el-menu-item>
          <el-menu-item index="permission">
            <el-icon><el-icon-lock /></el-icon>
            <span>权限管理</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container class="main-content">
      <!-- 头部 -->
      <el-header height="60px" class="header">
        <div class="header-left">
          <el-icon class="toggle-sidebar" @click="toggleSidebar">
            <el-icon-fold v-if="!isCollapse" />
            <el-icon-expand v-else />
          </el-icon>
          
          <!-- 添加面包屑导航 -->
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute">{{ currentRoute }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              管理员 <el-icon><el-icon-arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 内容区 -->
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>
    
    <!-- 添加个人信息抽屉 -->
    <CommonDrawer
      v-model="profileDrawerVisible"
      title="个人信息"
      @confirm="saveProfile"
      @cancel="profileDrawerVisible = false"
    >
      <div class="profile-content">
        <el-form label-width="80px">
          <el-form-item label="用户名">
            <el-input v-model="userProfile.username" disabled />
          </el-form-item>
          <el-form-item label="姓名">
            <el-input v-model="userProfile.name" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="userProfile.email" />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="userProfile.phone" />
          </el-form-item>
          <el-form-item label="角色">
            <el-input v-model="userProfile.role" disabled />
          </el-form-item>
        </el-form>
      </div>
    </CommonDrawer>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Odometer as ElIconOdometer,
  User as ElIconUser,
  Key as ElIconKey,
  Lock as ElIconLock,
  Fold as ElIconFold,
  Expand as ElIconExpand,
  ArrowDown as ElIconArrowDown,
  Setting as ElIconSetting,
  Monitor as ElIconMonitor,
  Warning as ElIconWarning,
  Document as ElIconDocument,
  Tools as ElIconTools,
  Box as ElIconBox,
  OfficeBuilding as ElIconOfficeBuilding,
  Notebook as ElIconNotebook,
  Files as ElIconFiles,
  Cpu as ElIconCpu,
  Timer as ElIconTimer,
  Loading as ElIconLoading,
  CircleCheck as ElIconCircleCheck
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 控制侧边栏折叠状态
const isCollapse = ref(false)

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

// 获取当前路由
const route = useRoute()
const router = useRouter()

// 计算当前激活的菜单项
  const activeMenu = computed(() => {
    const path = route.path.split('/')[1] || 'dashboard'
    // 如果是子菜单，返回对应的路径
    const subMenuItems = [
      'user', 'role', 'permission',
      'gpu', 'cpu', 'storage',
      'device', 'supplier', 'model',
      'repair-pending', 'repair-processing', 'repair-completed'
    ]
    if(subMenuItems.includes(path)) {
      return path
    }
    return path
  })

// 简化面包屑实现，直接使用路由名称
const currentRoute = computed(() => {
  const pathSegment = route.path.split('/')[1]
  if (!pathSegment) return '仪表盘'
  
  const routeMap: Record<string, string> = {
    'dashboard': '仪表盘',
    'user': '用户管理',
    'role': '角色管理',
    'permission': '权限管理',
    'system': '系统管理',
    'server': '服务器管理',
    'gpu': 'GPU管理',
    'cpu': 'CPU管理',
    'storage': '存储管理',
    'alarm': '告警监控',
    'repair': '维修工单',
    'repair-pending': '未处理工单',
    'repair-processing': '处理中工单',
    'repair-completed': '已完成工单',
    'basic': '基础设置',
    'device': '设备管理',
    'supplier': '供应商管理',
    'model': '设备型号'
  }
  
  return routeMap[pathSegment] || pathSegment
})

// 个人信息抽屉控制
const profileDrawerVisible = ref(false)

// 用户个人信息
const userProfile = reactive({
  username: 'admin',
  name: '系统管理员',
  email: 'admin@example.com',
  phone: '13800138000',
  role: '超级管理员'
})

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  if (command === 'profile') {
    profileDrawerVisible.value = true
  } else if (command === 'logout') {
    // 这里可以添加退出登录的逻辑
    ElMessage.success('退出登录成功')
    router.push('/login')
  }
}

// 保存个人信息
const saveProfile = () => {
  // 这里可以添加保存个人信息的逻辑，例如发送API请求
  ElMessage.success('个人信息保存成功')
  profileDrawerVisible.value = false
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
  transition: width 0.3s;
  overflow: hidden;
  position: relative;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-text {
  color: white;
  font-size: 24px;
  margin: 0;
  font-weight: bold;
}

.logo-collapsed {
  font-size: 28px;
}

.el-menu-vertical {
  border-right: none;
}

.el-menu-vertical:not(.el-menu--collapse) {
  width: 220px;
}

/* 子菜单样式调整 */
:deep(.el-sub-menu__title) {
  color: #bfcbd9 !important;
}

:deep(.el-sub-menu__title:hover) {
  background-color: #3a5692 !important;
}

:deep(.el-menu--inline) {
  background-color: #2a4682 !important; /* 调整为更浅的蓝色 */
}

:deep(.el-menu--inline .el-menu-item) {
  background-color: #2a4682 !important;
}

/* 所有菜单项的悬停效果 */
:deep(.el-menu-item:hover) {
  background-color: #3a5692 !important; /* 悬停时更浅一些 */
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #3494e6, #ec6ead) !important;
}

.header {
  background: linear-gradient(90deg, #3494e6 0%, #ec6ead 100%);
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: white;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
}

.toggle-sidebar {
  font-size: 20px;
  cursor: pointer;
  margin-right: 15px;
  color: white;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: white;
}

.content {
  background-color: #f0f2f5;
  padding: 20px;
}

.breadcrumb {
  margin-left: 15px;
}

/* 修改面包屑颜色，使其在渐变背景上更易读 */
:deep(.el-breadcrumb__item) {
  color: rgba(255, 255, 255, 0.7);
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: white;
  font-weight: 600;
}

:deep(.el-breadcrumb__inner a) {
  color: rgba(255, 255, 255, 0.7);
  font-weight: normal;
}

:deep(.el-breadcrumb__inner a:hover) {
  color: white;
}

:deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.7);
}
</style>

<style scoped>
/* 保持原有样式不变 */

.profile-content {
  padding: 20px;
}
</style>