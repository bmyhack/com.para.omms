<template>
  <el-drawer
    v-model="visible"
    :title="title"
    :size="size"
    :direction="direction"
    :before-close="handleClose"
    :destroy-on-close="destroyOnClose"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :with-header="withHeader"
    :append-to-body="appendToBody"
    :modal="modal"
    :custom-class="customClass"
  >
    <!-- 自定义头部 -->
    <template v-if="$slots.header" #header>
      <slot name="header"></slot>
    </template>
    
    <!-- 主要内容 -->
    <slot></slot>
    
    <!-- 底部操作区 -->
    <template v-if="$slots.footer || showFooter" #footer>
      <div class="drawer-footer">
        <slot name="footer">
          <el-button @click="handleCancel">{{ cancelText }}</el-button>
          <el-button type="primary" @click="handleConfirm" :loading="confirmLoading">
            {{ confirmText }}
          </el-button>
        </slot>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

// 定义组件属性
const props = defineProps({
  // 控制抽屉是否显示
  modelValue: {
    type: Boolean,
    default: false
  },
  // 抽屉标题
  title: {
    type: String,
    default: '详情'
  },
  // 抽屉宽度
  size: {
    type: [String, Number],
    default: '30%'
  },
  // 抽屉方向
  direction: {
    type: String,
    default: 'rtl', // 默认从右侧打开
    validator: (val: string) => ['ltr', 'rtl', 'ttb', 'btt'].includes(val)
  },
  // 是否显示底部
  showFooter: {
    type: Boolean,
    default: true
  },
  // 确认按钮文本
  confirmText: {
    type: String,
    default: '确定'
  },
  // 取消按钮文本
  cancelText: {
    type: String,
    default: '取消'
  },
  // 确认按钮加载状态
  confirmLoading: {
    type: Boolean,
    default: false
  },
  // 关闭时销毁内容
  destroyOnClose: {
    type: Boolean,
    default: false
  },
  // 点击遮罩关闭
  closeOnClickModal: {
    type: Boolean,
    default: true
  },
  // 按ESC关闭
  closeOnPressEscape: {
    type: Boolean,
    default: true
  },
  // 显示关闭按钮
  showClose: {
    type: Boolean,
    default: true
  },
  // 显示头部
  withHeader: {
    type: Boolean,
    default: true
  },
  // 追加到body
  appendToBody: {
    type: Boolean,
    default: false
  },
  // 是否需要遮罩层
  modal: {
    type: Boolean,
    default: true
  },
  // 自定义类名
  customClass: {
    type: String,
    default: ''
  }
})

// 定义事件
const emit = defineEmits([
  'update:modelValue',
  'open',
  'opened',
  'close',
  'closed',
  'cancel',
  'confirm'
])

// 内部可见性状态
const visible = ref(props.modelValue)

// 监听props变化
watch(
  () => props.modelValue,
  (val) => {
    visible.value = val
  }
)

// 监听内部状态变化
watch(
  () => visible.value,
  (val) => {
    emit('update:modelValue', val)
    if (!val) {
      emit('close')
    } else {
      emit('open')
    }
  }
)

// 关闭前的回调
const handleClose = (done: () => void) => {
  done()
}

// 取消按钮点击事件
const handleCancel = () => {
  visible.value = false
  emit('cancel')
}

// 确认按钮点击事件
const handleConfirm = () => {
  emit('confirm')
}
</script>

<style scoped>
.drawer-footer {
  display: flex;
  justify-content: flex-end;
  padding: 10px 20px;
  border-top: 1px solid #e4e7ed;
}
</style>