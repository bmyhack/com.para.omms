<template>
  <div class="role-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button type="primary" @click="dialogVisible = true">
            新增角色
          </el-button>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="角色名称">
          <el-input v-model="searchForm.name" placeholder="请输入角色名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 表格区域 -->
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="createdAt" label="创建时间" />
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="success" @click="handlePermission(scope.row)">权限设置</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页区域 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
      
      <!-- 新增/编辑角色对话框 -->
      <el-dialog v-model="dialogVisible" :title="dialogType === 'add' ? '新增角色' : '编辑角色'">
        <el-form :model="form" label-width="80px">
          <el-form-item label="角色名称">
            <el-input v-model="form.name" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="form.description" type="textarea" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitForm">确定</el-button>
          </span>
        </template>
      </el-dialog>
      
      <!-- 权限设置对话框 -->
      <el-dialog v-model="permissionDialogVisible" title="权限设置">
        <el-tree
          ref="permissionTree"
          :data="permissionData"
          show-checkbox
          node-key="id"
          :default-checked-keys="checkedPermissions"
          :props="{ label: 'name' }"
        />
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="permissionDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="savePermissions">保存</el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// 搜索表单
const searchForm = reactive({
  name: ''
})

// 表格数据
const tableData = ref([
  {
    id: 1,
    name: '管理员',
    description: '系统管理员',
    createdAt: '2023-01-01 00:00:00'
  },
  {
    id: 2,
    name: '普通用户',
    description: '普通用户',
    createdAt: '2023-01-01 00:00:00'
  }
])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)

// 角色对话框
const dialogVisible = ref(false)
const dialogType = ref('add')
const form = reactive({
  id: 0,
  name: '',
  description: ''
})

// 权限对话框
const permissionDialogVisible = ref(false)
const permissionTree = ref(null)
const currentRoleId = ref(0)
const permissionData = ref([
  {
    id: 1,
    name: '用户管理',
    children: [
      { id: 11, name: '查看用户' },
      { id: 12, name: '创建用户' },
      { id: 13, name: '编辑用户' },
      { id: 14, name: '删除用户' }
    ]
  },
  {
    id: 2,
    name: '角色管理',
    children: [
      { id: 21, name: '查看角色' },
      { id: 22, name: '创建角色' },
      { id: 23, name: '编辑角色' },
      { id: 24, name: '删除角色' }
    ]
  }
])
const checkedPermissions = ref([11, 21])

// 方法
const handleSearch = () => {
  // 实现搜索逻辑
}

const resetSearch = () => {
  searchForm.name = ''
  handleSearch()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  // 重新加载数据
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  // 重新加载数据
}

const handleEdit = (row: any) => {
  dialogType.value = 'edit'
  form.id = row.id
  form.name = row.name
  form.description = row.description
  dialogVisible.value = true
}

const handleDelete = (row: any) => {
  // 实现删除逻辑
}

const submitForm = () => {
  // 实现表单提交逻辑
  dialogVisible.value = false
}

const handlePermission = (row: any) => {
  currentRoleId.value = row.id
  // 加载角色的权限
  permissionDialogVisible.value = true
}

const savePermissions = () => {
  // 保存权限设置
  permissionDialogVisible.value = false
}
</script>

<style scoped>
.role-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>