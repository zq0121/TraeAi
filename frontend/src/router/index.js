import { createRouter, createWebHistory } from 'vue-router'
import store from '../store/index.js'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  {
    path: '/', component: () => import('../components/Layout.vue'), redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'detection/image', name: 'ImageDetection', component: () => import('../views/detection/ImageDetection.vue') },
      { path: 'detection/video', name: 'VideoDetection', component: () => import('../views/detection/VideoDetection.vue') },
      { path: 'detection/camera', name: 'CameraDetection', component: () => import('../views/detection/CameraDetection.vue') },
      { path: 'records', name: 'Records', component: () => import('../views/Records.vue') },
      { path: 'analysis', name: 'Analysis', component: () => import('../views/Analysis.vue') },

      { path: 'production', name: 'Production', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'production' } },
      { path: 'equipment', name: 'Equipment', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'equipment' } },
      { path: 'maintenance', name: 'Maintenance', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'maintenance' } },
      { path: 'material', name: 'Material', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'material' } },
      { path: 'warehouse', name: 'Warehouse', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'warehouse' } },
      { path: 'quality', name: 'Quality', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'quality' } },
      { path: 'energy', name: 'Energy', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'energy' } },
      { path: 'safety', name: 'Safety', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'safety' } },
      { path: 'order', name: 'Order', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'order' } },
      { path: 'iot', name: 'Iot', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'iot' } },
      { path: 'model', name: 'Model', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'model' } },
      { path: 'report', name: 'Report', component: () => import('../views/ModulePage.vue'), meta: { moduleKey: 'report' } },

      { path: 'system/users', name: 'UserManagement', component: () => import('../views/system/UserManagement.vue'), meta: { admin: true } },
      { path: 'system/roles', name: 'RoleManagement', component: () => import('../views/system/RoleManagement.vue'), meta: { admin: true } },
      { path: 'system/logs', name: 'Logs', component: () => import('../views/system/Logs.vue'), meta: { admin: true } },
      { path: 'system/settings', name: 'Settings', component: () => import('../views/system/Settings.vue'), meta: { admin: true } },
      { path: 'files/images', name: 'ImageFiles', component: () => import('../views/files/ImageFiles.vue') },
      { path: 'files/videos', name: 'VideoFiles', component: () => import('../views/files/VideoFiles.vue') }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  if (to.path !== '/login' && !store.getters.token) return next('/login')
  if (to.meta.admin && !store.getters.isAdmin) return next('/dashboard')
  next()
})

export default router
