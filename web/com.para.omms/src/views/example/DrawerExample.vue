<template>
  <div>
    <el-button type="primary" @click="openDrawer">打开抽屉</el-button>
    
    <CommonDrawer
      v-model="drawerVisible"
      title="用户详情"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    >
      <div class="drawer-content">
        <el-form label-width="100px">
          <el-form-item label="用户名">
            <el-input v-model="form.username" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="form.email" />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="form.phone" />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="form.role" style="width: 100%">
              <el-option label="管理员" value="admin" />
              <el-option label="普通用户" value="user" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
    </CommonDrawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// 控制抽屉显示
const drawerVisible = ref(false)

// 表单数据
const form = reactive({
  username: '',
  email: '',
  phone: '',
  role: 'user'
})

// 打开抽屉
const openDrawer = () => {
  drawerVisible.value = true
}

// 确认按钮事件
const handleConfirm = () => {
  console.log('提交表单', form)
  drawerVisible.value = false
}

// 取消按钮事件
const handleCancel = () => {
  console.log('取消操作')
}
</script>

<style scoped>
.drawer-content {
  padding: 20px;
}
</style>