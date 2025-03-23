<template>
  <div class="dashboard-container">
    <!-- 欢迎卡片 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <div class="welcome-content">
            <div class="welcome-info">
              <h2>欢迎回来，管理员</h2>
              <p>今天是 {{ currentDate }}，祝您工作愉快！</p>
            </div>
            <div class="welcome-stats">
              <div class="stat-item">
                <el-icon><el-icon-alarm-clock /></el-icon>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.onlineTime }}</div>
                  <div class="stat-label">系统运行时间</div>
                </div>
              </div>
              <div class="stat-item">
                <el-icon><el-icon-view /></el-icon>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.visits }}</div>
                  <div class="stat-label">今日访问量</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据概览卡片 -->
    <el-row :gutter="20" class="dashboard-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="data-card server-card">
          <div class="data-card-content">
            <div class="card-icon">
              <el-icon><el-icon-monitor /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ stats.servers }}</div>
              <div class="card-label">服务器总数</div>
            </div>
          </div>
          <div class="card-footer">
            <span>在线: {{ stats.onlineServers }}</span>
            <span>离线: {{ stats.offlineServers }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="data-card alarm-card">
          <div class="data-card-content">
            <div class="card-icon">
              <el-icon><el-icon-warning /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ stats.alarms }}</div>
              <div class="card-label">告警总数</div>
            </div>
          </div>
          <div class="card-footer">
            <span>严重: {{ stats.criticalAlarms }}</span>
            <span>一般: {{ stats.normalAlarms }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="data-card repair-card">
          <div class="data-card-content">
            <div class="card-icon">
              <el-icon><el-icon-document /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ stats.repairs }}</div>
              <div class="card-label">维修工单</div>
            </div>
          </div>
          <div class="card-footer">
            <span>待处理: {{ stats.pendingRepairs }}</span>
            <span>已完成: {{ stats.completedRepairs }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="data-card user-card">
          <div class="data-card-content">
            <div class="card-icon">
              <el-icon><el-icon-user /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-value">{{ stats.users }}</div>
              <div class="card-label">系统用户</div>
            </div>
          </div>
          <div class="card-footer">
            <span>活跃: {{ stats.activeUsers }}</span>
            <span>今日新增: {{ stats.newUsers }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="dashboard-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>服务器资源使用率</span>
            </div>
          </template>
          <div class="chart-container" ref="resourceChartRef"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>告警趋势</span>
            </div>
          </template>
          <div class="chart-container" ref="alarmChartRef"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动和待办事项 -->
    <el-row :gutter="20" class="dashboard-row">
      <el-col :span="16">
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in activities"
              :key="index"
              :timestamp="activity.time"
              :type="activity.type"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="todo-card">
          <template #header>
            <div class="card-header">
              <span>待办事项</span>
            </div>
          </template>
          <el-table :data="todos" style="width: 100%">
            <el-table-column prop="title" label="任务"></el-table-column>
            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="scope">
                <el-tag :type="getPriorityType(scope.row.priority)">
                  {{ scope.row.priority }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { 
  Monitor as ElIconMonitor, 
  Warning as ElIconWarning,
  Document as ElIconDocument,
  User as ElIconUser,
  AlarmClock as ElIconAlarmClock,
  View as ElIconView
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 定义类型接口
interface StatsData {
  onlineTime: string;
  visits: number;
  servers: number;
  onlineServers: number;
  offlineServers: number;
  alarms: number;
  criticalAlarms: number;
  normalAlarms: number;
  repairs: number;
  pendingRepairs: number;
  completedRepairs: number;
  users: number;
  activeUsers: number;
  newUsers: number;
}

interface Activity {
  content: string;
  time: string;
  type: string;
}

interface TodoItem {
  title: string;
  priority: string;
}

// 当前日期
const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long'
})

// 统计数据
const stats = reactive<StatsData>({
  onlineTime: '23天14小时',
  visits: 1254,
  servers: 128,
  onlineServers: 120,
  offlineServers: 8,
  alarms: 24,
  criticalAlarms: 5,
  normalAlarms: 19,
  repairs: 36,
  pendingRepairs: 12,
  completedRepairs: 24,
  users: 56,
  activeUsers: 32,
  newUsers: 3
})

// 最近活动
const activities: Activity[] = [
  { content: '服务器GPU-01温度过高，已触发告警', time: '10分钟前', type: 'warning' },
  { content: '管理员更新了系统配置', time: '30分钟前', type: 'primary' },
  { content: '新增维修工单：存储设备故障', time: '1小时前', type: 'info' },
  { content: '用户张三登录系统', time: '2小时前', type: 'info' },
  { content: '服务器CPU-05完成维护，恢复上线', time: '3小时前', type: 'success' }
]

// 待办事项
const todos: TodoItem[] = [
  { title: '处理GPU-01温度告警', priority: '高' },
  { title: '审核新增用户申请', priority: '中' },
  { title: '更新服务器固件', priority: '中' },
  { title: '备份数据库', priority: '低' }
]

// 获取优先级对应的标签类型
const getPriorityType = (priority: string) => {
  const map: Record<string, string> = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return map[priority] || 'info'
}

// 图表引用
const resourceChartRef = ref<HTMLElement | null>(null)
const alarmChartRef = ref<HTMLElement | null>(null)

// 初始化图表
onMounted(() => {
  // 保持原有代码不变
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-row {
  margin-bottom: 20px;
}

.welcome-card {
  margin-bottom: 20px;
  background: linear-gradient(90deg, #3494e6 0%, #ec6ead 100%);
  color: white;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-info h2 {
  margin-top: 0;
  font-size: 24px;
}

.welcome-stats {
  display: flex;
  gap: 30px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-item .el-icon {
  font-size: 24px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.data-card {
  height: 160px;
  overflow: hidden;
  position: relative;
}

.data-card-content {
  display: flex;
  align-items: center;
  padding: 20px;
}

.card-icon {
  font-size: 48px;
  margin-right: 20px;
  color: #3494e6;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #303133;
}

.card-label {
  font-size: 16px;
  color: #909399;
}

.card-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 10px 20px;
  background-color: #f5f7fa;
  border-top: 1px solid #ebeef5;
  color: #606266;
}

.server-card .card-icon {
  color: #3494e6;
}

.alarm-card .card-icon {
  color: #e6a23c;
}

.repair-card .card-icon {
  color: #409eff;
}

.user-card .card-icon {
  color: #67c23a;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 350px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-card, .todo-card {
  height: 400px;
  overflow-y: auto;
}

/* 自定义滚动条 */
.activity-card::-webkit-scrollbar,
.todo-card::-webkit-scrollbar {
  width: 6px;
}

.activity-card::-webkit-scrollbar-thumb,
.todo-card::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.activity-card::-webkit-scrollbar-track,
.todo-card::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .welcome-stats {
    margin-top: 15px;
  }
  
  .data-card {
    margin-bottom: 20px;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>