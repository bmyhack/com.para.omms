import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../layout/index.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/index.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'user',
        name: 'user',
        component: () => import('../views/user/index.vue'),
        meta: { title: '用户管理', icon: 'user' }
      },
      {
        path: 'role',
        name: 'role',
        component: () => import('../views/role/index.vue'),
        meta: { title: '角色管理', icon: 'role' }
      },
      {
        path: 'permission',
        name: 'permission',
        component: () => import('../views/permission/index.vue'),
        meta: { title: '权限管理', icon: 'permission' }
      },
      
      // 404页面路由，放在children中，这样会在主布局内显示
      {
        path: ':pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('../views/error/404.vue'),
        meta: { title: '404' }
      }
    ]
  },
  
  // 登录页面路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router