import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import './assets/styles/global.css'  // 引入全局样式
import CommonDrawer from './components/CommonDrawer.vue'

// 创建应用实例
const app = createApp(App)

app.use(router)
app.use(ElementPlus, {
  locale: zhCn
})

// 注册全局组件
app.component('CommonDrawer', CommonDrawer)

app.mount('#app')